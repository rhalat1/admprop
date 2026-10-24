import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
import subprocess
import imageio_ffmpeg

# MOBILE HD RESOLUTION (720x1280) - Lightweight, crystal clear on smartphones, ~3-4 MB
WIDTH = 720
HEIGHT = 1280
FPS = 30

FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"

# "MODO DÍA" PALETTE (Century 21 Invictus Light Theme)
GOLD = (190, 160, 95)            # #BEA05F
GOLD_ACCENT = (155, 120, 55)     # #9B7837
OBSIDIAN = (18, 18, 18)          # #121212
CHARCOAL = (50, 50, 50)          # #323232
WHITE = (255, 255, 255)
LIGHT_CARD = (255, 255, 255, 235)
LIGHT_BORDER = (190, 160, 95, 210)
GREEN_CHECK = (39, 174, 96)

def f_bold(size):
    return ImageFont.truetype(FONT_BOLD, size)

def f_reg(size):
    return ImageFont.truetype(FONT_REG, size)

def load_img(rel_path):
    path = os.path.join("public/urubo-bella-flor/images", rel_path)
    return Image.open(path).convert("RGB")

print("Loading media for Mobile Light Mode Reel...")
img_drone = load_img("drone-urbanizacion.jpg")
img_entrada = load_img("entrada-bella-flor.jpg")
img_calles = load_img("calles-pavimentadas.jpg")
img_terreno = load_img("terreno-real-frente.jpg")
img_casa = load_img("casa-proyecto-render.jpg")
img_piscina = load_img("piscina-principal.jpg")
img_clubhouse = load_img("club-house-churrasquera.jpg")
img_cancha = load_img("cancha-tenis.jpg")
img_canchas_drone = load_img("drone-canchas.jpg")
img_asesora = load_img("asesora-roxana-pozo.jpg") # Now 360x360 square from official post

# Load route video frames
route_cap = cv2.VideoCapture("public/urubo-bella-flor/images/recorrido-8min-urubo.mp4")
route_frames = []
while True:
    ret, frame = route_cap.read()
    if not ret:
        break
    route_frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
route_cap.release()
print(f"Loaded {len(route_frames)} route frames.")

# Subtle top and bottom gradients for light theme readability
grad_top = Image.new('RGBA', (WIDTH, 240), (0,0,0,0))
d_gt = ImageDraw.Draw(grad_top)
for y in range(240):
    alpha = int(130 * (1.0 - (y / 240.0)**1.5))
    d_gt.line([(0, y), (WIDTH, y)], fill=(250, 250, 250, alpha))

grad_bottom = Image.new('RGBA', (WIDTH, 320), (0,0,0,0))
d_gb = ImageDraw.Draw(grad_bottom)
for y in range(320):
    alpha = int(160 * ((y / 320.0)**1.3))
    d_gb.line([(0, y), (WIDTH, y)], fill=(245, 245, 245, alpha))

def pan_and_scan(img, progress, pan_dir='left_to_right', zoom_start=1.03, zoom_end=1.12):
    bw, bh = img.size
    base_scale = max(WIDTH / bw, HEIGHT / bh)
    cur_zoom = zoom_start + (zoom_end - zoom_start) * progress
    scale = base_scale * cur_zoom
    
    nw = int(bw * scale)
    nh = int(bh * scale)
    res = img.resize((nw, nh), Image.Resampling.BILINEAR)
    
    extra_x = max(0, nw - WIDTH)
    extra_y = max(0, nh - HEIGHT)
    
    if pan_dir == 'left_to_right':
        left = int(extra_x * (0.2 + 0.6 * progress))
        top = extra_y // 2
    elif pan_dir == 'right_to_left':
        left = int(extra_x * (0.8 - 0.6 * progress))
        top = extra_y // 2
    elif pan_dir == 'bottom_to_top':
        left = extra_x // 2
        top = int(extra_y * (0.7 - 0.4 * progress))
    else:
        left = extra_x // 2
        top = extra_y // 2
        
    left = max(0, min(extra_x, left))
    top = max(0, min(extra_y, top))
    
    canvas = res.crop((left, top, left + WIDTH, top + HEIGHT)).convert('RGBA')
    canvas.paste(grad_top, (0, 0), grad_top)
    canvas.paste(grad_bottom, (0, HEIGHT - 320), grad_bottom)
    return canvas

def draw_pill(draw, x, y, text, font, bg_color=GOLD, text_color=WHITE, pad_x=22, pad_y=10):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + pad_x * 2
    h = th + pad_y * 2
    x0 = x - w // 2
    y0 = y - h // 2
    draw.rounded_rectangle([x0 - 2, y0 - 1, x0 + w + 2, y0 + h + 3], radius=h // 2, fill=(0, 0, 0, 35))
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h // 2, fill=bg_color)
    draw.text((x0 + pad_x, y0 + pad_y - 2), text, font=font, fill=text_color)
    return y0, y0 + h

def draw_light_card(draw, x0, y0, x1, y1, radius=20, fill=LIGHT_CARD, outline=LIGHT_BORDER, width=2):
    draw.rounded_rectangle([x0 - 2, y0 - 1, x1 + 2, y1 + 5], radius=radius, fill=(0, 0, 0, 30))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def draw_centered_text(draw, y, text, font, fill=OBSIDIAN, shadow_color=(255, 255, 255, 180)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    if shadow_color:
        draw.text((x + 1, y + 1), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bbox[3] - bbox[1])

def draw_top_progress(canvas, frame_idx, total_frames):
    d = ImageDraw.Draw(canvas)
    h = 6
    d.rectangle([0, 0, WIDTH, h], fill=(225, 225, 225, 190))
    fill_w = int(WIDTH * (frame_idx / total_frames))
    d.rectangle([0, 0, fill_w, h], fill=GOLD)

# Make circular avatar for Roxana Pozo WITHOUT ANY DISTORTION
def make_avatar(img, size=180):
    w, h = img.size
    min_dim = min(w, h)
    # Center crop square
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    square = img.crop((left, top, left + min_dim, top + min_dim))
    res = square.resize((size, size), Image.Resampling.LANCZOS)
    
    mask = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size, size], fill=255)
    
    avatar = Image.new('RGBA', (size, size), (0,0,0,0))
    avatar.paste(res, (0, 0), mask)
    
    ring = Image.new('RGBA', (size, size), (0,0,0,0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([2, 2, size - 2, size - 2], outline=GOLD, width=4)
    return Image.alpha_composite(avatar, ring)

avatar_roxana = make_avatar(img_asesora, 180)

# SCENE TIMINGS (Synchronized to voiceover parts)
SCENE_TIMINGS = [
    (0.00,  7.78),  # 0: Hook
    (7.78,  14.81), # 1: Route & Conectividad
    (14.81, 20.69), # 2: Entrada & Calles
    (20.69, 26.95), # 3: Terreno Real
    (26.95, 32.76), # 4: Casa de tus sueños
    (32.76, 39.86), # 5: Amenidades
    (39.86, 47.23), # 6: Documentación & Precio
    (47.23, 56.50), # 7: Cierre C21 & Roxana
]

TOTAL_SECONDS = 56.5
TOTAL_FRAMES = int(TOTAL_SECONDS * FPS) # 1695 frames

raw_video_path = "public/urubo-bella-flor/images/temp_reel_mobile.mp4"
final_video_path = "public/urubo-bella-flor/images/reel-presentacion-instagram.mp4"

print(f"Generating {TOTAL_FRAMES} frames ({TOTAL_SECONDS}s) at 720x1280 mobile HD...")
writer = imageio.get_writer(raw_video_path, fps=FPS, codec='libx264', pixelformat='yuv420p', bitrate='3M')

for frame_idx in range(TOTAL_FRAMES):
    sec = frame_idx / FPS
    
    scene_idx = 0
    for idx, (t0, t1) in enumerate(SCENE_TIMINGS):
        if t0 <= sec < t1:
            scene_idx = idx
            break
        elif sec >= SCENE_TIMINGS[-1][0]:
            scene_idx = 7
            
    t0, t1 = SCENE_TIMINGS[scene_idx]
    progress = min(1.0, max(0.0, (sec - t0) / (t1 - t0)))
    
    # --- SCENE 0: HOOK ---
    if scene_idx == 0:
        canvas = pan_and_scan(img_drone, progress, pan_dir='left_to_right', zoom_start=1.04, zoom_end=1.12)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 90, "📍 URUBÓ • SANTA CRUZ, BOLIVIA", f_bold(20), bg_color=GOLD, text_color=WHITE)
        
        card_y = 1010
        draw_light_card(d, 35, card_y, WIDTH - 35, card_y + 190)
        draw_centered_text(d, card_y + 18, "¿BUSCAS EL TERRENO PERFECTO?", f_bold(28), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 60, "Urbanización Bella Flor • Urubó", f_bold(24), fill=GOLD_ACCENT)
        draw_centered_text(d, card_y + 102, "A sólo minutos del 4to Anillo y Equipetrol", f_reg(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 138, "¡La oportunidad que estabas esperando!", f_bold(18), fill=GOLD)
        canvas = Image.alpha_composite(canvas, overlay)
        
    # --- SCENE 1: RUTA ---
    elif scene_idx == 1:
        r_idx = int(progress * (len(route_frames) - 1))
        r_img = route_frames[r_idx]
        rw, rh = r_img.size
        target_w = WIDTH
        target_h = int(rh * (target_w / rw))
        r_resized = r_img.resize((target_w, target_h), Image.Resampling.BILINEAR)
        
        base = Image.new('RGBA', (WIDTH, HEIGHT), (248, 247, 244, 255))
        paste_y = (HEIGHT - target_h) // 2 - 30
        base.paste(r_resized, (0, paste_y))
        
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        draw_pill(d, WIDTH // 2, 90, "🚗 CONECTIVIDAD INMEDIATA", f_bold(20), bg_color=GOLD, text_color=WHITE)
        
        card_y = 1010
        draw_light_card(d, 35, card_y, WIDTH - 35, card_y + 190)
        draw_centered_text(d, card_y + 18, "¡A SÓLO 8 MINUTOS EXACTOS!", f_bold(30), fill=GOLD_ACCENT)
        draw_centered_text(d, card_y + 65, "4.2 km de ruta 100% asfaltada", f_bold(22), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 102, "Desde el Puente Mario Foianini y Equipetrol", f_reg(19), fill=CHARCOAL)
        draw_centered_text(d, card_y + 138, "Rápido, seguro y de fácil acceso", f_bold(18), fill=GOLD)
        canvas = Image.alpha_composite(base, overlay)

    # --- SCENE 2: INGRESO & CALLES ---
    elif scene_idx == 2:
        if progress < 0.5:
            sub_p = progress / 0.5
            canvas = pan_and_scan(img_entrada, sub_p, pan_dir='bottom_to_top', zoom_start=1.05, zoom_end=1.14)
        else:
            sub_p = (progress - 0.5) / 0.5
            canvas = pan_and_scan(img_calles, sub_p, pan_dir='left_to_right', zoom_start=1.03, zoom_end=1.12)
            
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        draw_pill(d, WIDTH // 2, 90, "🛡️ URBANIZACIÓN CONSOLIDADA", f_bold(20), bg_color=GOLD, text_color=WHITE)
        
        card_y = 1010
        draw_light_card(d, 35, card_y, WIDTH - 35, card_y + 190)
        draw_centered_text(d, card_y + 18, "Urbanización Privada Bella Flor", f_bold(28), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 60, "• Pórtico y seguridad las 24 horas", f_bold(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 92, "• Vías totalmente pavimentadas", f_bold(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 124, "• Luz eléctrica, agua y servicios completos", f_reg(19), fill=CHARCOAL)
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 3: TERRENO REAL ---
    elif scene_idx == 3:
        canvas = pan_and_scan(img_terreno, progress, pan_dir='left_to_right', zoom_start=1.03, zoom_end=1.12)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        draw_pill(d, WIDTH // 2, 90, "📐 CARACTERÍSTICAS DEL LOTE", f_bold(20), bg_color=GOLD, text_color=WHITE)
        
        card_y = 1000
        draw_light_card(d, 35, card_y, WIDTH - 35, card_y + 205)
        draw_centered_text(d, card_y + 16, "704.74 m² (100% PLANO)", f_bold(32), fill=GOLD_ACCENT)
        draw_centered_text(d, card_y + 60, "Lote 23 • Manzana 1", f_bold(23), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 95, "✓ 19.88 metros de frente para tu diseño", f_bold(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 128, "✓ Terreno nivelado, listo para construir", f_reg(19), fill=CHARCOAL)
        draw_centered_text(d, card_y + 160, "¡Sin gastos extras de movimiento de tierra!", f_bold(18), fill=GREEN_CHECK)
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 4: CASA DE TUS SUEÑOS ---
    elif scene_idx == 4:
        canvas = pan_and_scan(img_casa, progress, pan_dir='left_to_right', zoom_start=1.04, zoom_end=1.12)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        draw_pill(d, WIDTH // 2, 90, "🏡 IMAGINA CONSTRUIR AQUÍ", f_bold(20), bg_color=GOLD, text_color=WHITE)
        
        card_y = 1010
        draw_light_card(d, 35, card_y, WIDTH - 35, card_y + 190)
        draw_centered_text(d, card_y + 18, "Diseño Minimalista a tu Medida", f_bold(28), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 60, "Espacio ideal para residencia de 2 plantas", f_bold(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 92, "con piscina privada, terraza y amplios jardines", f_reg(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 128, "¡La vida que tu familia merece!", f_bold(19), fill=GOLD_ACCENT)
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 5: AMENIDADES ---
    elif scene_idx == 5:
        if progress < 0.35:
            p_sub = progress / 0.35
            canvas = pan_and_scan(img_piscina, p_sub, pan_dir='left_to_right', zoom_start=1.03, zoom_end=1.10)
            tag_title = "Piscinas Recreativas & Solárium"
        elif progress < 0.70:
            p_sub = (progress - 0.35) / 0.35
            canvas = pan_and_scan(img_clubhouse, p_sub, pan_dir='left_to_right', zoom_start=1.03, zoom_end=1.10)
            tag_title = "Club House & Churrasqueras"
        else:
            p_sub = (progress - 0.70) / 0.30
            canvas = pan_and_scan(img_cancha, p_sub, pan_dir='left_to_right', zoom_start=1.03, zoom_end=1.10)
            tag_title = "Canchas de Tenis y Fútbol Iluminadas"
            
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        draw_pill(d, WIDTH // 2, 90, "🌴 AMENIDADES TIPO RESORT", f_bold(20), bg_color=GOLD, text_color=WHITE)
        
        card_y = 1010
        draw_light_card(d, 35, card_y, WIDTH - 35, card_y + 190)
        draw_centered_text(d, card_y + 18, tag_title, f_bold(28), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 60, "• Parque infantil y amplias áreas verdes", f_reg(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 92, "• Churrasqueras equipadas para reuniones", f_reg(20), fill=CHARCOAL)
        draw_centered_text(d, card_y + 128, "• Confort, deporte y desconexión total", f_bold(19), fill=GOLD_ACCENT)
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 6: DOCUMENTACIÓN & PRECIO ---
    elif scene_idx == 6:
        canvas = pan_and_scan(img_canchas_drone, progress, pan_dir='bottom_to_top', zoom_start=1.04, zoom_end=1.12)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))
        d = ImageDraw.Draw(overlay)
        draw_pill(d, WIDTH // 2, 90, "✅ DOCUMENTACIÓN 100% AL DÍA", f_bold(20), bg_color=GREEN_CHECK, text_color=WHITE)
        
        card_y = 960
        draw_light_card(d, 30, card_y, WIDTH - 30, card_y + 245, fill=(255, 255, 255, 245), width=3)
        draw_centered_text(d, card_y + 16, "¡FOLIO REAL INDIVIDUAL LISTO!", f_bold(26), fill=GREEN_CHECK)
        draw_centered_text(d, card_y + 54, "PRECIO DE OPORTUNIDAD", f_bold(21), fill=CHARCOAL)
        draw_centered_text(d, card_y + 86, "$94,400 USD", f_bold(48), fill=GOLD_ACCENT)
        draw_centered_text(d, card_y + 158, "Solo $133.95 USD / m²", f_bold(24), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 196, "Precio por debajo de mercado en Urubó", f_reg(19), fill=CHARCOAL)
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 7: CIERRE MODO DÍA - CENTURY 21 INVICTUS ---
    else:
        base = Image.new('RGBA', (WIDTH, HEIGHT), (250, 249, 246, 255))
        d = ImageDraw.Draw(base)
        
        d.rectangle([20, 20, WIDTH - 20, HEIGHT - 20], outline=GOLD, width=2)
        d.rectangle([30, 30, WIDTH - 30, HEIGHT - 30], outline=(GOLD[0], GOLD[1], GOLD[2], 90), width=1)
        
        draw_pill(d, WIDTH // 2, 100, "CENTURY 21 INVICTUS", f_bold(22), bg_color=GOLD, text_color=WHITE, pad_x=32, pad_y=12)
        
        # Circular avatar WITHOUT DISTORTION
        av_x = (WIDTH - 180) // 2
        av_y = 170
        base.paste(avatar_roxana, (av_x, av_y), avatar_roxana)
        
        draw_centered_text(d, 375, "Roxana Pozo", f_bold(38), fill=OBSIDIAN)
        draw_centered_text(d, 425, "Asesora Inmobiliaria Century 21", f_bold(22), fill=GOLD_ACCENT)
        draw_centered_text(d, 460, "Century 21 Invictus • Equipetrol, Santa Cruz", f_reg(19), fill=CHARCOAL)
        
        card_y = 520
        draw_light_card(d, 40, card_y, WIDTH - 40, card_y + 320, fill=(255, 255, 255, 255), width=2)
        draw_centered_text(d, card_y + 25, "CONTACTA A ROXANA POZO", f_bold(26), fill=GOLD_ACCENT)
        draw_centered_text(d, card_y + 68, "Comenta \"INFO\" en este video", f_bold(24), fill=OBSIDIAN)
        draw_centered_text(d, card_y + 102, "y te enviamos la ubicación y ficha técnica", f_reg(20), fill=CHARCOAL)
        
        btn_y = card_y + 155
        d.rounded_rectangle([80, btn_y, WIDTH - 80, btn_y + 70], radius=35, fill=(37, 211, 102))
        draw_centered_text(d, btn_y + 18, "📲 WhatsApp: +591 785 35562", f_bold(24), fill=WHITE, shadow_color=None)
        
        draw_centered_text(d, card_y + 255, "O toca el enlace del perfil para agendar tu visita", f_reg(18), fill=CHARCOAL)
        
        draw_pill(d, WIDTH // 2, 900, "704.74 m² • Bella Flor, Urubó • $94,400 USD", f_bold(18), bg_color=(240, 238, 233), text_color=OBSIDIAN, pad_x=24, pad_y=10)
        canvas = base

    # Progress bar
    draw_top_progress(canvas, frame_idx + 1, TOTAL_FRAMES)
    
    frame_rgb = canvas.convert('RGB')
    writer.append_data(np.array(frame_rgb))
    
    if (frame_idx + 1) % 300 == 0 or frame_idx == TOTAL_FRAMES - 1:
        print(f"Rendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({((frame_idx + 1)/TOTAL_FRAMES)*100:.1f}%)...")

writer.close()
print("Mobile video generated. Merging audio...")

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [
    ffmpeg_exe, "-y",
    "-i", raw_video_path,
    "-i", "public/urubo-bella-flor/images/full_voiceover.mp3",
    "-c:v", "libx264",
    "-crf", "24",
    "-preset", "fast",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "128k",
    "-movflags", "+faststart",
    final_video_path
]
subprocess.run(cmd, check=True)

if os.path.exists(raw_video_path):
    os.remove(raw_video_path)

print(f"Finished! Output saved at: {final_video_path}")
