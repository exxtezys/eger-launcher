#!/usr/bin/env python3
"""FancyMenu layouts — Егерь 1939, professional reception-room composition.

Canvas: 427x240 (Minecraft GUI coordinates). 
Design: paper document on left, brass/table button column on right, 
animated room background, stamp, brass accents, per-screen character.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "customization")
ASSETS = "/config/fancymenu/assets"

# Palette
CREAM = "#F5E8C6"
CREAM_D = "#E6D5B0"
PAPER_SHADOW = "#C4B48A"
INK = "#211812"
ACCENT = "#8B2E22"
ACCENT_H = "#A63B2C"
GOLD = "#C9A96E"
GOLD_D = "#8A7248"
MUTED = "#8A7860"
MUTED_L = "#A89878"
DARK = "#1A1410"
BRASS = "#B8965A"
WHITE = "#F5EBD3"

TITLE = "ЕГЕРЬ"
SUBTITLE = "НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939"
FOOTER = "© 1944 Опытная дегустационная станция · Архив НКПП"

# (file, identifier, headline, subhead, form_no, status, body_lines, note, buttons, mode)
# mode: "full" = paper+table+buttons layout; "header" = top plaque only (vanilla center content safe)
SCREENS = [
    ("ege-title.txt", "title_screen", "ДОСТУПНЫЕ РЕЖИМЫ", "Объявление отдела майонеза", "Ф-01", "ОЖИДАЕТ НАЗНАЧЕНИЯ",
     ["Объект: дегустационная станция №7", "Партия: майонез «Егерь», серия 1939", "К допуску: уполномоченные сотрудники"],
     "", [("Играть", "mc_titlescreen_singleplayer_button"),
          ("Сервер", "mc_titlescreen_multiplayer_button"),
          ("Настройки", "mc_titlescreen_options_button"),
          ("Выйти", "mc_titlescreen_quit_button")], "full"),
    ("ege-loading.txt", "progress_screen", "ДЕГУСТАЦИЯ", "Майонез maturity phase", "Ф-07", "ИДЁТ ПРОВЕРКА ПАРТИИ",
     ["Подготовка образцов...", "Проверка герметичности тары", "Ожидайте завершения процедуры"],
     "Ожидайте завершения процедуры", [], "header"),
    ("ege-connect.txt", "connect_screen", "ПОДКЛЮЧЕНИЕ", "Установка связи со станцией", "Ф-12", "РАДИОКАНАЛ ОТКРЫТ",
     ["Вызов удалённой станции...", "Согласование протокола передачи", "Не отключайте радиолинию"],
     "Установка связи...", [], "header"),
    ("ege-receiving.txt", "receiving_level_screen", "ПРИЁМ ДАННЫХ", "Загрузка сохранения партии", "Ф-14", "ПЕРЕДАЧА ДОКУМЕНТОВ",
     ["Получение архива партии...", "Сверка контрольных сумм", "Целостность документов проверяется"],
     "Приём документов...", [], "header"),
    ("ege-pause.txt", "pause_screen", "ПАУЗА", "Перерыв в дегустации", "Ф-03", "СЕАНС ПРИОСТАНОВЛЕН",
     ["Дегустация временно приостановлена", "Материалы партии сохранены на столе", "Возобновите при готовности"],
     "", [("Вернуться", "mc_pausescreen_return_to_game_button"),
          ("Настройки", "mc_pausescreen_options_button"),
          ("Выйти", "mc_pausescreen_quit_button")], "full"),
    ("ege-stations.txt", "join_multiplayer_screen", "СТАНЦИИ", "Доступные дегустационные точки", "Ф-11", "РЕЕСТР СТАНЦИЙ",
     ["Выберите станцию из реестра", "Проверьте статус соединения", "Допуск только по пропуску НКПП"],
     "Выберите станцию в списке", [], "header"),
    ("ege-options.txt", "options_screen", "НАСТРОЙКИ", "Параметры дегустационной станции", "Ф-09", "РЕГУЛИРОВКА ОБОРУДОВАНИЯ",
     ["Отрегулируйте параметры станции", "Изменения вступают немедленно", "Храните бланк в архиве"],
     "Настройте параметры станции", [], "header"),
    ("ege-newworld.txt", "create_world_screen", "НОВАЯ СТАНЦИЯ", "Создание дегустационной точки", "Ф-02", "РЕГИСТРАЦИЯ ОБЪЕКТА",
     ["Заполните бланк регистрации", "Укажите параметры новой станции", "Объект будет занесён в архив НКПП"],
     "Заполните бланк регистрации", [], "header"),
    ("ege-death.txt", "death_screen", "АКТ ПОТЕРИ", "Дегустационная комиссия фиксирует", "Ф-99", "ПАРТИЯ УТРАЧЕНА",
     ["Зафиксирована потеря образца", "Комиссия рекомендует повторный допуск", "Материалы направлены в архив"],
     "", [("Возродиться", "mc_deathscreen_respawn_button"),
          ("В меню", "mc_deathscreen_titlemenu_button")], "full"),
    ("ege-disconnected.txt", "disconnected_screen", "СВЯЗЬ ПОТЕРЯНА", "Станция временно недоступна", "Ф-13", "КАНАЛ РАЗОРВАН",
     ["Радиоканал со станцией прерван", "Проверьте линию связи", "Повторите попытку подключения"],
     "Проверьте соединение", [], "header"),
]


def layout(ident, body):
    return f"""type = fancymenu_layout

layout-meta {{
  identifier = {ident}
  layout_index = 0
  is_enabled = true
  render_custom_elements_behind_vanilla = true
}}

menu_background {{
  image_path = [source:local]{ASSETS}/anim_bg.gif
  slide = false
  repeat_texture = false
  background_type = image
}}

customization {{
  action = backgroundoptions
  keepaspectratio = true
}}

{body}
"""


def shape(eid, color, x, y, w, h, anchor="top-left", radius=0, opacity=1.0, fade="no_fading"):
    return f"""element {{
  element_type = shape
  instance_identifier = {eid}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  anchor_point = {anchor}
  color = {color}
  corner_radius_top_left = {radius}
  corner_radius_top_right = {radius}
  corner_radius_bottom_left = {radius}
  corner_radius_bottom_right = {radius}
  base_opacity = {opacity:.2f}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = {fade}
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  auto_sizing = false
  sticky_anchor = false
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}}

"""


def image(eid, src, x, y, w, h, anchor="top-left", opacity=1.0, fade="no_fading"):
    return f"""element {{
  source = [source:local]{ASSETS}/{src}
  repeat_texture = false
  nine_slice_texture = false
  nine_slice_texture_border_x = 5
  nine_slice_texture_border_y = 5
  element_type = image
  instance_identifier = {eid}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = {fade}
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = {opacity:.2f}
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}}

"""


def text(eid, value, x, y, w, h, anchor, color, scale=1.0, shadow=True, fade="fadein"):
    # Escape newlines for FancyMenu text_v2 source - use literal \n in value? 
    # FancyMenu text_v2 takes source directly; newlines in file can break parsing.
    # Replace actual newlines with space for safety, or keep single line.
    safe = str(value).replace("\n", " ")
    return f"""element {{
  source = {safe}
  source_mode = direct
  shadow = {"true" if shadow else "false"}
  scale = {scale:.2f}
  base_color = {color}
  text_border = 0
  line_spacing = 1
  enable_scrolling = false
  auto_line_wrapping = true
  remove_html_breaks = true
  parse_markdown = false
  element_type = text_v2
  instance_identifier = {eid}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = {fade}
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  sticky_anchor = false
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}}

"""


def vanilla_btn(vid, label, x, y, w, h, anchor="top-left"):
    return f"""vanilla_button {{
  button_element_executable_block_identifier = {vid}-exec
  [executable_block:{vid}-exec][type:generic] = [executables:]
  backgroundnormal = [source:local]{ASSETS}/btn_normal.png
  backgroundhovered = [source:local]{ASSETS}/btn_hover.png
  background_texture_inactive = [source:local]{ASSETS}/btn_normal.png
  restartbackgroundanimations = true
  loopbackgroundanimations = true
  nine_slice_custom_background = true
  nine_slice_border_x = 6
  nine_slice_border_y = 6
  navigatable = true
  widget_active_state_requirement_container_identifier = {vid}-active
  [loading_requirement_container_meta:{vid}-active] = [groups:][instances:]
  element_type = vanilla_button
  instance_identifier = {vid}
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
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = {vid}-load
  [loading_requirement_container_meta:{vid}-load] = [groups:][instances:]
  hoverlabel = 
  label = {label}
  label_base_color = {WHITE}
  label_hover_color = #FFFFFF
  label_scale = 1.0
  label_shadow = true
}}

"""


def build_screen(name, ident, headline, subhead, form_no, status, body_lines, note, buttons, mode="full"):
    b = ""
    ov = 0.32 if ident == "death_screen" else 0.20
    b += shape("overlay", DARK, 0, 0, 427, 240, opacity=ov)

    if mode == "header":
        b += shape("plaque_shadow", PAPER_SHADOW, 8, 8, 250, 52, radius=5, opacity=0.45)
        b += shape("plaque", CREAM, 6, 6, 250, 52, radius=5, opacity=0.90)
        b += image("plaque_tex", "paper.png", 6, 6, 250, 52, opacity=0.14)
        b += image("plaque_brass", "brass_strip.png", 6, 6, 250, 3, opacity=0.60)
        b += image("plaque_brass_b", "brass_strip.png", 6, 55, 250, 3, opacity=0.35)
        b += text("title", TITLE, 14, 12, 120, 20, "top-left", ACCENT, 1.2, True, "fadein")
        b += shape("rule_a", ACCENT, 14, 30, 48, 1, opacity=0.9)
        b += text("subtitle", SUBTITLE, 14, 33, 230, 8, "top-left", MUTED, 0.45, False, "fadein")
        b += text("headline", headline, 14, 42, 160, 10, "top-left", ACCENT, 0.72, True, "fadein")
        b += text("form_no", form_no, 210, 12, 40, 8, "top-left", GOLD_D, 0.50, False, "no_fading")
        b += text("status", status, 120, 42, 130, 8, "top-left", MUTED_L, 0.45, False, "fadein")
        b += shape("badge", CREAM_D, 340, 8, 80, 24, radius=4, opacity=0.75)
        b += image("badge_tex", "paper_dark.png", 340, 8, 80, 24, opacity=0.15)
        b += text("badge_t", "НКПП", 346, 12, 68, 8, "top-left", ACCENT, 0.55, True, "no_fading")
        b += text("badge_s", "1939", 346, 20, 68, 8, "top-left", MUTED, 0.45, False, "no_fading")
        b += text("footer", FOOTER, 0, -10, 427, 8, "bottom-centered", MUTED_L, 0.45, False, "no_fading")
        return layout(ident, b)

    b += shape("paper_shadow", PAPER_SHADOW, 12, 12, 266, 218, radius=6, opacity=0.55)
    b += shape("paper", CREAM, 10, 10, 266, 218, radius=6, opacity=0.93)
    b += image("paper_tex", "paper.png", 10, 10, 266, 218, opacity=0.18)
    b += shape("paper_b_t", GOLD_D, 14, 14, 258, 1, opacity=0.30)
    b += shape("paper_b_b", GOLD_D, 14, 223, 258, 1, opacity=0.30)
    b += shape("paper_b_l", GOLD_D, 14, 14, 1, 210, opacity=0.30)
    b += shape("paper_b_r", GOLD_D, 271, 14, 1, 210, opacity=0.30)
    b += image("brass_paper", "brass_strip.png", 10, 10, 266, 4, opacity=0.55)

    b += shape("table_shadow", DARK, 282, 12, 135, 218, radius=6, opacity=0.35)
    b += shape("table", CREAM_D, 280, 10, 137, 218, radius=6, opacity=0.88)
    b += image("table_tex", "paper_dark.png", 280, 10, 137, 218, opacity=0.22)
    b += image("brass_top", "brass_strip.png", 280, 10, 137, 6, opacity=0.95)
    b += image("brass_bot", "brass_strip.png", 280, 222, 137, 6, opacity=0.95)

    b += image("stamp", "stamp_eger.png", 220, 14, 44, 44, opacity=0.85)

    b += text("title_shadow", TITLE, 20, 18, 200, 30, "top-left", DARK, 1.9, True, "no_fading")
    b += text("title", TITLE, 18, 16, 200, 30, "top-left", ACCENT, 1.9, True, "fadein")
    b += shape("rule_a", ACCENT, 18, 44, 72, 2, opacity=0.95)
    b += shape("rule_b", GOLD, 18, 47, 52, 1, opacity=0.85)
    b += text("subtitle", SUBTITLE, 18, 50, 210, 10, "top-left", MUTED, 0.55, False, "fadein")

    b += text("form_no", form_no, 18, 64, 40, 10, "top-left", GOLD_D, 0.60, False, "fadein")
    b += text("status", status, 52, 64, 170, 10, "top-left", MUTED_L, 0.52, False, "fadein")
    b += shape("sep", GOLD_D, 18, 74, 244, 1, opacity=0.35)

    b += text("headline", headline, 18, 80, 240, 14, "top-left", ACCENT, 1.0, True, "fadein")
    b += text("subhead", subhead, 18, 94, 240, 10, "top-left", MUTED, 0.65, False, "fadein")

    for i, line in enumerate(body_lines[:4]):
        yy = 112 + i * 13
        b += shape(f"bullet_{i}", ACCENT, 18, yy + 3, 2, 2, radius=1, opacity=0.55)
        b += text(f"body_{i}", line, 24, yy, 230, 10, "top-left", INK, 0.58, False, "fadein")
    b += shape("sig_line", GOLD_D, 18, 196, 90, 1, opacity=0.35)
    b += text("sig_label", "Подпись ответственного", 18, 198, 120, 8, "top-left", MUTED_L, 0.45, False, "no_fading")
    b += shape("date_line", GOLD_D, 160, 196, 60, 1, opacity=0.35)
    b += text("date_label", "Дата", 160, 198, 40, 8, "top-left", MUTED_L, 0.45, False, "no_fading")
    b += text("sheet", "Лист 1 / 1", 230, 198, 40, 8, "top-left", MUTED_L, 0.42, False, "no_fading")

    b += text("panel_label", "ПАНЕЛЬ УПРАВЛЕНИЯ", 286, 20, 125, 10, "top-left", MUTED, 0.50, False, "fadein")
    b += shape("panel_sep", GOLD_D, 286, 30, 125, 1, opacity=0.30)
    b += text("panel_form", form_no, 286, 34, 125, 8, "top-left", GOLD_D, 0.50, False, "no_fading")

    if buttons:
        btn_w, btn_h, gap = 121, 20, 4
        total_h = len(buttons) * btn_h + (len(buttons) - 1) * gap
        start_y = 218 - 10 - total_h
        bx = 288
        for i, (label, vid) in enumerate(buttons):
            by = start_y + i * (btn_h + gap)
            b += vanilla_btn(vid, label, bx, by, btn_w, btn_h)
    else:
        note_lines = [l for l in note.split("\n") if l.strip()]
        ny = 168
        for i, nl in enumerate(note_lines[:4]):
            b += text(f"note_{i}", nl, 286, ny + i * 11, 125, 10, "top-left", MUTED, 0.58, False, "fadein")
        b += shape("note_rule", GOLD_D, 286, 162, 40, 1, opacity=0.35)

    b += text("footer", FOOTER, 0, -10, 427, 8, "bottom-centered", MUTED_L, 0.45, False, "no_fading")
    for idx, (rx, ry) in enumerate([(12, 12), (270, 12), (12, 222), (270, 222)]):
        b += shape(f"rivet_{idx}", BRASS, rx, ry, 4, 4, radius=2, opacity=0.75)

    return layout(ident, b)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, ident, headline, subhead, form_no, status, body_lines, note, buttons, mode in SCREENS:
        content = build_screen(name, ident, headline, subhead, form_no, status, body_lines, note, buttons, mode)
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("wrote", name)

if __name__ == "__main__":
    main()
