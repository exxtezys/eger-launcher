#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS=os.path.join(ROOT,"src/main/resources/config/fancymenu/assets")
OUTDIR=os.path.join(ROOT,"build/fm-mocks")
os.makedirs(OUTDIR,exist_ok=True)
W,H=427,240; SCALE=3; SW,SH=W*SCALE,H*SCALE
def load_font(size,bold=False):
    try: return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)
    except: return ImageFont.load_default()
bg=Image.open(os.path.join(ASSETS,'anim_bg.gif')).convert('RGBA').resize((SW,SH),Image.LANCZOS)
paper_tex=Image.open(os.path.join(ASSETS,'paper.png')).convert('RGBA')
paper_dark_tex=Image.open(os.path.join(ASSETS,'paper_dark.png')).convert('RGBA')
stamp=Image.open(os.path.join(ASSETS,'stamp_eger.png')).convert('RGBA')
brass=Image.open(os.path.join(ASSETS,'brass_strip.png')).convert('RGBA')
btn_n=Image.open(os.path.join(ASSETS,'btn_normal.png')).convert('RGBA')
SCREENS=[
 ('ege-title','ДОСТУПНЫЕ РЕЖИМЫ','Объявление отдела майонеза','Ф-01','ОЖИДАЕТ НАЗНАЧЕНИЯ',['Играть','Сервер','Настройки','Выйти'],'full'),
 ('ege-loading','ДЕГУСТАЦИЯ','Майонез maturity phase','Ф-07','ИДЁТ ПРОВЕРКА ПАРТИИ',[],'header'),
 ('ege-pause','ПАУЗА','Перерыв в дегустации','Ф-03','СЕАНС ПРИОСТАНОВЛЕН',['Вернуться','Настройки','Выйти'],'full'),
 ('ege-stations','СТАНЦИИ','Доступные дегустационные точки','Ф-11','РЕЕСТР СТАНЦИЙ',[],'header'),
 ('ege-death','АКТ ПОТЕРИ','Дегустационная комиссия фиксирует','Ф-99','ПАРТИЯ УТРАЧЕНА',['Возродиться','В меню'],'full'),
 ('ege-disconnected','СВЯЗЬ ПОТЕРЯНА','Станция временно недоступна','Ф-13','КАНАЛ РАЗОРВАН',[],'header'),
]
for name,headline,subhead,form_no,status,buttons,mode in SCREENS:
    img=bg.copy(); d=ImageDraw.Draw(img,'RGBA')
    def R(x,y,w,h): return (x*SCALE,y*SCALE,(x+w)*SCALE,(y+h)*SCALE)
    def T(x,y): return (x*SCALE,y*SCALE)
    d.rectangle(R(0,0,427,240), fill=(26,20,16,51))
    f_title=load_font(22*SCALE,True); f_sub=load_font(6*SCALE); f_head=load_font(11*SCALE,True)
    f_shead=load_font(7*SCALE); f_small=load_font(6*SCALE); f_footer=load_font(5*SCALE)
    if mode=='header':
        d.rounded_rectangle(R(8,8,250,52), radius=5*SCALE, fill=(196,180,138,115))
        d.rounded_rectangle(R(6,6,250,52), radius=5*SCALE, fill=(245,232,198,230))
        pt=paper_tex.resize((250*SCALE,52*SCALE),Image.LANCZOS); pt.putalpha(36); img.alpha_composite(pt,T(6,6))
        bt=brass.resize((250*SCALE,3*SCALE),Image.LANCZOS); bt.putalpha(153); img.alpha_composite(bt,T(6,6))
        d=ImageDraw.Draw(img,'RGBA')
        f_t=load_font(13*SCALE,True); f_hs=load_font(7*SCALE,True)
        d.text(T(14,12),'ЕГЕРЬ',fill=(139,46,34,255),font=f_t)
        d.rectangle(R(14,30,48,1),fill=(139,46,34,230))
        d.text(T(14,33),'НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939',fill=(138,120,96,255),font=load_font(5*SCALE))
        d.text(T(14,42),headline,fill=(139,46,34,255),font=f_hs)
        d.text(T(210,12),form_no,fill=(138,114,72,255),font=f_small)
        d.text(T(120,42),status,fill=(168,152,120,255),font=load_font(5*SCALE))
        d.rounded_rectangle(R(340,8,80,24), radius=4*SCALE, fill=(230,213,176,191))
        d.text(T(346,12),'НКПП',fill=(139,46,34,255),font=load_font(6*SCALE,True))
        d.text(T(346,20),'1939',fill=(138,120,96,255),font=load_font(5*SCALE))
    else:
        d.rounded_rectangle(R(12,12,266,218), radius=6*SCALE, fill=(196,180,138,140))
        d.rounded_rectangle(R(10,10,266,218), radius=6*SCALE, fill=(245,232,198,237))
        pt=paper_tex.resize((266*SCALE,218*SCALE),Image.LANCZOS); pt.putalpha(46); img.alpha_composite(pt,T(10,10))
        bt=brass.resize((266*SCALE,4*SCALE),Image.LANCZOS); bt.putalpha(140); img.alpha_composite(bt,T(10,10))
        d=ImageDraw.Draw(img,'RGBA')
        for rx,ry,rw,rh in [(14,14,258,1),(14,223,258,1),(14,14,1,210),(271,14,1,210)]: d.rectangle(R(rx,ry,rw,rh), fill=(138,114,72,77))
        d.rounded_rectangle(R(282,12,135,218), radius=6*SCALE, fill=(26,20,16,89))
        d.rounded_rectangle(R(280,10,137,218), radius=6*SCALE, fill=(230,213,176,224))
        tt=paper_dark_tex.resize((137*SCALE,218*SCALE),Image.LANCZOS); tt.putalpha(56); img.alpha_composite(tt,T(280,10))
        bt2=brass.resize((137*SCALE,6*SCALE),Image.LANCZOS); img.alpha_composite(bt2,T(280,10)); img.alpha_composite(bt2,T(280,222))
        st=stamp.resize((44*SCALE,44*SCALE),Image.LANCZOS); st.putalpha(217); img.alpha_composite(st,T(220,14))
        d=ImageDraw.Draw(img,'RGBA')
        d.text(T(20,18),'ЕГЕРЬ',fill=(26,20,16,255),font=f_title); d.text(T(18,16),'ЕГЕРЬ',fill=(139,46,34,255),font=f_title)
        d.rectangle(R(18,44,72,2),fill=(139,46,34,242)); d.rectangle(R(18,47,52,1),fill=(201,169,110,217))
        d.text(T(18,50),'НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939',fill=(138,120,96,255),font=f_sub)
        d.text(T(18,64),form_no,fill=(138,114,72,255),font=f_small); d.text(T(52,64),status,fill=(168,152,120,255),font=f_small)
        d.rectangle(R(18,74,244,1),fill=(138,114,72,89))
        d.text(T(18,80),headline,fill=(139,46,34,255),font=f_head); d.text(T(18,94),subhead,fill=(138,120,96,255),font=f_shead)
        d.text(T(286,20),'ПАНЕЛЬ УПРАВЛЕНИЯ',fill=(138,120,96,255),font=f_small); d.rectangle(R(286,30,125,1),fill=(138,114,72,77))
        d.text(T(286,34),form_no,fill=(138,114,72,255),font=f_small)
        if buttons:
            btn_w,btn_h,gap=121,20,4; total_h=len(buttons)*btn_h+(len(buttons)-1)*gap; start_y=218-10-total_h; bx=288
            for i,lab in enumerate(buttons):
                by=start_y+i*(btn_h+gap)
                bimg=btn_n.resize((btn_w*SCALE,btn_h*SCALE),Image.LANCZOS); img.alpha_composite(bimg,T(bx,by))
                d=ImageDraw.Draw(img,'RGBA'); fbtn=load_font(7*SCALE,True)
                bb=d.textbbox((0,0),lab,font=fbtn); tw,th=bb[2]-bb[0],bb[3]-bb[1]
                tx=(bx+btn_w/2)*SCALE-tw/2; ty=(by+btn_h/2)*SCALE-th/2-SCALE
                d.text((tx+1,ty+1),lab,fill=(30,20,15,180),font=fbtn); d.text((tx,ty),lab,fill=(245,235,211,255),font=fbtn)
    ft='© 1944 Опытная дегустационная станция · Архив НКПП'
    fb=d.textbbox((0,0),ft,font=load_font(5*SCALE)); d.text(((SW-(fb[2]-fb[0]))/2,(240-10)*SCALE),ft,fill=(168,152,120,255),font=load_font(5*SCALE))
    img.convert('RGB').save(os.path.join(OUTDIR,name+'.png'))
    print('ok',name)
