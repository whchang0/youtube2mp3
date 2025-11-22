#!/usr/bin/env python3
"""
Generate icon for YouTube to MP3 converter
Creates PNG and ICO files
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("Pillow not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont
    import os

def create_icon():
    """Create application icon"""
    # Create 256x256 image
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background circle (YouTube red)
    center = size // 2
    radius = size // 2 - 10
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=(255, 0, 0, 255)  # YouTube red
    )
    
    # Draw play button triangle (white)
    triangle_size = radius * 0.6
    triangle_points = [
        (center - triangle_size * 0.4, center - triangle_size * 0.6),
        (center - triangle_size * 0.4, center + triangle_size * 0.6),
        (center + triangle_size * 0.6, center)
    ]
    draw.polygon(triangle_points, fill=(255, 255, 255, 255))
    
    # Draw MP3 text at bottom
    try:
        # Try to use a font
        font_size = int(size * 0.15)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    text = "MP3"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = center - text_width // 2
    text_y = size - text_height - 20
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Save PNG
    img.save('youtube2mp3.png', 'PNG')
    print("Created youtube2mp3.png")
    
    # Create ICO with multiple sizes
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = []
    for ico_size in ico_sizes:
        ico_img = img.resize(ico_size, Image.Resampling.LANCZOS)
        ico_images.append(ico_img)
    
    ico_images[0].save('youtube2mp3.ico', format='ICO', sizes=[(s[0], s[1]) for s in ico_sizes])
    print("Created youtube2mp3.ico")
    
    # Also create a 48x48 PNG for app icon
    icon_48 = img.resize((48, 48), Image.Resampling.LANCZOS)
    icon_48.save('youtube2mp3_48.png', 'PNG')
    print("Created youtube2mp3_48.png")

if __name__ == "__main__":
    create_icon()

