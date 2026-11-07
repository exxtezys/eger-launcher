package com.elium.launcher;

import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.Timer;
import javax.swing.border.EmptyBorder;
import java.awt.AlphaComposite;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.FontMetrics;
import java.awt.GradientPaint;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RadialGradientPaint;
import java.awt.RenderingHints;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.RoundRectangle2D;
import java.awt.image.BufferedImage;
import java.util.Random;
import java.util.function.IntConsumer;

final class UI {
    private UI() {}

    static Graphics2D smooth(Graphics g) {
        Graphics2D g2 = (Graphics2D) g.create();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_LCD_HRGB);
        g2.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
        g2.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        return g2;
    }

    static Color alpha(Color c, int a) {
        return new Color(c.getRed(), c.getGreen(), c.getBlue(), a);
    }

    static void centerText(Graphics2D g, String s, int w, int h) {
        FontMetrics fm = g.getFontMetrics();
        g.drawString(s, (w - fm.stringWidth(s)) / 2, (h - fm.getHeight()) / 2 + fm.getAscent());
    }

    static void sketchRect(Graphics2D g, float x, float y, float w, float h, Color ink, long seed) {
        Random r = new Random(seed);
        java.awt.Stroke old = g.getStroke();
        for (int pass = 0; pass < 2; pass++) {
            g.setColor(alpha(ink, pass == 0 ? ink.getAlpha() : ink.getAlpha() / 2));
            g.setStroke(new BasicStroke(pass == 0 ? 1.6f : 1f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
            float j = 1.6f;
            float[][] c = {{x, y}, {x + w, y}, {x + w, y + h}, {x, y + h}};
            for (int i = 0; i < 4; i++) {
                float[] a = c[i], b = c[(i + 1) % 4];
                float over = 3 + r.nextFloat() * 4;
                float dx = b[0] - a[0], dy = b[1] - a[1];
                float len = (float) Math.hypot(dx, dy);
                float ux = dx / len, uy = dy / len;
                java.awt.geom.Path2D.Float p = new java.awt.geom.Path2D.Float();
                p.moveTo(a[0] - ux * over + (r.nextFloat() - .5f) * j, a[1] - uy * over + (r.nextFloat() - .5f) * j);
                int seg = Math.max(2, (int) (len / 40));
                for (int s = 1; s <= seg; s++) {
                    float tt = s / (float) seg;
                    p.lineTo(a[0] + dx * tt + ux * (s == seg ? over : 0) + (r.nextFloat() - .5f) * j,
                            a[1] + dy * tt + uy * (s == seg ? over : 0) + (r.nextFloat() - .5f) * j);
                }
                g.draw(p);
            }
        }
        g.setStroke(old);
    }

    /** Full-window backdrop: picture (cover-scaled + dimmed) or gradient with a faint pixel pattern. */
    static final class Backdrop extends JPanel {
        private final Theme t;
        private BufferedImage cache;

        Backdrop(Theme t) {
            super(null);
            this.t = t;
        }

        @Override
        protected void paintComponent(Graphics g) {
            int w = getWidth(), h = getHeight();
            if (cache == null || cache.getWidth() != w || cache.getHeight() != h) cache = render(w, h);
            g.drawImage(cache, 0, 0, null);
        }

        private BufferedImage render(int w, int h) {
            BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
            Graphics2D g = smooth(img.getGraphics());
            if (t.background != null) {
                double s = Math.max((double) w / t.background.getWidth(), (double) h / t.background.getHeight());
                int iw = (int) Math.ceil(t.background.getWidth() * s), ih = (int) Math.ceil(t.background.getHeight() * s);
                g.drawImage(t.background, (w - iw) / 2, (h - ih) / 2, iw, ih, null);
                g.setColor(new Color(0, 0, 0, (int) (t.backgroundDim * 255)));
                g.fillRect(0, 0, w, h);
            } else {
                g.setPaint(new GradientPaint(0, 0, t.bg, w, h, t.bg2));
                g.fillRect(0, 0, w, h);
                Random r = new Random(1337);
                int cell = 22;
                for (int y = 0; y < h; y += cell) {
                    for (int x = 0; x < w; x += cell) {
                        int a = r.nextInt(100) < 18 ? 6 + r.nextInt(14) : 0;
                        if (a == 0) continue;
                        g.setColor(new Color(255, 255, 255, a));
                        g.fillRect(x + 1, y + 1, cell - 2, cell - 2);
                    }
                }
                g.setPaint(new RadialGradientPaint(w * 0.25f, h * 0.45f, w * 0.55f,
                        new float[]{0f, 1f}, new Color[]{alpha(t.accent, 46), alpha(t.accent, 0)}));
                g.fillRect(0, 0, w, h);
            }
            g.setPaint(new GradientPaint(0, h * 0.55f, new Color(0, 0, 0, 0), 0, h, new Color(0, 0, 0, 120)));
            g.fillRect(0, 0, w, h);
            g.dispose();
            return img;
        }
    }

    /** Rounded translucent card. */
    static final class Card extends JPanel {
        private final Color fill;
        private final int radius;
        private final Theme.Style style;
        private final Color ink;
        private final Color shadow;
        private BufferedImage handCache;

        Card(Color fill, int radius) {
            this(fill, radius, Theme.Style.CLEAN, Color.WHITE, new Color(0, 0, 0, 90));
        }

        Card(Theme t, Color fill) {
            this(fill, t.radius, t.style, t.text, t.paperShadow);
        }

        private Card(Color fill, int radius, Theme.Style style, Color ink, Color shadow) {
            super(null);
            this.fill = fill;
            this.radius = radius;
            this.style = style;
            this.ink = ink;
            this.shadow = shadow;
            setOpaque(false);
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int w = getWidth(), h = getHeight();
            if (w <= 0 || h <= 0) {
                g2.dispose();
                return;
            }
            if (style == Theme.Style.HAND) {
                if (handCache == null || handCache.getWidth() != w || handCache.getHeight() != h) {
                    handCache = renderHand(w, h);
                }
                g2.drawImage(handCache, 0, 0, null);
                g2.dispose();
                return;
            }
            if (style == Theme.Style.SKETCH) {
                g2.setColor(fill);
                g2.fillRect(4, 4, w - 8, h - 8);
                Random r = new Random(w * 31L + h);
                for (int i = 0; i < w * h / 40; i++) {
                    g2.setColor(new Color(255, 255, 255, r.nextInt(10)));
                    g2.fillRect(r.nextInt(w), r.nextInt(h), 1, 1 + r.nextInt(3));
                }
                sketchRect(g2, 6, 6, w - 12, h - 12, alpha(ink, 210), w * 7L + h);
                g2.dispose();
                return;
            }
            g2.setColor(fill);
            g2.fill(new RoundRectangle2D.Float(0, 0, w, h, radius * 2f, radius * 2f));
            Random r = new Random(w * 31L + h);
            for (int i = 0; i < w * h / 60; i++) {
                int a = r.nextInt(14);
                g2.setColor(r.nextBoolean() ? new Color(255, 250, 220, a) : new Color(0, 0, 0, a + 6));
                g2.fillRect(r.nextInt(w), r.nextInt(h), 1 + r.nextInt(2), 1);
            }
            g2.setColor(new Color(0, 0, 0, 140));
            g2.drawRect(0, 0, w - 1, h - 1);
            g2.setColor(new Color(214, 204, 160, 34));
            g2.drawRect(3, 3, w - 7, h - 7);
            if (style == Theme.Style.MILITARY) {
                for (int[] p : new int[][]{{12, 12}, {w - 12, 12}, {12, h - 12}, {w - 12, h - 12}}) {
                    g2.setColor(new Color(0, 0, 0, 150));
                    g2.fillOval(p[0] - 5, p[1] - 4, 10, 10);
                    g2.setColor(new Color(120, 116, 82));
                    g2.fillOval(p[0] - 5, p[1] - 5, 9, 9);
                    g2.setColor(new Color(186, 180, 136));
                    g2.fillOval(p[0] - 3, p[1] - 3, 3, 3);
                }
            }
            g2.dispose();
        }

        private BufferedImage renderHand(int w, int h) {
            BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
            Graphics2D g = smooth(img.getGraphics());
            java.awt.geom.Path2D.Float paper = Ink.tornPath(1.5f, 1.5f, w - 3f, h - 5f, w * 31L + h);
            g.setColor(alpha(shadow, 170));
            java.awt.geom.AffineTransform old = g.getTransform();
            g.translate(2, 2);
            g.fill(paper);
            g.setTransform(old);
            g.setColor(fill);
            g.fill(paper);
            Random r = new Random(w * 17L + h * 7L);
            for (int i = 0; i < w * h / 90; i++) {
                g.setColor(new Color(28, 27, 24, 8 + r.nextInt(12)));
                g.fillRect(r.nextInt(w), r.nextInt(h), 1, 1);
            }
            g.setColor(alpha(Color.WHITE, 60));
            g.drawLine(6, 2, w - 8, 2);
            Ink.tornBorder(g, 1.5f, 1.5f, w - 3f, h - 5f, alpha(ink, 235), w * 31L + h);
            g.dispose();
            return img;
        }
    }

    enum Kind { PRIMARY, GHOST, WINDOW, CLOSE }

    static final class Btn extends JButton {
        private final Theme t;
        private final Kind kind;
        private boolean hover;

        Btn(Theme t, String text, Kind kind) {
            super(text);
            this.t = t;
            this.kind = kind;
            setContentAreaFilled(false);
            setBorderPainted(false);
            setFocusPainted(false);
            setOpaque(false);
            setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
            setFont(t.font(kind == Kind.PRIMARY ? java.awt.Font.BOLD : java.awt.Font.PLAIN, kind == Kind.PRIMARY ? 18f : 13f));
            addMouseListener(new MouseAdapter() {
                @Override public void mouseEntered(MouseEvent e) { hover = true; repaint(); }
                @Override public void mouseExited(MouseEvent e) { hover = false; repaint(); }
            });
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int w = getWidth(), h = getHeight();
            boolean on = isEnabled();
            if (!on) g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.5f));
            if (t.style == Theme.Style.HAND) {
                paintHand(g2, w, h, on);
                g2.dispose();
                return;
            }
            float r = kind == Kind.PRIMARY ? t.radius : Math.min(10, t.radius * 2);
            switch (kind) {
                case PRIMARY -> {
                    Color c = hover && on ? t.accentHover : t.accent;
                    if (t.style == Theme.Style.SKETCH) {
                        g2.setColor(c);
                        g2.fillRect(3, 3, w - 6, h - 6);
                        sketchRect(g2, 4, 4, w - 8, h - 8, alpha(t.onAccent, hover && on ? 255 : 200), 77);
                        g2.setColor(t.onAccent);
                        g2.setFont(getFont());
                        centerText(g2, getText(), w, h);
                        g2.dispose();
                        return;
                    }
                    g2.setPaint(new GradientPaint(0, 0, c.brighter(), 0, h, c.darker()));
                    g2.fill(new RoundRectangle2D.Float(0, 0, w, h, r, r));
                    if (t.style == Theme.Style.MILITARY) {
                        g2.setColor(new Color(255, 245, 200, 60));
                        g2.drawLine(1, 1, w - 2, 1);
                        g2.drawLine(1, 1, 1, h - 2);
                        g2.setColor(new Color(0, 0, 0, 150));
                        g2.drawRect(0, 0, w - 1, h - 1);
                        g2.drawLine(2, h - 2, w - 2, h - 2);
                        g2.setStroke(new BasicStroke(2f));
                        g2.setColor(new Color(0, 0, 0, 40));
                        for (int x = -h; x < w; x += 14) g2.drawLine(x, h, x + h, 0);
                        g2.setStroke(new BasicStroke(1f));
                    }
                    g2.setColor(t.onAccent);
                }
                case GHOST -> {
                    g2.setColor(hover && on ? new Color(255, 255, 255, 34) : new Color(255, 255, 255, 16));
                    if (t.style == Theme.Style.SKETCH) {
                        g2.fillRect(3, 3, w - 6, h - 6);
                        sketchRect(g2, 4, 4, w - 8, h - 8, alpha(t.text, hover && on ? 220 : 140), 31);
                    } else {
                        g2.fill(new RoundRectangle2D.Float(0, 0, w, h, r, r));
                    }
                    g2.setColor(t.text);
                }
                case WINDOW, CLOSE -> {
                    if (hover) {
                        g2.setColor(kind == Kind.CLOSE ? t.offline : new Color(255, 255, 255, 30));
                        g2.fill(new RoundRectangle2D.Float(0, 0, w, h, r, r));
                    }
                    g2.setColor(hover && kind == Kind.CLOSE ? Color.WHITE : t.muted);
                    g2.setStroke(new BasicStroke(1.6f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                    int cx = w / 2, cy = h / 2;
                    if (kind == Kind.CLOSE) {
                        g2.drawLine(cx - 5, cy - 5, cx + 5, cy + 5);
                        g2.drawLine(cx + 5, cy - 5, cx - 5, cy + 5);
                    } else {
                        g2.drawLine(cx - 6, cy, cx + 6, cy);
                    }
                    g2.dispose();
                    return;
                }
            }
            g2.setFont(getFont());
            centerText(g2, getText(), w, h);
            g2.dispose();
        }

        private void paintHand(Graphics2D g2, int w, int h, boolean on) {
            switch (kind) {
                case PRIMARY -> {
                    int dy = getModel().isPressed() ? 2 : 0;
                    int dx = hover && on && dy == 0 ? 1 : 0;
                    g2.translate(dx, dy);
                    g2.setColor(hover && on ? t.accentHover : t.accent);
                    g2.fillRect(0, 0, w - 2, h - 3);
                    Ink.tornBorder(g2, 1, 1, w - 4, h - 4, alpha(t.text, 220), 1939);
                    g2.setColor(t.onAccent);
                    g2.setFont(getFont());
                    FontMetrics fm = g2.getFontMetrics();
                    float tw = 0;
                    for (char ch : getText().toCharArray()) tw += fm.charWidth(ch) + 0.8f;
                    tw -= 0.8f;
                    Ink.spaced(g2, getText(), (w - tw) / 2f, (h - fm.getHeight()) / 2f + fm.getAscent() - 1, 0.8f);
                }
                case GHOST -> {
                    if (hover && on) {
                        Ink.hatch(g2, new java.awt.Rectangle(2, 2, w - 4, h - 4), (float) Math.toRadians(45), 7f,
                                alpha(t.inkSoft, 55));
                    }
                    Ink.tornBorder(g2, 1.5f, 1.5f, w - 4, h - 4, alpha(t.text, hover && on ? 220 : 150), 77);
                    g2.setColor(t.text);
                    g2.setFont(getFont());
                    FontMetrics fm = g2.getFontMetrics();
                    g2.drawString(getText(), (w - fm.stringWidth(getText())) / 2f,
                            (h - fm.getHeight()) / 2f + fm.getAscent() - 1);
                }
                case WINDOW, CLOSE -> {
                    int cx = w / 2, cy = h / 2;
                    if (hover) {
                        g2.setColor(kind == Kind.CLOSE ? alpha(t.text, 230) : alpha(t.panel, 220));
                        g2.fillRect(3, 3, w - 6, h - 6);
                    } else if (t.background != null || t.handPaper != null) {
                        g2.setColor(alpha(t.panel, 175));
                        g2.fillOval(cx - 11, cy - 11, 22, 22);
                    }
                    g2.setColor(hover && kind == Kind.CLOSE ? t.panel : t.text);
                    g2.setStroke(new BasicStroke(1.8f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                    if (kind == Kind.CLOSE) {
                        g2.drawLine(cx - 5, cy - 5, cx + 5, cy + 5);
                        g2.drawLine(cx + 5, cy - 5, cx - 5, cy + 5);
                    } else {
                        g2.drawLine(cx - 6, cy + 1, cx + 6, cy + 1);
                    }
                }
            }
        }
    }

    static final class Field extends JTextField {
        private final Theme t;
        private final String placeholder;

        Field(Theme t, String text, String placeholder) {
            super(text);
            this.t = t;
            this.placeholder = placeholder;
            setOpaque(false);
            setForeground(t.text);
            setCaretColor(t.accent);
            setSelectionColor(alpha(t.accent, 120));
            setFont(t.font(java.awt.Font.PLAIN, 16f));
            setBorder(new EmptyBorder(0, t.style == Theme.Style.HAND ? 8 : 16, 0,
                    t.style == Theme.Style.HAND ? 8 : 16));
            addFocusListener(new java.awt.event.FocusAdapter() {
                @Override public void focusGained(java.awt.event.FocusEvent e) { repaint(); }
                @Override public void focusLost(java.awt.event.FocusEvent e) { repaint(); }
            });
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            float r = Math.min(12, t.radius * 2);
            if (t.style == Theme.Style.HAND) {
                int w = getWidth(), h = getHeight();
                if (hasFocus()) {
                    g2.setColor(t.accent);
                    g2.setStroke(new BasicStroke(2f));
                } else {
                    g2.setColor(alpha(t.text, 170));
                    g2.setStroke(new BasicStroke(1.1f));
                }
                g2.drawLine(1, h - 2, w - 2, h - 2);
                if (hasFocus()) {
                    g2.setColor(alpha(t.accent, 70));
                    g2.drawLine(1, h - 2, w - 2, h - 2);
                }
                if (getText().isEmpty() && !hasFocus()) {
                    g2.setColor(t.muted);
                    g2.setFont(t.font(java.awt.Font.PLAIN, 12f));
                    FontMetrics fm = g2.getFontMetrics();
                    g2.drawString(placeholder, 8, (h - fm.getHeight()) / 2 + fm.getAscent());
                }
                g2.dispose();
                super.paintComponent(g);
                return;
            }
            g2.setColor(t.field);
            if (t.style == Theme.Style.SKETCH) {
                g2.fillRect(3, 3, getWidth() - 6, getHeight() - 6);
                sketchRect(g2, 4, 4, getWidth() - 8, getHeight() - 8, alpha(t.text, hasFocus() ? 230 : 120), 13);
            } else {
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), r, r));
                g2.setColor(hasFocus() ? t.accent : new Color(255, 255, 255, 30));
                g2.setStroke(new BasicStroke(hasFocus() ? 1.6f : 1f));
                g2.draw(new RoundRectangle2D.Float(0.8f, 0.8f, getWidth() - 1.6f, getHeight() - 1.6f, r, r));
            }
            if (getText().isEmpty() && !hasFocus()) {
                g2.setColor(t.muted);
                g2.setFont(getFont());
                FontMetrics fm = g2.getFontMetrics();
                g2.drawString(placeholder, 16, (getHeight() - fm.getHeight()) / 2 + fm.getAscent());
            }
            g2.dispose();
            super.paintComponent(g);
        }
    }

    /** Thin rounded progress bar; value < 0 = indeterminate (animated). */
    static final class Progress extends JComponent {
        private final Theme t;
        private double value = -1;
        private float phase;
        private final Timer anim;

        Progress(Theme t) {
            this.t = t;
            anim = new Timer(16, e -> { phase = (phase + 0.012f) % 1f; repaint(); });
        }

        void set(double v) {
            value = v;
            if (v < 0 && isShowing()) anim.start(); else anim.stop();
            repaint();
        }

        void stop() { anim.stop(); }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int w = getWidth(), h = getHeight();
            boolean square = t.style != Theme.Style.CLEAN;
            float rr = square ? 0 : h;
            g2.setColor(new Color(0, 0, 0, 90));
            g2.fill(new RoundRectangle2D.Float(0, 0, w, h, rr, rr));
            g2.setColor(t.style == Theme.Style.MILITARY ? t.online : t.style == Theme.Style.SKETCH ? t.text : t.accent);
            if (value < 0) {
                float seg = w * 0.3f;
                float x = -seg + (w + seg) * phase;
                g2.setClip(new RoundRectangle2D.Float(0, 0, w, h, rr, rr));
                g2.fill(new RoundRectangle2D.Float(x, 0, seg, h, rr, rr));
            } else {
                g2.fill(new RoundRectangle2D.Float(0, 0, (float) (w * Math.min(1, value)), h, rr, rr));
            }
            if (t.style == Theme.Style.MILITARY) {
                g2.setClip(null);
                g2.setColor(new Color(0, 0, 0, 120));
                for (int x = 7; x < w; x += 8) g2.drawLine(x, 0, x, h);
                g2.drawRect(0, 0, w - 1, h - 1);
            } else if (t.style == Theme.Style.SKETCH) {
                g2.setClip(null);
                g2.setColor(new Color(0, 0, 0, 70));
                for (int x = -h; x < w; x += 5) g2.drawLine(x, h, x + h, 0);
            }
            g2.dispose();
        }
    }

    /** Pill with a colored dot: server status. */
    static final class Pill extends JComponent {
        private final Theme t;
        private String text = "";
        private Color dot;

        Pill(Theme t) {
            this.t = t;
            this.dot = t.muted;
            setFont(t.font(java.awt.Font.PLAIN, 13f));
        }

        void set(String text, Color dot) {
            this.text = text;
            this.dot = dot;
            setSize(getPreferredSize());
            repaint();
        }

        @Override
        public Dimension getPreferredSize() {
            FontMetrics fm = getFontMetrics(getFont());
            return new Dimension(fm.stringWidth(text) + 46, 32);
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int h = getHeight();
            g2.setColor(new Color(0, 0, 0, 90));
            g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), h, h, h));
            g2.setColor(alpha(dot, 70));
            g2.fillOval(10, h / 2 - 8, 16, 16);
            g2.setColor(dot);
            g2.fillOval(14, h / 2 - 4, 8, 8);
            g2.setColor(t.text);
            g2.setFont(getFont());
            FontMetrics fm = g2.getFontMetrics();
            g2.drawString(text, 34, (h - fm.getHeight()) / 2 + fm.getAscent());
            g2.dispose();
        }
    }

    static final class Steps extends JComponent {
        enum State { PENDING, ACTIVE, DONE }

        private final Theme t;
        private final String[] labels;
        private final State[] states;
        private float spin;
        private final Timer anim;

        Steps(Theme t, String[] labels) {
            this.t = t;
            this.labels = labels;
            this.states = new State[labels.length];
            java.util.Arrays.fill(states, State.PENDING);
            setFont(t.font(java.awt.Font.PLAIN, 14f));
            anim = new Timer(30, e -> { spin = (spin + 12f) % 360f; repaint(); });
        }

        void activate(int index) {
            for (int i = 0; i < states.length; i++) {
                states[i] = i < index ? State.DONE : i == index ? State.ACTIVE : State.PENDING;
            }
            if (!anim.isRunning()) anim.start();
            repaint();
        }

        void finish() {
            java.util.Arrays.fill(states, State.DONE);
            anim.stop();
            repaint();
        }

        void stop() { anim.stop(); }

        static int rowHeight() { return 30; }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            g2.setFont(getFont());
            FontMetrics fm = g2.getFontMetrics();
            int rh = rowHeight();
            for (int i = 0; i < labels.length; i++) {
                int y = i * rh, cy = y + rh / 2;
                switch (states[i]) {
                    case DONE -> {
                        g2.setColor(t.online);
                        g2.fillOval(0, cy - 9, 18, 18);
                        g2.setColor(t.onAccent);
                        g2.setStroke(new BasicStroke(2.2f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                        g2.drawPolyline(new int[]{5, 8, 13}, new int[]{cy, cy + 4, cy - 4}, 3);
                    }
                    case ACTIVE -> {
                        g2.setColor(alpha(t.accent, 50));
                        g2.setStroke(new BasicStroke(2.4f));
                        g2.drawOval(1, cy - 8, 16, 16);
                        g2.setColor(t.accent);
                        g2.setStroke(new BasicStroke(2.4f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                        g2.drawArc(1, cy - 8, 16, 16, (int) -spin, 100);
                    }
                    case PENDING -> {
                        g2.setColor(new Color(255, 255, 255, 40));
                        g2.fillOval(5, cy - 4, 8, 8);
                    }
                }
                g2.setColor(states[i] == State.PENDING ? alpha(t.muted, 150) : t.text);
                g2.drawString(labels[i], 30, (y + (rh - fm.getHeight()) / 2) + fm.getAscent());
            }
            g2.dispose();
        }
    }

    static final class Badge extends JComponent {
        private final Theme t;
        private final String text;

        Badge(Theme t, String text) {
            this.t = t;
            this.text = text;
            setFont(t.font(java.awt.Font.BOLD, 11f));
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int w = getWidth(), h = getHeight();
            Color ink = switch (t.style) {
                case MILITARY -> new Color(0xC0442E);
                case SKETCH -> t.text;
                case CLEAN -> new Color(0xF2B33D);
                case HAND -> t.accent;
            };
            float rr = t.style == Theme.Style.CLEAN ? h : 0;
            if (t.style != Theme.Style.CLEAN) g2.rotate(Math.toRadians(-4), w / 2.0, h / 2.0);
            g2.setColor(alpha(ink, 40));
            g2.fill(new RoundRectangle2D.Float(1, 1, w - 2, h - 2, rr, rr));
            g2.setColor(ink);
            g2.setStroke(new BasicStroke(1.6f));
            g2.draw(new RoundRectangle2D.Float(1.5f, 1.5f, w - 3f, h - 3f, rr, rr));
            g2.setFont(getFont());
            centerText(g2, text, w, h);
            g2.dispose();
        }
    }

    static final class Toggle extends JComponent {
        private final Theme t;
        private final String label;
        boolean on;

        Toggle(Theme t, String label, boolean on) {
            this.t = t;
            this.label = label;
            this.on = on;
            setFont(t.font(java.awt.Font.PLAIN, 14f));
            setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
            addMouseListener(new MouseAdapter() {
                @Override public void mouseClicked(MouseEvent e) { Toggle.this.on = !Toggle.this.on; repaint(); }
            });
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int h = getHeight(), sw = 42, sh = 24, y = (h - sh) / 2;
            g2.setColor(on ? t.accent : new Color(255, 255, 255, 40));
            g2.fill(new RoundRectangle2D.Float(0, y, sw, sh, sh, sh));
            g2.setColor(Color.WHITE);
            g2.fillOval(on ? sw - sh + 3 : 3, y + 3, sh - 6, sh - 6);
            g2.setColor(t.text);
            g2.setFont(getFont());
            FontMetrics fm = g2.getFontMetrics();
            g2.drawString(label, sw + 12, (h - fm.getHeight()) / 2 + fm.getAscent());
            g2.dispose();
        }
    }

    /** Stepped slider (e.g. RAM in 512 MB steps). */
    static final class Slider extends JComponent {
        private final Theme t;
        private final int min, max, step;
        int value;
        private final IntConsumer onChange;

        Slider(Theme t, int min, int max, int step, int value, IntConsumer onChange) {
            this.t = t;
            this.min = min;
            this.max = max;
            this.step = step;
            this.onChange = onChange;
            setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
            MouseAdapter m = new MouseAdapter() {
                @Override public void mousePressed(MouseEvent e) { drag(e.getX()); }
                @Override public void mouseDragged(MouseEvent e) { drag(e.getX()); }
            };
            addMouseListener(m);
            addMouseMotionListener(m);
            setValue(value);
        }

        void setValue(int v) {
            int clamped = Math.max(min, Math.min(max, Math.round((float) v / step) * step));
            value = clamped;
            onChange.accept(value);
            repaint();
        }

        private void drag(int x) {
            int pad = 10;
            double f = (x - pad) / (double) Math.max(1, getWidth() - pad * 2);
            setValue((int) (min + Math.max(0, Math.min(1, f)) * (max - min)));
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = smooth(g);
            int pad = 10, w = getWidth() - pad * 2, cy = getHeight() / 2;
            double f = (value - min) / (double) Math.max(1, max - min);
            g2.setColor(new Color(255, 255, 255, 30));
            g2.fill(new RoundRectangle2D.Float(pad, cy - 3, w, 6, 6, 6));
            g2.setColor(t.accent);
            g2.fill(new RoundRectangle2D.Float(pad, cy - 3, (float) (w * f), 6, 6, 6));
            int kx = (int) (pad + w * f);
            g2.setColor(alpha(t.accent, 70));
            g2.fillOval(kx - 11, cy - 11, 22, 22);
            g2.setColor(Color.WHITE);
            g2.fillOval(kx - 7, cy - 7, 14, 14);
            g2.dispose();
        }
    }
}
