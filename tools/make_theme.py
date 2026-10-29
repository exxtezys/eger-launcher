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


background()
logo()
icon()
print("ok")
