package com.elium.launcher;

import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import java.awt.Color;
import java.awt.Desktop;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.Point;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.RoundRectangle2D;
import java.awt.image.BufferedImage;
import java.net.URI;
import java.nio.file.Path;
import java.util.List;
import java.util.regex.Pattern;

public final class LauncherApp {
    private static final Pattern NICK = Pattern.compile("[A-Za-z0-9_]{3,16}");
    private static final int CARD_W = 340;
    static final String VERSION = "0.1.0";
    private static final String[][] STEPS = {
            {"java", "Java 21"},
            {"game", "Minecraft"},
            {"neoforge", "NeoForge и библиотеки"},
            {"assets", "Ресурсы игры"},
            {"modpack", "Моды сервера"},
            {"launch", "Запуск игры"},
    };

    private final Config cfg;
    private final Theme t;
    private final int maxRam;
    private JFrame frame;
    private UI.Field nickField;
    private UI.Btn play;
    private UI.Btn settings;
    private UI.Progress bar;
    private JLabel status;
    private UI.Pill server;
    private UI.Card loginCard;
    private UI.Card loadCard;
    private UI.Steps steps;
    private JLabel loadAction;
    private JLabel loadFile;
    private JLabel loadBytes;
    private UI.Progress loadBar;
    private final Object rateLock = new Object();
    private long rateBytes = -1, rateTime;
    private double speed;
    private int ramMb;
    private boolean autoConnect;

    private LauncherApp(Config cfg) {
        this.cfg = cfg;
        this.t = Theme.load(cfg.projectName, cfg.minecraftVersion);
        long totalMb = ((com.sun.management.OperatingSystemMXBean)
                java.lang.management.ManagementFactory.getOperatingSystemMXBean()).getTotalMemorySize() / 1048576;
        this.maxRam = (int) Math.max(2048, totalMb - 2048);
        this.ramMb = Math.min(cfg.ramMb(), maxRam);
        this.autoConnect = cfg.autoConnect();
    }

    public static void main(String[] args) {
        try {
            Config cfg = new Config();
            if (SelfUpdate.run(cfg)) {
                System.exit(0);
                return;
            }
            SwingUtilities.invokeLater(() -> new LauncherApp(cfg).show());
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Ошибка запуска: " + e.getMessage(), "Лаунчер", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void show() {
        frame = new JFrame(t.title + " (тестовая версия " + VERSION + ")");
        frame.setUndecorated(true);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(t.width, t.height);
        frame.setShape(new RoundRectangle2D.Double(0, 0, t.width, t.height, t.radius * 2 + 4, t.radius * 2 + 4));
        frame.setIconImages(List.of(icon(16), icon(32), icon(64)));

        UI.Backdrop root = new UI.Backdrop(t);
        frame.setContentPane(root);
        int w = t.width, h = t.height;

        loginCard = buildLoginCard();
        loginCard.setLocation(w - CARD_W - 40, (h - loginCard.getHeight()) / 2 + 10);
        root.add(loginCard);
        loadCard = buildLoadCard();
        loadCard.setLocation(w - CARD_W - 40, (h - loadCard.getHeight()) / 2 + 10);
        loadCard.setVisible(false);
        root.add(loadCard);

        UI.Btn min = new UI.Btn(t, "", UI.Kind.WINDOW);
        min.setBounds(w - 88, 8, 36, 28);
        min.addActionListener(e -> frame.setState(JFrame.ICONIFIED));
        root.add(min);
        UI.Btn close = new UI.Btn(t, "", UI.Kind.CLOSE);
        close.setBounds(w - 46, 8, 36, 28);
        close.addActionListener(e -> System.exit(0));
        root.add(close);

        JLabel top = text(t.title, Font.BOLD, 13f, t.muted);
        top.setBounds(20, 12, 300, 20);
        root.add(top);

        int leftW = w - CARD_W - 100;
        int y = h / 2 - 110;
        if (t.logo != null) {
            JComponent logo = new Picture(t.logo, t.logoHeight);
            logo.setBounds(48, y + 74 - t.logoHeight, leftW, t.logoHeight);
            root.add(logo);
        } else {
            JLabel title = text(t.title.toUpperCase(), Font.BOLD, 64f, t.text);
            title.setBounds(44, y, leftW, 80);
            root.add(title);
        }
        JLabel sub = text(t.subtitle, Font.PLAIN, 17f, t.muted);
        sub.setBounds(48, y + 82, leftW, 26);
        root.add(sub);

        server = new UI.Pill(t);
        server.setLocation(48, y + 124);
        if (!cfg.serverHost.isEmpty()) {
            server.set("Проверка сервера...", t.muted);
            root.add(server);
        }

        int lx = 48;
        for (String[] link : t.links) {
            UI.Btn b = new UI.Btn(t, link[0], UI.Kind.GHOST);
            int bw = b.getFontMetrics(b.getFont()).stringWidth(link[0]) + 32;
            b.setBounds(lx, h - 64, bw, 36);
            b.addActionListener(e -> browse(link[1]));
            root.add(b);
            lx += bw + 10;
        }

        JComponent drag = new JComponent() {};
        drag.setBounds(0, 0, w - 96, 44);
        dragMove(drag, frame);
        root.add(drag);

        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
        if (nickField.getText().isEmpty()) nickField.requestFocusInWindow(); else play.requestFocusInWindow();

        if (!cfg.serverHost.isEmpty()) {
            pingServer();
            new Timer(30_000, e -> pingServer()).start();
        }
    }

    private UI.Card buildLoginCard() {
        int ch = 330, pad = 28, iw = CARD_W - pad * 2;
        UI.Card card = new UI.Card(t.panel, t.radius);
        card.setSize(CARD_W, ch);

        JLabel head = text("ЯВКА НА ФРОНТ", Font.BOLD, 24f, t.text);
        head.setBounds(pad, 24, iw, 30);
        card.add(head);
        UI.Badge badge = new UI.Badge(t, "ТЕСТ");
        badge.setBounds(pad + iw - 58, 28, 58, 22);
        card.add(badge);
        JLabel hint = text("Позывной: латиница, цифры и _ (3–16)", Font.PLAIN, 12.5f, t.muted);
        hint.setBounds(pad, 54, iw, 20);
        card.add(hint);

        nickField = new UI.Field(t, cfg.nick(), "Позывной");
        nickField.setBounds(pad, 88, iw, 48);
        nickField.addActionListener(e -> start());
        card.add(nickField);

        play = new UI.Btn(t, "В БОЙ", UI.Kind.PRIMARY);
        play.setBounds(pad, 150, iw - 58, 54);
        play.addActionListener(e -> start());
        card.add(play);

        settings = new UI.Btn(t, "⚙", UI.Kind.GHOST);
        settings.setFont(new Font("Segoe UI Symbol", Font.PLAIN, 20));
        settings.setToolTipText("Настройки");
        settings.setBounds(pad + iw - 50, 150, 50, 54);
        settings.addActionListener(e -> openSettings());
        card.add(settings);

        status = text(summary(), Font.PLAIN, 13f, t.muted);
        status.setBounds(pad, 226, iw, 20);
        card.add(status);
        bar = new UI.Progress(t);
        bar.setBounds(pad, 254, iw, 8);
        bar.setVisible(false);
        card.add(bar);

        JLabel ver = text("Лаунчер " + VERSION + " · тестовая версия", Font.PLAIN, 11.5f, UI.alpha(t.muted, 160));
        ver.setBounds(pad, ch - 40, iw, 18);
        card.add(ver);
        return card;
    }

    private UI.Card buildLoadCard() {
        int pad = 28, iw = CARD_W - pad * 2;
        int stepsH = STEPS.length * UI.Steps.rowHeight();
        int ch = 70 + stepsH + 150;
        UI.Card card = new UI.Card(t.panel, t.radius);
        card.setSize(CARD_W, ch);

        JLabel head = text("СБОРЫ", Font.BOLD, 24f, t.text);
        head.setBounds(pad, 24, iw, 30);
        card.add(head);

        String[] labels = new String[STEPS.length];
        for (int i = 0; i < STEPS.length; i++) labels[i] = STEPS[i][1];
        steps = new UI.Steps(t, labels);
        steps.setBounds(pad, 66, iw, stepsH);
        card.add(steps);

        int y = 66 + stepsH + 14;
        loadAction = text(" ", Font.BOLD, 13.5f, t.text);
        loadAction.setBounds(pad, y, iw, 20);
        card.add(loadAction);
        loadFile = text(" ", Font.PLAIN, 12f, t.muted);
        loadFile.setBounds(pad, y + 22, iw, 18);
        card.add(loadFile);
        loadBar = new UI.Progress(t);
        loadBar.setBounds(pad, y + 50, iw, 8);
        card.add(loadBar);
        loadBytes = text(" ", Font.PLAIN, 12f, t.muted);
        loadBytes.setBounds(pad, y + 66, iw, 18);
        card.add(loadBytes);

        JLabel hint = text("Первый запуск долгий, дальше — только обновления", Font.PLAIN, 11.5f,
                UI.alpha(t.muted, 160));
        hint.setBounds(pad, ch - 40, iw, 18);
        card.add(hint);
        return card;
    }

    private void openSettings() {
        JDialog d = new JDialog(frame, "Настройки", true);
        d.setUndecorated(true);
        int dw = 420, dh = 330;
        d.setSize(dw, dh);
        d.setShape(new RoundRectangle2D.Double(0, 0, dw, dh, t.radius * 2, t.radius * 2));
        UI.Card root = new UI.Card(t.dialog, t.radius);
        d.setContentPane(root);
        dragMove(root, d);

        JLabel head = text("Настройки", Font.BOLD, 20f, t.text);
        head.setBounds(28, 22, 300, 28);
        root.add(head);

        JLabel ramLabel = text("", Font.PLAIN, 14f, t.text);
        ramLabel.setBounds(28, 70, 360, 20);
        root.add(ramLabel);
        UI.Slider ram = new UI.Slider(t, 1024, maxRam, 512, ramMb,
                v -> ramLabel.setText("Оперативная память: " + gb(v)));
        ram.setBounds(18, 94, dw - 36, 32);
        root.add(ram);
        JLabel ramHint = text("Рекомендуется 4–6 ГБ для сборки с модами", Font.PLAIN, 12f, t.muted);
        ramHint.setBounds(28, 126, 360, 18);
        root.add(ramHint);

        UI.Toggle connect = new UI.Toggle(t, "Сразу подключаться к серверу", autoConnect);
        connect.setBounds(28, 160, 360, 30);
        connect.setVisible(!cfg.serverHost.isEmpty());
        root.add(connect);

        UI.Btn folder = new UI.Btn(t, "Открыть папку игры", UI.Kind.GHOST);
        folder.setBounds(28, 206, dw - 56, 40);
        folder.addActionListener(e -> {
            try { Desktop.getDesktop().open(cfg.gameDir.toFile()); } catch (Exception ex) { error(ex); }
        });
        root.add(folder);

        UI.Btn cancel = new UI.Btn(t, "Отмена", UI.Kind.GHOST);
        cancel.setBounds(28, dh - 66, 120, 42);
        cancel.addActionListener(e -> d.dispose());
        root.add(cancel);
        UI.Btn save = new UI.Btn(t, "Сохранить", UI.Kind.PRIMARY);
        save.setFont(t.font(Font.BOLD, 15f));
        save.setBounds(dw - 28 - 160, dh - 66, 160, 42);
        save.addActionListener(e -> {
            ramMb = ram.value;
            autoConnect = connect.on;
            try { cfg.saveUser(nickField.getText().trim(), ramMb, autoConnect); } catch (Exception ex) { error(ex); }
            status.setText(summary());
            d.dispose();
        });
        root.add(save);
        d.getRootPane().setDefaultButton(save);

        d.setLocationRelativeTo(frame);
        d.setVisible(true);
    }

    private String summary() {
        return "Память " + gb(ramMb) + (autoConnect && !cfg.serverHost.isEmpty() ? " · автовход на сервер" : "");
    }

    private static String gb(int mb) {
        return (mb % 1024 == 0 ? Integer.toString(mb / 1024) : String.format("%.1f", mb / 1024.0)) + " ГБ";
    }

    private JLabel text(String s, int style, float size, Color c) {
        JLabel l = new JLabel(s);
        l.setFont(t.font(style, size));
        l.setForeground(c);
        return l;
    }

    private static void dragMove(JComponent handle, java.awt.Window window) {
        MouseAdapter m = new MouseAdapter() {
            private Point start;
            @Override public void mousePressed(MouseEvent e) { start = e.getPoint(); }
            @Override public void mouseDragged(MouseEvent e) {
                Point p = e.getLocationOnScreen();
                window.setLocation(p.x - start.x, p.y - start.y);
            }
        };
        handle.addMouseListener(m);
        handle.addMouseMotionListener(m);
    }

    private void browse(String url) {
        try { Desktop.getDesktop().browse(URI.create(url)); } catch (Exception e) { error(e); }
    }

    private void pingServer() {
        Thread th = new Thread(() -> {
            String text;
            Color col;
            try {
                ServerPing.Status st = ServerPing.ping(cfg.serverHost, cfg.serverPort);
                text = "Фронт открыт · " + st.online() + "/" + st.max() + " бойцов";
                col = t.online;
            } catch (Exception e) {
                text = "Фронт закрыт — сессия ещё не началась";
                col = t.offline;
            }
            String ft = text;
            Color fc = col;
            SwingUtilities.invokeLater(() -> server.set(ft, fc));
        }, "ping");
        th.setDaemon(true);
        th.start();
    }

    private void start() {
        String nick = nickField.getText().trim();
        if (!NICK.matcher(nick).matches()) {
            status.setForeground(t.offline);
            status.setText("Неверный позывной: 3–16 символов, A–Z, 0–9, _");
            nickField.requestFocusInWindow();
            return;
        }
        status.setForeground(t.muted);
        int ram = ramMb;
        boolean connect = autoConnect;
        setBusy(true);
        Thread worker = new Thread(() -> {
            try {
                cfg.saveUser(nick, ram, connect);
                Net.Progress p = new Net.Progress() {
                    @Override public void update(String text, int done, int total) { progress(text, done, total); }
                    @Override public void stage(String key) { LauncherApp.this.stage(key); }
                    @Override public void file(String name) { LauncherApp.this.file(name); }
                    @Override public void bytes(long done, long total) { LauncherApp.this.bytes(done, total); }
                };
                Path javaw = JavaRuntime.ensure(cfg.gameDir, p);
                GameInstaller.Profile prof = new GameInstaller(cfg).install(javaw, p);
                ModpackSync.sync(cfg, p);
                p.stage("launch");
                p.bytes(-1, -1);
                progress("Запуск игры...", 0, 0);
                Process proc = GameLauncher.launch(cfg, javaw, prof, nick, ram, connect);
                Thread.sleep(4000);
                if (!proc.isAlive() && proc.exitValue() != 0) {
                    throw new IllegalStateException("Игра завершилась с кодом " + proc.exitValue()
                            + ".\nЛог: " + cfg.gameDir.resolve("game-output.log"));
                }
                SwingUtilities.invokeLater(() -> {
                    steps.finish();
                    loadAction.setText("Игра запущена — окно Minecraft откроется сейчас");
                });
                Thread.sleep(1500);
                System.exit(0);
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> {
                    setBusy(false);
                    status.setForeground(t.offline);
                    status.setText("Ошибка — подробности в окне");
                    error(e);
                });
            }
        }, "launch");
        worker.start();
    }

    private void setBusy(boolean busy) {
        loginCard.setVisible(!busy);
        loadCard.setVisible(busy);
        if (busy) {
            synchronized (rateLock) { rateBytes = -1; speed = 0; }
            steps.activate(0);
            loadAction.setText("Подготовка...");
            loadFile.setText(" ");
            loadBytes.setText(" ");
            loadBar.set(-1);
        } else {
            steps.stop();
            loadBar.stop();
            status.setText(summary());
        }
    }

    private void progress(String text, int done, int total) {
        SwingUtilities.invokeLater(() -> {
            loadAction.setText(total > 1 ? text + "  " + done + " / " + total : text);
            if (total > 1 && !bytesActive) loadBar.set(done / (double) total);
        });
    }

    private volatile boolean bytesActive;

    private void stage(String key) {
        for (int i = 0; i < STEPS.length; i++) {
            if (STEPS[i][0].equals(key)) {
                int idx = i;
                SwingUtilities.invokeLater(() -> steps.activate(idx));
            }
        }
        bytes(-1, -1);
        file(null);
    }

    private void file(String name) {
        SwingUtilities.invokeLater(() -> loadFile.setText(name == null ? " " : name));
    }

    private void bytes(long done, long total) {
        if (done < 0) {
            bytesActive = false;
            synchronized (rateLock) { rateBytes = -1; speed = 0; }
            SwingUtilities.invokeLater(() -> { loadBytes.setText(" "); loadBar.set(-1); });
            return;
        }
        bytesActive = true;
        long now = System.nanoTime();
        double sp;
        synchronized (rateLock) {
            if (rateBytes < 0 || done < rateBytes) {
                rateBytes = done;
                rateTime = now;
            } else if (now - rateTime >= 500_000_000L) {
                double inst = (done - rateBytes) / ((now - rateTime) / 1e9);
                speed = speed == 0 ? inst : speed * 0.7 + inst * 0.3;
                rateBytes = done;
                rateTime = now;
            } else {
                return;
            }
            sp = speed;
        }
        StringBuilder s = new StringBuilder(mb(done));
        if (total > 0) s.append(" из ").append(mb(total));
        if (sp > 0) {
            s.append("  ·  ").append(mb((long) sp)).append("/с");
            if (total > done) s.append("  ·  осталось ").append(eta((long) ((total - done) / sp)));
        }
        String txt = s.toString();
        double frac = total > 0 ? done / (double) total : -1;
        SwingUtilities.invokeLater(() -> {
            loadBytes.setText(txt);
            loadBar.set(frac);
        });
    }

    private static String mb(long b) {
        if (b < 1024 * 1024) return String.format("%.0f КБ", b / 1024.0);
        if (b < 1024L * 1024 * 1024) return String.format("%.1f МБ", b / 1048576.0);
        return String.format("%.2f ГБ", b / 1073741824.0);
    }

    private static String eta(long sec) {
        if (sec < 60) return sec + " с";
        if (sec < 3600) return (sec / 60) + " мин " + (sec % 60) + " с";
        return (sec / 3600) + " ч " + (sec % 3600 / 60) + " мин";
    }

    private void error(Exception e) {
        JOptionPane.showMessageDialog(frame, e.getMessage() == null ? e.toString() : e.getMessage(),
                "Ошибка", JOptionPane.ERROR_MESSAGE);
    }

    private Image icon(int size) {
        if (t.icon != null) return t.icon.getScaledInstance(size, size, Image.SCALE_SMOOTH);
        if (t.logo != null) return t.logo.getScaledInstance(-1, size, Image.SCALE_SMOOTH);
        BufferedImage img = new BufferedImage(size, size, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = UI.smooth(img.getGraphics());
        g.setColor(t.accent);
        g.fillRoundRect(0, 0, size, size, size / 3, size / 3);
        g.setColor(t.onAccent);
        g.setFont(t.font(Font.BOLD, size * 0.62f));
        UI.centerText(g, t.title.substring(0, 1).toUpperCase(), size, size);
        g.dispose();
        return img;
    }

    private static final class Picture extends JComponent {
        private final BufferedImage img;
        private final int height;

        Picture(BufferedImage img, int height) {
            this.img = img;
            this.height = height;
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = UI.smooth(g);
            int w = img.getWidth() * height / img.getHeight();
            g2.drawImage(img, 0, 0, Math.min(w, getWidth()), height, null);
            g2.dispose();
        }
    }
}
