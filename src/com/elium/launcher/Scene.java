package com.elium.launcher;

import java.awt.AlphaComposite;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Composite;
import java.awt.Graphics2D;
import java.awt.RadialGradientPaint;
import java.awt.Shape;
import java.awt.geom.AffineTransform;
import java.awt.geom.Arc2D;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Line2D;
import java.awt.geom.Path2D;
import java.time.LocalTime;
import java.util.Random;

/**
 * Живые детали поверх нарисованной комнаты: часы идут, дирижабль ползёт за окном,
 * пыль висит в свете лампы, сама лампа подрагивает.
 *
 * Координаты — в логической сетке 920x560, как в tools/gen-scene.py.
 */
final class Scene {
    static final int W = 920, H = 560;
    /** Внутренняя часть окна (за рамой), по ней ходит дирижабль. */
    static final int WIN_X = 564, WIN_Y = 38, WIN_W = 312, WIN_H = 206;
    static final int BAR_A = 668, BAR_B = 772, BAR_Y = 141;
    static final int LAMP_X = 470, LAMP_Y = 126;
    static final int CLOCK_X = 516, CLOCK_Y = 58, CLOCK_R = 23;

    private static final int MOTES = 58;
    private final double[] baseX = new double[MOTES];
    private final double[] baseY = new double[MOTES];
    private final double[] phase = new double[MOTES];
    private final double[] speed = new double[MOTES];
    private final double[] size = new double[MOTES];

    Scene() {
        Random r = new Random(1944);
        for (int i = 0; i < MOTES; i++) {
            baseX[i] = 320 + r.nextDouble() * 440;
            baseY[i] = 230 + r.nextDouble() * 300;
            phase[i] = r.nextDouble() * Math.PI * 2;
            speed[i] = 5 + r.nextDouble() * 15;
            size[i] = 0.7 + r.nextDouble() * 1.35;
        }
    }

    void paint(Graphics2D g, double time) {
        lamp(g, time);
        clock(g);
        airship(g, time);
        dust(g, time);
    }

    private void lamp(Graphics2D g, double t) {
        double flicker = Math.sin(t * 0.66) * 0.5 + 0.5
                + Math.sin(t * 12.7) * 0.02 + Math.sin(t * 28.3) * 0.015;
        float a = (float) (0.055 + 0.05 * Math.max(0, Math.min(1, flicker)));
        float r = 150f;
        g.setPaint(new RadialGradientPaint(LAMP_X, LAMP_Y, r,
                new float[]{0f, 0.55f, 1f},
                new Color[]{new Color(255, 214, 150, (int) (a * 255)),
                        new Color(255, 206, 140, (int) (a * 120)),
                        new Color(255, 200, 130, 0)}));
        g.fillRect((int) (LAMP_X - r), (int) (LAMP_Y - r), (int) (r * 2), (int) (r * 2));
    }

    private void clock(Graphics2D g) {
        LocalTime now = LocalTime.now();
        double hour = (now.getHour() % 12 + now.getMinute() / 60.0) * 30 - 90;
        double minute = (now.getMinute() + now.getSecond() / 60.0) * 6 - 90;
        double second = now.getSecond() * 6 - 90;
        g.setStroke(new BasicStroke(2.2f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.setColor(new Color(38, 30, 20, 235));
        hand(g, hour, 10);
        g.setStroke(new BasicStroke(1.35f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        hand(g, minute, 15);
        g.setStroke(new BasicStroke(0.9f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.setColor(new Color(140, 46, 34, 210));
        hand(g, second, 17);
        g.setColor(new Color(38, 30, 20, 235));
        g.fill(new Ellipse2D.Double(CLOCK_X - 1.7, CLOCK_Y - 1.7, 3.4, 3.4));
    }

    private void hand(Graphics2D g, double deg, double len) {
        double a = Math.toRadians(deg);
        g.draw(new Line2D.Double(CLOCK_X, CLOCK_Y,
                CLOCK_X + Math.cos(a) * len, CLOCK_Y + Math.sin(a) * len));
    }

    private void airship(Graphics2D g, double t) {
        double period = 52;
        // стартуем с середины окна, чтобы дирижабль был виден сразу
        double p = ((t + 14) % period) / period;
        double x = 500 + p * 470;
        double y = 116 + Math.sin(t * 0.55) * 2.6;
        double fade = Math.min(1, Math.min(p / 0.07, (1 - p) / 0.07));
        if (fade <= 0) return;

        Shape clip = g.getClip();
        g.clipRect(WIN_X, WIN_Y, WIN_W, WIN_H);
        Composite oc = g.getComposite();
        g.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, (float) fade));
        AffineTransform tr = g.getTransform();
        g.translate(x, y);

        // корпус заметно темнее неба, иначе силуэт пропадает на ночном фоне
        Color hull = new Color(9, 12, 17);
        g.setColor(hull);
        g.fill(new Ellipse2D.Double(-32, -10, 64, 20));
        // гондола
        g.fill(new Path2D.Double(new java.awt.geom.RoundRectangle2D.Double(-12, 7, 26, 7, 5, 5)));
        // хвостовое оперение
        Path2D fin = new Path2D.Double();
        fin.moveTo(29, -7);
        fin.lineTo(40, -16);
        fin.lineTo(38, -2);
        fin.lineTo(41, 11);
        fin.lineTo(29, 5);
        fin.closePath();
        g.fill(fin);
        // лунный блик по верхней кромке
        g.setColor(new Color(228, 218, 190, 205));
        g.setStroke(new BasicStroke(1.15f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g.draw(new Arc2D.Double(-31, -9.6, 62, 19.2, 8, 164, Arc2D.OPEN));
        g.setColor(new Color(150, 144, 128, 100));
        g.draw(new Arc2D.Double(-31, -9, 62, 19, 185, 160, Arc2D.OPEN));
        // швы обшивки
        g.setColor(new Color(190, 182, 160, 40));
        g.setStroke(new BasicStroke(0.7f));
        for (int i = -2; i <= 2; i++) {
            double sx = i * 11.5;
            g.draw(new Arc2D.Double(sx - 6, -9.2, 12, 18.4, 200, 140, Arc2D.OPEN));
        }
        // освещённые окна гондолы
        g.setColor(new Color(244, 198, 118, 235));
        for (int i = 0; i <= 2; i++) {
            g.fill(new Ellipse2D.Double(-8.5 + i * 6.4, 9.5, 2.4, 2.0));
        }
        // винт и руль
        g.setColor(new Color(16, 19, 24));
        g.setStroke(new BasicStroke(1.1f));
        g.draw(new Line2D.Double(14, 10.5, 20, 10.5));
        g.draw(new Line2D.Double(20, 8.5, 20, 12.5));
        g.setColor(new Color(228, 218, 190, 150));
        g.draw(new Line2D.Double(34, -12, 36.5, -8));
        // ходовой огонь
        float blink = (float) (0.30 + 0.70 * Math.abs(Math.sin(t * 2.2)));
        g.setColor(new Color(240, 92, 66, (int) (230 * blink)));
        g.fill(new Ellipse2D.Double(-34, -1, 3.2, 3.2));
        g.setTransform(tr);
        g.setComposite(oc);
        g.setClip(clip);

        muntins(g);
    }

    /** Решётка окна поверх дирижабля, чтобы он проходил за ней. */
    private void muntins(Graphics2D g) {
        g.setColor(new Color(54, 43, 30));
        g.fillRect(BAR_A - 2, WIN_Y, 4, WIN_H);
        g.fillRect(BAR_B - 2, WIN_Y, 4, WIN_H);
        g.fillRect(WIN_X, BAR_Y - 2, WIN_W, 4);
        g.setColor(new Color(186, 152, 96, 110));
        g.drawLine(BAR_A - 1, WIN_Y, BAR_A - 1, WIN_Y + WIN_H);
        g.drawLine(BAR_B - 1, WIN_Y, BAR_B - 1, WIN_Y + WIN_H);
        g.drawLine(WIN_X, BAR_Y - 1, WIN_X + WIN_W, BAR_Y - 1);
        g.setColor(new Color(12, 10, 7, 110));
        g.drawLine(BAR_A + 2, WIN_Y, BAR_A + 2, WIN_Y + WIN_H);
        g.drawLine(BAR_B + 2, WIN_Y, BAR_B + 2, WIN_Y + WIN_H);
    }

    private void dust(Graphics2D g, double t) {
        g.setColor(new Color(255, 244, 214));
        for (int i = 0; i < MOTES; i++) {
            double y = baseY[i] - ((t * speed[i] + phase[i] * 40) % 300);
            if (y < 210) y += 300;
            double x = baseX[i] + Math.sin(t * 0.42 + phase[i]) * 16
                    + Math.cos(t * 0.21 + phase[i] * 2) * 7;
            double tw = 0.35 + 0.65 * Math.abs(Math.sin(t * 0.8 + phase[i] * 3));
            int alpha = (int) (16 + 64 * tw);
            g.setColor(new Color(255, 243, 210, alpha));
            double s = size[i];
            g.fill(new Ellipse2D.Double(x, y, s, s));
        }
    }
}
