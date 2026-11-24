#!/usr/bin/env python3
"""Generate 10 professional FancyMenu variants for Eger 1939."""
import os, shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_SRC = os.path.join(ROOT, "src", "main", "resources", "config", "fancymenu", "assets")
VARIANTS = os.path.join(ROOT, "variants")
BASE_BG = os.path.join(ROOT, "theme", "scene.png")

# Each palette: name, CREAM,CREAM_D,PAPER_SHADOW,INK,ACCENT,ACCENT_H,GOLD,GOLD_D,MUTED,MUTED_L,DARK,BRASS,WHITE, overlay_alpha
PALETTES = [
    ("v1_cream_oxblood", "#F5E8C6","#E6D5B0","#C4B48A","#211812","#8B2E22","#A63B2C","#C9A96E","#8A7248","#8A7860","#A89878","#1A1410","#B8965A","#F5EBD3",0.20),
    ("v2_dossier_ink",   "#E8E0D0","#D8CCB8","#B8A890","#1A1816","#3A2E22","#544232","#A08860","#7A6848","#7A7268","#968E82","#141210","#A08860","#F0E8D8",0.22),
    ("v3_walnut_brass",  "#DDD0B8","#CCBEA0","#A89878","#241A12","#6B3A1E","#854A28","#C9A96E","#8A7248","#8A7A62","#A09078","#181008","#C9A96E","#F5E8D0",0.22),
    ("v4_night_archive", "#2A241C","#221C16","#3A3228","#F0E4CC","#C9A96E","#E0C080","#C9A96E","#8A7248","#A89878","#C0B090","#0C0A08","#C9A96E","#F5EBD3",0.38),
    ("v5_parchment",     "#F2EAD8","#E4D8C0","#C8BA98","#2A2218","#5A3A22","#724A2C","#C9A96E","#8A7248","#8A7C68","#A09480","#1A1610","#B8965A","#F8F0E0",0.18),
    ("v6_slate_steel",   "#DDD8CC","#CCC6B8","#A8A298","#1E1E1C","#4A3A2A","#5E4A36","#B8A888","#8A7A60","#807A70","#9A9488","#121210","#B0A080","#F0ECE0",0.22),
    ("v7_rustic_red",    "#E6D8BC","#D4C4A4","#B8A888","#281810","#7A2E18","#943820","#C9A96E","#8A7248","#8A7860","#A09078","#180C08","#B8965A","#F5E8D0",0.22),
    ("v8_mono_press",    "#EEEEE8","#DDDDD4","#B0B0A8","#181818","#2A2A2A","#404040","#A09070","#807060","#787870","#949088","#0C0C0C","#A09070","#F5F5F0",0.20),
    ("v9_olive_field",   "#DCE4CC","#CCD4B8","#A8B090","#1C2414","#3A4A22","#4A5E2C","#B8A060","#8A7848","#7A8468","#96A084","#101408","#B0A060","#F0F4E4",0.22),
    ("v10_burgundy",     "#E8DDD0","#D8CAB8","#B8A898","#241418","#6A2028","#842832","#C9A96E","#8A7248","#8A7868","#A09488","#140C0E","#B8965A","#F5EDE4",0.22),
]

SCREENS = [
    ("ege-title.txt", "title_screen", "ДОСТУПНЫЕ РЕЖИМЫ", "Объявление отдела майонеза", "Ф-01", "ОЖИДАЕТ НАЗНАЧЕНИЯ",
     ["Объект: дегустационная станция №7", "Партия: майонез «Егерь», серия 1939", "К допуску: уполномоченные сотрудники"],
     "", [("Играть","mc_titlescreen_singleplayer_button"),("Сервер","mc_titlescreen_multiplayer_button"),("Настройки","mc_titlescreen_options_button"),("Выйти","mc_titlescreen_quit_button")], "full"),
    ("ege-loading.txt","progress_screen","ДЕГУСТАЦИЯ","Майонез maturity phase","Ф-07","ИДЁТ ПРОВЕРКА ПАРТИИ",
     ["Подготовка образцов...","Проверка герметичности тары","Ожидайте завершения процедуры"],"Ожидайте завершения процедуры",[],"header"),
    ("ege-connect.txt","connect_screen","ПОДКЛЮЧЕНИЕ","Установка связи со станцией","Ф-12","РАДИОКАНАЛ ОТКРЫТ",
     ["Вызов удалённой станции...","Согласование протокола передачи","Не отключайте радиолинию"],"Установка связи...",[],"header"),
    ("ege-receiving.txt","receiving_level_screen","ПРИЁМ ДАННЫХ","Загрузка сохранения партии","Ф-14","ПЕРЕДАЧА ДОКУМЕНТОВ",
     ["Получение архива партии...","Сверка контрольных сумм","Целостность документов проверяется"],"Приём документов...",[],"header"),
    ("ege-pause.txt","pause_screen","ПАУЗА","Перерыв в дегустации","Ф-03","СЕАНС ПРИОСТАНОВЛЕН",
     ["Дегустация временно приостановлена","Материалы партии сохранены на столе","Возобновите при готовности"],
     "",[("Вернуться","mc_pausescreen_return_to_game_button"),("Настройки","mc_pausescreen_options_button"),("Выйти","mc_pausescreen_quit_button")],"full"),
    ("ege-stations.txt","join_multiplayer_screen","СТАНЦИИ","Доступные дегустационные точки","Ф-11","РЕЕСТР СТАНЦИЙ",
     ["Выберите станцию из реестра","Проверьте статус соединения","Допуск только по пропуску НКПП"],"Выберите станцию в списке",[],"header"),
    ("ege-options.txt","options_screen","НАСТРОЙКИ","Параметры дегустационной станции","Ф-09","РЕГУЛИРОВКА ОБОРУДОВАНИЯ",
     ["Отрегулируйте параметры станции","Изменения вступают немедленно","Храните бланк в архиве"],"Настройте параметры станции",[],"header"),
    ("ege-newworld.txt","create_world_screen","НОВАЯ СТАНЦИЯ","Создание дегустационной точки","Ф-02","РЕГИСТРАЦИЯ ОБЪЕКТА",
     ["Заполните бланк регистрации","Укажите параметры новой станции","Объект будет занесён в архив НКПП"],"Заполните бланк регистрации",[],"header"),
    ("ege-death.txt","death_screen","АКТ ПОТЕРИ","Дегустационная комиссия фиксирует","Ф-99","ПАРТИЯ УТРАЧЕНА",
     ["Зафиксирована потеря образца","Комиссия рекомендует повторный допуск","Материалы направлены в архив"],
     "",[("Возродиться","mc_deathscreen_respawn_button"),("В меню","mc_deathscreen_titlemenu_button")],"full"),
    ("ege-disconnected.txt","disconnected_screen","СВЯЗЬ ПОТЕРЯНА","Станция временно недоступна","Ф-13","КАНАЛ РАЗОРВАН",
     ["Радиоканал со станцией прерван","Проверьте линию связи","Повторите попытку подключения"],"Проверьте соединение",[],"header"),
]

TITLE="ЕГЕРЬ"; SUBTITLE="НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939"; FOOTER="© 1944 Опытная дегустационная станция · Архив НКПП"

def shape(eid,color,x,y,w,h,anchor="top-left",radius=0,opacity=1.0,fade="no_fading"):
    return f"""element {{
  element_type = shape
  instance_identifier = {eid}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  anchor_point = {anchor}
  color = {color}
  corner_radius_top_left = {radius}
  corner_radius_top_right = {radius}
  corner_radius_bottom_left = {radius}
  corner_radius_bottom_right = {radius}
  base_opacity = {opacity:.2f}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = {fade}
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  auto_sizing = false
  sticky_anchor = false
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}}

"""

def image_el(eid,src,x,y,w,h,anchor="top-left",opacity=1.0,fade="no_fading"):
    return f"""element {{
  source = [source:local]/config/fancymenu/assets/{src}
  repeat_texture = false
  nine_slice_texture = false
  nine_slice_texture_border_x = 5
  nine_slice_texture_border_y = 5
  element_type = image
  instance_identifier = {eid}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = {fade}
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = {opacity:.2f}
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}}

"""

def text_el(eid,value,x,y,w,h,anchor,color,scale=1.0,shadow=True,fade="fadein"):
    safe=str(value).replace("\n"," ")
    return f"""element {{
  source = {safe}
  source_mode = direct
  shadow = {"true" if shadow else "false"}
  scale = {scale:.2f}
  base_color = {color}
  text_border = 0
  line_spacing = 1
  enable_scrolling = false
  auto_line_wrapping = true
  remove_html_breaks = true
  parse_markdown = false
  element_type = text_v2
  instance_identifier = {eid}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = {fade}
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  sticky_anchor = false
  anchor_point = {anchor}
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
}}

"""

def vanilla_btn(vid,label,x,y,w,h,WHITE):
    return f"""vanilla_button {{
  button_element_executable_block_identifier = {vid}-exec
  [executable_block:{vid}-exec][type:generic] = [executables:]
  backgroundnormal = [source:local]/config/fancymenu/assets/btn_normal.png
  backgroundhovered = [source:local]/config/fancymenu/assets/btn_hover.png
  background_texture_inactive = [source:local]/config/fancymenu/assets/btn_normal.png
  restartbackgroundanimations = true
  loopbackgroundanimations = true
  nine_slice_custom_background = true
  nine_slice_border_x = 6
  nine_slice_border_y = 6
  navigatable = true
  widget_active_state_requirement_container_identifier = {vid}-active
  [loading_requirement_container_meta:{vid}-active] = [groups:][instances:]
  element_type = vanilla_button
  instance_identifier = {vid}
  appearance_delay = no_delay
  appearance_delay_seconds = 1.0
  fade_in_v2 = fadein
  fade_in_speed = 1.0
  fade_out = no_fading
  fade_out_speed = 1.0
  base_opacity = 1.0
  auto_sizing = false
  auto_sizing_base_screen_width = 1920
  auto_sizing_base_screen_height = 1080
  sticky_anchor = false
  anchor_point = top-left
  x = {x}
  y = {y}
  width = {w}
  height = {h}
  stretch_x = false
  stretch_y = false
  stay_on_screen = true
  element_loading_requirement_container_identifier = {vid}-load
  [loading_requirement_container_meta:{vid}-load] = [groups:][instances:]
  hoverlabel = 
  label = {label}
  label_base_color = {WHITE}
  label_hover_color = #FFFFFF
  label_scale = 1.0
  label_shadow = true
}}

"""

def layout(ident,body,bgname):
    return f"""type = fancymenu_layout

layout-meta {{
  identifier = {ident}
  layout_index = 0
  is_enabled = true
  render_custom_elements_behind_vanilla = true
}}

menu_background {{
  image_path = [source:local]/config/fancymenu/assets/{bgname}
  slide = false
  repeat_texture = false
  background_type = image
}}

customization {{
  action = backgroundoptions
  keepaspectratio = true
}}

{body}
"""

def build_screen(ident,headline,subhead,form_no,status,body_lines,note,buttons,mode,pal,bgname):
    _,CREAM,CREAM_D,PAPER_SHADOW,INK,ACCENT,ACCENT_H,GOLD,GOLD_D,MUTED,MUTED_L,DARK,BRASS,WHITE,ov = pal
    b=""
    b+=shape("overlay",DARK,0,0,427,240,opacity=ov)
    if mode=="header":
        b+=shape("plaque_shadow",PAPER_SHADOW,8,8,250,52,radius=5,opacity=0.45)
        b+=shape("plaque",CREAM,6,6,250,52,radius=5,opacity=0.90)
        b+=image_el("plaque_tex","paper.png",6,6,250,52,opacity=0.14)
        b+=image_el("plaque_brass","brass_strip.png",6,6,250,3,opacity=0.60)
        b+=text_el("title",TITLE,14,12,120,20,"top-left",ACCENT,1.2,True,"fadein")
        b+=shape("rule_a",ACCENT,14,30,48,1,opacity=0.9)
        b+=text_el("subtitle",SUBTITLE,14,33,230,8,"top-left",MUTED,0.45,False,"fadein")
        b+=text_el("headline",headline,14,42,160,10,"top-left",ACCENT,0.72,True,"fadein")
        b+=text_el("form_no",form_no,210,12,40,8,"top-left",GOLD_D,0.50,False,"no_fading")
        b+=text_el("status",status,120,42,130,8,"top-left",MUTED_L,0.45,False,"fadein")
        b+=shape("badge",CREAM_D,340,8,80,24,radius=4,opacity=0.75)
        b+=text_el("badge_t","НКПП",346,12,68,8,"top-left",ACCENT,0.55,True,"no_fading")
        b+=text_el("badge_s","1939",346,20,68,8,"top-left",MUTED,0.45,False,"no_fading")
        b+=text_el("footer",FOOTER,0,-10,427,8,"bottom-centered",MUTED_L,0.45,False,"no_fading")
        return layout(ident,b,bgname)
    b+=shape("paper_shadow",PAPER_SHADOW,12,12,266,218,radius=6,opacity=0.55)
    b+=shape("paper",CREAM,10,10,266,218,radius=6,opacity=0.93)
    b+=image_el("paper_tex","paper.png",10,10,266,218,opacity=0.18)
    b+=shape("pb_t",GOLD_D,14,14,258,1,opacity=0.30); b+=shape("pb_b",GOLD_D,14,223,258,1,opacity=0.30)
    b+=shape("pb_l",GOLD_D,14,14,1,210,opacity=0.30); b+=shape("pb_r",GOLD_D,271,14,1,210,opacity=0.30)
    b+=image_el("brass_paper","brass_strip.png",10,10,266,4,opacity=0.55)
    b+=shape("table_shadow",DARK,282,12,135,218,radius=6,opacity=0.35)
    b+=shape("table",CREAM_D,280,10,137,218,radius=6,opacity=0.88)
    b+=image_el("table_tex","paper_dark.png",280,10,137,218,opacity=0.22)
    b+=image_el("brass_top","brass_strip.png",280,10,137,6,opacity=0.95)
    b+=image_el("brass_bot","brass_strip.png",280,222,137,6,opacity=0.95)
    b+=image_el("stamp","stamp_eger.png",220,14,44,44,opacity=0.85)
    b+=text_el("title_shadow",TITLE,20,18,200,30,"top-left",DARK,1.9,True,"no_fading")
    b+=text_el("title",TITLE,18,16,200,30,"top-left",ACCENT,1.9,True,"fadein")
    b+=shape("rule_a",ACCENT,18,44,72,2,opacity=0.95); b+=shape("rule_b",GOLD,18,47,52,1,opacity=0.85)
    b+=text_el("subtitle",SUBTITLE,18,50,210,10,"top-left",MUTED,0.55,False,"fadein")
    b+=text_el("form_no",form_no,18,64,40,10,"top-left",GOLD_D,0.60,False,"fadein")
    b+=text_el("status",status,52,64,170,10,"top-left",MUTED_L,0.52,False,"fadein")
    b+=shape("sep",GOLD_D,18,74,244,1,opacity=0.35)
    b+=text_el("headline",headline,18,80,240,14,"top-left",ACCENT,1.0,True,"fadein")
    b+=text_el("subhead",subhead,18,94,240,10,"top-left",MUTED,0.65,False,"fadein")
    for i,line in enumerate(body_lines[:4]):
        yy=112+i*13
        b+=shape(f"bullet_{i}",ACCENT,18,yy+3,2,2,radius=1,opacity=0.55)
        b+=text_el(f"body_{i}",line,24,yy,230,10,"top-left",INK,0.58,False,"fadein")
    b+=shape("sig_line",GOLD_D,18,196,90,1,opacity=0.35)
    b+=text_el("sig_label","Подпись ответственного",18,198,120,8,"top-left",MUTED_L,0.45,False,"no_fading")
    b+=text_el("panel_label","ПАНЕЛЬ УПРАВЛЕНИЯ",286,20,125,10,"top-left",MUTED,0.50,False,"fadein")
    b+=shape("panel_sep",GOLD_D,286,30,125,1,opacity=0.30)
    if buttons:
        btn_w,btn_h,gap=121,20,4
        total_h=len(buttons)*btn_h+(len(buttons)-1)*gap
        start_y=218-10-total_h; bx=288
        for i,(label,vid) in enumerate(buttons):
            by=start_y+i*(btn_h+gap)
            b+=vanilla_btn(vid,label,bx,by,btn_w,btn_h,WHITE)
    b+=text_el("footer",FOOTER,0,-10,427,8,"bottom-centered",MUTED_L,0.45,False,"no_fading")
    for idx,(rx,ry) in enumerate([(12,12),(270,12),(12,222),(270,222)]):
        b+=shape(f"rivet_{idx}",BRASS,rx,ry,4,4,radius=2,opacity=0.75)
    return layout(ident,b,bgname)

def make_variant_bg(pal, idx):
    name=pal[0]
    base=Image.open(BASE_BG).convert("RGBA")
    W,H=base.size
    TW,TH=640,int(640*H/W)
    base=base.resize((TW,TH),Image.LANCZOS)
    # tint based on palette mood
    darkness = 0.62 + (idx%3)*0.04
    base=ImageEnhance.Brightness(base).enhance(darkness)
    base=ImageEnhance.Contrast(base).enhance(1.05)
    # color wash
    accent = pal[5].lstrip('#')
    ar,ag,ab = int(accent[0:2],16),int(accent[2:4],16),int(accent[4:6],16)
    wash = Image.new("RGBA",(TW,TH),(ar//6,ag//6,ab//6,35))
    base=Image.alpha_composite(base,wash)
    vig=Image.new("RGBA",(TW,TH),(0,0,0,0))
    vd=ImageDraw.Draw(vig)
    for i in range(80):
        a=int(120*(1-i/80)**1.5)
        vd.rectangle((i,i,TW-i,TH-i), outline=(10,8,5,a))
    base=Image.alpha_composite(base,vig)
    return base.convert("RGB")

def main():
    os.makedirs(VARIANTS, exist_ok=True)
    for vi,pal in enumerate(PALETTES):
        vname=f"v{vi+1}"
        vdir=os.path.join(VARIANTS,vname)
        cust=os.path.join(vdir,"customization"); ast=os.path.join(vdir,"assets")
        os.makedirs(cust,exist_ok=True); os.makedirs(ast,exist_ok=True)
        # bg
        bg=make_variant_bg(pal,vi)
        bgname=f"bg_{vi+1}.png"
        bg.save(os.path.join(ast,bgname), optimize=True)
        # copy shared assets
        for fn in ["paper.png","paper_dark.png","brass_strip.png","stamp_eger.png","btn_normal.png","btn_hover.png"]:
            src=os.path.join(ASSETS_SRC,fn)
            if os.path.exists(src): shutil.copy2(src, os.path.join(ast,fn))
        # layouts
        for name,ident,headline,subhead,form_no,status,body_lines,note,buttons,mode in SCREENS:
            content=build_screen(ident,headline,subhead,form_no,status,body_lines,note,buttons,mode,pal,bgname)
            with open(os.path.join(cust,name),"w",encoding="utf-8",newline="\n") as f: f.write(content)
        # mock
        mock=bg.convert("RGBA").resize((427*2,240*2),Image.LANCZOS)
        d=ImageDraw.Draw(mock,"RGBA")
        CREAM,ACCENT,MUTED,GOLD = pal[1],pal[5],pal[9],pal[7]
        def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
        d.rectangle((0,0,854,480), fill=(20,16,12,40))
        d.rounded_rectangle((20,20,552,456), radius=12, fill=(*hx(CREAM),235))
        d.rounded_rectangle((560,20,834,456), radius=12, fill=(*hx(pal[2]),220))
        try: ft=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",44)
        except: ft=ImageFont.load_default()
        try: fs=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",14)
        except: fs=ft
        d.text((38,36),"ЕГЕРЬ",fill=(*hx(ACCENT),255),font=ft)
        d.text((38,86),"НАРКОМАТ ПИЩЕВОЙ ПРОМЫШЛЕННОСТИ · 1939",fill=(*hx(MUTED),255),font=fs)
        d.text((38,120),"ДОСТУПНЫЕ РЕЖИМЫ",fill=(*hx(ACCENT),255),font=fs)
        # buttons
        for i,lab in enumerate(["Играть","Сервер","Настройки","Выйти"]):
            bx,by=576,300+i*36
            d.rounded_rectangle((bx,by,bx+242,by+30), radius=4, fill=(*hx(ACCENT),230))
            d.text((bx+12,by+7),lab,fill=(245,235,211,255),font=fs)
        mock.convert("RGB").save(os.path.join(vdir,"mock.png"))
        with open(os.path.join(vdir,"README.txt"),"w",encoding="utf-8") as f:
            f.write(f"Variant {vi+1}: {pal[0]}\nPalette: {', '.join(str(x) for x in pal[1:15])}\n")
        print("ok",vname,pal[0])

if __name__=="__main__":
    main()
