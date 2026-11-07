"""Генерирует оформление «Егерь» в стиле Второй мировой: потёртый фон, трафаретный логотип, иконку.
Выход: theme/background.png, theme/logo.png, theme/icon.png, icon.ico."""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "theme"
OUT.mkdir(exist_ok=True)
FONT = "C:/Windows/Fonts/impact.ttf"
rnd = random.Random(1941)


def noise(w, h, scale, seed):
    r = random.Random(seed)
    small = Image.new("L", (max(1, w // scale), max(1, h // scale)))
    small.putdata([r.randint(0, 255) for _ in range(small.width * small.height)])
    return small.resize((w, h), Image.BICUBIC)


def grunge(w, h, seed):
    """Многооктавный шум: пятна, грязь, неравномерный износ."""
    acc = Image.new("L", (w, h), 128)
    for i, (scale, weight) in enumerate(((180, 0.5), (60, 0.3), (14, 0.15), (3, 0.08))):
        acc = Image.blend(acc, noise(w, h, scale, seed + i), weight)
    return acc


def scratches(draw, w, h, n, color_fn, seed):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        ang = r.uniform(-0.6, 0.6) + (math.pi / 2 if r.random() < 0.25 else 0)
        ln = r.uniform(20, 220)
        pts = []
        for k in range(8):
            t = k / 7
            pts.append((x + math.cos(ang) * ln * t + r.uniform(-2, 2), y + math.sin(ang) * ln * t + r.uniform(-2, 2)))
        draw.line(pts, fill=color_fn(r), width=r.choice((1, 1, 1, 2)))


def paper(size=512):
    """Светлая бумага для ручного стиля: зерно, волокна, редкие пятна. Тайл 512x512."""
    r = random.Random(1939)
    base = Image.new("RGB", (size, size), (201, 197, 185))
    g = grunge(size, size, 41)
    base = Image.composite(Image.new("RGB", (size, size), (228, 224, 213)), base,
                           g.point(lambda v: max(0, (v - 150)) * 2))
    base = Image.composite(Image.new("RGB", (size, size), (167, 163, 149)), base,
                           g.point(lambda v: max(0, (105 - v)) * 2))

    d = ImageDraw.Draw(base)
    for _ in range(340):
        x, y = r.uniform(0, size), r.uniform(0, size)
        ln = r.uniform(4, 26)
        ang = r.uniform(-0.22, 0.22)
        d.line([(x, y), (x + math.cos(ang) * ln, y + math.sin(ang) * ln)],
               fill=r.choice(((188, 184, 172), (214, 210, 199), (176, 172, 160))), width=1)

    stains = Image.new("L", (size, size), 0)
    sd = ImageDraw.Draw(stains)
    for _ in range(6):
        x, y = r.uniform(0, size), r.uniform(0, size)
        rr = r.uniform(8, 30)
        sd.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7], fill=r.randint(18, 42))
    stains = stains.filter(ImageFilter.GaussianBlur(6))
    base = Image.composite(Image.new("RGB", (size, size), (150, 146, 133)), base, stains)

    # плёночное зерно, чтобы бумага не была плоской
    grain = noise(size, size, 1, 77).point(lambda v: 128 + (v - 128) // 6)
    base = ImageChops.overlay(base, Image.merge("RGB", (grain, grain, grain)))
    base.save(OUT / "paper.png")


def hand_icon_panel(size):
    """Один размер иконки ручного стиля: бумага, тушь, латунная орбита, трафаретная «Е»."""
    ss = 4
    s = size * ss
    img = Image.new("RGBA", (s, s), (201, 197, 185, 255))
    g = grunge(s, s, 59)
    img = Image.composite(Image.new("RGBA", (s, s), (228, 224, 213, 255)), img,
                          g.point(lambda v: max(0, (v - 158)) * 2).convert("L"))
    d = ImageDraw.Draw(img)
    ink = (28, 27, 24, 255)
    brass = (160, 124, 60, 255)

    frame = max(ss, round(s * 0.012))
    d.rectangle([0, 0, s - 1, s - 1], outline=ink, width=frame)

    small = size <= 32
    if not small:
        d.arc([s * 0.13, s * 0.22, s * 0.87, s * 0.78], 200, 340, fill=brass, width=max(ss, round(s * 0.011)))
        d.arc([s * 0.18, s * 0.28, s * 0.82, s * 0.72], 20, 160, fill=brass, width=max(ss, round(s * 0.011)))

    thick = s * (0.15 if small else 0.125)
    left, right = s * 0.30, s * 0.72
    top, bot = s * 0.21, s * 0.79
    stem_r = left + thick
    d.rectangle([left, top, stem_r, bot], fill=ink)
    bars = ((top, top + thick * 1.05), (s * 0.5 - thick * 0.525, s * 0.5 + thick * 0.525),
            (bot - thick * 1.05, bot))
    for y0, y1 in bars:
        d.rectangle([stem_r, y0, right, y1], fill=ink)

    if not small:
        # перемычки трафарета: узкие прорези бумагой сразу за стойкой
        slit0 = stem_r + thick * 0.18
        slit1 = slit0 + thick * 0.30
        for y0, y1 in bars:
            d.rectangle([slit0, y0, slit1, y1], fill=(201, 197, 185, 255))

    return img.resize((size, size), Image.LANCZOS)


def hand_icon():
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    hand_icon_panel(256).save(OUT / "hand-icon.png")
    frames = [hand_icon_panel(w) for w, _ in sizes]
    frames[-1].save(ROOT / "icon.ico", format="ICO", sizes=sizes, append_images=frames[:-1])


def background(w=920, h=560):
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    top, bot = (64, 68, 44), (30, 32, 22)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))

    g = grunge(w, h, 7)
    dark = Image.new("RGB", (w, h), (18, 18, 12))
    light = Image.new("RGB", (w, h), (112, 108, 74))
    base = Image.composite(dark, base, g.point(lambda v: max(0, (110 - v)) * 2))
    base = Image.composite(light, base, g.point(lambda v: max(0, (v - 165)) * 2))

    # ржавые подтёки
    rust = Image.new("RGB", (w, h), (112, 58, 26))
    rmask = Image.new("L", (w, h), 0)
    rd = ImageDraw.Draw(rmask)
    for _ in range(9):
        x = rnd.uniform(0, w)
        y0 = rnd.uniform(-40, h * 0.5)
        ln = rnd.uniform(80, 300)
        for k in range(int(ln)):
            rd.ellipse([x - 3 + math.sin(k / 9) * 2, y0 + k, x + 3 + math.sin(k / 9) * 2, y0 + k + 3],
                       fill=int(90 * (1 - k / ln)))
    rmask = rmask.filter(ImageFilter.GaussianBlur(3))
    rmask = ImageChops.multiply(rmask, noise(w, h, 6, 3).point(lambda v: min(255, v + 80)))
    base = Image.composite(rust, base, rmask)

    # заклёпки по краям (броня/борт)
    d = ImageDraw.Draw(base)
    for x in range(26, w, 58):
        for y in (14, h - 14):
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(46, 47, 32))
            d.ellipse([x - 4, y - 5, x + 3, y + 2], fill=(92, 92, 62))
            d.ellipse([x - 2, y - 3, x, y - 1], fill=(140, 138, 100))
    d.line([(0, 28), (w, 28)], fill=(22, 23, 15), width=2)
    d.line([(0, 29), (w, 29)], fill=(86, 88, 60), width=1)
    d.line([(0, h - 29), (w, h - 29)], fill=(22, 23, 15), width=2)

    # крупная трафаретная звезда-выцветший знак на борту
    star = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(star)
    cx, cy, R = int(w * 0.30), int(h * 0.52), 210
    pts = []
    for i in range(10):
        rr = R if i % 2 == 0 else R * 0.40
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    sd.polygon(pts, fill=255)
    star = ImageChops.multiply(star, grunge(w, h, 21).point(lambda v: 255 if v > 118 else int(v * 0.6)))
    star = star.point(lambda v: int(v * 0.16))
    base = Image.composite(Image.new("RGB", (w, h), (150, 40, 28)), base, star)

    # трафаретная надпись бортового номера
    stencil = Image.new("L", (w, h), 0)
    std = ImageDraw.Draw(stencil)
    std.text((w - 330, h - 150), "№ 1944", font=ImageFont.truetype(FONT, 64), fill=46)
    stencil = ImageChops.multiply(stencil, noise(w, h, 2, 9).point(lambda v: 255 if v > 90 else 0))
    base = Image.composite(Image.new("RGB", (w, h), (200, 196, 150)), base, stencil)

    # царапины: светлые (голый металл) и тёмные
    d = ImageDraw.Draw(base)
    scratches(d, w, h, 70, lambda r: (r.randint(120, 160), r.randint(116, 150), r.randint(84, 110)), 11)
    scratches(d, w, h, 50, lambda r: (r.randint(12, 24), r.randint(12, 24), r.randint(8, 14)), 12)

    # плёночное зерно + виньетка
    grain = noise(w, h, 1, 77).point(lambda v: 128 + (v - 128) // 5)
    base = ImageChops.overlay(base, Image.merge("RGB", (grain, grain, grain)))
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.35], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    base = Image.composite(base, Image.new("RGB", (w, h), (8, 8, 5)), vig)
    base.save(OUT / "background.png")


def stencil_text(text, size, color, distress_seed, pad=20):
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=font)
    w, h = r - l + pad * 2, b - t + pad * 2
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.text((pad - l, pad - t), text, font=font, fill=255)
    # перемычки трафарета: горизонтальные прорези
    for yy in (int(h * 0.36), int(h * 0.62)):
        md.rectangle([0, yy, w, yy + max(2, size // 26)], fill=0)
    # износ краски
    wear = grunge(w, h, distress_seed).point(lambda v: 0 if v < 96 else 255)
    chips = Image.new("L", (w, h), 255)
    cd = ImageDraw.Draw(chips)
    r2 = random.Random(distress_seed)
    for _ in range(int(w * h / 900)):
        x, y = r2.uniform(0, w), r2.uniform(0, h)
        s = r2.uniform(1, 4)
        cd.ellipse([x - s, y - s, x + s, y + s], fill=0)
    mask = ImageChops.multiply(ImageChops.multiply(mask, wear), chips)
    img = Image.new("RGBA", (w, h), color + (0,))
    img.putalpha(mask)
    return img


def logo():
    title = stencil_text("ЕГЕРЬ", 132, (214, 204, 160), 5)
    shadow = Image.new("RGBA", title.size, (0, 0, 0, 0))
    shadow.putalpha(title.getchannel("A").point(lambda v: v * 0.55))
    canvas = Image.new("RGBA", (title.width + 12, title.height + 12), (0, 0, 0, 0))
    canvas.alpha_composite(shadow, (8, 8))
    canvas.alpha_composite(title, (0, 0))
    canvas.save(OUT / "logo.png")


def icon():
    S = 1024
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    plate = Image.new("RGB", (S, S), (70, 74, 46))
    g = grunge(S, S, 33)
    plate = Image.composite(Image.new("RGB", (S, S), (34, 36, 22)), plate, g.point(lambda v: max(0, 120 - v) * 2))
    d = ImageDraw.Draw(plate)
    scratches(d, S, S, 60, lambda r: (r.randint(130, 170), r.randint(126, 160), r.randint(90, 120)), 5)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([40, 40, S - 40, S - 40], radius=90, fill=255)
    img.paste(plate, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 40, S - 40, S - 40], radius=90, outline=(24, 25, 16), width=22)
    for x, y in ((120, 120), (S - 120, 120), (120, S - 120), (S - 120, S - 120)):
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(40, 41, 27))
        d.ellipse([x - 20, y - 24, x + 14, y + 10], fill=(118, 116, 80))

    star = Image.new("L", (S, S), 0)
    sd = ImageDraw.Draw(star)
    cx, cy, R = S // 2, S // 2 + 20, 380
    pts = [(cx + (R if i % 2 == 0 else R * 0.40) * math.cos(-math.pi / 2 + i * math.pi / 5),
            cy + (R if i % 2 == 0 else R * 0.40) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    sd.polygon(pts, fill=255)
    star = ImageChops.multiply(star, grunge(S, S, 44).point(lambda v: 0 if v < 92 else 255))
    red = Image.new("RGBA", (S, S), (176, 36, 26, 255))
    red.putalpha(star)
    img.alpha_composite(red)

    letter = stencil_text("Е", 470, (230, 222, 180), 8, pad=0)
    img.alpha_composite(letter, ((S - letter.width) // 2, cy - letter.height // 2 + 10))

    bw, bh = 500, 150
    bx, by = S - bw - 60, S - bh - 70
    tag = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    td.rectangle([bx, by, bx + bw, by + bh], fill=(200, 160, 60, 255))
    td.rectangle([bx + 10, by + 10, bx + bw - 10, by + bh - 10], outline=(60, 40, 10, 255), width=8)
    f = ImageFont.truetype(FONT, 104)
    tb = td.textbbox((0, 0), "ТЕСТ", font=f)
    td.text((bx + (bw - (tb[2] - tb[0])) / 2 - tb[0], by + (bh - (tb[3] - tb[1])) / 2 - tb[1]), "ТЕСТ",
            font=f, fill=(50, 32, 8, 255))
    tag = tag.rotate(-6, resample=Image.BICUBIC, center=(bx + bw / 2, by + bh / 2))
    img.alpha_composite(tag)

    img.resize((512, 512), Image.LANCZOS).save(OUT / "icon.png")
    img.save(ROOT / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def _star(draw, cx, cy, r, fill):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.28
        a = -math.pi / 2 + i * math.pi / 4
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


def _air_ship(draw, cx, cy, s, ink, alpha):
    c = (28, 27, 24, alpha)
    draw.ellipse([cx - s, cy - s * 0.42, cx + s, cy + s * 0.42], outline=c, width=int(4 * s / 120))
    draw.line([(cx + s * 0.55, cy - s * 0.30), (cx + s * 1.15, cy - s * 0.52), (cx + s * 1.15, cy + s * 0.10)],
              fill=c, width=int(4 * s / 120))
    draw.line([(cx + s * 0.55, cy + s * 0.30), (cx + s * 1.15, cy + s * 0.52), (cx + s * 1.15, cy - s * 0.10)],
              fill=c, width=int(4 * s / 120))
    draw.rounded_rectangle([cx - s * 0.28, cy + s * 0.38, cx + s * 0.20, cy + s * 0.66],
                           radius=s * 0.10, outline=c, width=int(3 * s / 120))
    draw.line([(cx + s * 0.30, cy), (cx + s * 0.62, cy)], fill=c, width=int(3 * s / 120))
    draw.arc([cx + s * 0.62, cy - s * 0.22, cx + s * 0.92, cy + s * 0.22], 250, 110,
             fill=c, width=int(3 * s / 120))


def _wheat(draw, x, y, h, ink, alpha, lean):
    c = (28, 27, 24, alpha)
    draw.arc([x - h * 0.10, y - h, x + h * 0.10 + lean * h, y + h * 0.2], 250, 80, fill=c, width=max(3, int(h / 55)))
    for i in range(7):
        t = i / 6
        gx = x + lean * h * t + math.sin(t * 2.2) * h * 0.04
        gy = y - h * (0.25 + 0.62 * t)
        for side in (-1, 1):
            draw.ellipse([gx + side * h * 0.045 - h * 0.022, gy - h * 0.055,
                          gx + side * h * 0.045 + h * 0.022, gy + h * 0.055],
                         outline=c, width=max(2, int(h / 90)))


def hand_hero(w=1400, h=1800):
    """Тушь, рука с открытой банкой майонеза, орбиты, звёзды, дирижабль, пшеница. Без текста."""
    ss = 2
    W, H = w * ss, h * ss
    ink = (28, 27, 24)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def S(v):
        return v * ss

    # орбитальные кольца
    cx, cy = 700, 940
    rings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for rx, ry, rot, alpha, wd in ((430, 170, -14, 150, 5), (520, 225, 17, 115, 4), (350, 305, 0, 85, 3)):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], outline=ink + (alpha,), width=S(wd))
        layer = layer.rotate(rot, resample=Image.BICUBIC, center=(S(cx), S(cy)))
        rings = Image.alpha_composite(rings, layer)
    img = Image.alpha_composite(img, rings)

    d = ImageDraw.Draw(img)

    # звёзды и точки
    rnd_stars = random.Random(1939)
    for _ in range(26):
        ang = rnd_stars.uniform(0, math.tau)
        dist = rnd_stars.uniform(420, 760)
        sx, sy = cx + math.cos(ang) * dist * 0.72, cy + math.sin(ang) * dist * 0.78
        if 0 < sx < w and 0 < sy < h:
            _star(d, S(sx), S(sy), S(rnd_stars.uniform(6, 18)), ink + (rnd_stars.randint(120, 210),))
    for _ in range(40):
        sx, sy = rnd_stars.uniform(80, w - 80), rnd_stars.uniform(80, h - 80)
        d.ellipse([S(sx) - 3, S(sy) - 3, S(sx) + 3, S(sy) + 3], fill=ink + (rnd_stars.randint(70, 150),))

    # дирижабль
    ship = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _air_ship(ImageDraw.Draw(ship), S(1110), S(330), S(150), ink, 230)
    ship = ship.rotate(-7, resample=Image.BICUBIC, center=(S(1110), S(330)))
    img = Image.alpha_composite(img, ship)
    d = ImageDraw.Draw(img)

    # пшеница по нижним углам
    _wheat(d, S(170), S(1500), S(430), ink, 210, 0.16)
    _wheat(d, S(1210), S(1560), S(390), ink, 210, -0.20)

    # банка: корпус
    body = [S(455), S(792), S(945), S(792), S(945), S(1360), S(455), S(1360)]
    d.rounded_rectangle([S(455), S(792), S(945), S(1360)], radius=S(78), outline=ink + (245,), width=S(8))
    # майонез: штриховка внутри банки
    mayo_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mayo_mask).rounded_rectangle([S(470), S(930), S(930), S(1345)], radius=S(64), fill=255)
    mayo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mayo)
    for off in range(-W, W, S(26)):
        md.line([(off, S(1320)), (off + S(500), S(820))], fill=ink + (80,), width=S(3))
    mayo.putalpha(Image.composite(mayo.getchannel("A"), Image.new("L", (W, H), 0), mayo_mask))
    img = Image.alpha_composite(img, mayo)
    d = ImageDraw.Draw(img)
    # поверхность майонеза
    d.arc([S(470), S(890), S(930), S(1000)], 0, 180, fill=ink + (200,), width=S(6))
    d.arc([S(470), S(900), S(930), S(1010)], 0, 180, fill=ink + (120,), width=S(3))
    # горловина и открытый венец
    d.ellipse([S(432), S(742), S(968), S(838)], outline=ink + (245,), width=S(8))
    d.ellipse([S(462), S(760), S(938), S(820)], outline=ink + (180,), width=S(4))
    d.line([(S(500), S(800)), (S(500), S(890))], fill=ink + (140,), width=S(3))
    d.line([(S(900), S(800)), (S(900), S(890))], fill=ink + (140,), width=S(3))
    # блики стекла
    d.line([(S(520), S(950)), (S(520), S(1280))], fill=ink + (90,), width=S(5))
    d.line([(S(560), S(980)), (S(560), S(1240))], fill=ink + (55,), width=S(3))
    # этикетка-звезда (без текста)
    d.ellipse([S(620), S(1030), S(780), S(1190)], outline=ink + (110,), width=S(4))
    _star(d, S(700), S(1110), S(48), ink + (110,))

    # крышка рядом
    d.ellipse([S(980), S(1290), S(1215), S(1375)], outline=ink + (230,), width=S(7))
    d.ellipse([S(1000), S(1302), S(1195), S(1362)], outline=ink + (120,), width=S(3))
    d.arc([S(980), S(1375), S(1215), S(1440)], 180, 360, fill=ink + (200,), width=S(6))

    # ложка в банке
    spoon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spoon)
    cx0, cy0 = S(610), S(690)
    sd.ellipse([cx0 - S(72), cy0 - S(46), cx0 + S(72), cy0 + S(46)], outline=ink + (235,), width=S(6))
    sd.line([(S(640), S(735)), (S(760), S(1140))], fill=ink + (225,), width=S(9))
    spoon = spoon.rotate(-12, resample=Image.BICUBIC, center=(S(650), S(900)))
    img = Image.alpha_composite(img, spoon)

    # рука справа: ладонь, четыре пальца, большой палец, предплечье
    hand = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hand)
    # предплечье и ладонь — сплошной силуэт
    hd.polygon([(S(1040), S(1450)), (S(1215), S(1465)), (S(1335), S(1830)), (S(1115), S(1830))],
               fill=ink + (255,))
    hd.polygon([(S(985), S(1035)), (S(1165), S(1065)), (S(1235), S(1300)), (S(1195), S(1505)),
                (S(1035), S(1520)), (S(958), S(1295))], fill=ink + (255,))
    # большой палец поверх банки
    hd.line([(S(1015), S(1375)), (S(850), S(1320))], fill=ink + (255,), width=S(82), joint="curve")
    # четыре пальца, обхватывающие банку
    fingers = ((1045, 1040, 795, 1075), (1055, 1128, 800, 1165), (1060, 1216, 812, 1255), (1048, 1304, 828, 1340))
    for x0, y0, x1, y1 in fingers:
        hd.line([(S(x0), S(y0)), (S((x0 + x1) / 2), S((y0 + y1) / 2 + 16)), (S(x1), S(y1))],
                fill=ink + (255,), width=S(66), joint="curve")
    # суставы и складки — прозрачные прорези
    for x0, y0, x1, y1 in fingers:
        hd.arc([S(x0 - 36), S(y0 - 26), S(x0 + 36), S(y0 + 44)], 70, 250, fill=(0, 0, 0, 0), width=S(4))
        hd.line([(S(950), S(y0 - 34)), (S(938), S(y0 + 34))], fill=(0, 0, 0, 0), width=S(4))
    for i in range(3):
        hd.line([(S(1035 + i * 8), S(1110 + i * 80)), (S(1180), S(1130 + i * 80))], fill=(0, 0, 0, 0), width=S(3))
    # манжета и складки предплечья
    hd.line([(S(1035), S(1560)), (S(1210), S(1550))], fill=(0, 0, 0, 0), width=S(5))
    hd.line([(S(1090), S(1640)), (S(1245), S(1630))], fill=(0, 0, 0, 0), width=S(3))
    img = Image.alpha_composite(img, hand)

    img = img.resize((w, h), Image.LANCZOS)
    img.save(OUT / "hand-hero.png")


background()
logo()
icon()
paper()
hand_icon()
hand_hero()
print("ok")
