from PIL import Image, ImageDraw
import os

base_dir = r"C:\Users\User\Documents\eger-launcher\src\main\resources\config\fancymenu\assets"
os.makedirs(base_dir, exist_ok=True)

# 1. Зелёный фон ПДА с scanlines (256x256 тайл)
pda_bg = Image.new('RGB', (256, 256), color='#0a1a0a')
draw = ImageDraw.Draw(pda_bg)
for y in range(0, 256, 4):
    draw.rectangle([(0, y), (256, y+2)], fill='#0d210d')
for x in range(0, 256, 4):
    draw.rectangle([(x, 0), (x+2, 256)], fill='#081808')
pda_bg.save(os.path.join(base_dir, 'pda_bg.png'))
print("Created: pda_bg.png")

# 2. Уголок рамки ПДА (64x64)
pda_frame = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(pda_frame)
draw.rectangle([(0, 0), (63, 63)], fill=(15, 35, 15, 255))
draw.rectangle([(3, 3), (60, 60)], fill=(25, 55, 25, 255))
draw.rectangle([(0, 0), (16, 3)], fill=(80, 140, 80, 255))
draw.rectangle([(0, 0), (3, 16)], fill=(80, 140, 80, 255))
pda_frame.save(os.path.join(base_dir, 'pda_frame_corner.png'))
print("Created: pda_frame_corner.png")

# 3. Кнопка ПДА нормальная (200x40)
btn = Image.new('RGBA', (200, 40), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(btn)
draw.rectangle([(2, 2), (197, 37)], fill=(10, 30, 10, 220))
draw.rectangle([(2, 2), (197, 37)], outline=(60, 120, 60, 255), width=1)
draw.line([(2, 19), (197, 19)], fill=(20, 50, 20, 150))
btn.save(os.path.join(base_dir, 'pda_button.png'))
print("Created: pda_button.png")

# 4. Кнопка ПДА hover (200x40)
btn_h = Image.new('RGBA', (200, 40), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(btn_h)
draw.rectangle([(2, 2), (197, 37)], fill=(30, 70, 30, 230))
draw.rectangle([(2, 2), (197, 37)], outline=(100, 180, 100, 255), width=2)
draw.line([(2, 19), (197, 19)], fill=(50, 100, 50, 180))
btn_h.save(os.path.join(base_dir, 'pda_button_hover.png'))
print("Created: pda_button_hover.png")

# 5. Логотип区域 (400x80) - декоративный элемент
logo = Image.new('RGBA', (400, 80), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(logo)
for i in range(0, 360, 45):
    draw.rectangle([(i, 5), (i+40, 75)], fill=(50, 100, 50, 200))
    draw.rectangle([(i+5, 10), (i+35, 70)], fill=(80, 160, 80, 255))
logo.save(os.path.join(base_dir, 'pda_logo.png'))
print("Created: pda_logo.png")

# 6. Иконка радиации (64x64)
rad = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(rad)
draw.ellipse([(4, 4), (60, 60)], fill=(20, 50, 20, 200), outline=(80, 160, 80, 255))
draw.ellipse([(24, 24), (40, 40)], fill=(10, 25, 10, 255))
draw.polygon([(32, 14), (42, 30), (22, 30)], fill=(80, 160, 80, 255))
draw.polygon([(32, 50), (42, 34), (22, 34)], fill=(80, 160, 80, 255))
draw.polygon([(14, 32), (30, 22), (30, 42)], fill=(80, 160, 80, 255))
draw.polygon([(50, 32), (34, 22), (34, 42)], fill=(80, 160, 80, 255))
rad.save(os.path.join(base_dir, 'pda_radiation.png'))
print("Created: pda_radiation.png")

# 7. Разделительная линия (200x4)
sep = Image.new('RGBA', (200, 4), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(sep)
draw.rectangle([(0, 1), (199, 2)], fill=(60, 120, 60, 200))
sep.save(os.path.join(base_dir, 'pda_separator.png'))
print("Created: pda_separator.png")

# 8. Панель контента (400x300)
panel = Image.new('RGBA', (400, 300), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(panel)
draw.rectangle([(0, 0), (399, 299)], fill=(10, 25, 10, 230))
draw.rectangle([(0, 0), (399, 299)], outline=(60, 120, 60, 255), width=2)
draw.rectangle([(5, 5), (394, 294)], outline=(30, 70, 30, 180), width=1)
panel.save(os.path.join(base_dir, 'pda_panel.png'))
print("Created: pda_panel.png")

print("\nAll PDA textures created successfully!")
