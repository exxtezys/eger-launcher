package com.elium.launcher;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Launcher auto-update from the latest GitHub release of update.github (public repo, no token):
 * the release must carry an EliumLauncher.jar asset; the release body may hold "sha1: <hex>" for verification.
 * Windows locks a running jar, so the swap happens in two steps:
 * 1) the old launcher downloads EliumLauncher.jar.new, starts it with -Delium.update.install=1 and exits;
 * 2) the new process waits until the old jar is unlocked, copies itself over it and starts the normal launcher.
 */
public final class SelfUpdate {
    private static final String INSTALL_FLAG = "elium.update.install";
    private static final String JAR_ASSET = "EliumLauncher.jar";
    private static final java.util.regex.Pattern SHA1_LINE =
            java.util.regex.Pattern.compile("(?im)^\\s*sha1:\\s*([0-9a-f]{40})\\s*$");

    private static String releaseSha1(String body) {
        if (body == null) return null;
        java.util.regex.Matcher m = SHA1_LINE.matcher(body);
        return m.find() ? m.group(1) : null;
    }

    private SelfUpdate() {}

    /** Returns true if this process must exit right away (an update step was handed to another process). */
    public static boolean run(Config cfg) {
        Path self = selfJar();
        if (self == null) return false;
        if (System.getProperty(INSTALL_FLAG) != null) return finishInstall(self);
        cleanup(self);
        if (!cfg.updateGithub.matches("[\\w.-]+/[\\w.-]+")) return false;
        try {
            Map<String, Object> rel = Json.obj(Json.parse(
                    Net.getText("https://api.github.com/repos/" + cfg.updateGithub + "/releases/latest")));
            Map<String, Object> asset = null;
            for (Object o : Json.arr(rel.get("assets"))) {
                if (JAR_ASSET.equals(Json.str(Json.obj(o), "name"))) asset = Json.obj(o);
            }
            if (asset == null) return false;
            String sha1 = releaseSha1(Json.str(rel, "body"));
            long size = asset.get("size") instanceof Number n ? n.longValue() : -1;
            if (sha1 != null ? sha1.equalsIgnoreCase(Net.sha1(self)) : size == Files.size(self)) return false;

            Path next = self.resolveSibling(self.getFileName() + ".new");
            Net.download(new Net.Task(Json.str(asset, "browser_download_url"), next, sha1, size));
            start(next, true);
            return true;
        } catch (IOException | RuntimeException e) {
            System.err.println("автообновление лаунчера пропущено: " + e);
            return false;
        }
    }

    private static boolean finishInstall(Path newJar) {
        String name = newJar.getFileName().toString();
        if (!name.endsWith(".new")) return false;
        Path target = newJar.resolveSibling(name.substring(0, name.length() - 4));
        IOException last = null;
        for (int i = 0; i < 50; i++) {
            try {
                Files.copy(newJar, target, StandardCopyOption.REPLACE_EXISTING);
                start(target, false);
                return true;
            } catch (IOException e) {
                last = e;
                sleep(200);
            }
        }
        System.err.println("не удалось заменить лаунчер, запускаю новую версию из .new: " + last);
        return false;
    }

    private static void cleanup(Path self) {
        try {
            Files.deleteIfExists(self.resolveSibling(self.getFileName() + ".new"));
        } catch (IOException e) {
            System.err.println("не удалить временный файл обновления: " + e.getMessage());
        }
    }

    private static Path selfJar() {
        try {
            Path p = Path.of(SelfUpdate.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            return Files.isRegularFile(p) ? p : null;
        } catch (Exception e) {
            return null;
        }
    }

    private static void start(Path jar, boolean install) throws IOException {
        List<String> cmd = new ArrayList<>();
        String app = System.getProperty("jpackage.app-path");
        if (!install && app != null && Files.isRegularFile(Path.of(app))) {
            new ProcessBuilder(app).directory(Path.of(app).getParent().toFile()).start();
            return;
        }
        cmd.add(javaExe().toString());
        for (String k : new String[]{"elium.dir", "elium.modpack.url", "jpackage.app-path", "jpackage.app-version"}) {
            if (System.getProperty(k) != null) cmd.add("-D" + k + "=" + System.getProperty(k));
        }
        if (install) cmd.add("-D" + INSTALL_FLAG + "=1");
        cmd.add("-jar");
        cmd.add(jar.toString());
        new ProcessBuilder(cmd).directory(jar.getParent().toFile()).start();
    }

    private static Path javaExe() {
        Path bin = Path.of(System.getProperty("java.home"), "bin");
        String[] names = System.getProperty("os.name", "").toLowerCase().contains("win")
                ? new String[]{"javaw.exe", "java.exe"} : new String[]{"java"};
        for (String n : names) {
            if (Files.isRegularFile(bin.resolve(n))) return bin.resolve(n);
        }
        throw new IllegalStateException("в комплекте лаунчера нет java");
    }

    private static void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
