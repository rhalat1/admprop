import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio

WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_SECONDS = 32
TOTAL_FRAMES = TOTAL_SECONDS * FPS # 960 frames

FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"

GOLD = (212, 184, 126)        # #D4B87E
GOLD_LIGHT = (235, 214, 170)
GOLD_DARK = (160, 135, 75)
DARK_BG = (15, 15, 15)
DARK_CARD = (18, 18, 18, 225)
BORDER_GOLD = (212, 184, 126, 210)
WHITE = (255, 255, 255)
LIGHT_GRAY = (215, 215, 215)
GREEN_CHECK = (50, 205, 50)

def f_bold(size):
    return ImageFont.truetype(FONT_BOLD, size)

def f_reg(size):
    return ImageFont.truetype(FONT_REG, size)

def load_img(rel_path):
    path = os.path.join("public/urubo-bella-flor/images", rel_path)
    return Image.open(path).convert("RGB")

print("Loading image and video assets...")
img_drone = load_img("drone-urbanizacion.jpg")
img_entrada = load_img("entrada-bella-flor.jpg")
img_calles = load_img("calles-pavimentadas.jpg")
img_terreno = load_img("terreno-real-frente.jpg")
img_casa = load_img("casa-proyecto-render.jpg")
img_piscina = load_img("piscina-principal.jpg")
img_clubhouse = load_img("club-house-churrasquera.jpg")
img_cancha = load_img("cancha-tenis.jpg")
img_futbol = load_img("cancha-futbol-noche.jpg")
img_canchas_drone = load_img("drone-canchas.jpg")
img_asesora = load_img("asesora-roxana-pozo.jpg")

# Route video
route_cap = cv2.VideoCapture("public/urubo-bella-flor/images/recorrido-8min-urubo.mp4")
route_frames = []
while True:
    ret, frame = route_cap.read()
    if not ret:
        break
    route_frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
route_cap.release()
print(f"Loaded {len(route_frames)} route frames.")

# Precompute blurred backgrounds to make rendering ultra fast
def make_blur_bg(img):
    bw, bh = img.size
    scale = max(WIDTH / bw, HEIGHT / bh)
    res = img.resize((int(bw * scale), int(bh * scale)), Image.Resampling.BILINEAR)
    left = (res.width - WIDTH) // 2
    top = (res.height - HEIGHT) // 2
    crop = res.crop((left, top, left + WIDTH, top + HEIGHT))
    blur = crop.filter(ImageFilter.GaussianBlur(radius=30))
    # Darken overlay
    dark = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 140))
    return Image.alpha_composite(blur.convert('RGBA'), dark)

print("Precomputing blurred backgrounds...")
bg_drone = make_blur_bg(img_drone)
bg_route = make_blur_bg(route_frames[0])
bg_entrada = make_blur_bg(img_entrada)
bg_calles = make_blur_bg(img_calles)
bg_terreno = make_blur_bg(img_terreno)
bg_casa = make_blur_bg(img_casa)
bg_piscina = make_blur_bg(img_piscina)
bg_clubhouse = make_blur_bg(img_clubhouse)
bg_cancha = make_blur_bg(img_cancha)
bg_canchas_drone = make_blur_bg(img_canchas_drone)

def draw_top_progress(canvas, frame_idx, total_frames):
    d = ImageDraw.Draw(canvas)
    h = 8
    d.rectangle([0, 0, WIDTH, h], fill=(30, 30, 30, 180))
    fill_w = int(WIDTH * (frame_idx / total_frames))
    d.rectangle([0, 0, fill_w, h], fill=GOLD)

def draw_pill(draw, x, y, text, font, bg_color=GOLD, text_color=(15, 15, 15), pad_x=28, pad_y=12):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + pad_x * 2
    h = th + pad_y * 2
    x0 = x - w // 2
    y0 = y - h // 2
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h // 2, fill=bg_color)
    draw.text((x0 + pad_x, y0 + pad_y - 2), text, font=font, fill=text_color)
    return y0, y0 + h

def draw_glass_card(draw, x0, y0, x1, y1, radius=24, fill=DARK_CARD, outline=BORDER_GOLD, width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def draw_centered_text(draw, y, text, font, fill=WHITE, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    if shadow:
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 200))
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bbox[3] - bbox[1])

def place_fg_image(base_canvas, img, progress, card_h_max=1100, zoom_amt=0.06):
    bw, bh = img.size
    card_w = 980
    card_h = int(card_w * (bh / bw))
    if card_h > card_h_max:
        card_h = card_h_max
        card_w = int(card_h * (bw / bh))
    
    cur_zoom = 1.0 + zoom_amt * progress
    fg_w = int(card_w * cur_zoom)
    fg_h = int(card_h * cur_zoom)
    res = img.resize((fg_w, fg_h), Image.Resampling.BILINEAR)
    
    c_left = (fg_w - card_w) // 2
    c_top = (fg_h - card_h) // 2
    clipped = res.crop((c_left, c_top, c_left + card_w, c_top + card_h))
    
    mask = Image.new('L', (card_w, card_h), 0)
    m_d = ImageDraw.Draw(mask)
    m_d.rounded_rectangle([0, 0, card_w, card_h], radius=28, fill=255)
    
    paste_x = (WIDTH - card_w) // 2
    paste_y = (HEIGHT - card_h) // 2 - 40
    
    # Shadow
    shadow = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    s_d = ImageDraw.Draw(shadow)
    s_d.rounded_rectangle([paste_x - 8, paste_y - 8, paste_x + card_w + 8, paste_y + card_h + 14], radius=32, fill=(0, 0, 0, 180))
    base = Image.alpha_composite(base_canvas, shadow)
    
    base.paste(clipped, (paste_x, paste_y), mask)
    
    # Gold border
    border = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    b_d = ImageDraw.Draw(border)
    b_d.rounded_rectangle([paste_x, paste_y, paste_x + card_w, paste_y + card_h], radius=28, outline=BORDER_GOLD, width=3)
    base = Image.alpha_composite(base, border)
    
    return base, paste_x, paste_y, card_w, card_h

# Pre-render circular Roxana avatar
def make_circular_avatar(img, size=240):
    res = img.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size, size], fill=255)
    
    avatar = Image.new('RGBA', (size, size), (0,0,0,0))
    avatar.paste(res, (0, 0), mask)
    
    # Gold ring border
    ring = Image.new('RGBA', (size, size), (0,0,0,0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([2, 2, size - 2, size - 2], outline=GOLD, width=6)
    return Image.alpha_composite(avatar, ring)

avatar_roxana = make_circular_avatar(img_asesora, 260)

output_path = "public/urubo-bella-flor/images/reel-presentacion-instagram.mp4"
writer = imageio.get_writer(output_path, fps=FPS, codec='libx264', pixelformat='yuv420p', bitrate='7M')

print("Generating 960 frames (32 seconds)...")

for frame_idx in range(TOTAL_FRAMES):
    sec = frame_idx / FPS
    
    # --- SCENE 1: HOOK (0.0s - 3.5s) ---
    if sec < 3.5:
        p = sec / 3.5
        canvas, px, py, cw, ch = place_fg_image(bg_drone.copy(), img_drone, p, card_h_max=1080)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        # Top pill
        draw_pill(d, WIDTH // 2, 140, "📍 URUBÓ • SANTA CRUZ, BOLIVIA", f_bold(28), bg_color=GOLD, text_color=(15,15,15))
        
        # Headline Card at Bottom
        card_y0 = py + ch + 35
        card_h = 240
        draw_glass_card(d, 50, card_y0, WIDTH - 50, card_y0 + card_h, radius=28)
        
        # Text
        draw_centered_text(d, card_y0 + 25, "¿BUSCAS EL TERRENO PERFECTO?", f_bold(44), fill=GOLD_LIGHT)
        draw_centered_text(d, card_y0 + 90, "Urbanización Bella Flor", f_bold(38), fill=WHITE)
        draw_centered_text(d, card_y0 + 150, "A minutos del 4to Anillo y Equipetrol", f_reg(30), fill=LIGHT_GRAY)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 2: ACCESO & CONECTIVIDAD (3.5s - 7.5s) ---
    elif sec < 7.5:
        sub_p = (sec - 3.5) / 4.0
        # Route video frames: sample according to progress
        r_idx = int(sub_p * (len(route_frames) - 1))
        r_img = route_frames[r_idx]
        
        canvas, px, py, cw, ch = place_fg_image(bg_route.copy(), r_img, 0.0, card_h_max=1050, zoom_amt=0.0)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 130, "🚗 CONECTIVIDAD INMEDIATA", f_bold(28), bg_color=GOLD, text_color=(15,15,15))
        
        # Route info card
        card_y0 = py + ch + 35
        card_h = 240
        draw_glass_card(d, 50, card_y0, WIDTH - 50, card_y0 + card_h, radius=28)
        
        draw_centered_text(d, card_y0 + 25, "¡A SÓLO 8 MINUTOS!", f_bold(50), fill=GOLD)
        draw_centered_text(d, card_y0 + 95, "4.2 km de ruta 100% asfaltada", f_bold(34), fill=WHITE)
        draw_centered_text(d, card_y0 + 150, "Desde el Puente Mario Foianini / 4to Anillo", f_reg(28), fill=LIGHT_GRAY)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 3: INGRESO & URBANIZACIÓN (7.5s - 11.5s) ---
    elif sec < 11.5:
        sub_p = (sec - 7.5) / 4.0
        if sub_p < 0.5:
            # Entrada
            p_sub = sub_p / 0.5
            canvas, px, py, cw, ch = place_fg_image(bg_entrada.copy(), img_entrada, p_sub, card_h_max=1050)
        else:
            # Calles pavimentadas
            p_sub = (sub_p - 0.5) / 0.5
            canvas, px, py, cw, ch = place_fg_image(bg_calles.copy(), img_calles, p_sub, card_h_max=1050)
            
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 130, "🛡️ URBANIZACIÓN CONSOLIDADA", f_bold(28), bg_color=GOLD, text_color=(15,15,15))
        
        card_y0 = py + ch + 30
        card_h = 245
        draw_glass_card(d, 50, card_y0, WIDTH - 50, card_y0 + card_h, radius=28)
        
        draw_centered_text(d, card_y0 + 25, "Urbanización Bella Flor", f_bold(42), fill=GOLD_LIGHT)
        draw_centered_text(d, card_y0 + 85, "• Pórtico y seguridad 24 horas", f_reg(30), fill=WHITE)
        draw_centered_text(d, card_y0 + 130, "• Vías totalmente pavimentadas", f_reg(30), fill=WHITE)
        draw_centered_text(d, card_y0 + 175, "• Agua, luz eléctrica y alcantarillado", f_reg(30), fill=LIGHT_GRAY)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 4: EL TERRENO REAL (11.5s - 16.0s) ---
    elif sec < 16.0:
        sub_p = (sec - 11.5) / 4.5
        canvas, px, py, cw, ch = place_fg_image(bg_terreno.copy(), img_terreno, sub_p, card_h_max=1050)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 130, "📐 CARACTERÍSTICAS DEL LOTE", f_bold(28), bg_color=GOLD, text_color=(15,15,15))
        
        card_y0 = py + ch + 30
        card_h = 250
        draw_glass_card(d, 50, card_y0, WIDTH - 50, card_y0 + card_h, radius=28)
        
        draw_centered_text(d, card_y0 + 20, "704.74 m² (100% PLANO)", f_bold(46), fill=GOLD)
        draw_centered_text(d, card_y0 + 85, "Lote 23 • Manzana 1", f_bold(34), fill=WHITE)
        draw_centered_text(d, card_y0 + 135, "✓ 19.88 metros de frente para tu diseño", f_reg(30), fill=WHITE)
        draw_centered_text(d, card_y0 + 180, "✓ Terreno nivelado, listo para construir", f_reg(30), fill=LIGHT_GRAY)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 5: LA CASA DE TUS SUEÑOS (16.0s - 20.5s) ---
    elif sec < 20.5:
        sub_p = (sec - 16.0) / 4.5
        canvas, px, py, cw, ch = place_fg_image(bg_casa.copy(), img_casa, sub_p, card_h_max=1050)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 130, "🏡 IMAGINA CONSTRUIR AQUÍ", f_bold(28), bg_color=GOLD, text_color=(15,15,15))
        
        card_y0 = py + ch + 30
        card_h = 245
        draw_glass_card(d, 50, card_y0, WIDTH - 50, card_y0 + card_h, radius=28)
        
        draw_centered_text(d, card_y0 + 25, "La Casa de tus Sueños", f_bold(44), fill=GOLD_LIGHT)
        draw_centered_text(d, card_y0 + 85, "Espacio ideal para residencia moderna", f_reg(32), fill=WHITE)
        draw_centered_text(d, card_y0 + 135, "con piscina privada, jardines y galería", f_reg(32), fill=WHITE)
        draw_centered_text(d, card_y0 + 180, "¡Dale vida a tus proyectos familiares!", f_bold(28), fill=GOLD)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 6: CLUB HOUSE & AMENIDADES (20.5s - 25.0s) ---
    elif sec < 25.0:
        sub_p = (sec - 20.5) / 4.5
        if sub_p < 0.33:
            p_sub = sub_p / 0.33
            canvas, px, py, cw, ch = place_fg_image(bg_piscina.copy(), img_piscina, p_sub, card_h_max=1050)
            tag_title = "Piscinas Recreativas & Solárium"
        elif sub_p < 0.66:
            p_sub = (sub_p - 0.33) / 0.33
            canvas, px, py, cw, ch = place_fg_image(bg_clubhouse.copy(), img_clubhouse, p_sub, card_h_max=1050)
            tag_title = "Club House & Churrasqueras"
        else:
            p_sub = (sub_p - 0.66) / 0.34
            canvas, px, py, cw, ch = place_fg_image(bg_cancha.copy(), img_cancha, p_sub, card_h_max=1050)
            tag_title = "Canchas de Tenis y Fútbol"
            
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 130, "🌴 AMENIDADES TIPO RESORT", f_bold(28), bg_color=GOLD, text_color=(15,15,15))
        
        card_y0 = py + ch + 30
        card_h = 245
        draw_glass_card(d, 50, card_y0, WIDTH - 50, card_y0 + card_h, radius=28)
        
        draw_centered_text(d, card_y0 + 25, tag_title, f_bold(42), fill=GOLD_LIGHT)
        draw_centered_text(d, card_y0 + 85, "• Parque infantil y amplias áreas verdes", f_reg(30), fill=WHITE)
        draw_centered_text(d, card_y0 + 130, "• Iluminación nocturna para deportes", f_reg(30), fill=WHITE)
        draw_centered_text(d, card_y0 + 175, "• Máxima seguridad para toda la familia", f_reg(30), fill=LIGHT_GRAY)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 7: DOCUMENTACIÓN & PRECIO (25.0s - 28.5s) ---
    elif sec < 28.5:
        sub_p = (sec - 25.0) / 3.5
        canvas, px, py, cw, ch = place_fg_image(bg_canchas_drone.copy(), img_canchas_drone, sub_p, card_h_max=950)
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        
        draw_pill(d, WIDTH // 2, 130, "✅ DOCUMENTACIÓN 100% AL DÍA", f_bold(28), bg_color=(46, 204, 113), text_color=(10,10,10))
        
        # Center Big Price Card
        card_y0 = py + ch + 25
        card_h = 320
        draw_glass_card(d, 40, card_y0, WIDTH - 40, card_y0 + card_h, radius=32, fill=(12, 12, 12, 235), outline=GOLD, width=3)
        
        draw_centered_text(d, card_y0 + 25, "¡FOLIO REAL INDIVIDUAL LISTO!", f_bold(36), fill=(46, 204, 113))
        draw_centered_text(d, card_y0 + 80, "PRECIO DE OPORTUNIDAD", f_bold(32), fill=LIGHT_GRAY)
        draw_centered_text(d, card_y0 + 125, "$94,400 USD", f_bold(68), fill=GOLD)
        draw_centered_text(d, card_y0 + 225, "Solo $133.95 USD / m²", f_bold(36), fill=WHITE)
        draw_centered_text(d, card_y0 + 270, "Precio por debajo de mercado en Urubó", f_reg(26), fill=LIGHT_GRAY)
        
        canvas = Image.alpha_composite(canvas, overlay)

    # --- SCENE 8: CIERRE VENDEDOR & CENTURY 21 INVICTUS (28.5s - 32.0s) ---
    else:
        sub_p = (sec - 28.5) / 3.5
        # Dark luxury background
        base = Image.new('RGBA', (WIDTH, HEIGHT), (14, 14, 14, 255))
        d = ImageDraw.Draw(base)
        
        # Gold frame accents
        d.rectangle([30, 30, WIDTH - 30, HEIGHT - 30], outline=GOLD_DARK, width=2)
        d.rectangle([45, 45, WIDTH - 45, HEIGHT - 45], outline=(GOLD[0], GOLD[1], GOLD[2], 80), width=1)
        
        # Agency top
        draw_pill(d, WIDTH // 2, 150, "CENTURY 21 INVICTUS", f_bold(32), bg_color=GOLD, text_color=(15,15,15), pad_x=40, pad_y=16)
        
        # Avatar
        av_x = (WIDTH - 260) // 2
        av_y = 250
        base.paste(avatar_roxana, (av_x, av_y), avatar_roxana)
        
        # Agent Name & Title
        draw_centered_text(d, 540, "Roxana Pozo", f_bold(52), fill=GOLD_LIGHT)
        draw_centered_text(d, 610, "Asesora Inmobiliaria Certificada", f_reg(32), fill=LIGHT_GRAY)
        draw_centered_text(d, 655, "Century 21 Invictus • Equipetrol, Santa Cruz", f_reg(28), fill=(170, 170, 170))
        
        # Main Selling Card
        card_y = 740
        draw_glass_card(d, 60, card_y, WIDTH - 60, card_y + 440, radius=32, fill=(24, 24, 24, 240), outline=GOLD, width=3)
        
        draw_centered_text(d, card_y + 35, "¿TE INTERESA ESTA PROPIEDAD?", f_bold(40), fill=GOLD)
        draw_centered_text(d, card_y + 95, "Comenta \"INFO\" en esta publicación", f_bold(34), fill=WHITE)
        draw_centered_text(d, card_y + 145, "y te enviamos la ubicación y ficha técnica", f_reg(30), fill=LIGHT_GRAY)
        
        # WhatsApp button style
        btn_y = card_y + 220
        d.rounded_rectangle([120, btn_y, WIDTH - 120, btn_y + 95], radius=48, fill=(37, 211, 102))
        draw_centered_text(d, btn_y + 24, "📲 WhatsApp: +591 785 35562", f_bold(36), fill=(10, 10, 10), shadow=False)
        
        draw_centered_text(d, card_y + 350, "O toca el enlace en el perfil para agendar tu visita", f_reg(26), fill=LIGHT_GRAY)
        
        # Property recap pill at bottom
        draw_pill(d, WIDTH // 2, 1340, "704.74 m² • Bella Flor, Urubó • $94,400 USD", f_bold(26), bg_color=(35, 35, 35), text_color=GOLD_LIGHT, pad_x=30, pad_y=14)
        
        canvas = base

    # Draw Top Progress Bar across all scenes
    draw_top_progress(canvas, frame_idx + 1, TOTAL_FRAMES)
    
    # Convert RGBA to RGB and write
    frame_rgb = canvas.convert('RGB')
    writer.append_data(np.array(frame_rgb))
    
    if (frame_idx + 1) % 150 == 0 or frame_idx == TOTAL_FRAMES - 1:
        print(f"Rendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({((frame_idx + 1)/TOTAL_FRAMES)*100:.1f}%)...")

writer.close()
print(f"Video generated successfully at: {output_path}")
