# -*- coding: utf-8 -*-
"""Generate the PDA wordmark used as the launcher logo.

Draws "S.T.A.L.K.E.R." + a PDA subtitle in the shipped fonts on a
transparent canvas, framed with thin brackets in the PDA green palette.

Run:    python tools/gen-pda-logo.py
Output: theme/pda_logo.png (+ copy into the jar resources)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "theme" / "fonts"
OUTS = [
    ROOT / "theme" / "pda_logo.png",
    ROOT / "src" / "main" / "resources" / "config" / "fancymenu" / "assets" / "pda_logo.png",
]

W, H = 720, 160
BRIGHT = (124, 255, 124, 255)
ACCENT = (96, 192, 96, 255)
MUTED = (80, 160, 80, 255)
SHADOW = (10, 40, 14, 170)


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    big = ImageFont.truetype(str(FONTS / "RussoOne-Regular.ttf"), 74)
    small = ImageFont.truetype(str(FONTS / "PTMono-Regular.ttf"), 23)

    x = 26
    y = 14
    # soft shadow, then the bright wordmark
    d.text((x + 2, y + 2), "S.T.A.L.K.E.R.", font=big, fill=SHADOW)
    d.text((x, y), "S.T.A.L.K.E.R.", font=big, fill=BRIGHT)

    rule_y = y + 88
    d.line([(x, rule_y), (x + 420, rule_y)], fill=ACCENT, width=1)
    d.text((x, rule_y + 9), "ПДА · ЗОНА ЧЕРНОБЫЛИ", font=small, fill=MUTED)

    # left bracket
    d.line([(8, 8), (8, H - 9)], fill=ACCENT, width=2)
    d.line([(8, 8), (20, 8)], fill=ACCENT, width=2)
    d.line([(8, H - 9), (20, H - 9)], fill=ACCENT, width=2)

    # small "signal" staircase on the right, PDA style
    for i in range(5):
        h = 8 + i * 6
        x0 = W - 78 + i * 11
        d.rectangle([x0, H - 14 - h, x0 + 8, H - 14], fill=ACCENT)
    d.line([(W - 80, H - 15), (W - 12, H - 15)], fill=MUTED, width=1)

    for out in OUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, format="PNG", optimize=True)
        print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
