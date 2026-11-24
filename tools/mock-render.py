#!/usr/bin/env python3
import sys, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "theme", "scene.png")

# palette index
idx = int(sys.argv[1]) if len(sys.argv)>1 else 0
palettes = [
    ("cream_oxblood", (245,232,198),(217,196,149),(139,46,34),(166,59,44),(168,136,102),(201,169,110),(107,66,34),(26,20,16)),
]
# reuse from gen-variants by import
import importlib.util
spec = importlib.util.spec_from_file_location("gv", os.path.join(ROOT,"tools","gen-variants.py"))
gv = importlib.util.module_from_spec(spec); spec.loader.exec_module(gv)

pal = gv.PALETTES[idx]
name, cream, shade, accent, hover, muted, highlight, ruler, vignette = pal
def hx(s): return tuple(int(s.lstrip('#')[i:i+2],16) for i in (0,2,4))

base = Image.open(SCENE).convert("RGB").resize((1280,720))
draw = ImageDraw.Draw(base)
try: font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
except: font = ImageFont.load_default()
# panel
draw.rectangle((40,80,460,600), fill=hx(cream))
draw.rectangle((480,80,900,600), fill=hx(shade))
# title
draw.text((60,90), "ЕГЕРЬ", fill=hx(accent), font=font)
draw.text((56,94), "ЕГЕРЬ", fill=hx(highlight), font=font)
draw.rectangle((60,152,180,155), fill=hx(accent))
draw.rectangle((60,157,150,159), fill=hx(highlight))
draw.text((60,167), "НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939", fill=hx(muted), font=font)
draw.text((60,202), "ДОСТУПНЫЕ РЕЖИМЫ", fill=hx(accent), font=font)
draw.text((60,226), "ОБЪЯВЛЕНИЕ ОТДЕЛА МАЙОНЕЗА", fill=hx(muted), font=font)
# buttons right bottom
for i,label in enumerate(["Играть","Сервер","Настройки","Выйти"]):
    x,y=520,420+i*52
    draw.rectangle((x,y,x+200,y+42), fill=hx(accent), outline=hx(ruler))
    draw.text((x+10,y+10), label, fill=(255,255,255), font=font)
# footer
draw.text((560,700), "© 1944 Опытная дегустационная станция", fill=hx(muted), font=font)
out = os.path.join(ROOT, "variants", "v%d" % (idx+1), "mock.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
base.save(out)
print(out)