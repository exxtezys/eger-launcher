# -*- coding: utf-8 -*-
"""Draws the launcher's painted scene: a 1939 tasting room, ink on aged paper.

Renders theme/scene.png at 2x (1840x1120) so the launcher can downscale it
smoothly. Everything that moves (airship, dust, lamp) is drawn live in Java;
this file is the static set.

Run: python tools/gen-scene.py
"""
import math
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "theme" / "fonts"
OUT = ROOT / "theme" / "scene.png"

S = 2                      # supersampling
W, H = 920, 560            # logical window size
INK = (43, 36, 27)
INK_SOFT = (78, 68, 53)
CREAM = (232, 224, 203)
PAPER = (222, 213, 192)
WALL_TOP = (203, 193, 171)
WALL_BOT = (219, 209, 186)
WOOD = (108, 76, 48)
WOOD_DARK = (72, 50, 31)
WOOD_LIGHT = (139, 102, 65)
BRASS = (168, 130, 74)
BRASS_LIGHT = (214, 179, 118)
BRASS_DARK = (104, 78, 39)
OXBLOOD = (128, 40, 30)
NIGHT_TOP = (18, 23, 31)
NIGHT_BOT = (40, 47, 56)

# shared with Scene.java
LAMP = (470, 118)
WINDOW = (556, 30, 884, 252)


def sc(v):
    return int(round(v * S))


def box(x0, y0, x1, y1):
    return [sc(x0), sc(y0), sc(x1), sc(y1)]


def layer():
    return Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))


def font(path, size):
    return ImageFont.truetype(str(FONTS / path), sc(size))


RUSSO = "RussoOne-Regular.ttf"
MONO = "PTMono-Regular.ttf"


def grain(img, amount=4.0):
    arr = np.array(img.convert("RGB")).astype(np.int16)
    noise = np.random.normal(0, amount, arr.shape[:2])
    noise = np.repeat(noise[:, :, None], 3, axis=2)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    out = Image.fromarray(arr).convert("RGBA")
    if img.mode == "RGBA":
        out.putalpha(img.getchannel("A"))
    return out


def blotches(img, n=90, dark=True, seed=7):
    rnd = random.Random(seed)
    lay = layer()
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        rx, ry = rnd.uniform(3, 26), rnd.uniform(3, 18)
        a = rnd.randint(2, 7)
        col = (60, 48, 34, a) if dark else (255, 250, 232, a)
        d.ellipse(box(x - rx, y - ry, x + rx, y + ry), fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(sc(2)))
    return Image.alpha_composite(img.convert("RGBA"), lay)


def hatch(img, poly, angle=45, gap=4, color=(43, 36, 27, 40), width=1, jitter=0.6, seed=1):
    """Cross-hatching clipped to a polygon."""
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon([(sc(x), sc(y)) for x, y in poly], fill=255)
    lay = layer()
    d = ImageDraw.Draw(lay)
    rnd = random.Random(seed)
    a = math.radians(angle)
    diag = math.hypot(W, H) * 1.2
    step = sc(gap)
    n = int(diag * S / step) + 2
    cx, cy = sc(W / 2), sc(H / 2)
    for i in range(-n, n):
        off = i * step + rnd.uniform(-jitter, jitter) * S
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        x0, y0 = cx + nx * off - dx * diag * S / 2, cy + ny * off - dy * diag * S / 2
        x1, y1 = cx + nx * off + dx * diag * S / 2, cy + ny * off + dy * diag * S / 2
        d.line([x0, y0, x1, y1], fill=color, width=sc(width))
    lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", img.size, 0), mask))
    return Image.alpha_composite(img.convert("RGBA"), lay)


def radial(img, cx, cy, r, color, power=1.6):
    """Soft radial bloom, added over the image."""
    y, x = np.ogrid[0:H * S, 0:W * S]
    d = np.sqrt((x - sc(cx)) ** 2 + (y - sc(cy)) ** 2) / (sc(r) + 1)
    a = np.clip(1 - d, 0, 1) ** power
    lay = np.zeros((H * S, W * S, 4), dtype=np.uint8)
    lay[:, :, 0], lay[:, :, 1], lay[:, :, 2] = color[0], color[1], color[2]
    lay[:, :, 3] = (a * color[3]).astype(np.uint8)
    return Image.alpha_composite(img.convert("RGBA"), Image.fromarray(lay, "RGBA"))


def vertical_gradient(size, top, bottom):
    w, h = size
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(3):
            arr[y, :, i] = int(top[i] + (bottom[i] - top[i]) * t)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def wood_grain(img, area, seed=3, strength=1.0):
    x0, y0, x1, y1 = area
    rnd = random.Random(seed)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rectangle(box(x0, y0, x1, y1), fill=255)
    lay = layer()
    d = ImageDraw.Draw(lay)
    for i in range(46):
        yy = y0 + (y1 - y0) * i / 46 + rnd.uniform(-2, 2)
        amp = rnd.uniform(0.6, 2.4) * strength
        phase = rnd.uniform(0, 6.28)
        pts = []
        for xx in range(sc(x0), sc(x1) + 1, sc(4)):
            t = (xx / S - x0) / max(1, (x1 - x0))
            yy2 = yy + math.sin(t * 9 + phase) * amp + math.sin(t * 31 + phase * 2) * amp * .35
            pts.append((xx, sc(yy2)))
        col = (42, 28, 17, rnd.randint(18, 46)) if i % 3 else (206, 168, 118, rnd.randint(10, 22))
        d.line(pts, fill=col, width=sc(1))
    for _ in range(70):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        d.line([sc(x), sc(y), sc(x + rnd.uniform(6, 30)), sc(y + rnd.uniform(-.7, .7))],
               fill=(35, 23, 14, 34), width=1)
    lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", img.size, 0), mask))
    return Image.alpha_composite(img.convert("RGBA"), lay)


# ---------------------------------------------------------------- wall

def star(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def draw_emblem(img):
    """Ghost of the state quality mark, printed on the wall behind the wordmark."""
    lay = layer()
    d = ImageDraw.Draw(lay)
    cx, cy = 266, 146
    ink = (78, 66, 48, 26)
    d.ellipse(box(cx - 92, cy - 92, cx + 92, cy + 92), outline=ink, width=sc(2))
    d.ellipse(box(cx - 84, cy - 84, cx + 84, cy + 84), outline=ink, width=sc(1))
    d.ellipse(box(cx - 62, cy - 62, cx + 62, cy + 62), outline=ink, width=sc(1))
    # dashed text ring
    for i in range(34):
        a = math.radians(i * 360 / 34)
        r0, r1 = 64, 78
        d.line([sc(cx + math.cos(a) * r0), sc(cy + math.sin(a) * r0),
                sc(cx + math.cos(a) * r1), sc(cy + math.sin(a) * r1)], fill=ink, width=sc(1))
    d.polygon([(sc(x), sc(y)) for x, y in star(cx, cy, 40, 17)], outline=ink, width=sc(2))
    # wheat sprigs
    for sgn in (-1, 1):
        for i in range(7):
            bx = cx + sgn * (24 + i * 3)
            by = cy + 54 - i * 11
            d.line([sc(cx + sgn * 20), sc(cy + 62), sc(bx), sc(by)], fill=ink, width=sc(1))
            d.ellipse(box(bx - 2.5, by - 4, bx + 2.5, by + 2), outline=ink, width=sc(1))
    img = Image.alpha_composite(img, lay)
    return img


def draw_clock(img):
    cx, cy, r = 516, 58, 23
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.ellipse(box(cx - r + 2, cy - r + 4, cx + r + 3, cy + r + 5), fill=(60, 46, 30, 40))
    d.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=BRASS, outline=(58, 44, 28, 230), width=sc(1.4))
    d.ellipse(box(cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), fill=(238, 229, 207, 255))
    d.ellipse(box(cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), outline=(96, 78, 52, 150), width=sc(1))
    for i in range(12):
        a = math.radians(i * 30)
        r0 = r - (7 if i % 3 else 9)
        d.line([sc(cx + math.cos(a) * r0), sc(cy + math.sin(a) * r0),
                sc(cx + math.cos(a) * (r - 4)), sc(cy + math.sin(a) * (r - 4))],
               fill=(50, 40, 28, 210), width=sc(1.2 if i % 3 else 1.8))
    # hands are drawn live by Scene.java
    d.ellipse(box(cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6), fill=(38, 30, 20, 235))
    img = Image.alpha_composite(img, lay)
    return img


def draw_wall(img):
    img = Image.alpha_composite(img, vertical_gradient((W * S, H * S), WALL_TOP, WALL_BOT))
    # faint wallpaper panels
    lay = layer()
    d = ImageDraw.Draw(lay)
    for x in range(0, 940, 128):
        d.line([sc(x), 0, sc(x), sc(380)], fill=(96, 82, 60, 16), width=sc(1))
        d.line([sc(x + 1), 0, sc(x + 1), sc(380)], fill=(255, 250, 232, 12), width=sc(1))
    # crown moulding
    d.rectangle(box(0, 0, W, 9), fill=(178, 166, 142, 255))
    d.line([0, sc(9), sc(W), sc(9)], fill=(88, 74, 52, 120), width=sc(1))
    d.line([0, sc(10), sc(W), sc(10)], fill=(255, 250, 230, 90), width=sc(1))
    # corner falloff
    d.polygon([(0, 0), (sc(140), 0), (0, sc(220))], fill=(70, 58, 42, 16))
    img = Image.alpha_composite(img, lay)
    img = blotches(img, 120, seed=11)
    img = draw_emblem(img)
    img = draw_clock(img)
    return img


# ---------------------------------------------------------------- window

def skyline(img, sx0, sx1, sy1):
    lay = layer()
    d = ImageDraw.Draw(lay)
    dark = (11, 15, 21, 255)
    d.rectangle(box(sx0, sy1 - 10, sx1, sy1), fill=dark)
    # long shop with a sawtooth roof
    x = sx0 + 4
    while x < sx0 + 74:
        d.polygon([(sc(x), sc(sy1 - 22)), (sc(x + 9), sc(sy1 - 34)), (sc(x + 18), sc(sy1 - 22))], fill=dark)
        x += 18
    d.rectangle(box(sx0 + 4, sy1 - 22, sx0 + 76, sy1), fill=dark)
    # taller block
    d.rectangle(box(sx0 + 76, sy1 - 40, sx0 + 132, sy1), fill=dark)
    d.rectangle(box(sx0 + 90, sy1 - 52, sx0 + 96, sy1), fill=dark)
    d.rectangle(box(sx0 + 88, sy1 - 54, sx0 + 98, sy1 - 50), fill=dark)
    # sheds and chimneys to the right
    d.rectangle(box(sx0 + 132, sy1 - 26, sx0 + 196, sy1), fill=dark)
    d.rectangle(box(sx0 + 160, sy1 - 46, sx0 + 167, sy1), fill=dark)
    d.rectangle(box(sx0 + 158, sy1 - 48, sx0 + 169, sy1 - 44), fill=dark)
    d.rectangle(box(sx0 + 196, sy1 - 18, sx0 + 250, sy1), fill=dark)
    d.rectangle(box(sx0 + 214, sy1 - 38, sx0 + 220, sy1), fill=dark)
    d.rectangle(box(sx0 + 212, sy1 - 40, sx0 + 222, sy1 - 36), fill=dark)
    d.rectangle(box(sx0 + 250, sy1 - 30, sx1, sy1), fill=dark)
    # lit windows
    rnd = random.Random(12)
    for _ in range(14):
        wx = rnd.uniform(sx0 + 6, sx1 - 6)
        wy = rnd.uniform(sy1 - 30, sy1 - 4)
        d.point((sc(wx), sc(wy)), fill=(232, 186, 104, 150))
    img = Image.alpha_composite(img, lay)
    return img


def draw_curtain(img):
    lay = layer()
    d = ImageDraw.Draw(lay)
    # rod
    d.line([sc(526), sc(21), sc(602), sc(21)], fill=(70, 54, 34, 255), width=sc(3))
    d.ellipse(box(520, 16, 530, 26), fill=BRASS)
    d.ellipse(box(598, 16, 608, 26), fill=BRASS)
    for rx in (534, 552, 570, 588):
        d.ellipse(box(rx - 2, 24, rx + 2, 30), outline=BRASS_DARK, width=sc(1))
    # heavy panel, softly gathered
    edge = [(598, 24), (592, 60), (597, 100), (589, 146), (595, 190), (587, 228), (591, 266)]
    panel = [(534, 24)] + edge + [(534, 266)]
    d.polygon([(sc(x), sc(y)) for x, y in panel], fill=(100, 40, 32, 255))
    d.line([(sc(x), sc(y)) for x, y in edge], fill=(44, 24, 18, 230), width=sc(2))
    d.line([sc(534), sc(24), sc(534), sc(266)], fill=(52, 28, 20, 200), width=sc(1))
    # folds
    for i in range(17):
        fx = 535 + i * 3.6
        pts = []
        for yy in range(26, 266, 6):
            pts.append((sc(fx + math.sin(yy / 21 + i * .8) * 2.2), sc(yy)))
        dark = (54, 24, 18, 120) if i % 2 else (58, 26, 20, 60)
        d.line(pts, fill=dark, width=sc(1))
        if i % 3 == 0:
            d.line([(x + sc(1), y) for x, y in pts], fill=(168, 92, 74, 26), width=1)
    # hem
    d.line([(sc(534), sc(266)), (sc(591), sc(266))], fill=(34, 18, 14, 230), width=sc(2))
    d.line([(sc(535), sc(263)), (sc(590), sc(263))], fill=(150, 82, 66, 60), width=1)
    img = Image.alpha_composite(img, lay)
    return img


def draw_window(img):
    x0, y0, x1, y1 = WINDOW
    # frame with brass bevel
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle(box(x0 - 4, y0 - 4, x1 + 4, y1 + 4), fill=(54, 44, 31, 110))
    d.rectangle(box(x0, y0, x1, y1), fill=BRASS)
    d.rectangle(box(x0 + 1.5, y0 + 1.5, x1 - 1.5, y1 - 1.5), fill=BRASS_DARK)
    d.rectangle(box(x0 + 4, y0 + 4, x1 - 4, y1 - 4), fill=BRASS_LIGHT)
    d.rectangle(box(x0 + 6, y0 + 6, x1 - 6, y1 - 6), fill=(44, 36, 25, 255))
    img = Image.alpha_composite(img, lay)

    # sky
    sx0, sy0, sx1, sy1 = x0 + 8, y0 + 8, x1 - 8, y1 - 8
    sky = vertical_gradient((sc(sx1 - sx0), sc(sy1 - sy0)), NIGHT_TOP, NIGHT_BOT)
    sky = grain(sky, 2.4)
    img.paste(sky, (sc(sx0), sc(sy0)))

    lay = layer()
    d = ImageDraw.Draw(lay)
    rnd = random.Random(44)
    for _ in range(190):
        x = rnd.uniform(sx0 + 4, sx1 - 4)
        y = rnd.uniform(sy0 + 4, sy1 - 26)
        a = rnd.randint(60, 235)
        r = rnd.choice([.5, .5, .6, .8, 1.0])
        d.ellipse(box(x - r, y - r, x + r, y + r), fill=(240, 232, 205, a))
    for _ in range(10):
        x, y = rnd.uniform(sx0 + 8, sx1 - 8), rnd.uniform(sy0 + 8, sy1 - 40)
        d.line([sc(x - 2.2), sc(y), sc(x + 2.2), sc(y)], fill=(238, 230, 200, 190), width=1)
        d.line([sc(x), sc(y - 2.2), sc(x), sc(y + 2.2)], fill=(238, 230, 200, 190), width=1)
    # moon
    mx, my, mr = 604, 84, 15
    d.ellipse(box(mx - mr, my - mr, mx + mr, my + mr), fill=(238, 231, 206, 255))
    for dx, dy, r2 in ((-5, -4, 3.8), (5, 2, 2.6), (-1, 6, 1.8)):
        d.ellipse(box(mx + dx - r2, my + dy - r2, mx + dx + r2, my + dy + r2), fill=(226, 218, 192, 90))
    img = Image.alpha_composite(img, lay)
    img = radial(img, mx, my, 64, (226, 222, 200, 46), power=2.0)

    lay = layer()
    d = ImageDraw.Draw(lay)
    # orbital chart etched into the sky
    rings = layer()
    rd = ImageDraw.Draw(rings)
    for rx, ry in ((152, 54), (114, 40), (76, 26)):
        rd.ellipse([sc(722 - rx), sc(142 - ry), sc(722 + rx), sc(142 + ry)],
                   outline=(236, 228, 204, 52), width=sc(1))
    rings = rings.rotate(-13, center=(sc(722), sc(142)), resample=Image.BICUBIC)
    lay = Image.alpha_composite(lay, rings)
    d = ImageDraw.Draw(lay)
    img = Image.alpha_composite(img, lay)
    img = skyline(img, sx0, sx1, sy1)

    # glass
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.polygon([(sc(sx0 + 26), sc(sy0)), (sc(sx0 + 50), sc(sy0)),
               (sc(sx0 + 10), sc(sy1)), (sc(sx0 - 14), sc(sy1))], fill=(255, 255, 255, 12))
    d.polygon([(sc(sx0 + 70), sc(sy0)), (sc(sx0 + 78), sc(sy0)),
               (sc(sx0 + 40), sc(sy1)), (sc(sx0 + 32), sc(sy1))], fill=(255, 255, 255, 8))
    # condensation in the lower corners
    rnd = random.Random(3)
    for _ in range(120):
        x = rnd.choice([rnd.uniform(sx0 + 2, sx0 + 60), rnd.uniform(sx1 - 60, sx1 - 2)])
        y = rnd.uniform(sy1 - 26, sy1 - 2)
        d.point((sc(x), sc(y)), fill=(226, 232, 228, rnd.randint(20, 70)))
    img = Image.alpha_composite(img, lay)

    # muntins and latch
    lay = layer()
    d = ImageDraw.Draw(lay)
    for i in (1, 2):
        mx = sx0 + (sx1 - sx0) * i // 3
        d.rectangle(box(mx - 2, sy0, mx + 2, sy1), fill=(54, 43, 30, 255))
        d.line([sc(mx - 1), sc(sy0), sc(mx - 1), sc(sy1)], fill=(186, 152, 96, 120), width=1)
        d.line([sc(mx + 2), sc(sy0), sc(mx + 2), sc(sy1)], fill=(12, 10, 7, 120), width=1)
    my = sy0 + (sy1 - sy0) // 2
    d.rectangle(box(sx0, my - 2, sx1, my + 2), fill=(54, 43, 30, 255))
    d.line([sc(sx0), sc(my - 1), sc(sx1), sc(my - 1)], fill=(186, 152, 96, 110), width=1)
    # rivets on the frame
    for rx, ry in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):
        d.ellipse(box(rx - 1.8, ry - 1.8, rx + 1.8, ry + 1.8), fill=BRASS_DARK)
        d.ellipse(box(rx - 1, ry - 1, rx + .6, ry + .2), fill=BRASS_LIGHT)
    # latch
    d.rounded_rectangle(box(754, my - 9, 762, my + 9), radius=sc(2), fill=BRASS_DARK, outline=INK, width=sc(1))
    d.ellipse(box(756, my - 3, 760, my + 1), fill=BRASS_LIGHT)
    img = Image.alpha_composite(img, lay)

    # sill
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle(box(x0 - 12, y1 + 1, x1 + 10, y1 + 12), fill=(170, 142, 100, 255))
    d.line([sc(x0 - 12), sc(y1 + 1), sc(x1 + 10), sc(y1 + 1)], fill=(238, 216, 172, 200), width=sc(2))
    d.line([sc(x0 - 12), sc(y1 + 11), sc(x1 + 10), sc(y1 + 11)], fill=(50, 39, 26, 200), width=sc(2))
    d.rectangle(box(x0 - 14, y1 + 12, x1 + 12, y1 + 20), fill=(60, 46, 30, 36))
    img = Image.alpha_composite(img, lay)
    return img


# ---------------------------------------------------------------- lamp

def soft_shadow(img, x0, y0, x1, y1, a=70, blur=4, color=(42, 30, 20)):
    lay = layer()
    ImageDraw.Draw(lay).ellipse(box(x0, y0, x1, y1), fill=color + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(sc(blur)))
    return Image.alpha_composite(img.convert("RGBA"), lay)


def soft_glow(img, x0, y0, x1, y1, color, a=30, blur=40):
    lay = layer()
    ImageDraw.Draw(lay).ellipse(box(x0, y0, x1, y1), fill=color + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(sc(blur)))
    return Image.alpha_composite(img.convert("RGBA"), lay)


def draw_lamp(img):
    lx, ly = LAMP
    # pool of warm light on the desk, thrown down and to the right
    img = soft_glow(img, lx - 150, 330, lx + 480, 600, (255, 208, 144), a=26, blur=55)
    img = soft_glow(img, lx - 40, 300, lx + 300, 560, (255, 220, 160), a=18, blur=38)
    # halo on the wall behind the shade
    img = soft_glow(img, lx - 120, 20, lx + 150, 250, (255, 214, 152), a=22, blur=34)

    lay = layer()
    d = ImageDraw.Draw(lay)
    # cord
    d.line([sc(lx), 0, sc(lx), sc(ly - 32)], fill=(48, 38, 26, 255), width=sc(2))
    d.line([sc(lx + 1), 0, sc(lx + 1), sc(ly - 32)], fill=(150, 124, 86, 90), width=1)
    # ceiling rose
    d.ellipse(box(lx - 7, 0, lx + 7, 6), fill=(96, 76, 46, 255))
    d.ellipse(box(lx - 4, 1, lx + 4, 4), fill=BRASS_LIGHT)
    # shade
    shade = [(lx - 33, ly - 30), (lx + 33, ly - 30), (lx + 23, ly), (lx - 23, ly)]
    d.polygon([(sc(x), sc(y)) for x, y in shade], fill=OXBLOOD)
    d.line([(sc(x), sc(y)) for x, y in shade] + [sc(shade[0][0]), sc(shade[0][1])],
           fill=INK, width=sc(1.4), joint="curve")
    d.arc(box(lx - 24, ly - 40, lx + 24, ly - 20), 200, 340, fill=(190, 120, 96, 90), width=sc(2))
    d.line([sc(lx - 23), sc(ly), sc(lx + 23), sc(ly)], fill=(243, 222, 172, 235), width=sc(2))
    # bulb
    d.ellipse(box(lx - 9, ly - 1, lx + 9, ly + 12), fill=(247, 224, 168, 255))
    d.ellipse(box(lx - 5, ly + 2, lx + 3, ly + 9), fill=(255, 248, 214, 255))
    img = Image.alpha_composite(img, lay)
    return radial(img, lx, ly + 6, 96, (255, 216, 150, 92), power=2.1)


# ---------------------------------------------------------------- wall props

def draw_certificate(img):
    x0, y0, x1, y1 = 488, 200, 550, 312
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle(box(x0 + 2, y0 + 2, x1 + 2, y1 + 2), fill=(60, 48, 32, 40))
    d.rectangle(box(x0, y0, x1, y1), fill=(231, 222, 200, 255))
    d.rectangle(box(x0, y0, x1, y1), outline=(74, 58, 38, 220), width=sc(2))
    d.rectangle(box(x0 + 4, y0 + 4, x1 - 4, y1 - 4), outline=(122, 100, 68, 140), width=sc(1))
    # heading rules and typed lines
    d.rectangle(box(x0 + 12, y0 + 12, x1 - 12, y0 + 16), fill=(60, 50, 38, 200))
    rnd = random.Random(5)
    for i in range(9):
        yy = y0 + 26 + i * 7
        wdt = x1 - 22 - (0 if i % 3 else rnd.uniform(6, 18))
        d.line([sc(x0 + 11), sc(yy), sc(wdt), sc(yy)], fill=(74, 62, 46, 105), width=sc(1))
    # state seal
    d.ellipse(box(x1 - 34, y1 - 34, x1 - 12, y1 - 12), outline=(148, 44, 34, 200), width=sc(1.4))
    d.ellipse(box(x1 - 30, y1 - 30, x1 - 16, y1 - 16), outline=(148, 44, 34, 130), width=1)
    d.ellipse(box(x1 - 25, y1 - 25, x1 - 21, y1 - 21), fill=(148, 44, 34, 180))
    # pin
    d.ellipse(box(x0 + 40, y0 - 2, x0 + 44, y0 + 2), fill=(90, 72, 44, 255))
    img = Image.alpha_composite(img, lay)
    return img


# ---------------------------------------------------------------- shelf and jars

def jar(img, cx, base, wdt, hgt, label_text=None, seed=1, tilt=0.0):
    x0, x1 = cx - wdt / 2, cx + wdt / 2
    y1 = base
    y0 = base - hgt
    img = soft_shadow(img, x0 - 5, base - 3, x1 + 9, base + 5, a=70, blur=3.5)
    lay = layer()
    d = ImageDraw.Draw(lay)
    # body
    body = [x0 + 2, y0 + 7, x1 - 2, y1 - 2]
    d.rounded_rectangle(box(*body), radius=sc(4), fill=(214, 207, 187, 240),
                        outline=(52, 43, 31, 240), width=sc(1.3))
    # contents
    d.rounded_rectangle(box(x0 + 3, y0 + hgt * .40, x1 - 3, y1 - 3), radius=sc(3),
                        fill=(232, 215, 175, 255))
    d.line([sc(x0 + 4), sc(y0 + hgt * .40), sc(x1 - 4), sc(y0 + hgt * .40)],
           fill=(252, 243, 214, 220), width=sc(1.3))
    d.line([sc(x0 + 4), sc(y0 + hgt * .42), sc(x1 - 4), sc(y0 + hgt * .42)],
           fill=(176, 152, 112, 90), width=1)
    # air bubbles and settling lines
    rnd = random.Random(seed * 31 + 5)
    for _ in range(7):
        bx = rnd.uniform(x0 + 6, x1 - 6)
        by = rnd.uniform(y0 + hgt * .45, y1 - 6)
        d.ellipse(box(bx - 1, by - 1, bx + 1, by + 1), outline=(248, 236, 204, 60), width=1)
    # glass: cold window reflection on the left, warm shading on the right
    d.polygon([(sc(x0 + 4), sc(y0 + 10)), (sc(x0 + wdt * .30), sc(y0 + 8)),
               (sc(x0 + wdt * .24), sc(y1 - 6)), (sc(x0 + 4), sc(y1 - 4))],
              fill=(196, 205, 202, 70))
    d.polygon([(sc(x1 - wdt * .22), sc(y0 + 9)), (sc(x1 - 3), sc(y0 + 9)),
               (sc(x1 - 3), sc(y1 - 4)), (sc(x1 - wdt * .18), sc(y1 - 6))],
              fill=(84, 70, 50, 34))
    d.line([sc(x0 + wdt * .30), sc(y0 + 9), sc(x0 + wdt * .25), sc(y1 - 8)],
           fill=(255, 252, 238, 150), width=sc(1.4))
    d.line([sc(x1 - 5), sc(y0 + 9), sc(x1 - 5), sc(y1 - 8)], fill=(70, 58, 42, 90), width=sc(1))
    # lid
    d.rounded_rectangle(box(x0 - 1, y0, x1 + 1, y0 + 9), radius=sc(2.5), fill=BRASS,
                        outline=(48, 38, 26, 230), width=sc(1))
    d.ellipse(box(x0 - 1, y0 - 1, x1 + 1, y0 + 5), fill=BRASS_LIGHT, outline=(54, 43, 30, 210))
    for i in range(7):
        lx = x0 + 3 + i * (wdt - 6) / 6
        d.line([sc(lx), sc(y0 + 4), sc(lx), sc(y0 + 8)], fill=(92, 70, 38, 110), width=1)
    # label
    ly0 = y0 + hgt * .48
    ly1 = y0 + hgt * .88
    d.rectangle(box(x0 + 4, ly0, x1 - 4, ly1), fill=(239, 231, 211, 255),
                outline=(138, 48, 36, 190), width=sc(1))
    d.rectangle(box(x0 + 5.5, ly0 + 1.5, x1 - 5.5, ly1 - 1.5), outline=(138, 48, 36, 90), width=1)
    d.polygon([(sc(x), sc(y)) for x, y in star(cx, ly0 + 5.5, 3.1, 1.3)], fill=(140, 48, 36, 210))
    if label_text:
        f = font(MONO, 4.4)
        d.text((sc(cx), sc(ly0 + 9)), label_text, font=f, fill=(52, 42, 30, 235), anchor="ma")
    else:
        for i in range(2):
            d.line([sc(x0 + 8), sc(ly0 + 10 + i * 3.4), sc(x1 - 8), sc(ly0 + 10 + i * 3.4)],
                   fill=(70, 58, 42, 100), width=1)
    # glass glare over the label's left edge
    d.line([sc(x0 + 7), sc(ly0 + 2), sc(x0 + 7), sc(ly1 - 2)], fill=(255, 252, 238, 90), width=sc(1))
    img = Image.alpha_composite(img, lay)
    return img


def draw_shelf(img):
    x0, x1, y = 548, 902, 348
    img = soft_shadow(img, x0 + 4, y + 10, x1, y + 24, a=45, blur=3)
    lay = layer()
    d = ImageDraw.Draw(lay)
    # wall shadow
    d.rectangle(box(x0, y - 4, x1, y + 16), fill=(70, 56, 38, 26))
    # board
    d.rectangle(box(x0, y, x1, y + 9), fill=(122, 88, 55, 255))
    d.line([sc(x0), sc(y), sc(x1), sc(y)], fill=(212, 178, 128, 200), width=sc(1.4))
    d.line([sc(x0), sc(y + 9), sc(x1), sc(y + 9)], fill=(48, 36, 24, 220), width=sc(2))
    # brackets
    for bx in (566, 700, 834):
        d.polygon([(sc(bx), sc(y + 9)), (sc(bx + 20), sc(y + 9)), (sc(bx), sc(y + 30))],
                  fill=(96, 70, 44, 255), outline=(48, 36, 24, 200))
        d.ellipse(box(bx + 2, y + 2, bx + 5, y + 5), fill=BRASS_LIGHT)
    img = Image.alpha_composite(img, lay)
    img = hatch(img, [(x0, y + 10), (x1, y + 10), (x1, y + 30), (x0, y + 30)],
                angle=62, gap=3.0, color=(58, 44, 28, 46), width=1, seed=12)
    for i, (cx, wdt, hgt) in enumerate(((584, 50, 66), (652, 44, 58), (716, 52, 74),
                                        (788, 44, 60), (858, 50, 64))):
        img = jar(img, cx, y, wdt, hgt, label_text="ЕГЕРЬ" if i != 3 else None, seed=i)
    return img


# ---------------------------------------------------------------- desk

def draw_desk(img):
    y0 = 378
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle(box(0, y0, W, H), fill=(102, 71, 46, 255))
    d.line([0, sc(y0), sc(W), sc(y0)], fill=(214, 176, 124, 200), width=sc(2))
    d.line([0, sc(y0 + 2), sc(W), sc(y0 + 2)], fill=(60, 42, 26, 160), width=sc(1))
    # front edge of the top
    d.rectangle(box(0, 532, W, H), fill=(58, 39, 24, 255))
    d.line([0, sc(532), sc(W), sc(532)], fill=(178, 138, 92, 130), width=sc(1))
    d.line([0, sc(534), sc(W), sc(534)], fill=(26, 17, 10, 170), width=sc(2))
    img = Image.alpha_composite(img, lay)
    img = wood_grain(img, (0, 382, W, 530), seed=9, strength=1.15)

    # leather blotter with a tooled border
    img = soft_shadow(img, 494, 396, 908, 532, a=70, blur=5)
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box(496, 392, 904, 524), radius=sc(7), fill=(78, 34, 27, 255),
                        outline=(38, 22, 16, 230), width=sc(2))
    d.rounded_rectangle(box(500, 396, 900, 520), radius=sc(5), outline=(176, 138, 78, 90), width=sc(1))
    d.rounded_rectangle(box(504, 400, 896, 516), radius=sc(4), outline=(176, 138, 78, 46), width=sc(1))
    # corner caps
    for cx, cy in ((502, 398), (898, 398), (502, 518), (898, 518)):
        d.ellipse(box(cx - 5, cy - 5, cx + 5, cy + 5), fill=BRASS_DARK)
        d.ellipse(box(cx - 3.5, cy - 3.5, cx + 3.5, cy + 3.5), fill=BRASS)
    # wear and leather grain
    rnd = random.Random(17)
    for _ in range(160):
        x, y = rnd.uniform(502, 898), rnd.uniform(398, 518)
        a = rnd.randint(4, 16)
        d.line([sc(x), sc(y), sc(x + rnd.uniform(2, 9)), sc(y + rnd.uniform(-1, 1))],
               fill=(34 + rnd.randint(0, 20), 20, 14, a), width=1)
    for _ in range(90):
        x, y = rnd.uniform(502, 898), rnd.uniform(398, 518)
        d.point((sc(x), sc(y)), fill=(140, 86, 66, rnd.randint(8, 22)))
    img = Image.alpha_composite(img, lay)
    img = soft_glow(img, 540, 380, 880, 520, (255, 206, 150), a=16, blur=42)
    img = hatch(img, [(496, 392), (520, 392), (520, 524), (496, 524)],
                angle=78, gap=2.6, color=(30, 18, 12, 80), width=1, seed=41)
    img = hatch(img, [(884, 392), (904, 392), (904, 524), (884, 524)],
                angle=78, gap=2.8, color=(30, 18, 12, 45), width=1, seed=42)
    img = hatch(img, [(0, 534), (920, 534), (920, 560), (0, 560)],
                angle=72, gap=2.4, color=(20, 12, 8, 70), width=1, seed=43)
    return img


def draw_paper_strip(img):
    """Sheet under the footer links, so their dark ink stays readable."""
    lay = layer()
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 12, 504, 506, 558
    d.polygon([(sc(x0 + 6), sc(y0)), (sc(x1 - 2), sc(y0 + 2)), (sc(x1 - 4), sc(y1)),
               (sc(x0 + 1), sc(y1 - 3))], fill=(56, 42, 26, 60))
    d.polygon([(sc(x0 + 4), sc(y0 - 2)), (sc(x1 - 6), sc(y0)), (sc(x1 - 8), sc(y1 - 4)),
               (sc(x0 - 1), sc(y1 - 6))], fill=(236, 227, 207, 255))
    d.line([sc(x0 + 4), sc(y0 - 2), sc(x1 - 6), sc(y0)], fill=(252, 246, 228, 160), width=sc(1))
    # printed letterhead only in the top band, so the link row stays clear
    d.line([sc(x0 + 20), sc(y0 + 5), sc(x0 + 104), sc(y0 + 5)], fill=(64, 52, 38, 150), width=sc(2))
    f = font(MONO, 4.6)
    d.text((sc(x0 + 112), sc(y0 + 2)), "ФОРМА 4-Д", font=f, fill=(92, 78, 58, 130))
    # red registry number in the corner, above the version line
    f = font(MONO, 6)
    d.text((sc(x1 - 58), sc(y0 + 1)), "№ 1944", font=f, fill=(140, 44, 32, 160))
    d.line([sc(x1 - 58), sc(y0 + 10), sc(x1 - 18), sc(y0 + 10)], fill=(140, 44, 32, 70), width=1)
    # faint pencil date in the left margin
    d.line([sc(x0 + 8), sc(y0 + 22), sc(x0 + 8), sc(y0 + 40)], fill=(148, 46, 34, 80), width=1)
    # turned corner
    d.polygon([(sc(x1 - 26), sc(y1 - 4)), (sc(x1 - 8), sc(y1 - 4)), (sc(x1 - 8), sc(y1 - 16))],
              fill=(208, 197, 172, 255), outline=(120, 104, 76, 110))
    img = Image.alpha_composite(img, lay)
    return blotches(img, 30, seed=33)


# ---------------------------------------------------------------- desk objects

def draw_forms(img):
    x0, y0, x1 = 600, 526, 664
    img = soft_shadow(img, x0, y0 + 2, x1 + 6, y0 + 14, a=60, blur=3)
    lay = layer()
    d = ImageDraw.Draw(lay)
    for i in range(5):
        yy = y0 + i * 2.2
        d.polygon([(sc(x0 + i), sc(yy)), (sc(x1 - i * .7), sc(yy + 1)),
                   (sc(x1 - 2), sc(yy + 9)), (sc(x0 + 1), sc(yy + 8))],
                  fill=(234, 225, 204, 255), outline=(72, 58, 40, 170), width=sc(1))
    for i in range(3):
        d.line([sc(x0 + 9), sc(y0 + 12 + i * 2.6), sc(x1 - 12), sc(y0 + 13 + i * 2.6)],
               fill=(84, 70, 52, 80), width=1)
    img = Image.alpha_composite(img, lay)
    return img


def draw_ledger(img):
    x0, y0, x1, y1 = 508, 400, 602, 458
    img = soft_shadow(img, x0, y1 - 2, x1 + 10, y1 + 12, a=80, blur=3)
    lay = layer()
    d = ImageDraw.Draw(lay)
    # leather cover under the pages
    d.rectangle(box(x0 - 2, y0 + 3, x1 + 2, y1 + 2), fill=(78, 52, 34, 255),
                outline=(42, 30, 19, 235), width=sc(1.2))
    # pages
    d.polygon([(sc(x0 + 1), sc(y0 + 4)), (sc(x0 + 47), sc(y0)), (sc(x0 + 47), sc(y1 - 2)),
               (sc(x0 + 1), sc(y1))], fill=(234, 225, 203, 255))
    d.polygon([(sc(x0 + 49), sc(y0)), (sc(x0 + 95), sc(y0 + 4)), (sc(x0 + 95), sc(y1)),
               (sc(x0 + 49), sc(y1 - 2))], fill=(228, 219, 196, 255))
    # gutter
    d.polygon([(sc(x0 + 44), sc(y0 + 1)), (sc(x0 + 52), sc(y0 + 1)),
               (sc(x0 + 52), sc(y1 - 1)), (sc(x0 + 44), sc(y1 - 1))],
              fill=(186, 172, 144, 180))
    # ruled lines and a red margin
    for i in range(8):
        yy = y0 + 11 + i * 5.1
        d.line([sc(x0 + 8), sc(yy), sc(x0 + 44), sc(yy - 0.6)], fill=(96, 82, 62, 55), width=1)
        d.line([sc(x0 + 52), sc(yy + .8), sc(x0 + 90), sc(yy)], fill=(96, 82, 62, 55), width=1)
    d.line([sc(x0 + 13), sc(y0 + 6), sc(x0 + 12), sc(y1 - 5)], fill=(146, 52, 40, 70), width=sc(1))
    # hurried pencil notes
    rnd = random.Random(14)
    for i in range(14):
        px = rnd.uniform(x0 + 16, x0 + 40)
        py = rnd.uniform(y0 + 10, y1 - 8)
        d.line([sc(px), sc(py), sc(px + rnd.uniform(4, 14)), sc(py + rnd.uniform(-.7, .7))],
               fill=(58, 48, 36, 135), width=1)
    for i in range(9):
        px = rnd.uniform(x0 + 54, x0 + 86)
        py = rnd.uniform(y0 + 10, y1 - 8)
        d.line([sc(px), sc(py), sc(px + rnd.uniform(4, 11)), sc(py + rnd.uniform(-.6, .6))],
               fill=(58, 48, 36, 120), width=1)
    # small approval stamp
    d.ellipse(box(x0 + 64, y0 + 26, x0 + 84, y0 + 40), outline=(148, 46, 34, 170), width=sc(1.2))
    d.polygon([(sc(x), sc(y)) for x, y in star(x0 + 74, y0 + 33, 5, 2)], fill=(148, 46, 34, 160))
    img = Image.alpha_composite(img, lay)
    return img


def draw_scale(img):
    cx, base = 704, 502
    img = soft_shadow(img, cx - 50, base - 10, cx + 58, base + 8, a=85, blur=3.5)
    lay = layer()
    d = ImageDraw.Draw(lay)
    # base
    d.ellipse(box(cx - 44, base - 16, cx + 44, base), fill=BRASS_DARK)
    d.ellipse(box(cx - 42, base - 14, cx + 42, base - 2), fill=BRASS)
    d.ellipse(box(cx - 29, base - 12, cx + 25, base - 4), fill=BRASS_LIGHT)
    d.arc(box(cx - 30, base - 12, cx + 26, base - 4), 200, 340, fill=(255, 238, 200, 140), width=sc(1))
    # column
    d.polygon([(sc(cx - 4), sc(base - 14)), (sc(cx + 4), sc(base - 14)),
               (sc(cx + 2.4), sc(base - 82)), (sc(cx - 2.4), sc(base - 82))], fill=BRASS)
    d.line([sc(cx - 1.6), sc(base - 16), sc(cx - 1.6), sc(base - 80)], fill=(245, 220, 174, 190), width=sc(1))
    d.line([sc(cx + 1.8), sc(base - 16), sc(cx + 1.8), sc(base - 80)], fill=(70, 52, 30, 120), width=sc(1))
    # beam
    by = base - 86
    d.polygon([(sc(cx - 48), sc(by + 4)), (sc(cx + 48), sc(by - 1)),
               (sc(cx + 48), sc(by + 2)), (sc(cx - 48), sc(by + 7))], fill=BRASS, outline=(66, 50, 30, 210))
    d.line([sc(cx - 46), sc(by + 4), sc(cx + 46), sc(by)], fill=(246, 220, 172, 190), width=sc(1))
    d.ellipse(box(cx - 3, by + 1, cx + 3, by + 6), fill=BRASS_LIGHT, outline=(60, 44, 26, 200))
    # pointer
    d.line([sc(cx), sc(by + 4), sc(cx), sc(by + 30)], fill=INK, width=sc(1))
    # chains and pans
    for px, py in ((cx - 48, by + 24), (cx + 48, by - 1)):
        for dx in (-11, 0, 11):
            d.line([sc(px), sc(py - 20), sc(px + dx), sc(py + 2)], fill=(90, 70, 40, 220), width=1)
        d.ellipse(box(px - 16, py - 1, px + 16, py + 7), fill=BRASS, outline=(62, 46, 28, 220))
        d.arc(box(px - 16, py - 2, px + 16, py + 8), 0, 180, fill=(62, 46, 28, 230), width=sc(1))
        d.ellipse(box(px - 14, py, px + 14, py + 5), fill=BRASS_LIGHT)
    # a sample jar on the left pan
    jx, jb = cx - 48, by + 22
    d.ellipse(box(jx - 12, jb - 3, jx + 12, jb + 2), fill=(214, 206, 186, 255), outline=(56, 46, 32, 220))
    d.rectangle(box(jx - 10, jb - 22, jx + 10, jb - 2), fill=(216, 209, 189, 230), outline=(56, 46, 32, 235), width=sc(1))
    d.rectangle(box(jx - 9, jb - 15, jx + 9, jb - 3), fill=(232, 216, 178, 255))
    d.rectangle(box(jx - 8, jb - 18, jx + 8, jb - 15), fill=(238, 229, 208, 255), outline=(140, 48, 36, 160))
    d.line([sc(jx - 7), sc(jb - 21), sc(jx - 7), sc(jb - 4)], fill=(255, 252, 238, 150), width=1)
    d.rectangle(box(jx - 10, jb - 24, jx + 10, jb - 20), fill=BRASS, outline=(48, 38, 26, 220))
    # weights on the right pan
    for wx, wy, wd, wh in ((cx + 48 - 12, by + 12, 13, 9), (cx + 48 + 2, by + 13, 9, 7)):
        d.rectangle(box(wx, wy, wx + wd, wy + wh), fill=(78, 76, 68, 255), outline=(36, 33, 28, 235))
        d.line([sc(wx + 1), sc(wy + 1), sc(wx + wd - 1), sc(wy + 1)], fill=(168, 162, 146, 200), width=1)
    img = Image.alpha_composite(img, lay)
    return img


def draw_tray(img):
    x0, y0, x1, y1 = 752, 476, 842, 506
    img = soft_shadow(img, x0 + 2, y1 - 2, x1 + 8, y1 + 10, a=70, blur=3)
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box(x0, y0, x1, y1), radius=sc(4), fill=(104, 71, 45, 255),
                        outline=(48, 34, 22, 230), width=sc(1.4))
    d.rounded_rectangle(box(x0 + 3, y0 + 3, x1 - 3, y1 - 3), radius=sc(3), outline=(176, 138, 78, 120), width=sc(1))
    # three tasting glasses with a sample
    for gx in (x0 + 16, x0 + 45, x0 + 74):
        gb = y1 - 8
        d.ellipse(box(gx - 11, gb - 3, gx + 11, gb + 3), fill=(74, 52, 34, 80))
        d.polygon([(sc(gx - 9), sc(gb - 18)), (sc(gx + 9), sc(gb - 18)),
                   (sc(gx + 7), sc(gb - 2)), (sc(gx - 7), sc(gb - 2))],
                  fill=(198, 204, 196, 150), outline=(52, 42, 30, 240), width=sc(1.2))
        d.polygon([(sc(gx - 8), sc(gb - 12)), (sc(gx + 8), sc(gb - 12)),
                   (sc(gx + 7), sc(gb - 3)), (sc(gx - 7), sc(gb - 3))], fill=(236, 221, 184, 255))
        d.line([sc(gx - 8), sc(gb - 13), sc(gx + 8), sc(gb - 13)], fill=(252, 244, 214, 235), width=sc(1.2))
        d.ellipse(box(gx - 9.5, gb - 20, gx + 9.5, gb - 15), fill=(206, 210, 200, 90),
                  outline=(52, 42, 30, 240), width=sc(1.2))
        d.ellipse(box(gx - 8, gb - 19, gx + 8, gb - 16), outline=(250, 246, 228, 120), width=1)
        d.line([sc(gx - 5), sc(gb - 19), sc(gx - 6), sc(gb - 4)], fill=(255, 252, 238, 190), width=sc(1.2))
    # sample spoon resting on the tray
    d.line([sc(x1 - 14), sc(y1 - 6), sc(x1 - 4), sc(y0 + 4)], fill=(126, 122, 108, 240), width=sc(1.6))
    d.ellipse(box(x1 - 18, y1 - 9, x1 - 10, y1 - 4), fill=(178, 176, 162, 255), outline=(70, 58, 42, 200))
    img = Image.alpha_composite(img, lay)
    return img


def draw_desk_jar(img):
    cx, base = 868, 522
    wdt, hgt = 72, 124
    img = jar(img, cx, base, wdt, hgt, label_text=None)
    lay = layer()
    d = ImageDraw.Draw(lay)
    f = font(RUSSO, 10)
    d.text((sc(cx), sc(base - 66)), "ЕГЕРЬ", font=f, fill=(88, 38, 30, 240), anchor="mm")
    f2 = font(MONO, 5.2)
    d.text((sc(cx), sc(base - 55)), "МАЙОНЕЗ", font=f2, fill=(60, 48, 36, 225), anchor="mm")
    d.line([sc(cx - 26), sc(base - 50), sc(cx + 26), sc(base - 50)], fill=(140, 50, 38, 150), width=1)
    f3 = font(MONO, 4.2)
    d.text((sc(cx), sc(base - 43)), "1939 · ОТК", font=f3, fill=(70, 56, 40, 190), anchor="mm")
    img = Image.alpha_composite(img, lay)
    return img


def draw_stamp(img):
    cx, base = 646, 546
    img = soft_shadow(img, cx - 22, base - 6, cx + 26, base + 6, a=80, blur=3)
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle(box(cx - 20, base - 16, cx + 20, base - 8), fill=BRASS_DARK)
    d.rectangle(box(cx - 20, base - 17, cx + 20, base - 13), fill=BRASS)
    d.rectangle(box(cx - 4, base - 32, cx + 4, base - 16), fill=(96, 66, 40, 255))
    d.ellipse(box(cx - 12, base - 44, cx + 12, base - 28), fill=(118, 80, 46, 255))
    d.ellipse(box(cx - 8, base - 41, cx + 6, base - 31), fill=(152, 108, 64, 255))
    d.line([sc(cx - 6), sc(base - 38), sc(cx + 2), sc(base - 33)], fill=(188, 144, 96, 120), width=sc(1))
    # ink pad
    d.rounded_rectangle(box(676, 530, 712, 552), radius=sc(2), fill=(48, 38, 26, 255),
                        outline=(30, 24, 18, 230))
    d.rectangle(box(680, 533, 708, 549), fill=(122, 38, 30, 235))
    d.line([sc(682), sc(536), sc(700), sc(536)], fill=(166, 66, 54, 110), width=1)
    img = Image.alpha_composite(img, lay)
    return img


def draw_inkwell(img):
    x0, y0 = 614, 406
    img = soft_shadow(img, x0 - 2, y0 + 6, x0 + 34, y0 + 32, a=70, blur=3)
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle(box(x0, y0, x0 + 24, y0 + 22), fill=(74, 64, 50, 255), outline=(38, 30, 22, 230))
    d.rectangle(box(x0 + 2, y0 + 2, x0 + 22, y0 + 20), fill=(30, 28, 24, 255))
    d.polygon([(sc(x0 + 2), sc(y0 + 2)), (sc(x0 + 8), sc(y0 + 2)),
               (sc(x0 + 5), sc(y0 + 20)), (sc(x0 + 2), sc(y0 + 20))], fill=(120, 116, 100, 90))
    d.line([sc(x0 + 16), sc(y0 + 4), sc(x0 + 34), sc(y0 + 34)], fill=(58, 44, 30, 255), width=sc(2))
    d.polygon([(sc(x0 + 32), sc(y0 + 31)), (sc(x0 + 36), sc(y0 + 36)), (sc(x0 + 33), sc(y0 + 37))],
              fill=(164, 150, 126, 255))
    img = Image.alpha_composite(img, lay)
    return img


def draw_magnifier(img):
    cx, cy, r = 804, 534, 18
    img = soft_shadow(img, cx - r, cy - r + 4, cx + r + 14, cy + r + 12, a=70, blur=4)
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=(208, 216, 210, 90), outline=BRASS, width=sc(3.4))
    d.ellipse(box(cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), outline=(242, 234, 214, 70), width=sc(1))
    d.polygon([(sc(cx - 12), sc(cy - 10)), (sc(cx - 6), sc(cy - 12)), (sc(cx + 8), sc(cy + 10)),
               (sc(cx + 3), sc(cy + 12))], fill=(255, 255, 250, 26))
    d.line([sc(cx + 13), sc(cy + 13), sc(cx + 29), sc(cy + 31)], fill=(74, 50, 30, 255), width=sc(4.4))
    d.line([sc(cx + 13), sc(cy + 13), sc(cx + 29), sc(cy + 31)], fill=(150, 108, 66, 255), width=sc(2.2))
    img = Image.alpha_composite(img, lay)
    return img


def draw_pencil(img):
    pts = [(700, 550), (752, 543), (753, 547), (701, 554)]
    img = soft_shadow(img, 704, 548, 758, 560, a=50, blur=2)
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.polygon([(sc(x), sc(y)) for x, y in pts], fill=(138, 44, 32, 255), outline=(66, 28, 20, 220))
    d.line([sc(700), sc(550.5), sc(752), sc(543.5)], fill=(196, 92, 74, 140), width=1)
    d.polygon([(sc(752), sc(543)), (sc(762), sc(541.5)), (sc(753), sc(547))], fill=(218, 202, 172, 255))
    d.polygon([(sc(762), sc(541.5)), (sc(765), sc(543)), (sc(753), sc(547))], fill=(90, 70, 50, 255))
    img = Image.alpha_composite(img, lay)
    return img


def draw_objects(img):
    img = draw_forms(img)
    img = draw_ledger(img)
    img = draw_inkwell(img)
    img = draw_scale(img)
    img = draw_tray(img)
    img = draw_desk_jar(img)
    img = draw_stamp(img)
    img = draw_magnifier(img)
    img = draw_pencil(img)
    return img


# ---------------------------------------------------------------- finish

def finish(img):
    # cool spill from the window onto the right-hand desk
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.polygon([(sc(560), sc(252)), (sc(884), sc(252)), (sc(920), sc(560)), (sc(520), sc(560))],
              fill=(150, 172, 196, 10))
    d.polygon([(sc(620), sc(252)), (sc(820), sc(252)), (sc(880), sc(560)), (sc(650), sc(560))],
              fill=(160, 180, 200, 8))
    img = Image.alpha_composite(img.convert("RGBA"), lay)
    # vignette
    y, x = np.ogrid[0:H * S, 0:W * S]
    dx = (x - sc(W * .42)) / sc(W * .62)
    dy = (y - sc(H * .5)) / sc(H * .62)
    d = np.sqrt(dx * dx + dy * dy)
    a = np.clip((d - .50) / .72, 0, 1) ** 1.25 * 88
    vg = np.zeros((H * S, W * S, 4), dtype=np.uint8)
    vg[:, :, 0], vg[:, :, 1], vg[:, :, 2] = 32, 24, 16
    vg[:, :, 3] = a.astype(np.uint8)
    img = Image.alpha_composite(img.convert("RGBA"), Image.fromarray(vg, "RGBA"))
    # overall grain and a faint warm wash
    img = grain(img, 2.8)
    wash = np.zeros((H * S, W * S, 4), dtype=np.uint8)
    wash[:, :, 0], wash[:, :, 1], wash[:, :, 2] = 246, 226, 184
    wash[:, :, 3] = 10
    img = Image.alpha_composite(img, Image.fromarray(wash, "RGBA"))
    return img


def main():
    os.makedirs(ROOT / "theme", exist_ok=True)
    img = Image.new("RGBA", (W * S, H * S), PAPER + (255,))
    img = draw_wall(img)
    img = draw_window(img)
    img = draw_certificate(img)
    img = draw_shelf(img)
    img = draw_desk(img)
    img = draw_paper_strip(img)
    img = draw_objects(img)
    img = draw_lamp(img)
    img = finish(img)
    img.convert("RGB").save(OUT, optimize=True)
    (ROOT / "theme" / "scene_small.png").write_bytes(b"")
    img.convert("RGB").resize((W, H), Image.LANCZOS).save(ROOT / "theme" / "scene_small.png", optimize=True)
    print("wrote", OUT, img.size)
    print("wrote", ROOT / "theme" / "scene_small.png")


if __name__ == "__main__":
    main()
