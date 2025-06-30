#!/usr/bin/env python3
"""
Create real ICO file for installer
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a real ICO file"""
    # Create a 256x256 image
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background circle
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=4)
    
    # Draw building icon
    building_color = (255, 255, 255, 255)
    
    # Main building
    building_x = size // 2 - 40
    building_y = size // 2 - 30
    building_w = 80
    building_h = 60
    
    draw.rectangle([building_x, building_y, building_x + building_w, building_y + building_h], 
                  fill=building_color, outline=(236, 240, 241, 255), width=2)
    
    # Windows
    window_size = 8
    for row in range(3):
        for col in range(4):
            x = building_x + 15 + col * 15
            y = building_y + 15 + row * 15
            draw.rectangle([x, y, x + window_size, y + window_size], 
                         fill=(52, 152, 219, 255))
    
    # Door
    door_x = building_x + building_w // 2 - 8
    door_y = building_y + building_h - 20
    draw.rectangle([door_x, door_y, door_x + 16, door_y + 20], 
                  fill=(52, 152, 219, 255))
    
    # Save as ICO with multiple sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for icon_size in icon_sizes:
        resized = img.resize(icon_size, Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Save as ICO
    images[0].save('app_icon.ico', format='ICO', sizes=[(img.width, img.height) for img in images])
    print("✅ Real ICO file created: app_icon.ico")

def create_banner():
    """Create installer banner"""
    # Create banner image
    banner = Image.new('RGB', (497, 314), (52, 152, 219))
    draw = ImageDraw.Draw(banner)
    
    # Add text
    try:
        # Try to use a system font
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    title = "AI Architectural\nSpace Analyzer PRO"
    draw.multiline_text((50, 80), title, fill=(255, 255, 255), font=font_large, align='left')
    
    # Subtitle
    subtitle = "Professional CAD Analysis Software"
    draw.text((50, 200), subtitle, fill=(236, 240, 241), font=font_small)
    
    # Version
    version = "Version 2.0 - Enterprise Edition"
    draw.text((50, 250), version, fill=(189, 195, 199), font=font_small)
    
    # Save as BMP
    banner.save('installer_banner.bmp', format='BMP')
    print("✅ Installer banner created: installer_banner.bmp")

def main():
    """Create all required assets"""
    print("🎨 Creating installer assets...")
    
    try:
        create_app_icon()
        create_banner()
        print("\n✅ ALL ASSETS CREATED SUCCESSFULLY!")
        print("\nNow run: build_installer.bat")
        
    except ImportError:
        print("❌ PIL (Pillow) not installed")
        print("Installing Pillow...")
        os.system("pip install Pillow")
        
        # Try again
        create_app_icon()
        create_banner()
        print("\n✅ ALL ASSETS CREATED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCreating simple fallback assets...")
        
        # Create minimal ICO file manually
        create_minimal_ico()

def create_minimal_ico():
    """Create minimal ICO file without PIL"""
    # Simple 16x16 ICO file header + bitmap data
    ico_data = bytes([
        # ICO header
        0x00, 0x00,  # Reserved
        0x01, 0x00,  # Type (1 = ICO)
        0x01, 0x00,  # Number of images
        
        # Image directory entry
        0x10,        # Width (16)
        0x10,        # Height (16)
        0x00,        # Colors (0 = no palette)
        0x00,        # Reserved
        0x01, 0x00,  # Planes
        0x20, 0x00,  # Bits per pixel (32)
        0x00, 0x04, 0x00, 0x00,  # Size of image data
        0x16, 0x00, 0x00, 0x00,  # Offset to image data
        
        # Bitmap data (16x16 32-bit RGBA)
    ] + [0x34, 0x98, 0xDB, 0xFF] * 256)  # Blue pixels
    
    with open('app_icon.ico', 'wb') as f:
        f.write(ico_data)
    
    print("✅ Minimal ICO file created")

if __name__ == "__main__":
    main()