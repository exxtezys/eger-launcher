package com.elium.launcher;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;

/**
 * Syncs the game dir with a remote manifest.json:
 * { "managed": ["mods"], "files": [ { "path": "mods/a.jar", "sha1": "...", "size": 123 } ] }
 * Files are fetched from <manifest dir>/<path> unless an explicit "url" is given.
 * Files inside "managed" folders that are NOT in the manifest are deleted (removes old/foreign mods).
 */
public final class ModpackSync {
    private ModpackSync() {}

    public static void sync(Config cfg, Net.Progress p) throws IOException {
        if (cfg.modpackUrl.isEmpty()) return;
        p.stage("modpack");
        p.update("Получение списка модов с сервера...", 0, 0);
        p.bytes(-1, -1);
        Map<String, Object> man;
        try {
            man = Json.obj(Json.parse(Net.getText(cfg.modpackUrl)));
        } catch (IOException e) {
            throw new IOException("Не удалось получить список модов с сервера (" + cfg.modpackUrl + ").\n"
                    + "Сервер выключен или раздача модов не запущена. Попробуйте позже.\n\n" + e.getMessage(), e);
        }
        URI base = URI.create(cfg.modpackUrl);
        Path root = cfg.gameDir.toAbsolutePath().normalize();

        List<Net.Task> tasks = new ArrayList<>();
        Set<Path> wanted = new HashSet<>();
        for (Object o : Json.arr(man.get("files"))) {
            Map<String, Object> f = Json.obj(o);
            String rel = Json.str(f, "path");
            Path target = root.resolve(rel).normalize();
            if (!target.startsWith(root)) throw new IOException("Недопустимый путь в манифесте: " + rel);
            wanted.add(target);
            String url = Json.str(f, "url");
            if (url == null) url = base.resolve(encode(rel)).toString();
            long size = f.get("size") instanceof Number n ? n.longValue() : -1;
            tasks.add(new Net.Task(url, target, Json.str(f, "sha1"), size));
        }

        for (Object o : Json.arr(man.get("managed"))) {
            Path dir = root.resolve(o.toString()).normalize();
            if (!dir.startsWith(root) || dir.equals(root) || !Files.isDirectory(dir)) continue;
            try (Stream<Path> s = Files.walk(dir)) {
                for (Path f : s.filter(Files::isRegularFile).toList()) {
                    if (!wanted.contains(f.toAbsolutePath().normalize())) Files.delete(f);
                }
            }
        }
        Net.downloadAll("Моды", tasks, p);
    }

    private static String encode(String rel) {
        StringBuilder b = new StringBuilder();
        for (String seg : rel.replace('\\', '/').split("/")) {
            if (b.length() > 0) b.append('/');
            b.append(java.net.URLEncoder.encode(seg, java.nio.charset.StandardCharsets.UTF_8).replace("+", "%20"));
        }
        return b.toString();
    }
}
