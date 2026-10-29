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
 * Player settings (nick, RAM) are stored in <gameDir>/launcher-user.properties.
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
        projectName = p.getProperty("project.name", "Elium");
        gameDirName = p.getProperty("game.dir", ".elium");
        minecraftVersion = p.getProperty("minecraft.version", "1.21.1");
        neoforgeVersion = p.getProperty("neoforge.version", "latest").trim();
        serverHost = p.getProperty("server.host", "").trim();
        serverPort = Integer.parseInt(p.getProperty("server.port", "25565").trim());
        modpackUrl = System.getProperty("elium.modpack.url", p.getProperty("modpack.url", "")).trim();
        updateGithub = System.getProperty("elium.update.github", p.getProperty("update.github", "")).trim();

        String appData = System.getenv("APPDATA");
        Path base = appData != null ? Path.of(appData) : Path.of(System.getProperty("user.home"));
        String dirOverride = System.getProperty("elium.dir");
        gameDir = dirOverride != null ? Path.of(dirOverride) : base.resolve(gameDirName);
        Files.createDirectories(gameDir);
        userFile = gameDir.resolve("launcher-user.properties");
        if (Files.exists(userFile)) {
            try (Reader r = Files.newBufferedReader(userFile, StandardCharsets.UTF_8)) { user.load(r); }
        }
    }

    public String nick() { return user.getProperty("nick", ""); }
    public int ramMb() { return Integer.parseInt(user.getProperty("ram", "4096")); }
    public boolean autoConnect() { return Boolean.parseBoolean(user.getProperty("autoConnect", "true")); }

    public void saveUser(String nick, int ram, boolean autoConnect) throws IOException {
        user.setProperty("nick", nick);
        user.setProperty("ram", Integer.toString(ram));
        user.setProperty("autoConnect", Boolean.toString(autoConnect));
        try (Writer w = Files.newBufferedWriter(userFile, StandardCharsets.UTF_8)) { user.store(w, projectName + " launcher"); }
    }
}
