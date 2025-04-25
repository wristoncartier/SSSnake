import os
from PIL import Image, ImageDraw, ImageFont
import io

# Create a simple icon
def create_icon(size=1024):
    # Create a new image with a transparent background
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle for the background
    bg_color = (26, 26, 42, 255)  # Dark purple background
    draw.rounded_rectangle([(50, 50), (size-50, size-50)], radius=100, fill=bg_color)
    
    # Draw an S snake
    snake_color = (0, 255, 143, 255)  # SSSnake green
    
    # Draw the snake body (S shape)
    line_width = 80
    points = []
    
    # Top curve
    for i in range(0, 180):
        angle = i * 3.14159 / 180
        x = size/2 + 200 * (1 - angle/3.14159)
        y = size/2 - 200 + 200 * angle/3.14159
        points.append((x, y))
    
    # Bottom curve
    for i in range(0, 180):
        angle = i * 3.14159 / 180
        x = size/2 - 200 + 200 * angle/3.14159
        y = size/2 + 200 * (1 - angle/3.14159)
        points.append((x, y))
    
    # Draw the snake
    for i in range(1, len(points)):
        draw.line([points[i-1], points[i]], fill=snake_color, width=line_width)
    
    # Add snake eyes
    eye_size = 30
    draw.ellipse([(points[0][0]-eye_size, points[0][1]-eye_size), 
                 (points[0][0]+eye_size, points[0][1]+eye_size)], 
                 fill=(255, 255, 255, 255))
    
    # Add pupil
    pupil_size = 15
    draw.ellipse([(points[0][0]-pupil_size, points[0][1]-pupil_size), 
                 (points[0][0]+pupil_size, points[0][1]+pupil_size)], 
                 fill=(0, 0, 0, 255))
    
    return img

# Create the icon
icon = create_icon(1024)

# Save the icon
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SSSnake.app/Contents/Resources/AppIcon.icns")
icon.save(icon_path.replace(".icns", ".png"))

# Convert to icns format using iconutil (macOS command)
png_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AppIcon.iconset")
if not os.path.exists(png_dir):
    os.makedirs(png_dir)

# Create different sizes for the iconset
sizes = [16, 32, 64, 128, 256, 512, 1024]
for size in sizes:
    resized = icon.resize((size, size), Image.LANCZOS)
    resized.save(os.path.join(png_dir, f"icon_{size}x{size}.png"))
    # Also save the @2x version
    if size * 2 <= 1024:
        resized2x = icon.resize((size*2, size*2), Image.LANCZOS)
        resized2x.save(os.path.join(png_dir, f"icon_{size}x{size}@2x.png"))

print(f"Icon created at {png_dir}")
print("To convert to .icns, run:")
print(f"iconutil -c icns {png_dir}")
