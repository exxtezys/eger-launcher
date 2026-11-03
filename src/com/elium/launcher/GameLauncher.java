package com.elium.launcher;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/** Builds the java command line from a Profile and starts the game. */
public final class GameLauncher {
    private GameLauncher() {}

    public static Process launch(Config cfg, Path javaw, GameInstaller.Profile prof,
                                 String nick, int ramMb, boolean connect) throws IOException {
        Path dir = cfg.gameDir;
        Path natives = dir.resolve("natives");
        Files.createDirectories(natives);

        Map<String, String> v = new HashMap<>();
        v.put("auth_player_name", nick);
        v.put("version_name", prof.id());
        v.put("game_directory", dir.toString());
        v.put("assets_root", dir.resolve("assets").toString());
        v.put("assets_index_name", prof.assetIndex());
        v.put("auth_uuid", offlineUuid(nick).toString().replace("-", ""));
        v.put("auth_access_token", "0");
        v.put("clientid", "0");
        v.put("auth_xuid", "0");
        v.put("user_type", "legacy");
        v.put("version_type", cfg.projectName);
        v.put("natives_directory", natives.toString());
        v.put("launcher_name", cfg.projectName);
        v.put("launcher_version", LauncherApp.VERSION);
        v.put("library_directory", dir.resolve("libraries").toString());
        v.put("classpath_separator", File.pathSeparator);
        v.put("classpath", prof.classpath().stream().map(Path::toString).collect(Collectors.joining(File.pathSeparator)));

        List<String> cmd = new ArrayList<>();
        cmd.add(javaw.toString());
        cmd.add("-Xmx" + ramMb + "M");
        cmd.add("-Xms" + Math.min(ramMb, 1024) + "M");
        cmd.add("-XX:+UseG1GC");
        cmd.add("-Dfile.encoding=UTF-8");
        for (String arg : cfg.extraJvmArgs().split("\\s+")) {
            if (!arg.isBlank()) cmd.add(arg);
        }
        addArgs(prof.jvmArgs(), v, cmd);
        cmd.add(prof.mainClass());
        addArgs(prof.gameArgs(), v, cmd);
        if (connect && !cfg.effectiveServerHost().isEmpty()) {
            cmd.add("--quickPlayMultiplayer");
            cmd.add(cfg.effectiveServerHost() + ":" + cfg.effectiveServerPort());
        }

        Files.writeString(dir.resolve("last-launch.txt"),
                String.join("\n", cmd).replace(v.get("classpath"), "<classpath>"), StandardCharsets.UTF_8);
        ProcessBuilder pb = new ProcessBuilder(cmd)
                .directory(dir.toFile())
                .redirectErrorStream(true);
        if (cfg.keepLogs()) {
            pb.redirectOutput(dir.resolve("game-output.log").toFile());
        } else {
            pb.redirectOutput(new java.io.File("NUL"));
        }
        return pb.start();
    }

    private static void addArgs(List<Object> args, Map<String, String> v, List<String> out) {
        for (Object a : args) {
            if (a instanceof String s) out.add(subst(s, v));
            else {
                Map<String, Object> m = Json.obj(a);
                if (!Rules.allowed(m.get("rules"))) continue;
                Object val = m.get("value");
                if (val instanceof String s) out.add(subst(s, v));
                else for (Object x : Json.arr(val)) out.add(subst(x.toString(), v));
            }
        }
    }

    private static String subst(String s, Map<String, String> v) {
        StringBuilder b = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            int st = s.indexOf("${", i);
            if (st < 0) { b.append(s, i, s.length()); break; }
            int en = s.indexOf('}', st);
            if (en < 0) { b.append(s, i, s.length()); break; }
            b.append(s, i, st);
            String key = s.substring(st + 2, en);
            b.append(v.getOrDefault(key, ""));
            i = en + 1;
        }
        return b.toString();
    }

    /** Same UUID the server computes for offline-mode players. */
    public static UUID offlineUuid(String nick) {
        return UUID.nameUUIDFromBytes(("OfflinePlayer:" + nick).getBytes(StandardCharsets.UTF_8));
    }
}
