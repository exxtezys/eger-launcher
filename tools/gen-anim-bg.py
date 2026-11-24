#!/usr/bin/env python3
"""Generate an animated FancyMenu background GIF for the Егерь 1939 theme."""
import os, random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "theme", "scene.png")
OUT = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "assets", "anim_bg.gif")

random.seed(42)
base = Image.open(SCENE).convert("RGBA")
W, H = base.size
# dust motes
motes = []
for i in range(60):
    motes.append({
        "x": random.uniform(0, W),
        "y": random.uniform(0, H),
        "vx": random.uniform(-0.6, 0.6),
        "vy": random.uniform(-0.3, 0.3),
        "r": random.uniform(1, 3),
        "a": random.randint(40, 120),
    })

frames = []
N = 24
for f in range(N):
    img = base.copy()
    draw = ImageDraw.Draw(img, "RGBA")
    # draw motes
    for m in motes:
        m["x"] = (m["x"] + m["vx"]) % W
        m["y"] = (m["y"] + m["vy"]) % H
        x, y = m["x"], m["y"]
        r = m["r"]
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(245, 232, 198, m["a"]))
    # airship
    ax = (f / N) * W * 0.8 + 100
    ay = 80 + (f % 6) * 2
    # simple airship shape
    draw.ellipse((ax, ay, ax+120, ay+30), fill=(60,40,30,200))
    draw.rectangle((ax+40, ay+25, ax+80, ay+45), fill=(40,25,15,200))
    frames.append(img.convert("P", palette=Image.ADAPTIVE, colors=128))

# save gif
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
print("wrote", OUT, "frames", len(frames))