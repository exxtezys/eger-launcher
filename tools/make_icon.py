"""Рисует иконку лаунчера: изометрический куб (трава/земля) в бирюзовом скруглённом квадрате + бейдж TEST.
Выход: theme/icon.png (512) и icon.ico (16..256) в корне проекта."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
S = 1024


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def make(test_badge=True):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # скруглённый фон с вертикальным градиентом
    bg = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(bg)
    for y in range(S):
        d.line([(0, y), (S, y)], fill=lerp((23, 163, 154, 255), (8, 52, 60, 255), y / S))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([24, 24, S - 24, S - 24], radius=210, fill=255)
    img.paste(bg, (0, 0), mask)

    # мягкий блик сверху
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([120, -260, S - 120, 420], fill=(255, 255, 255, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, Image.composite(glow, Image.new("RGBA", (S, S)), mask))

    # изометрический куб
    cx, top, r = S // 2, 210, 300
    h = int(r * 0.58)
    T = (cx, top)
    L = (cx - r, top + h)
    R = (cx + r, top + h)
    C = (cx, top + 2 * h)
    depth = 330
    Lb, Rb, Cb = (L[0], L[1] + depth), (R[0], R[1] + depth), (C[0], C[1] + depth)

    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([L, T, R, Rb, Cb, Lb], fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img, shadow.transform(shadow.size, Image.AFFINE, (1, 0, 0, 0, 1, -24)))

    d = ImageDraw.Draw(img)
    dirt_l, dirt_r = (121, 85, 58), (94, 64, 43)
    grass_top, grass_l, grass_r = (110, 196, 92), (84, 160, 70), (64, 130, 54)
    d.polygon([L, C, Cb, Lb], fill=dirt_l)
    d.polygon([C, R, Rb, Cb], fill=dirt_r)

    # пиксельная текстура земли
    import random
    rnd = random.Random(7)
    for face, base in (((L, C, Cb, Lb), dirt_l), ((C, R, Rb, Cb), dirt_r)):
        a, b, _, dd = face
        n = 8
        for i in range(n):
            for j in range(n):
                if rnd.random() < 0.35:
                    def pt(u, v):
                        return (a[0] + (b[0] - a[0]) * u + (dd[0] - a[0]) * v,
                                a[1] + (b[1] - a[1]) * u + (dd[1] - a[1]) * v)
                    shade = rnd.choice((-16, -9, 10))
                    col = tuple(max(0, min(255, c + shade)) for c in base)
                    d.polygon([pt(i / n, j / n), pt((i + 1) / n, j / n),
                               pt((i + 1) / n, (j + 1) / n), pt(i / n, (j + 1) / n)], fill=col)

    # трава: верх + свисающая кромка
    lip = 0.27
    Ll, Cl, Rl = (L[0], L[1] + depth * lip), (C[0], C[1] + depth * lip), (R[0], R[1] + depth * lip)
    d.polygon([L, C, Cl, Ll], fill=grass_l)
    d.polygon([C, R, Rl, Cl], fill=grass_r)
    for k in range(9):
        u = (k + 0.5) / 9
        for (p0, p1, col) in ((L, C, grass_l), (C, R, grass_r)):
            x = p0[0] + (p1[0] - p0[0]) * u
            y = p0[1] + (p1[1] - p0[1]) * u + depth * lip
            drop = depth * (0.06 + 0.07 * rnd.random())
            d.rectangle([x - 15, y - 2, x + 15, y + drop], fill=col)
    d.polygon([T, R, C, L], fill=grass_top)

    # буква E на верхней грани
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 260)
    except OSError:
        font = ImageFont.load_default()
    letter = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(letter)
    bbox = ld.textbbox((0, 0), "K", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    ld.text((S / 2 - tw / 2 - bbox[0], S / 2 - th / 2 - bbox[1]), "K", font=font, fill=(255, 255, 255, 235))
    # сплющиваем под изометрию: масштаб по Y 0.58 и поворот 45° внутри ромба
    letter = letter.rotate(45, resample=Image.BICUBIC, center=(S / 2, S / 2))
    letter = letter.resize((S, int(S * 0.58)), Image.BICUBIC)
    off_y = top + h - letter.height // 2
    img.alpha_composite(letter, (0, off_y))

    if test_badge:
        bw, bh = 470, 150
        bx, by = S - bw - 40, S - bh - 50
        badge = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle([bx, by + 10, bx + bw, by + bh + 10], radius=60, fill=(0, 0, 0, 110))
        badge = badge.filter(ImageFilter.GaussianBlur(10))
        img = Image.alpha_composite(img, badge)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=60, fill=(242, 179, 61, 255))
        bf = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 110)
        tb = d.textbbox((0, 0), "TEST", font=bf)
        d.text((bx + (bw - (tb[2] - tb[0])) / 2 - tb[0], by + (bh - (tb[3] - tb[1])) / 2 - tb[1]),
               "TEST", font=bf, fill=(40, 26, 6, 255))
    return img


icon = make()
(ROOT / "theme").mkdir(exist_ok=True)
icon.resize((512, 512), Image.LANCZOS).save(ROOT / "theme" / "icon.png")
icon.save(ROOT / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("ok", ROOT / "icon.ico")
