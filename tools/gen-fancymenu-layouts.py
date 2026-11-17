# -*- coding: utf-8 -*-
"""Generate PDA (S.T.A.L.K.E.R.) FancyMenu screen-customization layouts.

FancyMenu draws customization elements in GUI-scaled pixels. Minecraft's
default 854x480 window at GUI scale 2 gives a 427x240 logical canvas, so all
coordinates below are authored for exactly that.

Three layout variants are used, because vanilla screens differ a lot in how
crowded their upper area is:

  full  - title screen: frame, header, side info blocks, terminal panel
  light - sparse screens (pause, death, loading...): frame + header + status
  frame - dense screens (options, server list, world creation): frame only

Run:    python tools/gen-fancymenu-layouts.py
Output: src/main/resources/config/fancymenu/customization/ege-*.txt
"""
from pathlib import Path

OUT = (Path(__file__).resolve().parent.parent
       / "src" / "main" / "resources" / "config" / "fancymenu" / "customization")

W, H = 427, 240

BG = "#0a1a0a"
PANEL = "#0c200c"
SIDE = "#0a180a"

# file stem -> (screen id, accent, bright, muted, headline, subtitle, variant)
SCREENS = {
    "ege-title":        ("title_screen",            "#60C060", "#8CFF8C", "#56AE56",
                         "S.T.A.L.K.E.R.", "ЗОНА ЧЕРНОБЫЛИ", "full"),
    "ege-loading":      ("progress_screen",         "#60C060", "#8CFF8C", "#56AE56",
                         "ЗАГРУЗКА", "ПОДГОТОВКА ЗОНЫ", "light"),
    "ege-connect":      ("connect_screen",          "#60C060", "#8CFF8C", "#56AE56",
                         "ПОДКЛЮЧЕНИЕ", "УСТАНОВКА СВЯЗИ", "light"),
    "ege-receiving":    ("receiving_level_screen",  "#60C060", "#8CFF8C", "#56AE56",
                         "ПРИЁМ ДАННЫХ", "ЗАГРУЗКА УРОВНЯ", "light"),
    "ege-pause":        ("pause_screen",            "#60C060", "#8CFF8C", "#56AE56",
                         "ПАУЗА", "СИСТЕМА ОЖИДАЕТ", "light"),
    "ege-stations":     ("join_multiplayer_screen", "#60C060", "#8CFF8C", "#56AE56",
                         "СЕТЬ", "СПИСОК СТАНЦИЙ", "frame"),
    "ege-options":      ("options_screen",          "#60C060", "#8CFF8C", "#56AE56",
                         "НАСТРОЙКИ", "КОНФИГУРАЦИЯ ПДА", "frame"),
    "ege-newworld":     ("create_world_screen",     "#60C060", "#8CFF8C", "#56AE56",
                         "НОВЫЙ МИР", "СОЗДАНИЕ ЗОНЫ", "frame"),
    "ege-death":        ("death_screen",            "#A05050", "#FF9090", "#8A4A4A",
                         "ВЫ ПОГИБЛИ", "ЗОНА ЗАБРАЛА СВОЁ", "light"),
    "ege-disconnected": ("disconnected_screen",     "#A0A050", "#E8E880", "#787840",
                         "СВЯЗЬ ПОТЕРЯНА", "СИГНАЛ ПРЕРВАН", "light"),
}


def shape(eid, x, y, w, h, color):
    return (
        "element {\n"
        "  element_type = shape\n"
        f"  instance_identifier = {eid}\n"
        f"  x = {x}\n  y = {y}\n  width = {w}\n  height = {h}\n"
        "  anchor_point = top-left\n"
        f"  color = {color}\n"
        "}"
    )


def text(eid, x, y, scale, color, value, shadow="false", width=260, height=12):
    return (
        "element {\n"
        "  element_type = text_v2\n"
        f"  instance_identifier = {eid}\n"
        f"  x = {x}\n  y = {y}\n  width = {width}\n  height = {height}\n"
        "  anchor_point = top-left\n"
        f"  source = {value}\n"
        "  source_mode = direct\n"
        f"  shadow = {shadow}\n"
        "  enable_scrolling = false\n"
        "  auto_line_wrapping = false\n"
        f"  base_color = {color}\n"
        f"  scale = {scale}\n"
        "}"
    )


def frame(a):
    out = [
        shape("border_top", 0, 0, W, 1, a),
        shape("border_bottom", 0, H - 1, W, 1, a),
        shape("border_left", 0, 0, 1, H, a),
        shape("border_right", W - 1, 0, 1, H, a),
    ]
    arms = [(4, 4, 1, 1), (W - 20, 4, 1, 1), (4, H - 20, 1, 1), (W - 20, H - 20, 1, 1)]
    for i, (x, y, _, _) in enumerate(arms):
        bottom = y > H / 2
        right = x > W / 2
        out.append(shape(f"corner_{i}_h", x, y + (15 if bottom else 0), 16, 1, a))
        out.append(shape(f"corner_{i}_v", x + (15 if right else 0), y, 1, 16, a))
    return out


def block(eid, x, y, w, h, a, fill):
    return [
        shape(eid, x, y, w, h, fill),
        shape(eid + "_t", x, y, w, 1, a),
        shape(eid + "_b", x, y + h - 1, w, 1, a),
        shape(eid + "_l", x, y, 1, h, a),
        shape(eid + "_r", x + w - 1, y, 1, h, a),
    ]


def side_block(eid, x, y, w, h, a, fill, lines, muted, scale=0.6):
    out = block(eid, x, y, w, h, a, fill)
    step = 13
    top = y + max(8, (h - step * len(lines)) // 2)
    for i, line in enumerate(lines):
        out.append(text(f"{eid}_l{i}", x + 6, top + i * step, scale, muted, line,
                        "false", width=w - 10, height=step + 4))
    return out


def head(parts, a, b, m, headline, subtitle, title_scale=2.3, compact=False):
    if compact:
        # Small header for screens whose vanilla widgets start high up
        # (pause, death, loading, connection screens).
        parts += [
            text("header", 16, 8, 1.2, b, headline, "true", width=240, height=16),
            text("subtitle", 16, 25, 0.55, m, subtitle, "false", width=240, height=8),
            shape("header_rule", 16, 37, 96, 1, a),
            text("pda_label", W - 96, 10, 0.55, m, "ПДА-1.0", "false", width=80, height=8),
            text("pda_state", W - 96, 20, 0.55, a, "[ СВЯЗЬ ]", "false", width=80, height=8),
        ]
        return parts

    parts += [
        text("header", 16, 10, title_scale, b, headline, "true", width=300, height=24),
        text("subtitle", 16, 38, 0.7, m, subtitle, "false", width=260, height=10),
        text("pda_label", W - 94, 12, 0.6, m, "ПДА-1.0", "false", width=80, height=8),
        text("pda_state", W - 94, 23, 0.6, a, "[ СВЯЗЬ ]", "false", width=80, height=8),
        shape("header_rule", 16, 50, W - 32, 1, a),
        text("ticker", 16, 58, 0.6, m,
             "СИСТЕМА ГОТОВА   //   СЕКТОР 07   //   РАДИАЦИЯ: НОРМА",
             "false", width=W - 40, height=10),
    ]
    for i in range(0, (W - 32), 9):
        parts.append(shape(f"tick_{i}", 16 + i, 72, 4, 1, m))
    return parts


def status(parts, a, m, left="[ ПДА: ОНЛАЙН ]", right="СЕКТОР 07 / 04:17"):
    parts += [
        shape("status_rule", 0, H - 20, W, 1, a),
        text("status", 12, H - 16, 0.55, a, left, "false", width=180, height=8),
        text("status_right", W - 104, H - 16, 0.5, m, right, "false", width=100, height=8),
    ]
    return parts


TITLE_LEFT = [
    "СЕКТОР:", "  07", "ВРЕМЯ:", "  04:17",
    "РАДИАЦИЯ:", "  НОРМА", "ВЕТЕР:", "  С-В 3М/С",
]
TITLE_RIGHT = [
    "ЗАДАНИЕ:", "  НАЙТИ", "  АРТЕФАКТ", "  «ДУША»",
    "СТАТУС:", "  В ПОИСКЕ", "ГРУППА:", "  ОДИНОЧКА",
]
SIDE_LEFT = ["СЕКТОР:", "  07", "ВРЕМЯ:", "  04:17",
             "РАДИАЦИЯ:", "  НОРМА", "ВЕТЕР:", "  С-В 3М/С"]
SIDE_RIGHT = ["СЕАНС:", "  АКТИВЕН", "КАНАЛ:", "  3", "ПОМЕХИ:",
              "  НЕТ", "ЗАРЯД:", "  87%"]


def build(screen, accent, bright, muted, headline, subtitle, variant):
    a = accent + "FF"
    b = bright + "FF"
    m = muted + "FF"

    parts = [
        "type = fancymenu_layout",
        "",
        "layout-meta {",
        f"  identifier = {screen}",
        "  layout_index = 0",
        "  is_enabled = true",
        "  render_custom_elements_behind_vanilla = true",
        "}",
        "",
        # in-game screens stay slightly translucent so the world shows through
        shape("bg_fill", 0, 0, W, H, BG + ("FF" if variant in ("full", "frame") else "D8")),
    ]
    parts += frame(a)

    if variant == "full":
        head(parts, a, b, m, headline, subtitle, 2.3)
        parts += side_block("side_left", 4, 84, 102, 138, a, SIDE + "FF", TITLE_LEFT, m)
        parts += side_block("side_right", W - 106, 84, 102, 138, a, SIDE + "FF", TITLE_RIGHT, m)
        parts += block("panel", 108, 84, 212, 138, a, PANEL + "FF")
        parts += [
            text("panel_title", 112, 75, 0.55, m, "// ТЕРМИНАЛ", "false", width=120, height=8),
            text("panel_title_r", 236, 75, 0.55, m, "ДОСТУП: ЕСТЬ", "false", width=100, height=8),
        ]
        # no bottom status bar: vanilla Minecraft/NeoForge branding lives there
    elif variant == "light":
        head(parts, a, b, m, headline, subtitle, compact=True)
        status(parts, a, m, "[ ПДА: ОНЛАЙН ]", "СЕКТОР 07 / 04:17")
    # "frame" -> only the outer frame + corner brackets

    return "\n\n".join(parts) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, args in SCREENS.items():
        path = OUT / f"{stem}.txt"
        path.write_text(build(*args), encoding="utf-8", newline="\n")
        print("wrote", path, path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
