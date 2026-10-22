import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio

WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_DURATION = 31.0 # seconds
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)

FONT_BOLD_PATH = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG_PATH = "C:/Windows/Fonts/arial.ttf"

GOLD_COLOR = (190, 175, 135)
GOLD_LIGHT = (212, 198, 160)
DARK_BG = (18, 18, 18)
WHITE = (255, 255, 255)

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def create_glass_card(draw, x0, y0, x1, y1, radius=24, fill=(18, 18, 18, 210), outline=(190, 175, 135, 180), width=3):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def render_ken_burns(img, frame_ratio, target_w=WIDTH, target_h=HEIGHT, zoom_start=1.0, zoom_end=1.08):
    # Create beautiful blurred background
    # Scale img to fill 1080x1920 for blur
    bg_w, bg_h = img.size
    scale_bg = max(target_w / bg_w, target_h / bg_h)
    bg_resized = img.resize((int(bg_w * scale_bg), int(bg_h * scale_bg)), Image.Resampling.LANCZOS)
    # crop center
    left = (bg_resized.width - target_w) // 2
    top = (bg_resized.height - target_h) // 2
    bg_cropped = bg_resized.crop((left, top, left + target_w, top + target_h))
    bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=35))
    
    # Darken blurred background slightly
    dark_overlay = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 130))
    bg_blurred = Image.alpha_composite(bg_blurred.convert('RGBA'), dark_overlay)

    # Foreground image with smooth zoom
    current_zoom = zoom_start + (zoom_end - zoom_start) * frame_ratio
    # Foreground width fits ~960px with padding
    fg_base_w = 980
    fg_base_h = int(bg_h * (fg_base_w / bg_w))
    if fg_base_h > 1200:
        fg_base_h = 1200
        fg_base_w = int(bg_w * (fg_base_h / bg_h))
        
    cur_w = int(fg_base_w * current_zoom)
    cur_h = int(fg_base_h * current_zoom)
    fg_resized = img.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
    
    # Crop fg to fixed container (980 x fg_base_h) with rounded corners
    c_left = (cur_w - 980) // 2
    c_top = (cur_h - fg_base_h) // 2
    fg_clipped = fg_resized.crop((c_left, c_top, c_left + 980, c_top + fg_base_h))
    
    # Rounded corners mask
    mask = Image.new('L', (980, fg_base_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, 980, fg_base_h], radius=28, fill=255)
    
    # Shadow and border
    paste_x = (target_w - 980) // 2
    paste_y = (target_h - fg_base_h) // 2 - 40 # slightly higher than center to leave room for text
    
    # Draw subtle shadow on background
    shadow_box = Image.new('RGBA', (target_w, target_h), (0,0,0,0))
    s_draw = ImageDraw.Draw(shadow_box)
    s_draw.rounded_rectangle([paste_x - 6, paste_y - 6, paste_x + 986, paste_y + fg_base_h + 10], radius=32, fill=(0, 0, 0, 160))
    bg_blurred = Image.alpha_composite(bg_blurred, shadow_box)
    
    # Paste fg
    bg_blurred.paste(fg_clipped, (paste_x, paste_y), mask)
    
    # Draw gold border around fg
    border_overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,0))
    b_draw = ImageDraw.Draw(border_overlay)
    b_draw.rounded_rectangle([paste_x, paste_y, paste_x + 980, paste_y + fg_base_h], radius=28, fill=None, outline=GOLD_COLOR + (220,), width=3)
    bg_blurred = Image.alpha_composite(bg_blurred, border_overlay)
    
    return bg_blurred, paste_y, fg_base_h

print("Helper loaded.")
