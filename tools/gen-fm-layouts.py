#!/usr/bin/env python3
"""FancyMenu layouts — Егерь 1939, professional composition (427x240 GUI canvas)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "customization")

TITLE = "ЕГЕРЬ"
SUBTITLE = "НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939"
FOOTER = "© 1944 Опытная дегустационная станция"

CREAM = "#F5E8C6"; CREAM_SHADE = "#D9C495"; INK = "#211812"
ACCENT = "#8B2E22"; ACCENT_HOVER = "#A63B2C"; MUTED = "#A88866"
HIGHLIGHT = "#C9A96E"; RULER = "#6B4222"; VIGNETTE = "#1A1410"

SCREENS = [
    ("ege-title.txt", "title_screen", "ДОСТУПНЫЕ РЕЖИМЫ", "ОБЪЯВЛЕНИЕ ОТДЕЛА МАЙОНЕЗА", [("Играть","mc_titlescreen_singleplayer_button"),("Сервер","mc_titlescreen_multiplayer_button"),("Настройки","mc_titlescreen_options_button"),("Выйти","mc_titlescreen_quit_button")]),
    ("ege-loading.txt", "progress_screen", "ДЕГУСТАЦИЯ", "Маёнез maturity phase", []),
    ("ege-connect.txt", "connect_screen", "ПОДКЛЮЧЕНИЕ", "К станции через радиоволны", []),
    ("ege-receiving.txt", "receiving_level_screen", "ПРИЁМ", "Загрузка сохранения партии", []),
    ("ege-pause.txt", "pause_screen", "ПАУЗА", "Нажми R для продолжения", [("Вернуться","mc_pausescreen_return_to_game_button"),("Настройки","mc_pausescreen_options_button"),("Выйти","mc_pausescreen_quit_button")]),
    ("ege-stations.txt", "join_multiplayer_screen", "СТАНЦИИ", "Доступные дегустационные точки", []),
    ("ege-options.txt", "options_screen", "ОПЦИИ", "Настройка дегустации", []),
    ("ege-newworld.txt", "create_world_screen", "НОВАЯ СТАНЦИЯ", "Создание новой дегустационной точки", []),
    ("ege-death.txt", "death_screen", "КОНЕЦ МАРИНАДИ", "Дегустационный кома", [("Возродиться","mc_deathscreen_respawn_button"),("В меню","mc_deathscreen_titlemenu_button")]),
    ("ege-disconnected.txt", "disconnected_screen", "ОТСЫКЛЫВАЕМСЯ", "Станция временно недоступна", []),
]

def layout(ident, body):
    return ("type = fancymenu_layout\n\nlayout-meta {\n  identifier = %s\n  layout_index = 0\n  is_enabled = true\n  render_custom_elements_behind_vanilla = true\n}\n\nmenu_background {\n  image_path = [source:local]/config/fancymenu/assets/anim_bg.gif\n  slide = false\n  repeat_texture = false\n  background_type = image\n}\n\ncustomization {\n  action = backgroundoptions\n  keepaspectratio = true\n}\n\n%s\n" % (ident, body))

def shape(eid, color, x, y, w, h, anchor="top-left", radius=0, opacity=1.0):
    return ("element {\n  element_type = shape\n  instance_identifier = %s\n  x = %d\n  y = %d\n  width = %d\n  height = %d\n  anchor_point = %s\n  color = %s\n  corner_radius_top_left = %d\n  corner_radius_top_right = %d\n  corner_radius_bottom_left = %d\n  corner_radius_bottom_right = %d\n  base_opacity = %.2f\n  appearance_delay = no_delay\n  appearance_delay_seconds = 1.0\n  fade_in_v2 = no_fading\n  fade_in_speed = 1.0\n  fade_out = no_fading\n  fade_out_speed = 1.0\n  auto_sizing = false\n  sticky_anchor = false\n  stretch_x = false\n  stretch_y = false\n  stay_on_screen = true\n}\n\n" % (eid,x,y,w,h,anchor,color,radius,radius,radius,radius,opacity))

def text(eid, value, x, y, w, h, anchor, color, scale=1.0, shadow=True, fade="fadein"):
    return ("element {\n  source = %s\n  source_mode = direct\n  shadow = %s\n  scale = %.2f\n  base_color = %s\n  text_border = 0\n  line_spacing = 1\n  enable_scrolling = false\n  auto_line_wrapping = true\n  remove_html_breaks = true\n  parse_markdown = false\n  element_type = text_v2\n  instance_identifier = %s\n  appearance_delay = no_delay\n  appearance_delay_seconds = 1.0\n  fade_in_v2 = %s\n  fade_in_speed = 1.0\n  fade_out = no_fading\n  fade_out_speed = 1.0\n  base_opacity = 1.0\n  auto_sizing = false\n  sticky_anchor = false\n  anchor_point = %s\n  x = %d\n  y = %d\n  width = %d\n  height = %d\n  stretch_x = false\n  stretch_y = false\n  stay_on_screen = true\n}\n\n" % (value, "true" if shadow else "false", scale, color, eid, fade, anchor, x, y, w, h))

def btn(vid, label, x, y, w=110, h=22, accent=ACCENT, hover=ACCENT_HOVER):
    return ("vanilla_button {\n  element_type = vanilla_button\n  instance_identifier = %s\n  label_base_color = %s\n  label_hover_color = %s\n  label_scale = 1.0\n  label_shadow = true\n}\n\n" % (vid, accent, hover))

def build(ident, headline, sub, buttons):
    body = ""
    # top-left paper window (title block)
    body += shape("win_tl", CREAM, 8, 8, 200, 60, "top-left", 8, 0.88)
    # main paper panel (left two-thirds)
    body += shape("panel", CREAM, 8, 72, 260, 160, "top-left", 8, 0.85)
    # table surface (right side)
    body += shape("table", CREAM_SHADE, 272, 72, 147, 160, "top-left", 8, 0.80)
    # title
    body += text("title1", TITLE, 14, 12, 190, 28, "top-left", ACCENT, 1.6, True)
    body += text("title2", TITLE, 12, 14, 190, 28, "top-left", HIGHLIGHT, 1.6, True)
    body += shape("rule1", ACCENT, 14, 40, 60, 2, "top-left")
    body += shape("rule2", HIGHLIGHT, 14, 43, 45, 1, "top-left")
    body += text("sub", SUBTITLE, 14, 46, 190, 12, "top-left", MUTED, 0.7, False)
    # headline
    body += text("headline", headline, 14, 78, 250, 16, "top-left", ACCENT, 1.0, True)
    body += text("subhead", sub, 14, 92, 250, 12, "top-left", MUTED, 0.75, False)
    # footer
    body += text("footer", FOOTER, 0, -8, 420, 8, "bottom-centered", MUTED, 0.5, False)
    # rivets left edge
    for i in range(4):
        body += shape("rivet_%d"%i, RULER, 4, 80+i*36, 6, 6, "top-left", 3)
    # buttons bottom-right
    bx, by = 280, 170
    for label, vid in buttons:
        body += btn(vid, label, bx, by, 130, 20)
        by += 24
    # if many buttons, wrap to two columns
    return layout(ident, body)

def main():
    for name, ident, headline, sub, buttons in SCREENS:
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(ident, headline, sub, buttons))
        print("wrote", name)

main()