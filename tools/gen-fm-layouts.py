#!/usr/bin/env python3
"""FancyMenu layouts — Егерь 1939 room scene, rich composition."""
import os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "customization")

TITLE = "ЕГЕРЬ"
SUBTITLE = "НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939"
FOOTER = "© 1944 Опытная дегустационная станция"

CREAM = "#F5E8C6"; CREAM_SHADE = "#D9C495"; INK = "#211812"
ACCENT = "#8B2E22"; ACCENT_HOVER = "#A63B2C"; MUTED = "#A88866"
HIGHLIGHT = "#C9A96E"; RULER = "#6B4222"; VIGNETTE = "#1A1410"

def uid(name): return "%s-%s" % (name, random.randint(1000, 9999))

def layout(identifier, body):
    return "type = fancymenu_layout\n\nlayout-meta {\n  identifier = %s\n  layout_index = 0\n  is_enabled = true\n  render_custom_elements_behind_vanilla = true\n}\n\nmenu_background {\n  image_path = [source:location]{\"placeholder\":\"local\",\"values\":{\"path\":\"/config/fancymenu/assets/anim_bg.gif\"}}\n  slide = false\n  repeat_texture = false\n  background_type = image\n}\n\ncustomization {\n  action = backgroundoptions\n  keepaspectratio = true\n}\n\n%s\n" % (identifier, body)

def image(eid, src, x, y, w, h, anchor="top-left", opacity=1.0, fade="no_fading"):
    return """element {
  source = [source:local]/config/fancymenu/assets/%s
  repeat_texture = false
  nine_slice_texture = false
  nine_slice_texture_border_x = 5
  nine_slice_texture_border_y = 5
  element_type = image
  instance_identifier = %s
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = %s
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = %.2f
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  anchor_point = %s
  x = %d
  y = %d
  width = %d
  height = %d
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}

""" % (src, eid, fade, opacity, anchor, x, y, w, h)

def text(eid, value, x, y, w, h, anchor, color, scale=1.0, shadow=True):
    return """element {
  source = %s
  source_mode = direct
  shadow = %s
  scale = %.2f
  base_color = %s
  text_border = 0
  line_spacing = 1
  enable_scrolling = false
  auto_line_wrapping = true
  remove_html_breaks = true
  code_block_single_color = #737373FF
  code_block_multi_color = #565656FF
  headline_line_color = #A9A9A9FF
  separation_line_color = #A9A9A9FF
  hyperlink_color = #0771FCFF
  quote_color = #818181FF
  quote_indent = 8.0
  quote_italic = false
  bullet_list_dot_color = #A9A9A9FF
  bullet_list_indent = 8.0
  bullet_list_spacing = 3.0
  parse_markdown = false
  element_type = text_v2
  instance_identifier = %s
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = fadein
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  anchor_point = %s
  x = %d
  y = %d
  width = %d
  height = %d
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}

""" % (value, "true" if shadow else "false", scale, color, eid, anchor, x, y, w, h)

def shape(eid, color, x, y, w, h, anchor, radius=0, opacity=1.0):
    return """element {
  element_type = shape
  instance_identifier = %s
  x = %d
  y = %d
  width = %d
  height = %d
  anchor_point = %s
  color = %s
  corner_radius_top_left = %d
  corner_radius_top_right = %d
  corner_radius_bottom_left = %d
  corner_radius_bottom_right = %d
  base_opacity = %.2f
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = no_fading
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}

""" % (eid, x, y, w, h, anchor, color, radius, radius, radius, radius, opacity)

def btn(eid, label, x, y, w=220, h=40):
    return """element {
  button_element_executable_block_identifier = %s
  [executable_block:%s][type:generic] = [executables:]
  restartbackgroundanimations = true
  loopbackgroundanimations = true
  nine_slice_custom_background = false
  nine_slice_border_x = 5
  nine_slice_border_y = 5
  hoverlabel = 
  label = %s
  navigatable = true
  widget_active_state_requirement_container_identifier = %s
  [loading_requirement_container_meta:%s] = [groups:][instances:]
  element_type = custom_button
  instance_identifier = %s
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = fadein
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  anchor_point = top-left
  x = %d
  y = %d
  width = %d
  height = %d
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}

""" % (uid("blk"), uid("blk"), label, uid("req"), uid("req"), eid, x, y, w, h)

# ── SCREENS ────────────────────────────────────────────────────────────────
SCREENS = [
    ("ege-title.txt", "title_screen", "ДОСТУПНЫЕ РЕЖИМЫ", "ОБЪЯВЛЕНИЕ ОТДЕЛА МАЙОНЕЗА", [
        ("Играть", "mc_titlescreen_singleplayer_button"),
        ("Сервер", "mc_titlescreen_multiplayer_button"),
        ("Настройки", "mc_titlescreen_options_button"),
        ("Выйти", "mc_titlescreen_quit_button"),
    ]),
    ("ege-loading.txt", "progress_screen", "ДЕГУСТАЦИЯ", "Маёнез maturity phase", []),
    ("ege-connect.txt", "connect_screen", "ПОДКЛЮЧЕНИЕ", "К станции через радиоволны", []),
    ("ege-receiving.txt", "receiving_level_screen", "ПРИЁМ", "Загрузка сохранения партии", []),
    ("ege-pause.txt", "pause_screen", "ПАУЗА", "Нажми R для продолжения", [
        ("Вернуться", "mc_pausescreen_return_to_game_button"),
        ("Настройки", "mc_pausescreen_options_button"),
        ("Выйти", "mc_pausescreen_quit_button"),
    ]),
    ("ege-stations.txt", "join_multiplayer_screen", "СТАНЦИИ", "Доступные дегустационные точки", []),
    ("ege-options.txt", "options_screen", "ОПЦИИ", "Настройка дегустации", []),
    ("ege-newworld.txt", "create_world_screen", "НОВАЯ СТАНЦИЯ", "Создание новой дегустационной точки", []),
    ("ege-death.txt", "death_screen", "КОНЕЦ МАРИНАДИ", "Дегустационный кома", [
        ("Возродиться", "mc_deathscreen_respawn_button"),
        ("В меню", "mc_deathscreen_titlemenu_button"),
    ]),
    ("ege-disconnected.txt", "disconnected_screen", "ОТСЫКЛЫВАЕМСЯ", "Станция временно недоступна", []),
]

def build(ident, headline, sub, buttons):
    body = ""
    # composition: window/table panel on left, decorations
    body += shape("panel_left", CREAM, 40, 80, 420, 520, "top-left", 12, 0.85)
    body += shape("panel_right", CREAM_SHADE, 480, 80, 420, 520, "top-left", 12, 0.75)
    # title block
    body += text("title1", TITLE, 60, 90, 400, 60, "top-left", ACCENT, 2.6, True)
    body += text("title2", TITLE, 56, 94, 400, 60, "top-left", HIGHLIGHT, 2.6, True)
    body += shape("rule1", ACCENT, 60, 150, 120, 3, "top-left")
    body += shape("rule2", HIGHLIGHT, 60, 155, 90, 2, "top-left")
    body += text("sub", SUBTITLE, 60, 165, 400, 20, "top-left", MUTED, 1.0, False)
    # screen headline
    body += text("headline", headline, 60, 200, 400, 24, "top-left", ACCENT, 1.3, True)
    body += text("subhead", sub, 60, 222, 400, 16, "top-left", MUTED, 0.9, False)
    # footer
    body += text("footer", FOOTER, 0, -12, 900, 12, "bottom-centered", MUTED, 0.6, False)
    # buttons on right bottom
    bx, by = 520, 420
    for label, vid in buttons:
        body += btn(vid, label, bx, by, 200, 42)
        by += 52
    # rivets
    for i in range(6):
        body += shape("rivet_%d" % i, RULER, 24, 100 + i*70, 10, 10, "top-left", 5)
    return layout(ident, body)

def main():
    for name, ident, headline, sub, buttons in SCREENS:
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(ident, headline, sub, buttons))
        print("wrote", name)

main()