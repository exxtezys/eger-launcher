import os

"""
S.T.A.L.K.E.R. "Shadow of Chernobyl" theme for FancyMenu 3.9.14-hand.
All elements generated from text_v2 + shape only - no images (they render black).
Layouts live in src/main/resources/config/fancymenu/customization/
and are installed with local:absolute paths by LauncherApp.java.

Color palette (STALKER-inspired):
  STALKER_DARK   = "#2D2B26FF"  - dark paper/base
  STALKER_BASE   = "#4A463BFF"  - panel base
  STALKER_MID    = "#6B6657FF"  - mid tones
  STALKER_ACCENT = "#A8A479FF"  - gold/worn brass
  STALKER_GREEN  = "#8D8A6BFF"  - olive drab
  STALKER_TEXT   = "#E8E5D6FF"  - primary text
  STALKER_SOFT   = "#C0BCA8FF"  - secondary text
  STALKER_RED    = "#D45A49FF"  - danger/warning
  STALKER_HIGHLIGHT = "#FFD565FF" - amber highlight

Element types used:
  - text_v2  (source=local:..., source_mode=direct, shadow, base_color, scale)
  - shape    (color=..., corner_radius_*=0)
  - vanilla_button (label_base_color, label_hover_color, label_scale, label_shadow)
"""

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "customization")

# ── palette ────────────────────────────────────────────────────────────────
STALKER_DARK   = "#2D2B26FF"
STALKER_BASE   = "#4A463BFF"
STALKER_MID    = "#6B6657FF"
STALKER_ACCENT = "#A8A479FF"
STALKER_GREEN  = "#8D8A6BFF"
STALKER_TEXT   = "#E8E5D6FF"
STALKER_SOFT   = "#C0BCA8FF"
STALKER_RED    = "#D45A49FF"
STALKER_HL     = "#FFD565FF"

TITLE = "S.T.A.L.K.E.R."
SUB   = "ЗОНА ЧЕРНОБЫЛИ"
FOOTER = "© 2012 GSC Game World • ALL RIGHTS RESERVED"


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


def vanilla_button(eid, base=STALKER_ACCENT, hover=STALKER_TEXT):
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


# ── layout blocks ──────────────────────────────────────────────────────────
def sheet(dark):
    """Full-screen paper sheet with worn edges and STALKER-accented brass framing."""
    base = STALKER_DARK if dark else STALKER_BASE
    return [
        shape("stalker_paper", base, 0, 0, 2000, 1400, "top-left"),
        # top brass bar (worn)
        shape("stalker_top_band", STALKER_ACCENT, 0, 0, 2000, 6, "top-left"),
        # bottom brass bar
        shape("stalker_bottom_band", STALKER_ACCENT, 0, 0, 2000, 6, "bottom-left"),
        # left thin strip
        shape("stalker_side_l", STALKER_ACCENT, 0, 0, 4, 1400, "top-left"),
        # right thin strip
        shape("stalker_side_r", STALKER_ACCENT, 0, 0, 4, 1400, "top-right"),
    ]


def header(brand_color, sub_color):
    """Top-left block: title, brass rule, subtitle."""
    return [
        text("stalker_brand", TITLE, 24, 20, 560, 72, "top-left", brand_color, 2.8, True),
        shape("stalker_rule", STALKER_ACCENT, 26, 54, 120, 2, "top-left"),
        text("stalker_sub", SUB, 27, 62, 640, 16, "top-left", sub_color),
    ]


def footer(color):
    return [text("stalker_footer", FOOTER, 0, -28, 900, 12, "bottom-centered", color, 0.7)]


def make_buttons(ident, button_ids):
    """Return vanilla_button blocks for given instance identifiers."""
    return [vanilla_button(b) for b in button_ids]


# ── screen definitions ─────────────────────────────────────────────────────
# (file_name, screen_identifier, headline, subtitle, dark, button_ids)
SCREENS = [
    # title_screen   — main menu
    ("ege-title.txt",   "title_screen",   "НОВАЯ ПАРТИЯ",      "ВХОД В ЗОНУ",            False,
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
    ("ege-death.txt",   "death_screen",    "ПАРТИЯ ЗАКРЫТА",   "СМЕРТЬ В ЗОНЕ",        True,  ["mc_deathscreen_respawn_button",
                                                                      "mc_deathscreen_titlemenu_button"]),

    # disconnected_screen
    ("ege-disconnected.txt", "disconnected_screen", "СВЯЗЬ ПРЕРВАНА", "СТАНЦИЯ НЕ ОТВЕЧАЕТ", True,  []),
]


def build(identifier, headline, subtitle, dark, button_ids):
    """Build the full element list for one screen."""
    elements = sheet(dark)

    if identifier == "title_screen":
        elements += header(STALKER_TEXT, STALKER_SOFT)
        elements += footer(STALKER_SOFT)
        elements += make_buttons(identifier, button_ids)
    else:
        # For non-title screens: a dark band behind the column + header + footer
        if dark:
            elements.append(shape("stalker_band", STALKER_MID, 0, 0, 2000, 80, "mid-left"))
        elements += header(STALKER_TEXT, STALKER_SOFT)
        # headline/subtitle only for screens that have them
        if headline:
            elements.append(text("stalker_headline", headline, 0, -150, 1200, 48,
                                 "bottom-centered", STALKER_HL, 1.6, True))
        elements.append(text("stalker_sub", subtitle, 0, -96, 1200, 24,
                             "bottom-centered", STALKER_SOFT))
        elements += footer(STALKER_SOFT)
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