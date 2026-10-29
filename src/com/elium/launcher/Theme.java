package com.elium.launcher;

import javax.imageio.ImageIO;
import java.awt.Color;
import java.awt.Font;
import java.awt.GraphicsEnvironment;
import java.awt.image.BufferedImage;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URLConnection;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

/**
 * Launcher look. Defaults come from /theme.properties in the jar; a theme.properties next to the
 * exe (or jar) overrides them, so the design can be changed without rebuilding.
 */
public final class Theme {
    private final Properties p = new Properties();
    private final Path externalDir;

    public final Color bg, bg2, panel, dialog, field, accent, accentHover, onAccent, text, muted, online, offline;
    public final int radius, width, height, logoHeight;
    public final double backgroundDim;
    public final String title, subtitle;
    public final BufferedImage background, logo, icon;
    public final List<String[]> links = new ArrayList<>();
    private final Font baseFont;
    private final Font bodyFont;

    private Theme(String defaultTitle, String mcVersion) {
        externalDir = externalDir();
        try (InputStream in = Theme.class.getResourceAsStream("/theme.properties")) {
            if (in != null) p.load(new InputStreamReader(in, StandardCharsets.UTF_8));
        } catch (Exception e) {
            System.err.println("theme: встроенная тема не прочитана: " + e);
        }
        if (externalDir != null && Files.isRegularFile(externalDir.resolve("theme.properties"))) {
            try (InputStream in = Files.newInputStream(externalDir.resolve("theme.properties"))) {
                p.load(new InputStreamReader(in, StandardCharsets.UTF_8));
            } catch (Exception e) {
                System.err.println("theme: theme.properties рядом с лаунчером не прочитан: " + e);
            }
        }

        bg = color("color.background", "#0B1114");
        bg2 = color("color.background2", "#10343A");
        panel = color("color.panel", "#0E171BD9");
        dialog = color("color.dialog", "#121C21");
        field = color("color.field", "#0A1013");
        accent = color("color.accent", "#17A39A");
        accentHover = color("color.accent.hover", "#21C2B6");
        onAccent = color("color.on.accent", "#FFFFFF");
        text = color("color.text", "#E8F3F2");
        muted = color("color.muted", "#86A0A3");
        online = color("color.online", "#4CD07D");
        offline = color("color.offline", "#E0605A");

        radius = num("radius", 18);
        width = num("window.width", 920);
        height = num("window.height", 560);
        logoHeight = num("logo.height", 110);
        backgroundDim = Math.max(0, Math.min(1, Double.parseDouble(str("background.dim", "0.35"))));

        String t = str("title", "");
        title = t.isEmpty() ? defaultTitle : t;
        subtitle = str("subtitle", "Minecraft {mc} · NeoForge").replace("{mc}", mcVersion);

        background = image(str("background", ""));
        logo = image(str("logo", ""));
        icon = image(str("icon", "icon.png"));
        baseFont = loadFont();
        String body = str("font.body", "");
        bodyFont = body.isEmpty() || !installed(body) ? baseFont : new Font(body, Font.PLAIN, 14);

        for (String link : str("links", "").split(";")) {
            String[] kv = link.split("\\|", 2);
            if (kv.length == 2 && !kv[0].isBlank() && !kv[1].isBlank()) links.add(new String[]{kv[0].trim(), kv[1].trim()});
        }
    }

    public static Theme load(String defaultTitle, String mcVersion) {
        return new Theme(defaultTitle, mcVersion);
    }

    public Font font(int style, float size) {
        return (style == Font.BOLD ? baseFont.deriveFont(Font.PLAIN, size) : bodyFont.deriveFont(style, size));
    }

    private static boolean installed(String family) {
        return Arrays.asList(GraphicsEnvironment.getLocalGraphicsEnvironment().getAvailableFontFamilyNames()).contains(family);
    }

    private String str(String key, String def) {
        return p.getProperty(key, def).trim();
    }

    private int num(String key, int def) {
        try {
            return Integer.parseInt(str(key, Integer.toString(def)));
        } catch (NumberFormatException e) {
            return def;
        }
    }

    private Color color(String key, String def) {
        try {
            return parseColor(str(key, def));
        } catch (RuntimeException e) {
            System.err.println("theme: неверный цвет " + key + ", беру " + def);
            return parseColor(def);
        }
    }

    private static Color parseColor(String v) {
        String h = v.startsWith("#") ? v.substring(1) : v;
        long x = Long.parseLong(h, 16);
        if (h.length() == 6) return new Color((int) x);
        if (h.length() == 8) return new Color((int) (x >> 24) & 0xFF, (int) (x >> 16) & 0xFF, (int) (x >> 8) & 0xFF, (int) x & 0xFF);
        throw new IllegalArgumentException(v);
    }

    private Font loadFont() {
        String file = str("font.file", "");
        if (!file.isEmpty()) {
            try (InputStream in = open(file)) {
                if (in != null) {
                    Font f = Font.createFont(Font.TRUETYPE_FONT, in);
                    GraphicsEnvironment.getLocalGraphicsEnvironment().registerFont(f);
                    return f.deriveFont(Font.PLAIN, 14f);
                }
            } catch (Exception e) {
                System.err.println("theme: шрифт " + file + " не загружен: " + e);
            }
        }
        String name = str("font", "Segoe UI");
        return new Font(installed(name) ? name : Font.DIALOG, Font.PLAIN, 14);
    }

    private BufferedImage image(String v) {
        if (v.isEmpty()) return null;
        try (InputStream in = open(v)) {
            if (in != null) return ImageIO.read(in);
            System.err.println("theme: картинка не найдена: " + v);
        } catch (Exception e) {
            System.err.println("theme: картинка " + v + " не загружена: " + e);
        }
        return null;
    }

    /** http(s) URL, file next to the launcher, or resource inside the jar. */
    private InputStream open(String v) throws java.io.IOException {
        if (v.startsWith("http://") || v.startsWith("https://")) {
            URLConnection c = URI.create(v).toURL().openConnection();
            c.setConnectTimeout(5000);
            c.setReadTimeout(10000);
            c.setRequestProperty("User-Agent", "EliumLauncher");
            return c.getInputStream();
        }
        if (externalDir != null) {
            Path f = externalDir.resolve(v);
            if (Files.isRegularFile(f)) return Files.newInputStream(f);
        }
        return Theme.class.getResourceAsStream("/" + v.replaceFirst("^/", ""));
    }

    private static Path externalDir() {
        String app = System.getProperty("jpackage.app-path");
        if (app != null) return Path.of(app).getParent();
        try {
            Path jar = Path.of(Theme.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            return Files.isDirectory(jar) ? jar : jar.getParent();
        } catch (Exception e) {
            return null;
        }
    }
}
