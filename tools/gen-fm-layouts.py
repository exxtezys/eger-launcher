import os

"""
FancyMenu layouts for the "Егерь" 1939 theme.
Palette: warm cream paper (#DCD3BC), black ink (#231F19), oxblood red accent (#8B2E22),
brass (#A88870), paper shadow (#A99D82).
All coordinates are for Minecraft's default 854x480 window at GUI scale 2 → 427x240 logical canvas.
"""

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "customization")

# ── palette ────────────────────────────────────────────────────────────────
# Warm cream paper background
PAPER          = "#DCD3BC"   # light paper/base
PAPER_SHADOW   = "#A99D82"   # paper shadow/wear
INK            = "#231F19"   # black ink
ACCENT         = "#8B2E22"   # oxblood red / brass
ACCENT_HOVER   = "#A63B2C"   # accent hover
TEXT           = "#231F19"   # primary text (ink)
MUTED          = "#6B6354"   # secondary text / muted
SOFT           = "#C4B5A5"   # soft secondary
HIGHLIGHT      = "#D4A89A"   # highlight / warm brass
RULER          = "#4A3626"   # brass ruler / dark strip
VIGNETTE       = "#18130E"   # dark vignette band

TITLE          = "ЕГЕРЬ"
SUB            = "ОПЫТНАЯ ДЕГУСТАЦИОННАЯ СТАНЦИЯ · 1939"
FOOTER         = "© 1944 Наркомат пищевой промышленности"


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


def vanilla_button(eid, base=ACCENT, hover=TEXT):
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


def paper_sheet(dark):
    """Full-screen paper sheet with worn edges and brass framing."""
    base = PAPER_SHADOW if dark else PAPER
    return [
        shape("egertopaper", base, 0, 0, 2000, 1400, "top-left"),
        # top brass bar (worn)
        shape("egertopband", RULER, 0, 0, 2000, 6, "top-left"),
        # bottom brass bar
        shape("egerbottomband", RULER, 0, 0, 2000, 6, "bottom-left"),
        # left thin strip
        shape("egerside_l", RULER, 0, 0, 4, 1400, "top-left"),
        # right thin strip
        shape("egerside_r", RULER, 0, 0, 4, 1400, "top-right"),
        # vignette strip bottom
        shape("egerbottom_vignette", VIGNETTE, 0, 0, 2000, 30, "bottom-left"),
        # vignette strip top
        shape("egertop_vignette", VIGNETTE, 0, 0, 2000, 30, "top-left"),
    ]


def header(brand_color, sub_color):
    """Top-left block: title, brass rule, subtitle."""
    return [
        text("egertitle", TITLE, 24, 20, 560, 72, "top-left", brand_color, 2.8, True),
        shape("egerrule", ACCENT, 26, 54, 120, 2, "top-left"),
        text("egersub", SUB, 27, 62, 640, 16, "top-left", sub_color),
    ]


def footer(color):
    return [text("egerfooter", FOOTER, 0, -28, 900, 12, "bottom-centered", color, 0.7)]


def make_buttons(ident, button_ids):
    """Return vanilla_button blocks for given instance identifiers."""
    return [vanilla_button(b) for b in button_ids]


# ── screen definitions ─────────────────────────────────────────────────────
# (file_name, screen_identifier, headline, subtitle, dark, button_ids)
SCREENS = [
    # title_screen   — main menu
    ("ege-title.txt",   "title_screen",   "НОВАЯ ПАРТИЯ",      "ВХОД В СТАНЦИЮ",            False,
     ["mc_titlescreen_singleplayer_button", "mc_titlescreen_multiplayer_button",
      "mc_titlescreen_options_button", "mc_titlescreen_quit_button"]),

    # progress_screen — loading
    ("ege-loading.txt", "progress_screen", "ЗАГРУЗКА ПАРТИИ",   "ПОДГОТОВКА СТАНЦИИ",    True,  []),

    # connect_screen — multiplayer connect
    ("ege-connect.txt", "connect_screen",  "МНОГОИГРОКОВАЯ",    "ПОДКЛЮЧЕНИЕ К СТАНЦИИ", False, []),

    # receiving_level_screen
    ("ege-receiving.txt", "receiving_level_screen", "ПРИЁМ ПАРТИИ", "ПОЛУЧЕНИЕ ДАННЫХ",    True,  []),

    # pause_screen — F4
    ("ege-pause.txt",   "pause_screen",    "ПЕРЕРЫВ",          "ПАУЗА",                True,  ["mc_pausescreen_return_to_game_button",
                                                                      "mc_pausescreen_options_button",
                                                                      "mc_pausescreen_stats_button",
                                                                      "mc_pausescreen_disconnect_button"]),

    # join_multiplayer_screen
    ("ege-stations.txt","join_multiplayer_screen", "СТАНЦИИ",        "СПИСОК ДОСТУПНЫХ",     False, []),

    # options_screen
    ("ege-options.txt", "options_screen",  "НАСТРОЙКИ",        "ИГРОВОЙ ПАРАМЕТРЫ",   False, []),

    # create_world_screen
    ("ege-newworld.txt","create_world_screen", "НОВАЯ ПАРТИЯ",     "ОФОРМЛЕНИЕ УЧАСТКА",   False, []),

    # death_screen
    ("ege-death.txt",   "death_screen",    "ПАРТИЯ ЗАКРЫТА",   "СМЕРТЬ В СТАНЦИИ",        True,  ["mc_deathscreen_respawn_button",
                                                                      "mc_deathscreen_titlemenu_button"]),

    # disconnected_screen
    ("ege-disconnected.txt", "disconnected_screen", "СВЯЗЬ ПРЕРВАНА", "СТАНЦИЯ НЕ ОТВЕЧАЕТ", True,  []),
]


def build(identifier, headline, subtitle, dark, button_ids):
    """Build the full element list for one screen."""
    elements = paper_sheet(dark)

    if identifier == "title_screen":
        elements += header(TEXT, MUTED)
        elements += footer(MUTED)
        elements += make_buttons(identifier, button_ids)
    else:
        # For non-title screens: a dark band behind the column + header + footer
        if dark:
            elements.append(shape("egerband", PAPER_SHADOW, 0, 0, 2000, 80, "mid-left"))
        elements += header(TEXT, MUTED)
        # headline/subtitle only for screens that have them
        if headline:
            elements.append(text("egerheadline", headline, 0, -150, 1200, 48,
                                 "bottom-centered", ACCENT, 1.6, True))
        elements.append(text("egersub", subtitle, 0, -96, 1200, 24,
                             "bottom-centered", SOFT))
        elements += footer(SOFT)
        if identifier == "pause_screen":
            elements += make_buttons(identifier, button_ids)
        if identifier == "death_screen":
            elements += make_buttons(identifier, button_ids)

    return layout(identifier, elements)


def main():
    for name, ident, headline, subtitle, dark, btn_ids in SCREENS:
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(ident, headline, subtitle, dark, btn_ids))
        print("wrote", name)


if __name__ == "__main__":
    main()