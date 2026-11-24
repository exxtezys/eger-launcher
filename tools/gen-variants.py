#!/usr/bin/env python3
"""Generate 10 distinct FancyMenu layout variants for Егерь 1939."""
import os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "theme", "scene.png")
VARIANTS = os.path.join(ROOT, "variants")

PALETTES = [
    ("cream_oxblood", "#F5E8C6", "#D9C495", "#8B2E22", "#A63B2C", "#A88866", "#C9A96E", "#6B4222", "#1A1410"),
    ("ink_paper",     "#E8E0D0", "#C9C0B0", "#211812", "#3A2E22", "#8A8070", "#A08860", "#4A3626", "#0E0A08"),
    ("walnut_brass",  "#D9C9A5", "#B8A47E", "#5C3A1E", "#7A4E2A", "#9A8868", "#C9A96E", "#3A2410", "#140E08"),
    ("oxblood_dark",  "#2A1A14", "#1A0E08", "#C9A96E", "#E0C080", "#A88866", "#8B2E22", "#6B4222", "#0A0604"),
    ("parchment",     "#F0E8D0", "#D8CCB0", "#4A3626", "#6B4A30", "#9A8866", "#C9A96E", "#3A2410", "#18120E"),
    ("slate_brass",   "#D0CCC0", "#B0ACA0", "#3A3630", "#504A40", "#8A8678", "#C9A96E", "#2A2620", "#0A0A0A"),
    ("rustic",        "#E0D4B8", "#C0B090", "#7A3A1E", "#9A4A2A", "#9A8060", "#C9A96E", "#4A2410", "#140804"),
    ("mono_ink",      "#F0F0E8", "#D8D8D0", "#1A1A1A", "#3A3A3A", "#888880", "#C9A96E", "#2A2A2A", "#080808"),
    ("forest_brass",  "#D8E0C8", "#B8C0A8", "#2A3A1E", "#3A4A2A", "#889070", "#C9A96E", "#1A2410", "#0A0E08"),
    ("burgundy",      "#E8D8D0", "#C8B0A8", "#6A1E22", "#8A2E32", "#9A7068", "#C9A96E", "#4A1014", "#140408"),
]

SCREENS = [
    ("ege-title.txt", "title_screen", "ДОСТУПНЫЕ РЕЖИМЫ", "ОБЪЯВЛЕНИЕ ОТДЕЛА МАЙОНЕЗА"),
    ("ege-loading.txt", "progress_screen", "ДЕГУСТАЦИЯ", "Маёнез maturity phase"),
    ("ege-connect.txt", "connect_screen", "ПОДКЛЮЧЕНИЕ", "К станции через радиоволны"),
    ("ege-receiving.txt", "receiving_level_screen", "ПРИЁМ", "Загрузка сохранения партии"),
    ("ege-pause.txt", "pause_screen", "ПАУЗА", "Нажми R для продолжения"),
    ("ege-stations.txt", "join_multiplayer_screen", "СТАНЦИИ", "Доступные дегустационные точки"),
    ("ege-options.txt", "options_screen", "ОПЦИИ", "Настройка дегустации"),
    ("ege-newworld.txt", "create_world_screen", "НОВАЯ СТАНЦИЯ", "Создание новой дегустационной точки"),
    ("ege-death.txt", "death_screen", "КОНЕЦ МАРИНАДИ", "Дегустационный кома"),
    ("ege-disconnected.txt", "disconnected_screen", "ОТСЫКЛЫВАЕМСЯ", "Станция временно недоступна"),
]

BUTTONS = {
    "title_screen": [("Играть","mc_titlescreen_singleplayer_button"),("Сервер","mc_titlescreen_multiplayer_button"),("Настройки","mc_titlescreen_options_button"),("Выйти","mc_titlescreen_quit_button")],
    "pause_screen": [("Вернуться","mc_pausescreen_return_to_game_button"),("Настройки","mc_pausescreen_options_button"),("Выйти","mc_pausescreen_quit_button")],
    "death_screen": [("Возродиться","mc_deathscreen_respawn_button"),("В меню","mc_deathscreen_titlemenu_button")],
}

TITLE = "ЕГЕРЬ"
SUBTITLE = "НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939"
FOOTER = "© 1944 Опытная дегустационная станция"

def make_bg(palette, idx):
    name, cream, shade, accent, hover, muted, highlight, ruler, vignette = palette
    base = Image.open(SCENE).convert("RGBA")
    W, H = base.size
    img = base.copy()
    # color wash
    wash = Image.new("RGBA", (W,H), (0,0,0,60))
    img = Image.alpha_composite(img, wash)
    # vignette
    v = Image.new("RGBA",(W,H),(0,0,0,0))
    vd = ImageDraw.Draw(v)
    for i in range(0, 180, 4):
        a = int(160*(1-i/180))
        vd.rectangle((i,i,W-i,H-i), outline=(0,0,0,a))
    img = Image.alpha_composite(img, v)
    d = ImageDraw.Draw(img, "RGBA")
    random.seed(idx*13+7)
    for _ in range(70):
        x=random.randint(0,W); y=random.randint(0,H)
        r=random.randint(1,3); a=random.randint(30,110)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(245,232,198,a))
    ax = (idx*211) % (W-220) + 60
    ay = 50 + (idx*37) % 50
    d.ellipse((ax, ay, ax+150, ay+40), fill=(55,38,28,210))
    d.rectangle((ax+55, ay+34, ax+95, ay+58), fill=(38,24,14,210))
    small = img.resize((512, int(512*H/W)), Image.LANCZOS)
    return small

def shape(eid, color, x, y, w, h, anchor="top-left", radius=0, opacity=1.0):
    return ("element {\n  element_type = shape\n  instance_identifier = %s\n  x = %d\n  y = %d\n  width = %d\n  height = %d\n  anchor_point = %s\n  color = %s\n  corner_radius_top_left = %d\n  corner_radius_top_right = %d\n  corner_radius_bottom_left = %d\n  corner_radius_bottom_right = %d\n  base_opacity = %.2f\n}\n\n" % (eid, x, y, w, h, anchor, color, radius, radius, radius, radius, opacity))

def text(eid, value, x, y, w, h, anchor, color, scale=1.0, shadow=True):
    return ("element {\n  element_type = text_v2\n  instance_identifier = %s\n  source = %s\n  source_mode = direct\n  shadow = %s\n  scale = %.2f\n  base_color = %s\n  x = %d\n  y = %d\n  width = %d\n  height = %d\n  anchor_point = %s\n}\n\n" % (eid, value, "true" if shadow else "false", scale, color, x, y, w, h, anchor))

def btn(vid, label, x, y, w=220, h=42, accent="#8B2E22", hover="#A63B2C"):
    return ("vanilla_button {\n  element_type = vanilla_button\n  instance_identifier = %s\n  label_base_color = %s\n  label_hover_color = %s\n  label_scale = 1.1\n  label_shadow = true\n}\n\n" % (vid, accent, hover))

def layout(ident, body, bgname):
    return ("type = fancymenu_layout\n\nlayout-meta {\n  identifier = %s\n  layout_index = 0\n  is_enabled = true\n  render_custom_elements_behind_vanilla = true\n}\n\nmenu_background {\n  image_path = [source:local]/config/fancymenu/assets/%s\n  slide = false\n  repeat_texture = false\n  background_type = image\n}\n\ncustomization {\n  action = backgroundoptions\n  keepaspectratio = true\n}\n\n%s\n" % (ident, bgname, body))

def build(ident, headline, sub, buttons, pal, mode):
    name, cream, shade, accent, hover, muted, highlight, ruler, vignette = pal
    body = ""
    # window/table composition varies by mode
    if mode == 0:
        body += shape("panel", cream, 40, 80, 420, 520, "top-left", 12, 0.88)
        body += shape("table", shade, 480, 80, 420, 520, "top-left", 12, 0.80)
        tx, ty = 60, 90
    elif mode == 1:
        body += shape("panel", cream, 60, 60, 780, 160, "top-left", 12, 0.88)
        body += shape("table", shade, 60, 240, 780, 360, "top-left", 12, 0.80)
        tx, ty = 80, 80
    elif mode == 2:
        body += shape("panel", cream, 80, 100, 720, 480, "top-left", 16, 0.85)
        tx, ty = 110, 120
    else:
        body += shape("panel", cream, 40, 80, 820, 520, "top-left", 12, 0.88)
        tx, ty = 60, 90
    # title
    body += text("title1", TITLE, tx, ty, 400, 60, "top-left", accent, 2.6, True)
    body += text("title2", TITLE, tx-4, ty+4, 400, 60, "top-left", highlight, 2.6, True)
    body += shape("rule1", accent, tx, ty+62, 120, 3, "top-left")
    body += shape("rule2", highlight, tx, ty+67, 90, 2, "top-left")
    body += text("sub", SUBTITLE, tx, ty+78, 400, 20, "top-left", muted, 1.0, False)
    body += text("headline", headline, tx, ty+112, 400, 24, "top-left", accent, 1.3, True)
    body += text("subhead", sub, tx, ty+136, 400, 16, "top-left", muted, 0.9, False)
    # footer
    body += text("footer", FOOTER, 0, -12, 900, 12, "bottom-centered", muted, 0.6, False)
    # rivets
    for i in range(6):
        body += shape("rivet_%d"%i, ruler, 24, 100+i*70, 10, 10, "top-left", 5)
    # buttons placement varies
    if mode == 0:
        bx, by = 520, 420
        for label, vid in buttons:
            body += btn(vid, label, bx, by, 200, 42, accent, hover)
            by += 52
    elif mode == 1:
        bx, by = 100, 260
        for label, vid in buttons:
            body += btn(vid, label, bx, by, 200, 42, accent, hover)
            by += 52
    elif mode == 2:
        bx, by = 140, 300
        for label, vid in buttons:
            body += btn(vid, label, bx, by, 200, 42, accent, hover)
            by += 52
    else:
        bx, by = 100, 470
        for label, vid in buttons:
            body += btn(vid, label, bx, by, 180, 38, accent, hover)
            bx += 200
    return body

def main():
    os.makedirs(VARIANTS, exist_ok=True)
    for vi, pal in enumerate(PALETTES):
        vdir = os.path.join(VARIANTS, "v%d" % (vi+1))
        os.makedirs(os.path.join(vdir, "customization"), exist_ok=True)
        os.makedirs(os.path.join(vdir, "assets"), exist_ok=True)
        bg = make_bg(pal, vi)
        bgname = "bg_%d.png" % (vi+1)
        bg.save(os.path.join(vdir, "assets", bgname))
        mode = vi % 4
        for fname, ident, headline, sub in SCREENS:
            buttons = BUTTONS.get(ident, [])
            body = build(ident, headline, sub, buttons, pal, mode)
            content = layout(ident, body, bgname)
            with open(os.path.join(vdir, "customization", fname), "w", encoding="utf-8") as f:
                f.write(content)
        with open(os.path.join(vdir, "README.txt"), "w", encoding="utf-8") as f:
            f.write("Variant %d — palette %s — mode %d\n" % (vi+1, pal[0], mode))
        print("variant", vi+1, pal[0], "mode", mode)

if __name__ == "__main__":
    main()