package com.elium.launcher;

import java.io.IOException;
import java.io.InputStream;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;

/**
 * Project settings come from /launcher.properties inside the jar (edit before building).
 * Player settings (nick, RAM, UI, downloads) are stored in <gameDir>/launcher-user.properties.
 */
public final class Config {
    public final String projectName;
    public final String gameDirName;
    public final String minecraftVersion;
    public final String neoforgeVersion;
    public final String serverHost;
    public final int serverPort;
    public final String modpackUrl;
    public final String updateGithub;
    public final Path gameDir;

    private final Properties user = new Properties();
    private final Path userFile;

    public Config() throws IOException {
        Properties p = new Properties();
        try (InputStream in = Config.class.getResourceAsStream("/launcher.properties")) {
            if (in == null) throw new IOException("launcher.properties missing from jar");
            p.load(new java.io.InputStreamReader(in, StandardCharsets.UTF_8));
        }
        projectName = p.getProperty("project.name", "Eger");
        gameDirName = p.getProperty("game.dir", ".eger");
        minecraftVersion = p.getProperty("minecraft.version", "1.21.1");
        neoforgeVersion = p.getProperty("neoforge.version", "latest").trim();
        serverHost = p.getProperty("server.host", "").trim();
        serverPort = Integer.parseInt(p.getProperty("server.port", "25565").trim());
        String modpackUrlValue = p.getProperty("modpack.url", "").trim();
        updateGithub = System.getProperty("elium.update.github", p.getProperty("update.github", "")).trim();
        modpackUrlValue = System.getProperty("elium.modpack.url", modpackUrlValue).trim();
        modpackUrl = modpackUrlValue;

        String appData = System.getenv("APPDATA");
        Path base = appData != null ? Path.of(appData) : Path.of(System.getProperty("user.home"));
        String dirOverride = System.getProperty("elium.dir");
        gameDir = dirOverride != null ? Path.of(dirOverride) : base.resolve(gameDirName);
        Files.createDirectories(gameDir);
        userFile = gameDir.resolve("launcher-user.properties");
        if (Files.exists(userFile)) {
            try (Reader r = Files.newBufferedReader(userFile, StandardCharsets.UTF_8)) { user.load(r); }
        }
        if (user.getProperty("uiStyleRevision") == null) {
            user.setProperty("uiStyle", "hand");
            user.setProperty("uiStyleRevision", "1");
            try (Writer w = Files.newBufferedWriter(userFile, StandardCharsets.UTF_8)) {
                user.store(w, projectName + " launcher");
            } catch (IOException e) {
                System.err.println("config: миграция стиля не сохранена: " + e.getMessage());
            }
        }
    }

    public String nick() { return user.getProperty("nick", ""); }

    public int ramMb() { return intProp("ram", 4096, 1024, 32768); }

    public boolean autoConnect() { return boolProp("autoConnect", true); }

    public int maxDownloads() { return intProp("maxDownloads", 12, 1, 64); }

    public boolean autoUpdate() { return boolProp("autoUpdate", true); }

    public String modpackUrlOverride() { return strProp("modpackUrlOverride", ""); }

    public String effectiveModpackUrl() {
        String v = modpackUrlOverride();
        return v.isBlank() ? modpackUrl : v;
    }

    public String extraJvmArgs() { return strProp("extraJvmArgs", ""); }

    public String uiStyle() { return strProp("uiStyle", "hand"); }

    public boolean keepLogs() { return boolProp("keepLogs", true); }

    public String serverHostOverride() { return strProp("serverHostOverride", ""); }

    public String effectiveServerHost() {
        String v = serverHostOverride();
        return v.isBlank() ? serverHost : v;
    }

    public int serverPortOverride() { return intProp("serverPortOverride", serverPort, 1, 65535); }

    public int effectiveServerPort() {
        String v = user.getProperty("serverPortOverride", "").trim();
        return v.isBlank() ? serverPort : serverPortOverride();
    }

    public void saveUser(String nick, int ram, boolean autoConnect) throws IOException {
        saveUserSettings(nick, ram, autoConnect, maxDownloads(), autoUpdate(), modpackUrlOverride(),
                extraJvmArgs(), uiStyle(), keepLogs(), serverHostOverride(), serverPortOverride());
    }

    public void saveUserSettings(String nick, int ram, boolean autoConnect, int maxDownloads, boolean autoUpdate,
                                 String modpackUrlOverride, String extraJvmArgs, String uiStyle, boolean keepLogs,
                                 String serverHostOverride, int serverPortOverride) throws IOException {
        user.setProperty("nick", nick == null ? "" : nick);
        user.setProperty("ram", Integer.toString(ram));
        user.setProperty("autoConnect", Boolean.toString(autoConnect));
        user.setProperty("maxDownloads", Integer.toString(maxDownloads));
        user.setProperty("autoUpdate", Boolean.toString(autoUpdate));
        user.setProperty("modpackUrlOverride", modpackUrlOverride == null ? "" : modpackUrlOverride.trim());
        user.setProperty("extraJvmArgs", extraJvmArgs == null ? "" : extraJvmArgs.trim());
        user.setProperty("uiStyle", uiStyle == null || uiStyle.isBlank() ? "hand" : uiStyle.trim());
        user.setProperty("keepLogs", Boolean.toString(keepLogs));
        user.setProperty("serverHostOverride", serverHostOverride == null ? "" : serverHostOverride.trim());
        user.setProperty("serverPortOverride", Integer.toString(serverPortOverride));
        try (Writer w = Files.newBufferedWriter(userFile, StandardCharsets.UTF_8)) {
            user.store(w, projectName + " launcher");
        }
    }

    private String strProp(String key, String def) {
        String v = user.getProperty(key);
        return v == null ? def : v.trim();
    }

    private boolean boolProp(String key, boolean def) {
        String v = user.getProperty(key);
        if (v == null || v.isBlank()) return def;
        return Boolean.parseBoolean(v.trim());
    }

    private int intProp(String key, int def, int min, int max) {
        String v = user.getProperty(key);
        if (v == null || v.isBlank()) return def;
        try {
            int n = Integer.parseInt(v.trim());
            return Math.max(min, Math.min(max, n));
        } catch (NumberFormatException e) {
            return def;
        }
    }
}
