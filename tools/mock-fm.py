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

def R(x,y,w,h): return (x*SCALE,y*SCALE,(x+w)*SCALE,(y+h)*SCALE)
def T(x,y): return (x*SCALE,y*SCALE)
def blend_rect(img, rect, fill, radius=0):
    layer=Image.new('RGBA', img.size, (0,0,0,0))
    ld=ImageDraw.Draw(layer,'RGBA')
    if radius>0:
        ld.rounded_rectangle(rect, radius=radius, fill=fill)
    else:
        ld.rectangle(rect, fill=fill)
    return Image.alpha_composite(img, layer)
def blend_text(img, pos, text, fill, font):
    layer=Image.new('RGBA', img.size, (0,0,0,0))
    ld=ImageDraw.Draw(layer,'RGBA')
    ld.text(pos, text, fill=fill, font=font)
    return Image.alpha_composite(img, layer)

SCREENS=[
 ('ege-title','ДОСТУПНЫЕ РЕЖИМЫ','Объявление отдела майонеза','Ф-01','ОЖИДАЕТ НАЗНАЧЕНИЯ',['Играть','Сервер','Настройки','Выйти'],'full'),
 ('ege-loading','ДЕГУСТАЦИЯ','Майонез maturity phase','Ф-07','ИДЁТ ПРОВЕРКА ПАРТИИ',[],'header'),
 ('ege-pause','ПАУЗА','Перерыв в дегустации','Ф-03','СЕАНС ПРИОСТАНОВЛЕН',['Вернуться','Настройки','Выйти'],'full'),
 ('ege-stations','СТАНЦИИ','Доступные дегустационные точки','Ф-11','РЕЕСТР СТАНЦИЙ',[],'header'),
 ('ege-death','АКТ ПОТЕРИ','Дегустационная комиссия фиксирует','Ф-99','ПАРТИЯ УТРАЧЕНА',['Возродиться','В меню'],'full'),
 ('ege-disconnected','СВЯЗЬ ПОТЕРЯНА','Станция временно недоступна','Ф-13','КАНАЛ РАЗОРВАН',[],'header'),
]
for name,headline,subhead,form_no,status,buttons,mode in SCREENS:
    img=bg.copy()
    img=blend_rect(img, R(0,0,427,240), (26,20,16,51))
    f_title=load_font(22*SCALE,True); f_sub=load_font(6*SCALE); f_head=load_font(12*SCALE,True); f_shead=load_font(7*SCALE)
    f_small=load_font(6*SCALE)
    if mode=='header':
        img=blend_rect(img, R(8,8,250,52), (196,180,138,115), radius=5*SCALE)
        img=blend_rect(img, R(6,6,250,52), (245,232,198,230), radius=5*SCALE)
        pt=paper_tex.resize((250*SCALE,52*SCALE),Image.LANCZOS); pt.putalpha(36); img.alpha_composite(pt,T(6,6))
        bt=brass.resize((250*SCALE,3*SCALE),Image.LANCZOS); bt.putalpha(153); img.alpha_composite(bt,T(6,6))
        img=blend_text(img,T(14,12),'ЕГЕРЬ',(139,46,34,255),f_title)
        img=blend_rect(img,R(14,30,48,1),(139,46,34,230))
        img=blend_text(img,T(14,33),'НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939',(138,120,96,255),load_font(5*SCALE))
        img=blend_text(img,T(14,42),headline,(139,46,34,255),f_head)
        img=blend_text(img,T(210,12),form_no,(138,114,72,255),f_small)
        img=blend_text(img,T(120,42),status,(168,152,120,255),load_font(5*SCALE))
        img=blend_rect(img,R(340,8,80,24),(230,213,176,191),radius=4*SCALE)
        img=blend_text(img,T(346,12),'НКПП',(139,46,34,255),load_font(6*SCALE,True))
        img=blend_text(img,T(346,20),'1939',(138,120,96,255),load_font(5*SCALE))
    else:
        img=blend_rect(img,R(12,12,266,218),(196,180,138,140),radius=6*SCALE)
        img=blend_rect(img,R(10,10,266,218),(245,232,198,237),radius=6*SCALE)
        pt=paper_tex.resize((266*SCALE,218*SCALE),Image.LANCZOS); pt.putalpha(46); img.alpha_composite(pt,T(10,10))
        bt=brass.resize((266*SCALE,4*SCALE),Image.LANCZOS); bt.putalpha(140); img.alpha_composite(bt,T(10,10))
        for rx,ry,rw,rh in [(14,14,258,1),(14,223,258,1),(14,14,1,210),(271,14,1,210)]:
            img=blend_rect(img,R(rx,ry,rw,rh),(138,114,72,77))
        img=blend_rect(img,R(282,12,135,218),(26,20,16,71),radius=6*SCALE)
        img=blend_rect(img,R(280,10,137,218),(230,213,176,87),radius=6*SCALE)
        tt=paper_dark_tex.resize((137*SCALE,218*SCALE),Image.LANCZOS); tt.putalpha(15); img.alpha_composite(tt,T(280,10))
        img=blend_rect(img,R(280,10,137,218),(26,20,16,36),radius=6*SCALE)
        img=blend_rect(img,R(284,108,129,110),(26,20,16,41),radius=4*SCALE)
        bt2=brass.resize((137*SCALE,6*SCALE),Image.LANCZOS); img.alpha_composite(bt2,T(280,10)); img.alpha_composite(bt2,T(280,222))
        st=stamp.resize((44*SCALE,44*SCALE),Image.LANCZOS); st.putalpha(217); img.alpha_composite(st,T(220,14))
        img=blend_text(img,T(20,18),'ЕГЕРЬ',(26,20,16,255),f_title); img=blend_text(img,T(18,16),'ЕГЕРЬ',(139,46,34,255),f_title)
        img=blend_rect(img,R(18,44,72,2),(139,46,34,242)); img=blend_rect(img,R(18,47,52,1),(201,169,110,217))
        img=blend_text(img,T(18,50),'НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939',(138,120,96,255),f_sub)
        img=blend_text(img,T(18,64),form_no,(138,114,72,255),f_small); img=blend_text(img,T(52,64),status,(168,152,120,255),f_small)
        img=blend_rect(img,R(18,74,244,1),(138,114,72,89))
        img=blend_text(img,T(18,80),headline,(139,46,34,255),f_head); img=blend_text(img,T(18,94),subhead,(138,120,96,255),f_shead)
        img=blend_text(img,T(286,20),'ПАНЕЛЬ УПРАВЛЕНИЯ',(138,120,96,255),f_small); img=blend_rect(img,R(286,30,125,1),(138,114,72,77))
        img=blend_text(img,T(286,34),form_no,(138,114,72,255),f_small)
        if buttons:
            btn_w,btn_h,gap=121,20,4; total_h=len(buttons)*btn_h+(len(buttons)-1)*gap; start_y=218-10-total_h; bx=288
            for i,lab in enumerate(buttons):
                by=start_y+i*(btn_h+gap)
                bimg=btn_n.resize((btn_w*SCALE,btn_h*SCALE),Image.LANCZOS); img.alpha_composite(bimg,T(bx,by))
                fbtn=load_font(7*SCALE,True)
                # measure with temp draw
                tmp=Image.new('RGBA',(1,1)); td=ImageDraw.Draw(tmp)
                bb=td.textbbox((0,0),lab,font=fbtn); tw,th=bb[2]-bb[0],bb[3]-bb[1]
                tx=(bx+btn_w/2)*SCALE-tw/2; ty=(by+btn_h/2)*SCALE-th/2-SCALE
                img=blend_text(img,(int(tx+1),int(ty+1)),lab,(30,20,15,180),fbtn)
                img=blend_text(img,(int(tx),int(ty)),lab,(245,235,211,255),fbtn)
    ft='© 1944 Опытная дегустационная станция · Архив НКПП'
    tmp=Image.new('RGBA',(1,1)); td=ImageDraw.Draw(tmp)
    fb=td.textbbox((0,0),ft,font=load_font(5*SCALE))
    img=blend_text(img,(int((SW-(fb[2]-fb[0]))/2),int((240-10)*SCALE)),ft,(168,152,120,255),load_font(5*SCALE))
    img.convert('RGB').save(os.path.join(OUTDIR,name+'.png'))
    print('ok',name)
