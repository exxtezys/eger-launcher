package com.elium.launcher;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

/**
 * Admin tool: builds manifest.json for a modpack folder.
 * Usage: java -cp EliumLauncher.jar com.elium.launcher.MakeManifest <modpackFolder> [managedDir ...]
 * Folder layout mirrors the game dir (mods/, config/, resourcepacks/ ...). Upload the folder
 * together with the generated manifest.json and put its URL into launcher.properties (modpack.url).
 */
public final class MakeManifest {
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.out.println("Usage: MakeManifest <modpackFolder> [managedDir ...]   (default managed: mods)");
            return;
        }
        Path root = Path.of(args[0]).toAbsolutePath().normalize();
        List<Object> files = new ArrayList<>();
        try (Stream<Path> s = Files.walk(root)) {
            for (Path f : s.filter(Files::isRegularFile).sorted().toList()) {
                String rel = root.relativize(f).toString().replace('\\', '/');
                if (rel.equals("manifest.json")) continue;
                Map<String, Object> e = new LinkedHashMap<>();
                e.put("path", rel);
                e.put("sha1", Net.sha1(f));
                e.put("size", Files.size(f));
                files.add(e);
            }
        }
        List<Object> managed = new ArrayList<>();
        if (args.length > 1) managed.addAll(List.of(args).subList(1, args.length)); else managed.add("mods");
        Map<String, Object> man = new LinkedHashMap<>();
        man.put("managed", managed);
        man.put("files", files);
        Files.writeString(root.resolve("manifest.json"), Json.write(man), StandardCharsets.UTF_8);
        System.out.println("manifest.json: " + files.size() + " files, managed=" + managed);
    }
}
