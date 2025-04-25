import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPainterPath
from PyQt6.QtCore import Qt, QSize, QRect, QPoint

def create_roblox_icon():
    """Create a Roblox icon"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw stylized 'R' for Roblox
    painter.drawLine(8, 6, 8, 18)    # Vertical line
    painter.drawLine(8, 6, 14, 6)    # Top horizontal
    painter.drawLine(14, 6, 16, 8)   # Top right curve
    painter.drawLine(16, 8, 16, 10)  # Right vertical
    painter.drawLine(16, 10, 14, 12) # Middle right curve
    painter.drawLine(8, 12, 14, 12)  # Middle horizontal
    painter.drawLine(12, 12, 16, 18) # Diagonal to bottom
    
    painter.end()
    pixmap.save("icons/roblox.png")

def generate_icons():
    """Generate all the necessary icons for the application in Windsurf style"""
    # Windsurf uses flat, minimalist SVG-like icons
    
    # Create the icons directory if it doesn't exist
    if not os.path.exists("icons"):
        os.makedirs("icons")
    
    # Generate home icon (house)
    create_home_icon()
    
    # Generate open file icon (folder)
    create_open_icon()
    
    # Generate save icon (disk)
    create_save_icon()
    
    # Generate script icon (code brackets)
    create_script_icon()
    
    # Generate hub icon (grid of squares)
    create_hub_icon()
    
    # Generate profile icon (user)
    create_profile_icon()
    
    # Generate settings icon (gear)
    create_settings_icon()
    
    # Generate run icon (play triangle)
    create_run_icon()
    
    # Generate clear icon (trash)
    create_clear_icon()
    
    # Generate copy icon (copy)
    create_copy_icon()
    
    # Generate inject icon (paperclip)
    create_inject_icon()
    
    # Generate minimize and close icons
    create_window_icons()
    
    # Generate new tab icon
    create_new_tab_icon()
    
    # Generate save all icon
    create_save_all_icon()
    
    # Generate client icon
    create_client_icon()
    
    # Generate Roblox icon
    create_roblox_icon()
    
    print("Windsurf-style icons generated successfully!")

def create_home_icon():
    """Create a home icon (house)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw house
    painter.drawLine(4, 12, 12, 4)  # Left roof
    painter.drawLine(12, 4, 20, 12)  # Right roof
    painter.drawRect(6, 12, 12, 8)   # House body
    
    painter.end()
    pixmap.save("icons/home.png")

def create_script_icon():
    """Create a script icon (code brackets)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw code brackets
    painter.drawLine(8, 6, 4, 12)    # Left bracket top
    painter.drawLine(4, 12, 8, 18)   # Left bracket bottom
    painter.drawLine(16, 6, 20, 12)  # Right bracket top
    painter.drawLine(20, 12, 16, 18) # Right bracket bottom
    
    painter.end()
    pixmap.save("icons/script.png")

def create_hub_icon():
    """Create a hub icon (grid of squares)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw grid
    painter.drawRect(6, 6, 5, 5)    # Top left
    painter.drawRect(13, 6, 5, 5)   # Top right
    painter.drawRect(6, 13, 5, 5)   # Bottom left
    painter.drawRect(13, 13, 5, 5)  # Bottom right
    
    painter.end()
    pixmap.save("icons/hub.png")

def create_profile_icon():
    """Create a profile icon (user)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw user icon
    painter.drawEllipse(9, 6, 6, 6)  # Head
    painter.drawArc(6, 12, 12, 10, 0, 180 * 16)  # Body
    
    painter.end()
    pixmap.save("icons/profile.png")

def create_settings_icon():
    """Create a settings icon (gear)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw gear
    painter.drawEllipse(8, 8, 8, 8)  # Inner circle
    
    # Draw gear teeth
    for i in range(8):
        angle = i * 45
        rad = angle * 3.14159 / 180
        x1 = 12 + 4 * 1.4 * 0.7071 * (1 if angle % 90 == 0 else 0.7071) * (1 if angle < 180 else -1) * (1 if angle % 180 != 0 else 0)
        y1 = 12 + 4 * 1.4 * 0.7071 * (1 if angle % 90 != 0 else 0.7071) * (1 if angle > 90 and angle < 270 else -1) * (1 if angle % 180 != 90 else 0)
        x2 = 12 + 6 * 0.7071 * (1 if angle % 90 == 0 else 0.7071) * (1 if angle < 180 else -1) * (1 if angle % 180 != 0 else 0)
        y2 = 12 + 6 * 0.7071 * (1 if angle % 90 != 0 else 0.7071) * (1 if angle > 90 and angle < 270 else -1) * (1 if angle % 180 != 90 else 0)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    painter.end()
    pixmap.save("icons/settings.png")

def create_run_icon():
    """Create a run icon (play triangle)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw play triangle
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#ffffff")))
    
    points = [QPoint(8, 6), QPoint(18, 12), QPoint(8, 18)]
    painter.drawPolygon(points)
    
    painter.end()
    pixmap.save("icons/run.png")

def create_clear_icon():
    """Create a clear icon (trash)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw trash can
    painter.drawRect(7, 10, 10, 10)  # Body
    painter.drawLine(7, 10, 5, 7)    # Left handle
    painter.drawLine(17, 10, 19, 7)  # Right handle
    painter.drawLine(5, 7, 19, 7)    # Top
    
    # Draw lines inside trash
    painter.drawLine(10, 12, 10, 18)
    painter.drawLine(14, 12, 14, 18)
    
    painter.end()
    pixmap.save("icons/clear.png")

def create_copy_icon():
    """Create a copy icon (two rectangles)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw copy icon
    painter.drawRect(8, 8, 10, 10)  # Front document
    painter.drawRect(6, 6, 10, 10)  # Back document
    
    painter.end()
    pixmap.save("icons/copy.png")

def create_inject_icon():
    """Create an inject icon (paperclip)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw paperclip shape
    path = QPainterPath()
    path.moveTo(8, 6)       # Start at top left
    path.arcTo(8, 6, 8, 6, 180, -180)  # Top arc
    path.lineTo(16, 16)     # Right vertical line
    path.arcTo(8, 16, 8, 6, 0, -180)   # Bottom arc
    path.lineTo(8, 6)       # Left vertical line
    
    painter.drawPath(path)
    
    painter.end()
    pixmap.save("icons/inject.png")

def create_clip_icon():
    """Create a clip icon (clip)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw clip shape
    painter.drawRect(8, 8, 8, 8)  # Main body
    painter.drawLine(8, 8, 16, 8)  # Top clip
    painter.drawLine(8, 16, 16, 16)  # Bottom clip
    
    painter.end()
    pixmap.save("icons/clip.png")

def create_window_icons():
    """Create minimize and close icons"""
    # Minimize icon
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw minimize line
    painter.drawLine(8, 12, 16, 12)
    
    painter.end()
    pixmap.save("icons/minimize.png")
    
    # Close icon
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw X
    painter.drawLine(8, 8, 16, 16)
    painter.drawLine(16, 8, 8, 16)
    
    painter.end()
    pixmap.save("icons/close.png")

def create_new_tab_icon():
    """Create a new tab icon (plus)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw plus
    painter.drawLine(12, 6, 12, 18)  # Vertical
    painter.drawLine(6, 12, 18, 12)  # Horizontal
    
    painter.end()
    pixmap.save("icons/new_tab.png")

def create_open_icon():
    """Create an open file icon (folder)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw folder
    painter.drawRect(4, 8, 16, 12)  # Folder body
    painter.drawLine(4, 8, 8, 4)    # Left top
    painter.drawLine(8, 4, 12, 4)   # Top
    painter.drawLine(12, 4, 12, 8)  # Right top
    
    painter.end()
    pixmap.save("icons/open.png")

def create_save_icon():
    """Create a save icon (disk)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw save icon
    painter.drawRect(5, 5, 14, 14)  # Outer square
    painter.drawRect(8, 12, 8, 7)   # Inner rectangle
    painter.drawRect(7, 5, 10, 5)   # Top rectangle
    
    painter.end()
    pixmap.save("icons/save.png")

def create_save_all_icon():
    """Create a save all icon (multiple disks)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw save all icon (two disks)
    painter.drawRect(7, 7, 12, 12)  # Front disk
    painter.drawRect(5, 5, 12, 12)  # Back disk
    
    painter.end()
    pixmap.save("icons/save_all.png")

def create_client_icon():
    """Create a client icon (computer)"""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#ffffff"), 1.5))
    
    # Draw computer
    painter.drawRect(5, 6, 14, 10)  # Monitor
    painter.drawRect(8, 16, 8, 2)   # Stand
    painter.drawLine(6, 18, 18, 18) # Base
    
    painter.end()
    pixmap.save("icons/client.png")

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create QApplication instance first
    generate_icons()
    sys.exit(0)  # Exit without starting the event loop
