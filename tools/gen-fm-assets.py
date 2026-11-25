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
    N=24
    for f in range(N):
        img = base.copy()
        d = ImageDraw.Draw(img,"RGBA")
        # --- distant government building (right side, through window) ---
        bx0, by0 = TW - 250, 82
        bx1 = TW - 8
        bmid = (bx0 + bx1) // 2
        # atmospheric haze behind building
        for hyaze in range(18):
            a = int(22 * (1 - hyaze / 18))
            d.rectangle((bx0 - 20, by0 - 30 - hyaze, bx1, by0 - 30 - hyaze + 1), fill=(120, 85, 60, a))
        # main facade
        d.rectangle((bx0, by0, bx1, TH - 18), fill=(52, 36, 26, 185))
        # darker base plinth
        d.rectangle((bx0 - 4, TH - 52, bx1, TH - 18), fill=(38, 27, 20, 190))
        # cornice layers
        d.rectangle((bx0 - 8, by0 - 4, bx1, by0 + 2), fill=(72, 52, 38, 200))
        d.rectangle((bx0 - 12, by0 - 8, bx1, by0 - 3), fill=(60, 44, 32, 190))
        # pediment / central risalit
        ped_top = by0 - 42
        d.polygon([(bmid - 62, by0 - 6), (bmid + 62, by0 - 6), (bmid, ped_top)], fill=(58, 41, 30, 210))
        d.polygon([(bmid - 54, by0 - 7), (bmid + 54, by0 - 7), (bmid, ped_top + 7)], fill=(72, 52, 38, 120))
        # entablature band
        d.rectangle((bx0 - 6, by0 + 2, bx1, by0 + 12), fill=(66, 48, 35, 175))
        # columns
        for cx in range(bx0 + 18, bx1 - 14, 24):
            col_h = TH - 30 - (by0 + 12)
            d.rectangle((cx, by0 + 12, cx + 10, TH - 30), fill=(74, 54, 40, 175))
            d.rectangle((cx + 1, by0 + 13, cx + 3, TH - 31), fill=(95, 72, 52, 55))
            # capital
            d.rectangle((cx - 2, by0 + 10, cx + 12, by0 + 16), fill=(82, 60, 44, 185))
            d.rectangle((cx - 1, TH - 34, cx + 11, TH - 28), fill=(68, 50, 36, 180))
        # windows with warm interior light
        for row, wy in enumerate(range(by0 + 24, TH - 64, 28)):
            for col, wx in enumerate(range(bx0 + 22, bx1 - 24, 30)):
                lit = 118 + int(28 * math.sin(f * 0.28 + wx * 0.07 + wy * 0.11))
                warm = (min(255, lit + 35), min(255, int(lit * 0.78)), 55, 150)
                d.rectangle((wx, wy, wx + 12, wy + 16), fill=warm)
                d.rectangle((wx, wy, wx + 12, wy + 16), outline=(90, 65, 45, 130))
                # mullion
                d.line((wx + 6, wy + 1, wx + 6, wy + 15), fill=(60, 42, 30, 120), width=1)
                d.line((wx + 1, wy + 8, wx + 11, wy + 8), fill=(60, 42, 30, 120), width=1)
        # central door
        door_w, door_h = 28, 38
        dx0 = bmid - door_w // 2
        dy0 = TH - 30 - door_h
        d.rectangle((dx0, dy0, dx0 + door_w, TH - 30), fill=(40, 28, 20, 200))
        d.rectangle((dx0 + 2, dy0 + 2, dx0 + door_w - 2, TH - 30), outline=(110, 85, 55, 120))
        d.arc((dx0 + 2, dy0 - 8, dx0 + door_w - 2, dy0 + 18), 180, 360, fill=(110, 85, 55, 140))
        # small red banner accents on facade
        for bx in (bx0 + 8, bx1 - 18):
            d.rectangle((bx, by0 + 14, bx + 6, by0 + 34), fill=(150, 30, 35, 110))

        # --- flagpole and waving Soviet flag ---
        pole_x = bmid
        pole_top = by0 - 58
        pole_bot = by0 + 2
        # pole shadow
        d.line((pole_x + 2, pole_top + 2, pole_x + 2, pole_bot + 2), fill=(20, 14, 10, 90), width=2)
        d.rectangle((pole_x - 2, pole_top, pole_x + 2, pole_bot), fill=(88, 66, 44, 235))
        # finial
        d.ellipse((pole_x - 4, pole_top - 6, pole_x + 4, pole_top + 2), fill=(200, 170, 70, 230), outline=(120, 90, 40, 200))
        # warm glow behind flag
        for gr in range(36, 0, -4):
            ga = int(18 * (1 - gr / 36))
            d.ellipse((pole_x - gr, pole_top - gr // 2, pole_x + 80 + gr, pole_top + 55 + gr // 2), fill=(180, 40, 30, ga))
        # flag cloth with wave
        flag_w, flag_h = 78, 46
        wave_phase = f * 0.52
        pts_top = []
        pts_bot = []
        for i in range(flag_w + 1):
            tt = i / flag_w
            wy_off = int(5 * math.sin(wave_phase + tt * 3.0)) + int(2 * math.sin(wave_phase * 1.6 + tt * 5.5))
            taper = int(3 * tt)
            x = pole_x + 3 + i
            pts_top.append((x, pole_top + 5 + wy_off))
            pts_bot.append((x, pole_top + 5 + flag_h + wy_off - taper))
        poly = pts_top + pts_bot[::-1]
        d.polygon(poly, fill=(210, 32, 40, 245))
        # fabric folds (darker stripes)
        for fold in range(1, 5):
            fx = pole_x + 3 + int(flag_w * fold / 5)
            fy_off = int(5 * math.sin(wave_phase + (fold / 5) * 3.0))
            d.line((fx, pole_top + 7 + fy_off, fx - 2, pole_top + 5 + flag_h - int(3 * fold / 5) + fy_off),
                   fill=(120, 18, 24, 55), width=1)
        # gold fringe near hoist
        for yy in range(pole_top + 6, pole_top + 5 + flag_h, 4):
            fy_off = int(5 * math.sin(wave_phase + 0.02 * (yy - pole_top)))
            d.point((pole_x + 4, yy + fy_off), fill=(220, 190, 70, 160))

        # hammer & sickle (gold), positioned in canton
        hx, hy = pole_x + 18, pole_top + 22
        # star above hammer/sickle
        star_r = 3
        star_pts = []
        for si in range(10):
            ang = math.radians(-90 + si * 36)
            rr = star_r if si % 2 == 0 else star_r * 0.45
            star_pts.append((hx + rr * math.cos(ang), hy - 10 + rr * math.sin(ang)))
        d.polygon(star_pts, fill=(230, 200, 80, 245))
        # sickle arc
        for ang in range(210, 345, 10):
            a1 = math.radians(ang)
            a2 = math.radians(ang + 10)
            r1 = 8
            x1, y1 = hx + int(r1 * math.cos(a1)), hy + int(r1 * math.sin(a1))
            x2, y2 = hx + int(r1 * math.cos(a2)), hy + int(r1 * math.sin(a2))
            d.line((x1, y1, x2, y2), fill=(230, 200, 80, 245), width=2)
        # hammer handle
        d.line((hx - 6, hy + 7, hx + 6, hy - 7), fill=(230, 200, 80, 245), width=2)
        # hammer head
        d.polygon([(hx + 2, hy - 10), (hx + 10, hy - 6), (hx + 8, hy - 2), (hx, hy - 6)], fill=(230, 200, 80, 245))

        # --- lamp flicker ---
        flick = 0.5 + 0.5*math.sin(f*0.8) * 0.3 + 0.2*math.sin(f*2.1)
        glow_a = int(20 + 16*flick)
        gx,gy = TW-320, 42
        for r in range(80,0,-10):
            a = int(glow_a*(1-r/80))
            d.ellipse((gx-r, gy-r, gx+r, gy+r), fill=(255,210,140,a))

        # --- airship ---
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

        # --- dust motes ---
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
