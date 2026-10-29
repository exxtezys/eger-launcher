package com.elium.launcher;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

/**
 * Reuses Minecraft files already on this PC (other launchers keep the same libraries/ and assets/ layout),
 * so a fresh install copies them instead of downloading. A file is only taken if size and sha1 match.
 */
public final class LocalCache {
    private static volatile List<Path> roots;

    private LocalCache() {}

    /** Game dirs of known launchers that exist on this machine. */
    public static List<Path> roots() {
        List<Path> r = roots;
        if (r != null) return r;
        List<Path> found = new ArrayList<>();
        String appData = System.getenv("APPDATA");
        String home = System.getProperty("user.home");
        List<Path> candidates = new ArrayList<>();
        if (appData != null) {
            Path a = Path.of(appData);
            candidates.add(a.resolve(".minecraft"));
            candidates.add(a.resolve("ModrinthApp").resolve("meta"));
            candidates.add(a.resolve("com.modrinth.theseus").resolve("meta"));
            candidates.add(a.resolve("PolyMC"));
            candidates.add(a.resolve("PrismLauncher"));
            candidates.add(a.resolve("MultiMC"));
            candidates.add(a.resolve(".tlauncher").resolve("legacy").resolve("Minecraft").resolve("game"));
            candidates.add(a.resolve("ATLauncher"));
            candidates.add(a.resolve("gdlauncher_carbon").resolve("data"));
        }
        if (home != null) {
            candidates.add(Path.of(home, "curseforge", "minecraft", "Install"));
            candidates.add(Path.of(home, "AppData", "Local", "Packages", "Microsoft.4297127D64EC6_8wekyb3d8bbwe",
                    "LocalCache", "Roaming", ".minecraft"));
        }
        for (Path c : candidates) {
            if (Files.isDirectory(c.resolve("libraries")) || Files.isDirectory(c.resolve("assets"))
                    || Files.isDirectory(c.resolve("versions"))) {
                found.add(c);
            }
        }
        roots = List.copyOf(found);
        return roots;
    }

    /**
     * Tries to fill target from another launcher. relative = path inside the game dir
     * (e.g. libraries/org/foo/foo.jar, assets/objects/ab/ab12...). Returns true if copied and verified.
     */
    public static boolean tryCopy(Path gameDir, Path target, String sha1, long size) {
        if (sha1 == null && size < 0) return false;
        Path rel;
        try {
            rel = gameDir.toAbsolutePath().normalize().relativize(target.toAbsolutePath().normalize());
        } catch (IllegalArgumentException e) {
            return false;
        }
        if (rel.startsWith("..")) return false;
        for (Path root : roots()) {
            Path src = root.resolve(rel);
            if (!Files.isRegularFile(src)) continue;
            try {
                if (size >= 0 && Files.size(src) != size) continue;
                if (sha1 != null && !sha1.equalsIgnoreCase(Net.sha1(src))) continue;
                Files.createDirectories(target.getParent());
                Path tmp = target.resolveSibling(target.getFileName() + ".copy");
                Files.copy(src, tmp, StandardCopyOption.REPLACE_EXISTING);
                Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING);
                return true;
            } catch (IOException e) {
                System.err.println("local cache: не скопировать " + src + ": " + e.getMessage());
            }
        }
        return false;
    }

    /** Java 21+ already installed by another launcher or system-wide (javaw.exe), or null. */
    public static Path findJava21() {
        List<Path> dirs = new ArrayList<>();
        String appData = System.getenv("APPDATA");
        String local = System.getenv("LOCALAPPDATA");
        if (appData != null) {
            dirs.add(Path.of(appData, "ModrinthApp", "meta", "java_versions"));
            dirs.add(Path.of(appData, "com.modrinth.theseus", "meta", "java_versions"));
            dirs.add(Path.of(appData, "PrismLauncher", "java"));
            dirs.add(Path.of(appData, ".minecraft", "runtime"));
        }
        if (local != null) {
            dirs.add(Path.of(local, "Packages", "Microsoft.4297127D64EC6_8wekyb3d8bbwe", "LocalCache", "Local", "runtime"));
        }
        dirs.add(Path.of("C:\\Program Files\\Java"));
        dirs.add(Path.of("C:\\Program Files\\Eclipse Adoptium"));
        dirs.add(Path.of("C:\\Program Files\\Zulu"));
        dirs.add(Path.of("C:\\Program Files\\Microsoft"));
        for (Path d : dirs) {
            if (!Files.isDirectory(d)) continue;
            try (Stream<Path> s = Files.walk(d, 6)) {
                for (Path javaw : s.filter(p -> p.getFileName().toString().equalsIgnoreCase("javaw.exe")).toList()) {
                    Path home = javaw.getParent().getParent();
                    int major = majorVersion(home.resolve("release"));
                    if (major == 21) return javaw;
                }
            } catch (IOException | java.io.UncheckedIOException e) {
                System.err.println("local cache: не просмотреть " + d + ": " + e.getMessage());
            }
        }
        return null;
    }

    private static int majorVersion(Path release) {
        try {
            for (String line : Files.readAllLines(release)) {
                if (!line.startsWith("JAVA_VERSION=")) continue;
                String v = line.substring(line.indexOf('"') + 1, line.lastIndexOf('"'));
                return Integer.parseInt(v.split("[.+]")[0]);
            }
        } catch (IOException | RuntimeException e) {
            return -1;
        }
        return -1;
    }
}
