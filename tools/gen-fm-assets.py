"""Generates the FancyMenu texture set for the "Eger 1939" theme.

Run:  python tools/gen-fm-assets.py
Writes into src/main/resources/config/fancymenu/assets/.

Only needs Pillow. paper.png is the source texture and is left untouched.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "assets")

INK = (28, 27, 24)
BRASS = (160, 124, 60)
BRASS_LIGHT = (201, 167, 91)
SEAL = (142, 43, 34)


def load_paper():
    return Image.open(os.path.join(ASSETS, "paper.png")).convert("RGB")


def font(name, size):
    for candidate in (name, "georgia.ttf", "times.ttf", "arial.ttf"):
        path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", candidate)
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def paper_variant(src, tint, out_name):
    """Multiplies the paper by a tint so dark screens keep the paper fibre."""
    img = src.copy()
    px = img.load()
    w, h = img.size
    rnd = random.Random(1939)
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            n = rnd.randint(-4, 4)
            px[x, y] = (
                max(0, min(255, int(r * tint[0]) + n)),
                max(0, min(255, int(g * tint[1]) + n)),
                max(0, min(255, int(b * tint[2]) + n)),
            )
    img.save(os.path.join(ASSETS, out_name))
    print("wrote", out_name, img.size)


def brass_strip(src):
    """Thin brass band with rivets, tiles horizontally."""
    w, h = 512, 48
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = abs(y - h / 2) / (h / 2)
        shade = 1.0 - 0.45 * t
        d.line([(0, y), (w, y)], fill=(
            int(BRASS[0] * shade), int(BRASS[1] * shade), int(BRASS[2] * shade), 235))
    d.line([(0, 0), (w, 0)], fill=(BRASS_LIGHT + (200,)))
    d.line([(0, h - 1), (w, h - 1)], fill=(INK + (190,)))
    for x in range(32, w, 64):
        d.ellipse([x - 3, h // 2 - 3, x + 3, h // 2 + 3], fill=BRASS_LIGHT + (235,),
                  outline=INK + (170,))
    img.save(os.path.join(ASSETS, "brass_strip.png"))
    print("wrote brass_strip.png", img.size)


def seal(src):
    """Round ink stamp: outer ring, ЕГЕРЬ, 1939, ОТК."""
    size = 320
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 14
    d.ellipse([pad, pad, size - pad, size - pad], outline=SEAL + (210,), width=6)
    d.ellipse([pad + 14, pad + 14, size - pad - 14, size - pad - 14], outline=SEAL + (150,), width=2)
    f_big = font("constan.ttf", 56)
    f_mid = font("constan.ttf", 34)
    f_small = font("constan.ttf", 26)
    for text, f, y, alpha in (("ЕГЕРЬ", f_big, 78, 225), ("1939", f_mid, 152, 215), ("ОТК", f_small, 208, 190)):
        tw = d.textlength(text, font=f)
        d.text(((size - tw) / 2, y), text, font=f, fill=SEAL + (alpha,))
    d.line([(96, 146), (224, 146)], fill=SEAL + (170,), width=2)
    img = img.rotate(-9, resample=Image.BICUBIC, expand=False)
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(os.path.join(ASSETS, "stamp_eger.png"))
    print("wrote stamp_eger.png", img.size)


def main():
    paper = load_paper()
    paper_variant(paper, (0.40, 0.38, 0.34), "paper_dark.png")
    brass_strip(paper)
    seal(paper)


if __name__ == "__main__":
    main()
