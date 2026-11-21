#!/usr/bin/env python3
"""
FancyMenu layouts — Complete redesign for "Егорь" 1939 theme.
New visual language: bold asymmetrical paper, red accent strips,
dynamic header blocks, redesigned buttons.

Palette: Cream paper (#F5E8C6), Oxblood red (#8B2E22), Brass (#C9A96E),
Ink black (#211812), Muted parchment (#A88866).
All coordinates for Minecraft's default 854x480 window at GUI scale 2 → 427x240 logical canvas.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "customization")

# ── constants ──────────────────────────────────────────────────────────────
CREAM          = "#F5E8C6"          # light paper/base
CREAM_SHADE    = "#D9C495"          # paper shadow/wear
ACCENT         = "#8B2E22"          # oxblood red
ACCENT_HOVER   = "#A63B2C"          # accent hover
MUTED          = "#A88866"          # secondary text / parchment
HIGHLIGHT      = "#C9A96E"          # brass highlight
RULER          = "#6B4222"          # dark ruler / strip
VIGNETTE       = "#1A1410"          # deep vignette
TITLE          = "ЕГЕРЬ"
SUBTITLE       = "НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939"
FOOTER         = "© 1944 Опытная дегустационная станция"


# ── vanilla_button — uses inline colors so no forward-ref issues ────────────
def vanilla_button(eid, base="#8B2E22", hover="#211812"):
    return "\n".join([
        "vanilla_button {",
        "  element_type = vanilla_button",
        "  instance_identifier = %s" % eid,
        "  label_base_color = %s" % base,
        "  label_hover_color = %s" % hover,
        "  label_scale = 1.0",
        "  label_shadow = true",
        "}",
        "",
    ])


# ── primitives ─────────────────────────────────────────────────────────────
def layout(identifier, elements):
    parts = [
        "type = fancymenu_layout",
        "",
        "layout-meta {",
        "  identifier = %s" % identifier,
        "  layout_index = 0",
        "  is_enabled = true",
        "  render_custom_elements_behind_vanilla = true",
        "}",
        "",
    ]
    parts.extend(elements)
    return "\n".join(parts).rstrip() + "\n"


def text(eid, value, x, y, w, h, anchor, color, scale=1.0, shadow=False):
    return "\n".join([
        "element {",
        "  element_type = text_v2",
        "  instance_identifier = %s" % eid,
        "  x = %s" % x,
        "  y = %s" % y,
        "  width = %s" % w,
        "  height = %s" % h,
        "  anchor_point = %s" % anchor,
        "  source = %s" % value,
        "  source_mode = direct",
        "  shadow = %s" % ("true" if shadow else "false"),
        "  base_color = %s" % color,
        "  scale = %s" % scale,
        "}",
        "",
    ])


def shape(eid, color, x, y, w, h, anchor, radius=0):
    return "\n".join([
        "element {",
        "  element_type = shape",
        "  instance_identifier = %s" % eid,
        "  x = %s" % x,
        "  y = %s" % y,
        "  width = %s" % w,
        "  height = %s" % h,
        "  anchor_point = %s" % anchor,
        "  color = %s" % color,
        "  corner_radius_top_left = %s" % radius,
        "  corner_radius_top_right = %s" % radius,
        "  corner_radius_bottom_left = %s" % radius,
        "  corner_radius_bottom_right = %s" % radius,
        "}",
        "",
    ])


# ── build paper sheet with rivets (loop-based) ────────────────────────────
def paper_sheet(dark):
    base = CREAM_SHADE if dark else CREAM
    rivets_color = "#4A2C1A" if dark else "#7B5130"
    elements = [
        shape("newtopaper", base, 0, 0, 2000, 1400, "top-left"),
        # double top accent strip
        shape("newtopstrip1", RULER, 0, 0, 2000, 3, "top-left"),
        shape("newtopstrip2", ACCENT, 0, 3, 2000, 3, "top-left"),
    ]
    # brass rivet line left side
    for i in range(5):
        y = 80 + i * 24
        elements.append(shape("newrivet_%d" % i, rivets_color, 20, y, 8, 8, "top-left", radius=4))
    # brass accent bar bottom
    elements.append(shape("newbottombar", ACCENT, 0, 0, 2000, 28, "bottom-left"))
    # vignette bands
    elements.append(shape("newvignette_top", VIGNETTE, 0, 0, 2000, 16, "top-left"))
    elements.append(shape("newvignette_bot", VIGNETTE, 0, 0, 2000, 16, "bottom-left"))
    return elements


def new_header(brand_color, sub_color):
    """Bold header: large title, rule, subtitle in shifted positions."""
    return [
        # large offset title (double-layer for depth)
        text("newtitle1", TITLE, 36, 30, 600, 80, "top-left", brand_color, 3.2, True),
        text("newtitle2", TITLE, 34, 34, 580, 76, "top-left", sub_color, 3.2, True),
        # double rule
        shape("newrule1", ACCENT, 30, 88, 140, 3, "top-left"),
        shape("newrule2", HIGHLIGHT, 30, 93, 120, 2, "top-left"),
        # subtitle block
        text("newsub", SUBTITLE, 28, 105, 620, 28, "top-left", MUTED, 1.4, False),
    ]


def new_footer():
    return [text("newfooter", FOOTER, 0, -20, 900, 10, "bottom-centered", MUTED, 0.6)]


def new_button(eid, base="#8B2E22", hover="#211812"):
    return "\n".join([
        "vanilla_button {",
        "  element_type = vanilla_button",
        "  instance_identifier = %s" % eid,
        "  label_base_color = %s" % base,
        "  label_hover_color = %s" % hover,
        "  label_scale = 1.1",
        "  label_shadow = true",
        "}",
        "",
    ])


# ── screen definitions — entirely reimagined ───────────────────────────────
# Each entry: (file_name, screen_identifier, headline, sub_headline, dark, button_ids)
# dark=False means no ambient band; dark=True adds a dark shade band at top.
SCREENS = [
    # title_screen — main menu, full width
    ("ege-title.txt",   "title_screen",   "ДОСТУПНЫЕ РЕЖИМЫ", "ОБЪЯВЛЕНИЕ ОТДЕЛА МАЙОНЕЗА",     False, ["mc_titlescreen_singleplayer_button",
                                                              "mc_titlescreen_multiplayer_button",
                                                              "mc_titlescreen_options_button",
                                                              "mc_titlescreen_quit_button"]),

    # progress_screen — loading
    ("ege-loading.txt", "progress_screen", "ДЕГУСТАЦИЯ",      "Маёнез maturity phase",               True,  []),

    # connect_screen — multiplayer
    ("ege-connect.txt", "connect_screen",  "ПОДКЛЮЧЕНИЕ",     "К станции через радиоволны",          True,  []),

    # receiving_level_screen
    ("ege-receiving.txt", "receiving_level_screen", "ПРИЁМ",        "Загрузка сохранения партии",          True,  []),

    # pause_screen — F4
    ("ege-pause.txt",   "pause_screen",    "ПАУЗА",          "Нажми R для продолжения",             True,  ["mc_pausescreen_return_to_game_button",
                                                              "mc_pausescreen_options_button",
                                                              "mc_pausescreen_quit_button"]),

    # join_multiplayer_screen
    ("ege-stations.txt","join_multiplayer_screen", "СТАНЦИИ",       "Доступные дегустационные точки",     True,  []),

    # options_screen
    ("ege-options.txt", "options_screen",  "ОПЦИИ",          "Настройка дегустации",               True,  []),

    # create_world_screen
    ("ege-newworld.txt","create_world_screen", "НОВАЯ СТАНЦИЯ",  "Создание новой дегустационной точки", True,  []),

    # death_screen
    ("ege-death.txt",   "death_screen",    "КОНЕЦ МАРИНАДИ",  "Дегустационный кома",                 True,  ["mc_deathscreen_respawn_button",
                                                              "mc_deathscreen_titlemenu_button"]),

    # disconnected_screen
    ("ege-disconnected.txt", "disconnected_screen", "ОТСЫКЛЫВАЕМСЯ", "Станция временно недоступна", True,  []),
]


def build(identifier, headline, sub_headline, dark, button_ids):
    elements = paper_sheet(dark)
    elements += new_header(ACCENT, MUTED)

    if identifier == "title_screen":
        if headline:
            elements.append(text("newheadline", headline, 30, 148, 500, 20,
                                 "top-left", ACCENT, 1.15, False))
        if sub_headline:
            elements.append(text("newsubhead", sub_headline, 30, 164, 500, 14,
                                 "top-left", MUTED, 0.85, False))
        elements += new_footer()
        elements += [new_button(b) for b in button_ids]
    else:
        if dark:
            elements.append(shape("newband", CREAM_SHADE, 0, 0, 2000, 50, "mid-left"))
        if headline:
            elements.append(text("newheadline", headline, 0, -95, 1200, 28,
                                 "bottom-centered", ACCENT, 1.8, True))
        if sub_headline:
            elements.append(text("newsubhead", sub_headline, 0, -68, 1200, 16,
                                 "bottom-centered", MUTED, 1.0, False))
        elements += new_footer()
        if button_ids:
            elements += [new_button(b) for b in button_ids]

    return layout(identifier, elements)


def main():
    for name, ident, headline, subtitle, dark, btn_ids in SCREENS:
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(ident, headline, subtitle, dark, btn_ids))
        print("wrote", name)


main()