package com.elium.launcher;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Installs vanilla Minecraft + NeoForge into the game dir and builds a merged launch profile. */
public final class GameInstaller {
    private static final String MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json";
    private static final String NEO_META = "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml";
    private static final String NEO_MAVEN = "https://maven.neoforged.net/releases/net/neoforged/neoforge/";
    private static final String RESOURCES = "https://resources.download.minecraft.net/";

    /** Everything needed to build the java command line. */
    public record Profile(String id, String mainClass, List<Path> classpath,
                          List<Object> jvmArgs, List<Object> gameArgs, String assetIndex) {}

    private final Config cfg;
    private final Path dir;
    private final Path libs;

    public GameInstaller(Config cfg) {
        this.cfg = cfg;
        this.dir = cfg.gameDir;
        this.libs = dir.resolve("libraries");
    }

    public Profile install(Path javaw, Net.Progress p) throws IOException, InterruptedException {
        String mc = cfg.minecraftVersion;
        p.stage("game");
        Map<String, Object> vanilla = vanillaJson(mc, p);
        Path clientJar = dir.resolve("versions").resolve(mc).resolve(mc + ".jar");
        Map<String, Object> cd = Json.obj(Json.obj(vanilla.get("downloads")).get("client"));
        Net.downloadAll("Клиент Minecraft", List.of(new Net.Task(Json.str(cd, "url"), clientJar,
                Json.str(cd, "sha1"), ((Number) cd.get("size")).longValue())), p, dir);

        String neo = neoVersion(mc);
        String neoId = "neoforge-" + neo;
        Path neoJson = dir.resolve("versions").resolve(neoId).resolve(neoId + ".json");
        p.stage("neoforge");
        if (!Files.exists(neoJson)) runNeoInstaller(javaw, neo, p);
        Map<String, Object> forge = Json.obj(Json.parse(Files.readString(neoJson, StandardCharsets.UTF_8)));

        // Libraries: NeoForge first, vanilla after; first occurrence of group:artifact:classifier wins.
        Map<String, Path> cp = new LinkedHashMap<>();
        List<Net.Task> tasks = new ArrayList<>();
        collectLibs(forge, cp, tasks);
        collectLibs(vanilla, cp, tasks);
        Net.downloadAll("Библиотеки", tasks, p, dir);

        p.stage("assets");
        String assetId = downloadAssets(vanilla, p);

        // Vanilla client jar must NOT be on the classpath: NeoForge loads its own patched client
        // (it only needs versions/<mc>/<mc>.jar to exist on disk).
        List<Path> classpath = new ArrayList<>(cp.values());

        List<Object> jvm = new ArrayList<>(Json.arr(Json.obj(vanilla.get("arguments")).get("jvm")));
        List<Object> game = new ArrayList<>(Json.arr(Json.obj(vanilla.get("arguments")).get("game")));
        Map<String, Object> fa = Json.obj(forge.get("arguments"));
        if (fa != null) {
            jvm.addAll(Json.arr(fa.get("jvm")));
            game.addAll(Json.arr(fa.get("game")));
        }
        return new Profile(neoId, Json.str(forge, "mainClass"), classpath, jvm, game, assetId);
    }

    private Map<String, Object> vanillaJson(String mc, Net.Progress p) throws IOException {
        Path file = dir.resolve("versions").resolve(mc).resolve(mc + ".json");
        if (!Files.exists(file)) {
            p.update("Получение версии " + mc + "...", 0, 1);
            Map<String, Object> man = Json.obj(Json.parse(Net.getText(MANIFEST)));
            Map<String, Object> entry = null;
            for (Object o : Json.arr(man.get("versions"))) {
                if (mc.equals(Json.str(Json.obj(o), "id"))) entry = Json.obj(o);
            }
            if (entry == null) throw new IOException("Версия " + mc + " не найдена у Mojang");
            Net.download(new Net.Task(Json.str(entry, "url"), file, Json.str(entry, "sha1"), -1));
        }
        return Json.obj(Json.parse(Files.readString(file, StandardCharsets.UTF_8)));
    }

    private String neoVersion(String mc) throws IOException {
        if (!cfg.neoforgeVersion.isEmpty() && !cfg.neoforgeVersion.equals("latest")) return cfg.neoforgeVersion;
        // "1.21.1" -> NeoForge "21.1.x"
        String[] parts = mc.split("\\.");
        String prefix = parts[1] + "." + (parts.length > 2 ? parts[2] : "0") + ".";
        Path cache = dir.resolve("versions").resolve("neoforge-latest.txt");
        try {
            String xml = Net.getText(NEO_META);
            Matcher m = Pattern.compile("<version>(" + Pattern.quote(prefix) + "\\d+)</version>").matcher(xml);
            String last = null;
            while (m.find()) last = m.group(1);
            if (last == null) throw new IOException("NeoForge для " + mc + " не найден");
            Files.createDirectories(cache.getParent());
            Files.writeString(cache, last);
            return last;
        } catch (IOException e) {
            if (Files.exists(cache)) return Files.readString(cache).trim(); // offline: reuse installed
            throw e;
        }
    }

    private void runNeoInstaller(Path javaw, String neo, Net.Progress p) throws IOException, InterruptedException {
        Path inst = dir.resolve("neoforge-installer.jar");
        Net.downloadOne("Скачивание установщика NeoForge " + neo,
                new Net.Task(NEO_MAVEN + neo + "/neoforge-" + neo + "-installer.jar", inst, null, -1), p);
        p.update("Установка NeoForge " + neo + "...", 0, 0);
        p.bytes(-1, -1);
        Path profiles = dir.resolve("launcher_profiles.json");
        if (!Files.exists(profiles)) Files.writeString(profiles, "{\"profiles\":{}}");
        Path java = javaw.resolveSibling("java.exe");
        Process proc = new ProcessBuilder(java.toString(), "-jar", inst.toString(), "--install-client", dir.toString())
                .directory(dir.toFile())
                .redirectErrorStream(true)
                .start();
        try (java.io.BufferedReader r = new java.io.BufferedReader(
                new java.io.InputStreamReader(proc.getInputStream(), StandardCharsets.UTF_8));
             java.io.Writer log = Files.newBufferedWriter(dir.resolve("neoforge-install.log"), StandardCharsets.UTF_8)) {
            String line;
            while ((line = r.readLine()) != null) {
                log.write(line);
                log.write(System.lineSeparator());
                String s = line.strip();
                if (!s.isEmpty()) p.file(s.length() > 90 ? s.substring(0, 87) + "..." : s);
            }
        }
        p.file(null);
        int code = proc.waitFor();
        Files.deleteIfExists(inst);
        Files.deleteIfExists(dir.resolve("neoforge-installer.jar.log"));
        if (code != 0) throw new IOException("Установщик NeoForge завершился с кодом " + code
                + " (см. " + dir.resolve("neoforge-install.log") + ")");
    }

    private void collectLibs(Map<String, Object> version, Map<String, Path> cp, List<Net.Task> tasks) {
        for (Object o : Json.arr(version.get("libraries"))) {
            Map<String, Object> lib = Json.obj(o);
            if (!Rules.allowed(lib.get("rules"))) continue;
            String name = Json.str(lib, "name");
            String[] c = name.split(":");
            String key = c[0] + ":" + c[1] + (c.length > 3 ? ":" + c[3] : "");
            if (cp.containsKey(key)) continue;

            Map<String, Object> dl = Json.obj(lib.get("downloads"));
            Map<String, Object> art = dl == null ? null : Json.obj(dl.get("artifact"));
            String path;
            String url;
            String sha1 = null;
            long size = -1;
            if (art != null && Json.str(art, "path") != null) {
                path = Json.str(art, "path");
                url = Json.str(art, "url");
                sha1 = Json.str(art, "sha1");
                if (art.get("size") instanceof Number n) size = n.longValue();
            } else {
                path = mavenPath(name);
                String base = Json.str(lib, "url");
                url = (base == null ? "https://libraries.minecraft.net/" : base.endsWith("/") ? base : base + "/") + path;
            }
            Path target = libs.resolve(path);
            cp.put(key, target);
            if (url != null && !url.isEmpty()) tasks.add(new Net.Task(url, target, sha1, size));
        }
    }

    static String mavenPath(String name) {
        String[] c = name.split(":");
        String ext = "jar";
        String last = c[c.length - 1];
        if (last.contains("@")) {
            ext = last.substring(last.indexOf('@') + 1);
            c[c.length - 1] = last.substring(0, last.indexOf('@'));
        }
        String file = c[1] + "-" + c[2] + (c.length > 3 ? "-" + c[3] : "") + "." + ext;
        return c[0].replace('.', '/') + "/" + c[1] + "/" + c[2] + "/" + file;
    }

    private String downloadAssets(Map<String, Object> vanilla, Net.Progress p) throws IOException {
        Map<String, Object> ai = Json.obj(vanilla.get("assetIndex"));
        String id = Json.str(ai, "id");
        Path idxFile = dir.resolve("assets").resolve("indexes").resolve(id + ".json");
        Net.downloadAll("Индекс ресурсов", List.of(new Net.Task(Json.str(ai, "url"), idxFile, Json.str(ai, "sha1"), -1)), p, dir);
        Map<String, Object> objects = Json.obj(Json.obj(Json.parse(Files.readString(idxFile, StandardCharsets.UTF_8))).get("objects"));
        List<Net.Task> tasks = new ArrayList<>();
        java.util.Set<String> seen = new java.util.HashSet<>();
        for (Object o : objects.values()) {
            Map<String, Object> obj = Json.obj(o);
            String hash = Json.str(obj, "hash");
            if (!seen.add(hash)) continue;
            String sub = hash.substring(0, 2) + "/" + hash;
            tasks.add(new Net.Task(RESOURCES + sub, dir.resolve("assets").resolve("objects").resolve(sub),
                    hash, ((Number) obj.get("size")).longValue()));
        }
        Net.downloadAll("Ресурсы игры", tasks, p, dir);
        return id;
    }
}
