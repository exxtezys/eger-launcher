#!/usr/bin/env python3
"""Generate FancyMenu assets for Eger 1939 - paper, buttons, brass, stamp, bg."""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "assets")
THEME = os.path.join(ROOT, "theme", "scene.png")
os.makedirs(ASSETS, exist_ok=True)

random.seed(1939)

def hex_rgba(h, a=255):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4)) + (a,)

CREAM = hex_rgba("#F5E8C6")
CREAM_D = hex_rgba("#E8D7AE")
PAPER = hex_rgba("#EFE0C0")
INK = hex_rgba("#211812")
ACCENT = hex_rgba("#8B2E22")
ACCENT_H = hex_rgba("#A63B2C")
BRASS = hex_rgba("#C9A96E")
BRASS_D = hex_rgba("#8A7248")
MUTED = hex_rgba("#A88866")
DARK = hex_rgba("#2A2018")

def noise(img, amt=12, alpha=False):
    px = img.load()
    w,h = img.size
    for y in range(h):
        for x in range(w):
            p = px[x,y]
            n = random.randint(-amt, amt)
            if alpha:
                px[x,y] = (max(0,min(255,p[0]+n)), max(0,min(255,p[1]+n)), max(0,min(255,p[2]+n)), p[3])
            else:
                px[x,y] = (max(0,min(255,p[0]+n)), max(0,min(255,p[1]+n)), max(0,min(255,p[2]+n)))
    return img

def paper_texture(w,h,base_col=PAPER, edge_dark=True):
    img = Image.new("RGBA",(w,h), base_col)
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(0,h,4):
        a = random.randint(4,12)
        draw.line((0,i,w,i), fill=(180,160,130,a))
    for i in range(0,w,6):
        a = random.randint(2,8)
        draw.line((i,0,i,h), fill=(180,160,130,a))
    for _ in range(max(3,(w*h)//40000)):
        cx,cy = random.randint(0,w), random.randint(0,h)
        r = random.randint(20,60)
        for rr in range(r,0,-2):
            a = int(18*(1-rr/r))
            draw.ellipse((cx-rr,cy-rr,cx+rr,cy+rr), fill=(160,130,90,a))
    img = noise(img, 8, alpha=True)
    if edge_dark:
        v = Image.new("RGBA",(w,h),(0,0,0,0))
        vd = ImageDraw.Draw(v)
        for i in range(30):
            a = int(40*(1-i/30))
            vd.rectangle((i,i,w-i,h-i), outline=(80,60,40,a))
        img = Image.alpha_composite(img, v)
    return img

def make_button(w,h,normal=True):
    bg = ACCENT if normal else ACCENT_H
    img = Image.new("RGBA",(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(img,"RGBA")
    draw.rectangle((0,0,w-1,h-1), fill=bg)
    border = BRASS if normal else hex_rgba("#E0C080")
    draw.rectangle((0,0,w-1,h-1), outline=border)
    draw.rectangle((1,1,w-2,h-2), outline=(border[0],border[1],border[2],120))
    draw.line((2,2,w-3,2), fill=(255,230,180,50))
    draw.line((2,h-3,w-3,h-3), fill=(0,0,0,40))
    img = noise(img, 6, alpha=True)
    return img

def make_brass_strip(w,h):
    img = Image.new("RGBA",(w,h),(0,0,0,0))
    draw = ImageDraw.Draw(img,"RGBA")
    for x in range(w):
        t = x/max(1,w-1)
        g = int(160 + 60*math.sin(t*math.pi))
        r = min(255,int(g*1.05))
        g2 = min(255,int(g*0.88))
        b = min(255,int(g*0.55))
        draw.line((x,0,x,h), fill=(r,g2,b,255))
    draw.line((0,0,w,0), fill=(255,235,190,200))
    draw.line((0,h-1,w,h-1), fill=(60,40,20,180))
    for rx in range(12, w-12, max(40,w//8)):
        draw.ellipse((rx-3,h//2-3,rx+3,h//2+3), fill=(90,70,40,220))
        draw.ellipse((rx-2,h//2-2,rx+2,h//2+2), fill=(200,170,110,220))
    return noise(img,5,alpha=True)

def make_stamp(size=128):
    img = Image.new("RGBA",(size,size),(0,0,0,0))
    draw = ImageDraw.Draw(img,"RGBA")
    cx,cy = size//2, size//2
    r = size//2 - 6
    for i in range(4):
        draw.ellipse((cx-r+i,cy-r+i,cx+r-i,cy+r-i), outline=(139,46,34,200-i*30))
    r2 = r-10
    draw.ellipse((cx-r2,cy-r2,cx+r2,cy+r2), outline=(139,46,34,140))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 16)
        font2 = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 10)
    except:
        font = ImageFont.load_default(); font2=font
    draw.text((cx,cy-8), "ЕГЕРЬ", fill=(139,46,34,210), font=font, anchor="mm")
    draw.text((cx,cy+12), "1939", fill=(139,46,34,170), font=font2, anchor="mm")
    for _ in range(200):
        x,y=random.randint(0,size-1),random.randint(0,size-1)
        if img.getpixel((x,y))[3]>0:
            img.putpixel((x,y),(0,0,0,0))
    return img.rotate(-12, expand=False, resample=Image.BICUBIC)

def make_bg():
    base = Image.open(THEME).convert("RGBA")
    W,H = base.size
    TW,TH = 640, int(640*H/W)
    base = base.resize((TW,TH), Image.LANCZOS)
    base = ImageEnhance.Brightness(base).enhance(0.70)
    base = ImageEnhance.Contrast(base).enhance(1.06)
    tint = Image.new("RGBA",(TW,TH),(30,20,10,28))
    base = Image.alpha_composite(base, tint)
    vig = Image.new("RGBA",(TW,TH),(0,0,0,0))
    vd = ImageDraw.Draw(vig)
    for i in range(80):
        a = int(130*(1-i/80)**1.5)
        vd.rectangle((i,i,TW-i,TH-i), outline=(10,8,5,a))
    base = Image.alpha_composite(base, vig)

    motes=[]
    for _ in range(28):
        motes.append([random.uniform(0,TW), random.uniform(0,TH), random.uniform(-0.35,0.35), random.uniform(-0.12,0.12), random.uniform(1.0,2.2), random.randint(25,75)])

    frames=[]
    N=20
    for f in range(N):
        img = base.copy()
        d = ImageDraw.Draw(img,"RGBA")
        flick = 0.5 + 0.5*math.sin(f*0.8) * 0.3 + 0.2*math.sin(f*2.1)
        glow_a = int(20 + 16*flick)
        gx,gy = TW-210, 42
        for r in range(80,0,-10):
            a = int(glow_a*(1-r/80))
            d.ellipse((gx-r, gy-r, gx+r, gy+r), fill=(255,210,140,a))
        t = f/N
        ax = int(-120 + t*(TW+240))
        ay = int(38 + 6*math.sin(t*math.pi*2))
        d.ellipse((ax,ay,ax+100,ay+28), fill=(55,38,28,210), outline=(80,60,40,180))
        d.ellipse((ax+8,ay+4,ax+92,ay+22), fill=(70,50,35,70))
        d.rounded_rectangle((ax+36,ay+23,ax+64,ay+36), radius=2, fill=(40,28,18,220), outline=(90,70,45,160))
        d.polygon([(ax-4,ay+14),(ax+10,ay+6),(ax+10,ay+22)], fill=(55,38,28,200))
        for wx in range(ax+22, ax+78, 14):
            la = int(130+50*math.sin(f*0.6+wx))
            d.rectangle((wx,ay+11,wx+3,ay+16), fill=(255,220,150,la))
        for m in motes:
            m[0]=(m[0]+m[2])%TW
            m[1]=(m[1]+m[3])%TH
            rr=m[4]
            d.ellipse((m[0]-rr,m[1]-rr,m[0]+rr,m[1]+rr), fill=(245,232,198,m[5]))
        frames.append(img.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=96))

    out = os.path.join(ASSETS,"anim_bg.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)
    print("bg", out, os.path.getsize(out))

if __name__ == "__main__":
    paper_texture(512,512).save(os.path.join(ASSETS,"paper.png"))
    paper_texture(512,512,base_col=hex_rgba("#E6D5B0")).save(os.path.join(ASSETS,"paper_dark.png"))
    make_button(200,40,True).save(os.path.join(ASSETS,"btn_normal.png"))
    make_button(200,40,False).save(os.path.join(ASSETS,"btn_hover.png"))
    make_brass_strip(512,24).save(os.path.join(ASSETS,"brass_strip.png"))
    make_stamp(128).save(os.path.join(ASSETS,"stamp_eger.png"))
    make_bg()
    print("assets done")
