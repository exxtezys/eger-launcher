package com.elium.launcher;

import java.awt.AlphaComposite;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.geom.AffineTransform;
import java.awt.geom.Path2D;
import java.awt.image.BufferedImage;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

/**
 * Чернильные примитивы ручного стиля: рваные рамки, штриховка, эрозия текста, орбиты.
 * Только рисование, без состояния окна; тяжёлые маски кэшируются.
 */
final class Ink {
    private Ink() {}

    private static final Map<String, BufferedImage> TEXT_CACHE = new HashMap<>();

    /** Прямоугольник от руки: дрожащие края, снизу — рваный обрыв. */
    static void tornBorder(Graphics2D g, float x, float y, float w, float h, Color ink, long seed) {
        Random r = new Random(seed);
        Path2D.Float p = tornPath(x, y, w, h, seed);
        java.awt.Stroke old = g.getStroke();
        g.setColor(ink);
        g.setStroke(new BasicStroke(1.15f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.draw(p);
        g.setStroke(old);
    }

    /** Заполненный контур бумаги с рваным нижним краем. */
    static Path2D.Float tornPath(float x, float y, float w, float h, long seed) {
        Random r = new Random(seed);
        Path2D.Float p = new Path2D.Float();
        float j = 0.7f;
        p.moveTo(x + r.nextFloat() * j, y + r.nextFloat() * j);
        int seg = Math.max(4, (int) (w / 34));
        for (int i = 1; i <= seg; i++) {
            p.lineTo(x + w * i / seg + (r.nextFloat() - .5f) * j, y + (r.nextFloat() - .5f) * j);
        }
        seg = Math.max(2, (int) (h / 34));
        for (int i = 1; i <= seg; i++) {
            p.lineTo(x + w + (r.nextFloat() - .5f) * j, y + h * i / seg + (r.nextFloat() - .5f) * j);
        }
        // нижний край рвётся сильнее: зубцы и редкие вырывы
        seg = Math.max(6, (int) (w / 22));
        for (int i = seg - 1; i >= 0; i--) {
            float px = x + w * i / seg;
            float amp = r.nextInt(7) == 0 ? 4.5f : 1.6f;
            p.lineTo(px + (r.nextFloat() - .5f) * 1.4f, y + h + (r.nextFloat() - 1f) * amp);
        }
        seg = Math.max(2, (int) (h / 34));
        for (int i = seg - 1; i >= 0; i--) {
            p.lineTo(x + (r.nextFloat() - .5f) * j, y + h * i / seg + (r.nextFloat() - .5f) * j);
        }
        p.closePath();
        return p;
    }

    /** Косая штриховка внутри фигуры. */
    static void hatch(Graphics2D g, Shape clip, float angle, float gap, Color ink) {
        Graphics2D g2 = (Graphics2D) g.create();
        g2.clip(clip);
        Rectangle b = clip.getBounds();
        double diag = Math.hypot(b.width, b.height);
        AffineTransform old = g2.getTransform();
        g2.translate(b.x + b.width / 2.0, b.y + b.height / 2.0);
        g2.rotate(angle);
        g2.setColor(ink);
        g2.setStroke(new BasicStroke(1f));
        for (double x = -diag; x <= diag; x += gap) {
            g2.draw(new java.awt.geom.Line2D.Double(x, -diag, x, diag));
        }
        g2.setTransform(old);
        g2.dispose();
    }

    /** Текст с увеличенным трекингом; x — начало базовой линии. */
    static float spaced(Graphics2D g, String text, float x, float y, float tracking) {
        FontMetrics fm = g.getFontMetrics();
        float cx = x;
        for (int i = 0; i < text.length(); i++) {
            String ch = text.substring(i, i + 1);
            g.drawString(ch, cx, y);
            cx += fm.stringWidth(ch) + tracking;
        }
        return cx - x;
    }

    /** Печатный текст с эрозией краски; кэшируется по строке, шрифту, цвету и seed. */
    static void inkText(Graphics2D g, String text, Font font, float x, float y, long seed) {
        if (text == null || text.isEmpty()) return;
        Color color = g.getColor();
        Font f = font.deriveFont(font.getStyle(), Math.max(1f, font.getSize2D()));
        String key = text + "|" + f.getFamily() + "|" + f.getStyle() + "|" + f.getSize2D()
                + "|" + color.getRGB() + "|" + seed;
        BufferedImage img = TEXT_CACHE.get(key);
        if (img == null) {
            img = renderInkText(text, f, color, seed);
            TEXT_CACHE.put(key, img);
        }
        FontMetrics fm = g.getFontMetrics(f);
        g.drawImage(img, Math.round(x) - 4, Math.round(y) - fm.getAscent() - 4, null);
    }

    private static BufferedImage renderInkText(String text, Font font, Color color, long seed) {
        BufferedImage probe = new BufferedImage(1, 1, BufferedImage.TYPE_INT_ARGB);
        Graphics2D pg = probe.createGraphics();
        pg.setFont(font);
        FontMetrics fm = pg.getFontMetrics();
        int tw = Math.max(1, fm.stringWidth(text)), th = Math.max(1, fm.getHeight());
        pg.dispose();
        int pad = 8;
        BufferedImage mask = new BufferedImage(tw + pad * 2, th + pad * 2, BufferedImage.TYPE_INT_ARGB);
        Graphics2D mg = mask.createGraphics();
        mg.setRenderingHint(java.awt.RenderingHints.KEY_TEXT_ANTIALIASING,
                java.awt.RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        mg.setFont(font);
        mg.setColor(Color.WHITE);
        mg.drawString(text, pad, pad + fm.getAscent());
        mg.dispose();

        Random r = new Random(seed * 0x9E3779B97F4A7C15L + text.hashCode());
        Graphics2D er = mask.createGraphics();
        er.setComposite(AlphaComposite.Clear);
        int punches = Math.max(8, (tw * th) / 26);
        for (int i = 0; i < punches; i++) {
            int px = r.nextInt(Math.max(1, tw + pad * 2));
            int py = r.nextInt(Math.max(1, th + pad * 2));
            int rad = 1 + r.nextInt(2);
            er.fillOval(px, py, rad, rad);
        }
        for (int i = 0; i < 6; i++) {
            int py = r.nextInt(Math.max(1, th + pad * 2));
            er.drawLine(0, py, tw + pad * 2, py + r.nextInt(3) - 1);
        }
        er.dispose();

        BufferedImage out = new BufferedImage(mask.getWidth(), mask.getHeight(), BufferedImage.TYPE_INT_ARGB);
        Graphics2D og = out.createGraphics();
        og.drawImage(mask, 0, 0, null);
        og.setComposite(AlphaComposite.SrcIn);
        og.setColor(color);
        og.fillRect(0, 0, out.getWidth(), out.getHeight());
        og.dispose();
        return out;
    }

    /** Орбита от руки: эллипс с дрожанием, phase сдвигает рисунок. */
    static void orbit(Graphics2D g, float cx, float cy, float rx, float ry, float phase, Color ink) {
        Path2D.Float p = new Path2D.Float();
        int steps = 128;
        Random r = new Random((long) (phase * 1024) + 1939);
        for (int i = 0; i <= steps; i++) {
            double a = Math.PI * 2 * i / steps;
            double wobble = 1 + Math.sin(a * 3 + phase) * 0.012 + (r.nextDouble() - .5) * 0.006;
            float px = (float) (cx + Math.cos(a) * rx * wobble);
            float py = (float) (cy + Math.sin(a) * ry * wobble);
            if (i == 0) p.moveTo(px, py);
            else p.lineTo(px, py);
        }
        java.awt.Stroke old = g.getStroke();
        g.setColor(ink);
        g.setStroke(new BasicStroke(1.2f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.draw(p);
        g.setStroke(old);
    }
}
