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
    public final Color inkSoft, paperShadow;
    public enum Style { CLEAN, MILITARY, SKETCH, HAND }

    public final int radius, width, height, logoHeight;
    public final Style style;
    public final double backgroundDim;
    public final String title, subtitle;
    public final BufferedImage background, logo, icon, handHero, handPaper, handIcon, scene;
    public final List<String[]> links = new ArrayList<>();
    public final Font displayFont, bodyFont;

    private Theme(String defaultTitle, String mcVersion, String styleOverride) {
        externalDir = externalDir();
        try (InputStream in = Theme.class.getResourceAsStream("/theme.properties")) {
            if (in != null) p.load(new InputStreamReader(in, StandardCharsets.UTF_8));
        } catch (Exception e) {
            System.err.println("theme: встроенная тема не прочитана: " + e);
        }
        if (externalDir != null && Files.isRegularFile(externalDir.resolve("theme.properties"))) {
            Properties ext = new Properties();
            boolean loaded = false;
            try (InputStream in = Files.newInputStream(externalDir.resolve("theme.properties"))) {
                ext.load(new InputStreamReader(in, StandardCharsets.UTF_8));
                loaded = true;
            } catch (Exception e) {
                System.err.println("theme: theme.properties рядом с лаунчером не прочитан: " + e);
            }
            if (loaded) {
                int revision = 0;
                try {
                    revision = Integer.parseInt(ext.getProperty("theme.revision", "0").trim());
                } catch (NumberFormatException ignored) {
                }
                if (revision >= 2) {
                    p.putAll(ext);
                } else {
                    System.err.println("theme: внешняя тема устарела (нужна revision 2), игнорирую");
                }
            }
        }

        String styleValue = (styleOverride == null || styleOverride.isBlank()) ? str("ui.style", "hand") : styleOverride.trim();
        Style st;
        try {
            st = Style.valueOf(styleValue.toUpperCase(java.util.Locale.ROOT));
        } catch (IllegalArgumentException e) {
            System.err.println("theme: неизвестный ui.style, беру hand");
            st = Style.HAND;
        }
        style = st;
        boolean hand = st == Style.HAND;
        String cp = hand ? "color.hand." : "color.";

        bg = color(cp + "background", hand ? "#C9C5B9" : "#0B1114");
        bg2 = color(cp + "background2", hand ? "#A7A395" : "#10343A");
        panel = color(cp + "panel", hand ? "#E4E0D5" : "#0E171BD9");
        dialog = color(cp + "dialog", hand ? "#E4E0D5" : "#121C21");
        field = color(cp + "field", hand ? "#E4E0D5" : "#0A1013");
        accent = color(cp + "accent", hand ? "#A07C3C" : "#17A39A");
        accentHover = color(cp + "accent.hover", hand ? "#C09A52" : "#21C2B6");
        onAccent = color(cp + "on.accent", hand ? "#14130F" : "#FFFFFF");
        text = color(cp + "text", hand ? "#1C1B18" : "#E8F3F2");
        muted = color(cp + "muted", hand ? "#6A665B" : "#86A0A3");
        online = color(cp + "online", hand ? "#A07C3C" : "#4CD07D");
        offline = color(cp + "offline", hand ? "#1C1B18" : "#E0605A");
        inkSoft = color(cp + "ink.soft", hand ? "#3B3933" : "#86A0A3");
        paperShadow = color(cp + "paper.shadow", hand ? "#A7A395" : "#10343A");

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
        handHero = image(str("hand.hero", "hand-hero.png"));
        handPaper = image(str("hand.paper", "paper.png"));
        BufferedImage hi = image(str("hand.icon", "hand-icon.png"));
        handIcon = hi != null ? hi : icon;
        scene = image(str("scene", ""));

        Font display = loadFontFile("font.display.file");
        if (display == null) display = loadFontFile("font.file");
        if (display == null) {
            String name = str("font", hand ? "Impact" : "Segoe UI");
            display = new Font(installed(name) ? name : Font.DIALOG, Font.PLAIN, 14);
        }
        displayFont = display;
        Font bodyF = loadFontFile("font.body.file");
        if (bodyF == null) {
            String body = str("font.body", hand ? "Consolas" : "");
            bodyF = body.isEmpty() || !installed(body) ? displayFont : new Font(body, Font.PLAIN, 14);
        }
        bodyFont = bodyF;

        for (String link : str("links", "").split(";")) {
            String[] kv = link.split("\\|", 2);
            if (kv.length == 2 && !kv[0].isBlank() && !kv[1].isBlank()) links.add(new String[]{kv[0].trim(), kv[1].trim()});
        }
    }

    public static Theme load(String defaultTitle, String mcVersion) {
        return new Theme(defaultTitle, mcVersion, "");
    }

    public static Theme load(String defaultTitle, String mcVersion, String styleOverride) {
        return new Theme(defaultTitle, mcVersion, styleOverride);
    }

    public Font font(int style, float size) {
        return (style == Font.BOLD ? displayFont.deriveFont(Font.PLAIN, size) : bodyFont.deriveFont(style, size));
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

    private Font loadFontFile(String key) {
        String file = str(key, "");
        if (file.isEmpty()) return null;
        try (InputStream in = open(file)) {
            if (in != null) {
                Font f = Font.createFont(Font.TRUETYPE_FONT, in);
                GraphicsEnvironment.getLocalGraphicsEnvironment().registerFont(f);
                return f.deriveFont(Font.PLAIN, 14f);
            }
            System.err.println("theme: шрифт не найден: " + file);
        } catch (Exception e) {
            System.err.println("theme: шрифт " + file + " не загружен: " + e);
        }
        return null;
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
