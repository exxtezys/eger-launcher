package com.elium.launcher;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Downloads Eclipse Temurin JRE 21 into <gameDir>/runtime if not present. */
public final class JavaRuntime {
    private static final String URL =
            "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse";

    private JavaRuntime() {}

    public static Path ensure(Path gameDir, Net.Progress p) throws IOException {
        Path dir = gameDir.resolve("runtime").resolve("jre21");
        p.stage("java");
        Path java = find(dir);
        if (java != null) return java;
        p.update("Поиск Java 21 на компьютере...", 0, 0);
        java = LocalCache.findJava21();
        if (java != null && Files.isRegularFile(java.resolveSibling("java.exe"))) return java;

        Path zip = gameDir.resolve("runtime").resolve("jre21.zip");
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
        if (java == null) throw new IOException("javaw.exe не найден после распаковки Java");
        return java;
    }

    private static Path find(Path dir) throws IOException {
        if (!Files.isDirectory(dir)) return null;
        try (Stream<Path> s = Files.walk(dir, 3)) {
            return s.filter(f -> f.getFileName().toString().equals("javaw.exe")
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

    static void deleteTree(Path p) throws IOException {
        if (!Files.exists(p)) return;
        try (Stream<Path> s = Files.walk(p)) {
            for (Path f : s.sorted(java.util.Comparator.reverseOrder()).toList()) Files.delete(f);
        }
    }
}
