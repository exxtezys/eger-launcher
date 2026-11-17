# -*- coding: utf-8 -*-
"""Build the "eger-pda" resource pack (PDA green monochrome theme).

The pack overrides only vanilla GUI assets:

* title/minecraft.png, title/minceraft.png, title/edition.png -> transparent
  (removes the big Minecraft logo from the title screen)
* texts/splashes.txt -> single blank splash (no yellow splash text)
* gui/sprites/widget/button*.png, slider*.png, text_field*.png -> PDA palette

Output: src/main/resources/config/resourcepacks/eger-pda.zip

Run: python tools/gen-pda-resources.py
"""
import json
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "main" / "resources" / "config" / "resourcepacks" / "eger-pda.zip"

# PDA palette
EDGE = (96, 192, 96)
EDGE_HI = (140, 255, 140)
EDGE_DIM = (46, 90, 46)
GAP = (6, 16, 6)
INNER = (26, 58, 26)
FILL_TOP = (16, 48, 24)
FILL_BOTTOM = (8, 26, 12)
HANDLE_FILL = (20, 48, 26)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _blank(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def make_button():
    """200x20 nine-slice button (border 3)."""
    img = Image.new("RGBA", (200, 20), (0, 0, 0, 0))
    px = img.load()
    for y in range(20):
        t = y / 19.0
        px_col = _mix(FILL_TOP, FILL_BOTTOM, t)
        for x in range(200):
            px[x, y] = px_col + (255,)
    # scanlines
    for y in range(3, 17, 2):
        for x in range(3, 197):
            r, g, b, a = px[x, y]
            px[x, y] = (min(r + 6, 255), min(g + 8, 255), min(b + 6, 255), a)
    # 3px frame
    for i in range(200):
        px[i, 0] = EDGE + (255,)
        px[i, 19] = EDGE + (255,)
        px[i, 1] = GAP + (255,)
        px[i, 18] = GAP + (255,)
        px[i, 2] = INNER + (255,)
        px[i, 17] = INNER + (255,)
    for i in range(20):
        px[0, i] = EDGE + (255,)
        px[199, i] = EDGE + (255,)
        px[1, i] = GAP + (255,)
        px[198, i] = GAP + (255,)
        px[2, i] = INNER + (255,)
        px[197, i] = INNER + (255,)
    for cx, cy in ((0, 0), (199, 0), (0, 19), (199, 19)):
        px[cx, cy] = EDGE_HI + (255,)
    return img


def make_button_highlighted():
    img = make_button()
    px = img.load()
    for x in range(200):
        px[x, 0] = EDGE_HI + (255,)
        px[x, 19] = EDGE_HI + (255,)
    for y in range(20):
        px[0, y] = EDGE_HI + (255,)
        px[199, y] = EDGE_HI + (255,)
    return img


def make_button_disabled():
    img = make_button()
    px = img.load()
    for x in range(200):
        for y in (0, 19):
            px[x, y] = EDGE_DIM + (255,)
    for y in range(20):
        for x in (0, 199):
            px[x, y] = EDGE_DIM + (255,)
    return img


def make_slider():
    """200x20 nine-slice slider track (border 1)."""
    img = Image.new("RGBA", (200, 20), (0, 0, 0, 0))
    px = img.load()
    for y in range(20):
        t = y / 19.0
        col = _mix((12, 30, 14), (7, 20, 8), t)
        for x in range(200):
            px[x, y] = col + (255,)
    for x in range(200):
        px[x, 0] = (42, 90, 42, 255)
        px[x, 19] = (42, 90, 42, 255)
        px[x, 18] = (24, 54, 24, 255)
    for y in range(20):
        px[0, y] = (42, 90, 42, 255)
        px[199, y] = (42, 90, 42, 255)
    return img


def make_slider_handle():
    """8x20 nine-slice handle (border l2 t2 r2 b3)."""
    img = Image.new("RGBA", (8, 20), HANDLE_FILL + (255,))
    px = img.load()
    for y in range(20):
        px[0, y] = EDGE + (255,)
        px[7, y] = EDGE + (255,)
    for x in range(8):
        px[x, 0] = EDGE + (255,)
        px[x, 19] = EDGE + (255,)
        px[x, 17] = (28, 62, 28, 255)
    return img


def make_text_field():
    """200x20 nine-slice text field (border 1)."""
    img = Image.new("RGBA", (200, 20), (6, 16, 8, 255))
    px = img.load()
    for x in range(200):
        px[x, 0] = (42, 90, 42, 255)
        px[x, 19] = (42, 90, 42, 255)
    for y in range(20):
        px[0, y] = (42, 90, 42, 255)
        px[199, y] = (42, 90, 42, 255)
    return img


FILES = {
    "assets/minecraft/textures/gui/title/minecraft.png": lambda: _blank((1024, 256)),
    "assets/minecraft/textures/gui/title/minceraft.png": lambda: _blank((1024, 256)),
    "assets/minecraft/textures/gui/title/edition.png": lambda: _blank((512, 64)),
    "assets/minecraft/textures/gui/sprites/widget/button.png": make_button,
    "assets/minecraft/textures/gui/sprites/widget/button_highlighted.png": make_button_highlighted,
    "assets/minecraft/textures/gui/sprites/widget/button_disabled.png": make_button_disabled,
    "assets/minecraft/textures/gui/sprites/widget/slider.png": make_slider,
    "assets/minecraft/textures/gui/sprites/widget/slider_highlighted.png": make_slider,
    "assets/minecraft/textures/gui/sprites/widget/slider_handle.png": make_slider_handle,
    "assets/minecraft/textures/gui/sprites/widget/slider_handle_highlighted.png": make_slider_handle,
    "assets/minecraft/textures/gui/sprites/widget/text_field.png": make_text_field,
    "assets/minecraft/textures/gui/sprites/widget/text_field_highlighted.png": make_text_field,
}

PACK_META = {
    "pack": {
        "pack_format": 34,
        "description": "Eger PDA - S.T.A.L.K.E.R. green monochrome UI",
    }
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(PACK_META, indent=2))
        z.writestr("assets/minecraft/texts/splashes.txt", " \n")
        for path, factory in FILES.items():
            buf = __import__("io").BytesIO()
            factory().save(buf, format="PNG", optimize=True)
            z.writestr(path, buf.getvalue())
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
