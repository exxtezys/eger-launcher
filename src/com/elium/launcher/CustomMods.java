package com.elium.launcher;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;

/**
 * User-managed "custom" mods. They are stored in a separate folder so ModpackSync cannot delete them,
 * then copied into <gameDir>/mods as custom-<name>.jar after the modpack has been synchronized.
 */
final class CustomMods {
    record Mod(String name, Path source, boolean enabled) {}

    private CustomMods() {}

    static Path sourceDir(Config cfg) throws IOException {
        Path dir = cfg.customModsDir();
        Files.createDirectories(dir);
        return dir;
    }

    static List<Mod> list(Config cfg) throws IOException {
        Path dir = sourceDir(cfg);
        Properties state = loadState(dir);
        List<Path> jars = new ArrayList<>();
        try (var stream = Files.list(dir)) {
            stream.filter(Files::isRegularFile)
                    .filter(p -> p.getFileName().toString().toLowerCase().endsWith(".jar"))
                    .sorted(Comparator.comparing(p -> p.getFileName().toString()))
                    .forEach(jars::add);
        }

        Set<String> names = new HashSet<>();
        List<Mod> mods = new ArrayList<>();
        boolean changed = false;
        for (Path jar : jars) {
            String name = jar.getFileName().toString();
            names.add(name);
            boolean enabled = Boolean.parseBoolean(state.getProperty(name, "true"));
            mods.add(new Mod(name, jar, enabled));
            if (!state.containsKey(name)) {
                state.setProperty(name, Boolean.toString(enabled));
                changed = true;
            }
        }
        for (String key : new ArrayList<>(state.stringPropertyNames())) {
            if (!names.contains(key)) {
                state.remove(key);
                changed = true;
            }
        }
        if (changed) saveState(dir, state);
        return mods;
    }

    static void add(Config cfg, Path jar) throws IOException {
        if (!Files.isRegularFile(jar)) throw new IOException("Файл мода не найден: " + jar);
        String name = jar.getFileName().toString();
        if (!name.toLowerCase().endsWith(".jar")) throw new IOException("Можно добавлять только .jar: " + name);

        Path dir = sourceDir(cfg);
        Path target = dir.resolve(name);
        Files.copy(jar, target, java.nio.file.StandardCopyOption.REPLACE_EXISTING);

        Properties state = loadState(dir);
        state.setProperty(name, "true");
        saveState(dir, state);
    }

    static void remove(Config cfg, String name) throws IOException {
        Path dir = sourceDir(cfg);
        Files.deleteIfExists(dir.resolve(name));

        Properties state = loadState(dir);
        state.remove(name);
        saveState(dir, state);

        Files.deleteIfExists(cfg.gameDir.resolve("mods").resolve("custom-" + name));
    }

    static void setEnabled(Config cfg, String name, boolean enabled) throws IOException {
        Path dir = sourceDir(cfg);
        Properties state = loadState(dir);
        state.setProperty(name, Boolean.toString(enabled));
        saveState(dir, state);
    }

    static void sync(Config cfg, Net.Progress progress) throws IOException {
        Path mods = cfg.gameDir.resolve("mods");
        Files.createDirectories(mods);

        List<Mod> modsList = list(cfg);
        Set<String> wanted = new HashSet<>();
        for (Mod m : modsList) {
            if (m.enabled()) wanted.add("custom-" + m.name());
        }

        try (var stream = Files.list(mods)) {
            stream.filter(Files::isRegularFile)
                    .filter(p -> {
                        String n = p.getFileName().toString().toLowerCase();
                        return n.startsWith("custom-") && n.endsWith(".jar");
                    })
                    .forEach(p -> {
                        if (!wanted.contains(p.getFileName().toString())) {
                            try { Files.deleteIfExists(p); } catch (IOException ignored) {}
                        }
                    });
        }

        int total = wanted.size();
        int done = 0;
        for (Mod m : modsList) {
            if (!m.enabled()) continue;
            Path target = mods.resolve("custom-" + m.name());
            if (!Files.exists(target) || Files.size(target) != Files.size(m.source())) {
                Files.copy(m.source(), target, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            }
            done++;
            if (progress != null) progress.update("Custom mods: копирование", done, total);
        }
        if (progress != null) progress.bytes(-1, -1);
    }

    private static Properties loadState(Path dir) {
        Properties p = new Properties();
        Path file = dir.resolve("custom-mods.properties");
        if (Files.isRegularFile(file)) {
            try (var in = Files.newInputStream(file)) {
                p.load(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8));
            } catch (IOException ignored) {}
        }
        return p;
    }

    private static void saveState(Path dir, Properties state) throws IOException {
        Path file = dir.resolve("custom-mods.properties");
        try (var out = Files.newOutputStream(file)) {
            state.store(out, "Custom mods");
        }
    }
}
