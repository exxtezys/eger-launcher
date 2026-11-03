package com.elium.launcher;

import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;
import java.awt.Desktop;
import java.awt.Font;
import java.io.File;
import java.nio.file.Path;
import java.util.List;

final class AdminPanel {
    private AdminPanel() {}

    static void show(JFrame owner, Config cfg, Theme t) {
        JDialog d = new JDialog(owner, "Админ-панель: custom-моды", true);
        d.setUndecorated(true);
        int dw = 760, dh = 470;
        d.setSize(dw, dh);
        d.setShape(new java.awt.geom.RoundRectangle2D.Double(0, 0, dw, dh, t.radius * 2, t.radius * 2));

        UI.Card root = new UI.Card(t, t.dialog);
        d.setContentPane(root);
        LauncherApp.dragMove(root, d);

        JLabel head = label(t, "Custom-моды (soundpad и другие)", Font.BOLD, 20f);
        head.setBounds(28, 22, 420, 28);
        root.add(head);

        JLabel hint = label(t, "Файлы лежат в папке custom-mods. Включённые моды копируются в mods при запуске.", Font.PLAIN, 12f, t.muted);
        hint.setBounds(28, 50, dw - 56, 18);
        root.add(hint);

        DefaultTableModel model = new DefaultTableModel(new Object[]{"Мод", "Файл", "Включён"}, 0) {
            @Override public boolean isCellEditable(int row, int column) { return false; }
        };
        JTable table = new JTable(model);
        table.setFont(t.font(Font.PLAIN, 13f));
        table.setRowHeight(24);
        table.getTableHeader().setFont(t.font(Font.BOLD, 12f));
        JScrollPane scroll = new JScrollPane(table);
        scroll.setBounds(28, 82, dw - 56, 250);
        root.add(scroll);

        Runnable refresh = () -> {
            model.setRowCount(0);
            try {
                for (CustomMods.Mod m : CustomMods.list(cfg)) {
                    model.addRow(new Object[]{m.name(), m.source().getFileName().toString(), m.enabled() ? "Да" : "Нет"});
                }
            } catch (Exception e) {
                JOptionPane.showMessageDialog(d, e.getMessage(), "Ошибка", JOptionPane.ERROR_MESSAGE);
            }
        };
        refresh.run();

        UI.Btn add = new UI.Btn(t, "Добавить", UI.Kind.GHOST);
        add.setBounds(28, 346, 118, 40);
        add.addActionListener(e -> {
            JFileChooser fc = new JFileChooser();
            fc.setDialogTitle("Выбери .jar мода");
            if (fc.showOpenDialog(d) == JFileChooser.APPROVE_OPTION) {
                try {
                    CustomMods.add(cfg, fc.getSelectedFile().toPath());
                    CustomMods.sync(cfg, null);
                    refresh.run();
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(d, ex.getMessage(), "Ошибка", JOptionPane.ERROR_MESSAGE);
                }
            }
        });
        root.add(add);

        UI.Btn toggle = new UI.Btn(t, "Вкл/выкл", UI.Kind.GHOST);
        toggle.setBounds(154, 346, 118, 40);
        toggle.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row < 0) return;
            String name = String.valueOf(model.getValueAt(row, 0));
            boolean enabled = "Да".equals(String.valueOf(model.getValueAt(row, 2)));
            try {
                CustomMods.setEnabled(cfg, name, !enabled);
                CustomMods.sync(cfg, null);
                refresh.run();
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(d, ex.getMessage(), "Ошибка", JOptionPane.ERROR_MESSAGE);
            }
        });
        root.add(toggle);

        UI.Btn remove = new UI.Btn(t, "Удалить", UI.Kind.GHOST);
        remove.setBounds(280, 346, 118, 40);
        remove.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row < 0) return;
            String name = String.valueOf(model.getValueAt(row, 0));
            int ok = JOptionPane.showConfirmDialog(d, "Удалить " + name + "?", "Удаление", JOptionPane.YES_NO_OPTION);
            if (ok != JOptionPane.YES_OPTION) return;
            try {
                CustomMods.remove(cfg, name);
                CustomMods.sync(cfg, null);
                refresh.run();
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(d, ex.getMessage(), "Ошибка", JOptionPane.ERROR_MESSAGE);
            }
        });
        root.add(remove);

        UI.Btn folder = new UI.Btn(t, "Открыть папку", UI.Kind.GHOST);
        folder.setBounds(406, 346, 132, 40);
        folder.addActionListener(e -> {
            try {
                Desktop.getDesktop().open(CustomMods.sourceDir(cfg).toFile());
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(d, ex.getMessage(), "Ошибка", JOptionPane.ERROR_MESSAGE);
            }
        });
        root.add(folder);

        UI.Btn refreshBtn = new UI.Btn(t, "Обновить", UI.Kind.GHOST);
        refreshBtn.setBounds(546, 346, 118, 40);
        refreshBtn.addActionListener(e -> {
            try { refresh.run(); } catch (Exception ex) {
                JOptionPane.showMessageDialog(d, ex.getMessage(), "Ошибка", JOptionPane.ERROR_MESSAGE);
            }
        });
        root.add(refreshBtn);

        UI.Btn close = new UI.Btn(t, "Закрыть", UI.Kind.PRIMARY);
        close.setBounds(dw - 28 - 130, dh - 66, 130, 42);
        close.addActionListener(e -> d.dispose());
        root.add(close);

        d.setLocationRelativeTo(owner);
        d.setVisible(true);
    }

    private static JLabel label(Theme t, String text, int style, float size) {
        return label(t, text, style, size, t.text);
    }

    private static JLabel label(Theme t, String text, int style, float size, java.awt.Color c) {
        JLabel l = new JLabel(text);
        l.setFont(t.font(style, size));
        l.setForeground(c);
        return l;
    }
}
