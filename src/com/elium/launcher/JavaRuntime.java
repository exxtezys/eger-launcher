package com.elium.launcher;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Downloads Eclipse Temurin JRE 21 into <gameDir>/runtime if not present. */
public final class JavaRuntime {
    private static final String URL = adoptiumUrl();

    /**
     * Версия Temurin для зеркал (они не умеют «latest»). Формат как у Adoptium: 21.0.13+9.
     * Официальный адрес по-прежнему берёт последнюю версию; зеркала — эту.
     */
    static final String MIRROR_VERSION = "21.0.13+9";

    private static String osName() {
        String os = System.getProperty("os.name", "").toLowerCase();
        return os.contains("win") ? "windows" : os.contains("mac") ? "mac" : "linux";
    }

    private static String archName() {
        return System.getProperty("os.arch", "").toLowerCase().contains("aarch64") ? "aarch64" : "x64";
    }

    private static String adoptiumUrl() {
        return "https://api.adoptium.net/v3/binary/latest/21/ga/" + osName() + "/" + archName() + "/jre/hotspot/normal/eclipse";
    }

    /**
     * Зеркала JRE для конкретной версии. Только zip (Windows): на Linux/macOS Temurin идёт в tar.gz,
     * а распаковываем мы zip, так что там зеркал нет.
     */
    public static List<String> mirrorUrls(String version, String os, String arch) {
        if (version == null || !version.matches("21\\.\\d+\\.\\d+\\+\\d+")) return List.of();
        if (!"windows".equals(os)) return List.of();
        String under = version.replace('+', '_');
        String file = "OpenJDK21U-jre_" + arch + "_" + os + "_hotspot_" + under + ".zip";
        String tag = "jdk-" + version.replace("+", "%2B");
        return List.of(
                "https://mirrors.tuna.tsinghua.edu.cn/Adoptium/21/jre/" + arch + "/" + os + "/" + file,
                "https://gh-proxy.com/https://github.com/adoptium/temurin21-binaries/releases/download/" + tag + "/" + file);
    }

    private JavaRuntime() {}

    public static Path ensure(Path gameDir, Net.Progress p) throws IOException {
        Path dir = gameDir.resolve("runtime").resolve("jre21");
        p.stage("java");
        Path java = find(dir);
        if (java != null) return java;
        p.update("Поиск Java 21 на компьютере...", 0, 0);
        java = LocalCache.findJava21();
        if (java != null && Files.isRegularFile(java.resolveSibling(javaExeName()))) return java;

        Path zip = gameDir.resolve("runtime").resolve("jre21.zip");
        if (Net.mirrorsEnabled()) {
            for (String m : mirrorUrls(MIRROR_VERSION, osName(), archName())) Net.addMirror(URL, m);
        }
        Net.downloadOne("Скачивание Java 21", new Net.Task(URL, zip, null, -1), p);
        p.update("Распаковка Java 21...", 0, 0);
        p.bytes(-1, -1);
        Path tmp = dir.resolveSibling("jre21.tmp");
        deleteTree(tmp);
        unzip(zip, tmp, p);
        deleteTree(dir);
        Files.move(tmp, dir);
        Files.deleteIfExists(zip);
        p.file(null);
        java = find(dir);
        if (java == null) throw new IOException("java не найден после распаковки Java");
        return java;
    }

    private static Path find(Path dir) throws IOException {
        if (!Files.isDirectory(dir)) return null;
        try (Stream<Path> s = Files.walk(dir, 3)) {
            return s.filter(f -> f.getFileName().toString().equals(windows() ? "javaw.exe" : "java")
                            && f.getParent().getFileName().toString().equals("bin"))
                    .findFirst().orElse(null);
        }
    }

    private static void unzip(Path zip, Path to, Net.Progress p) throws IOException {
        Path root = to.toAbsolutePath().normalize();
        try (ZipInputStream in = new ZipInputStream(Files.newInputStream(zip))) {
            ZipEntry e;
            while ((e = in.getNextEntry()) != null) {
                if (!e.isDirectory()) p.file(e.getName().substring(e.getName().lastIndexOf('/') + 1));
                Path out = root.resolve(e.getName()).normalize();
                if (!out.startsWith(root)) throw new IOException("Bad zip entry: " + e.getName());
                if (e.isDirectory()) Files.createDirectories(out);
                else {
                    Files.createDirectories(out.getParent());
                    Files.copy(in, out, StandardCopyOption.REPLACE_EXISTING);
                }
            }
        }
    }

    private static String javaExeName() {
        return windows() ? "javaw.exe" : "java";
    }

    private static boolean windows() {
        return System.getProperty("os.name", "").toLowerCase().contains("win");
    }

    static void deleteTree(Path p) throws IOException {
        if (!Files.exists(p)) return;
        try (Stream<Path> s = Files.walk(p)) {
            for (Path f : s.sorted(java.util.Comparator.reverseOrder()).toList()) Files.delete(f);
        }
    }
}
