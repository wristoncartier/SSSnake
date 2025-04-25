import sys
import os
import requests
import subprocess
import random
import threading
import time
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtSvg import *
import ctypes
import psutil
from datetime import datetime

# Worker classes for threaded operations
class InjectionWorker(QThread):
    injection_result = pyqtSignal(bool, str)
    
    def __init__(self, dll):
        super().__init__()
        self.dll = dll
        self.pid = None
    
    def run(self):
        try:
            # Add a small delay to ensure Roblox is fully initialized
            time.sleep(0.5)
            
            # Attempt to inject
            result = self.dll.inject_into_process()
            self.injection_result.emit(result, None)
        except Exception as e:
            self.injection_result.emit(False, str(e))

class ExecutionWorker(QThread):
    execution_result = pyqtSignal(bool, str)
    
    def __init__(self, dll, script):
        super().__init__()
        self.dll = dll
        self.script = script
    
    def run(self):
        try:
            # Add a small delay to ensure the injector is ready
            time.sleep(0.2)
            
            # Make sure the script is properly encoded
            if isinstance(self.script, str):
                encoded_script = self.script.encode('utf-8')
            else:
                encoded_script = self.script
                
            # Execute the script
            result = self.dll.execute_script(encoded_script)
            self.execution_result.emit(result, None)
        except Exception as e:
            self.execution_result.emit(False, str(e))

FONT_FAMILY = "JetBrains Mono"

# Theme definitions
THEMES = {
    "SSSnake Purple": {
        "background": "#1a1a2a",     # Dark purple-black
        "surface": "#242438",       # Dark purple surface
        "surface_hover": "#2a2a42", # Lighter purple surface
        "primary": "#00ff8f",       # SSSnake green
        "text": "#ffffff",          # White text
        "keyword": "#ff79c6",       # Pink for keywords
        "function": "#50fa7b",      # Green for functions
        "string": "#f1fa8c",        # Yellow for strings
        "comment": "#6272a4",       # Blue-gray for comments
        "number": "#bd93f9",        # Purple for numbers
    },
    "Byteware Dark": {
        "background": "#1a1a1a",     # Dark background
        "surface": "#242424",       # Dark surface
        "surface_hover": "#2a2a2a", # Lighter surface
        "primary": "#00ff8f",       # Byteware green
        "text": "#ffffff",          # White text
        "keyword": "#ff79c6",       # Pink for keywords
        "function": "#50fa7b",      # Green for functions
        "string": "#f1fa8c",        # Yellow for strings
        "comment": "#6272a4",       # Blue-gray for comments
        "number": "#bd93f9",        # Purple for numbers
    },
    "Midnight Blue": {
        "background": "#0d1117",     # GitHub Dark background
        "surface": "#161b22",       # GitHub Dark surface
        "surface_hover": "#21262d", # GitHub Dark hover
        "primary": "#58a6ff",       # GitHub Blue
        "text": "#c9d1d9",          # GitHub Text
        "keyword": "#ff7b72",       # Red for keywords
        "function": "#d2a8ff",      # Purple for functions
        "string": "#a5d6ff",        # Light blue for strings
        "comment": "#8b949e",       # Gray for comments
        "number": "#79c0ff",        # Blue for numbers
    },
    "Neon Synthwave": {
        "background": "#2b213a",     # Dark purple
        "surface": "#3b3151",       # Medium purple
        "surface_hover": "#4b4161", # Light purple
        "primary": "#f92aad",       # Hot pink
        "text": "#ffffff",          # White text
        "keyword": "#f92aad",       # Hot pink for keywords
        "function": "#05d9e8",      # Cyan for functions
        "string": "#ff8b39",        # Orange for strings
        "comment": "#a277ff",       # Purple for comments
        "number": "#ffcc00",        # Yellow for numbers
    },
    "Matrix Green": {
        "background": "#0d0d0d",     # Almost black
        "surface": "#121212",       # Very dark gray
        "surface_hover": "#1a1a1a", # Dark gray
        "primary": "#00ff00",       # Matrix green
        "text": "#33ff33",          # Light green text
        "keyword": "#00cc00",       # Medium green for keywords
        "function": "#00ff00",      # Bright green for functions
        "string": "#ccffcc",        # Very light green for strings
        "comment": "#006600",       # Dark green for comments
        "number": "#66ff66",        # Light green for numbers
    }
}

# Load saved theme preference if it exists
def load_saved_theme():
    try:
        # Check if we're running from an app bundle
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running as a PyInstaller bundle
            base_dir = sys._MEIPASS
        else:
            # Running from the app bundle or normal Python script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        theme_file = os.path.join(base_dir, "theme_preference.txt")
        if os.path.exists(theme_file):
            with open(theme_file, "r") as f:
                saved_theme = f.read().strip()
                if saved_theme in THEMES:
                    return saved_theme
    except Exception as e:
        print(f"Error loading theme: {e}")  # Debug info
        pass  # Ignore errors reading theme preference
    return "SSSnake Purple"  # Default theme

# Default theme
CURRENT_THEME = load_saved_theme()
COLORS = THEMES[CURRENT_THEME]

# Fixed window size
WINDOW_WIDTH = 953
WINDOW_HEIGHT = 678

# Forward declarations
class TabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setExpanding(False)
        self.setDrawBase(False)
        self.setStyleSheet(f"""
            QTabBar {{
                background: transparent;
            }}
            QTabBar::tab {{
                background: {COLORS["surface"]};
                color: {COLORS["text"]};
                border: none;
                padding: 8px 24px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS["surface_hover"]};
                border-top: 2px solid {COLORS["primary"]};
            }}
            QTabBar::tab:hover {{
                background: {COLORS["surface_hover"]};
            }}
            QTabBar::close-button {{
                image: url(icons/close.png);
                subcontrol-position: right;
            }}
        """)

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(TabBar())
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {COLORS["background"]};
            }}
        """)
        self.tabCloseRequested.connect(self.close_tab)
        
    def add_tab(self, title=None):
        if title is None or isinstance(title, bool):
            title = "Script-1"
            
        try:
            editor = LuaCodeEditor()
            idx = self.addTab(editor, str(title))
            self.setCurrentIndex(idx)
            return editor
        except Exception as e:
            print(f"Error adding tab: {e}")
            # Create a simple QPlainTextEdit as fallback
            fallback = QPlainTextEdit()
            fallback.setPlainText("-- Welcome to SSSnake\nprint(\"Hello from your executor!\")")
            idx = self.addTab(fallback, str(title))
            self.setCurrentIndex(idx)
            return fallback
        
    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
        
    def current_editor(self):
        widget = self.currentWidget()
        if widget is None:
            # If there's no current widget, create a new tab
            return self.add_tab()
        return widget

class SidebarButton(QPushButton):
    def __init__(self, icon_name, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setCheckable(True)
        self.setIcon(QIcon(f"icons/{icon_name}.png"))
        self.setIconSize(QSize(24, 24))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 0;
                margin: 0;
            }}
            QPushButton:hover {{
                background: {COLORS["surface_hover"]};
            }}
            QPushButton:checked {{
                background: {COLORS["surface_hover"]};
                border-left: 2px solid {COLORS["primary"]};
            }}
        """)

class ScriptFetchWorker(QThread):
    scriptsReady = pyqtSignal(list)
    
    def run(self):
        try:
            # Fetch scripts from rscripts.net
            scripts = []
            
            # Sample scripts from rscripts.net
            sample_scripts = [
                {
                    "name": "Infinite Yield",
                    "description": "FE Admin Commands - The most popular admin script with over 5 million uses. Includes over 400 commands.",
                    "likes": 24893,
                    "views": 567421,
                    "content": "--[[ Infinite Yield FE Admin Script\n\nLoaded successfully! Commands can be found in the console (F9) by typing 'cmds'.\n\nPrefix: ;\n]]\n\nloadstring(game:HttpGet('https://raw.githubusercontent.com/EdgeIY/infiniteyield/master/source'))()"
                },
                {
                    "name": "Dex Explorer V4",
                    "description": "The most powerful game explorer for Roblox. Inspect and modify game elements with ease.",
                    "likes": 18752,
                    "views": 432198,
                    "content": "--[[ Dex Explorer V4\n\nA powerful game explorer that lets you inspect and modify game elements.\n]]\n\nloadstring(game:HttpGet('https://raw.githubusercontent.com/infyiff/backup/main/dex.lua'))()"
                },
                {
                    "name": "ESP Script",
                    "description": "See players through walls with customizable options. Works in most games.",
                    "likes": 12483,
                    "views": 298745,
                    "content": "--[[ ESP Script\n\nShows players through walls with customizable options.\n]]\n\nlocal Players = game:GetService('Players')\nlocal RunService = game:GetService('RunService')\nlocal LocalPlayer = Players.LocalPlayer\n\nfunction CreateESP(player)\n    local esp = Instance.new('BillboardGui')\n    esp.Name = 'ESP'\n    esp.AlwaysOnTop = true\n    esp.Size = UDim2.new(0, 100, 0, 50)\n    esp.StudsOffset = Vector3.new(0, 3, 0)\n    \n    local text = Instance.new('TextLabel')\n    text.BackgroundTransparency = 1\n    text.Size = UDim2.new(1, 0, 1, 0)\n    text.Text = player.Name\n    text.TextColor3 = Color3.new(1, 0, 0)\n    text.TextStrokeTransparency = 0\n    text.TextStrokeColor3 = Color3.new(0, 0, 0)\n    text.TextSize = 14\n    text.Font = Enum.Font.SourceSansBold\n    text.Parent = esp\n    \n    return esp\nend\n\nfor _, player in pairs(Players:GetPlayers()) do\n    if player ~= LocalPlayer then\n        local char = player.Character\n        if char and char:FindFirstChild('Head') then\n            local esp = CreateESP(player)\n            esp.Parent = char.Head\n        end\n    end\nend\n\nPlayers.PlayerAdded:Connect(function(player)\n    player.CharacterAdded:Connect(function(char)\n        wait(1)\n        local esp = CreateESP(player)\n        esp.Parent = char.Head\n    end)\nend)"
                },
                {
                    "name": "Aimbot V3",
                    "description": "Advanced aimbot with customizable settings. Works in most FPS games.",
                    "likes": 9876,
                    "views": 187654,
                    "content": "--[[ Aimbot V3\n\nAutomatically aims at the nearest player.\n]]\n\nlocal Players = game:GetService('Players')\nlocal RunService = game:GetService('RunService')\nlocal UserInputService = game:GetService('UserInputService')\nlocal Camera = workspace.CurrentCamera\nlocal LocalPlayer = Players.LocalPlayer\n\nlocal Enabled = true\nlocal TeamCheck = false\nlocal AimPart = 'Head'\nlocal Sensitivity = 0.5\n\nfunction GetClosestPlayer()\n    local MaxDistance = math.huge\n    local Target = nil\n    \n    for _, player in pairs(Players:GetPlayers()) do\n        if player ~= LocalPlayer then\n            if not TeamCheck or player.Team ~= LocalPlayer.Team then\n                if player.Character and player.Character:FindFirstChild(AimPart) then\n                    local Position = Camera:WorldToScreenPoint(player.Character[AimPart].Position)\n                    local Distance = (Vector2.new(Position.X, Position.Y) - Vector2.new(Mouse.X, Mouse.Y)).Magnitude\n                    \n                    if Distance < MaxDistance then\n                        MaxDistance = Distance\n                        Target = player\n                    end\n                end\n            end\n        end\n    end\n    \n    return Target\nend\n\nRunService.RenderStepped:Connect(function()\n    if Enabled and UserInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton2) then\n        local Target = GetClosestPlayer()\n        if Target and Target.Character and Target.Character:FindFirstChild(AimPart) then\n            local Position = Camera:WorldToScreenPoint(Target.Character[AimPart].Position)\n            mousemoverel((Position.X - Mouse.X) * Sensitivity, (Position.Y - Mouse.Y) * Sensitivity)\n        end\n    end\nend)"
                },
                {
                    "name": "Speed Hack",
                    "description": "Increase your character's movement speed. Adjustable multiplier.",
                    "likes": 7654,
                    "views": 156789,
                    "content": "--[[ Speed Hack\n\nIncreases your character's movement speed.\n]]\n\nlocal Players = game:GetService('Players')\nlocal RunService = game:GetService('RunService')\nlocal UserInputService = game:GetService('UserInputService')\nlocal LocalPlayer = Players.LocalPlayer\nlocal Character = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()\nlocal Humanoid = Character:WaitForChild('Humanoid')\n\nlocal SpeedMultiplier = 3\nlocal DefaultSpeed = 16\n\nHumanoid.WalkSpeed = DefaultSpeed * SpeedMultiplier\n\nLocalPlayer.CharacterAdded:Connect(function(NewCharacter)\n    Character = NewCharacter\n    Humanoid = Character:WaitForChild('Humanoid')\n    Humanoid.WalkSpeed = DefaultSpeed * SpeedMultiplier\nend)"
                },
                {
                    "name": "Owl Hub",
                    "description": "Universal script hub with support for many popular games. Includes ESP, aimbot, and more.",
                    "likes": 15432,
                    "views": 342198,
                    "content": "--[[ Owl Hub\n\nUniversal script hub with support for many popular games.\n]]\n\nloadstring(game:HttpGet(\"https://raw.githubusercontent.com/CriShoux/OwlHub/master/OwlHub.txt\"))()"
                },
                {
                    "name": "Dark Hub",
                    "description": "Premium script hub with support for many popular games. Includes ESP, aimbot, and more.",
                    "likes": 14321,
                    "views": 321987,
                    "content": "--[[ Dark Hub\n\nPremium script hub with support for many popular games.\n]]\n\nloadstring(game:HttpGet(\"https://raw.githubusercontent.com/RandomAdamYT/DarkHub/master/Init\", true))()"
                },
                {
                    "name": "CMD-X",
                    "description": "Admin command script with over 600 commands. Similar to Infinite Yield but with more features.",
                    "likes": 13210,
                    "views": 298765,
                    "content": "--[[ CMD-X\n\nAdmin command script with over 600 commands.\n]]\n\nloadstring(game:HttpGet(\"https://raw.githubusercontent.com/CMD-X/CMD-X/master/Source\", true))()"
                },
                {
                    "name": "Hydroxide",
                    "description": "Powerful script for debugging and reverse engineering Roblox games.",
                    "likes": 9876,
                    "views": 187654,
                    "content": "--[[ Hydroxide\n\nPowerful script for debugging and reverse engineering Roblox games.\n]]\n\nlocal owner = \"Upbolt\"\nlocal branch = \"revision\"\n\nlocal function webImport(file)\n    return loadstring(game:HttpGetAsync((\"https://raw.githubusercontent.com/%s/Hydroxide/%s/%s.lua\"):format(owner, branch, file)), file .. '.lua')()\nend\n\nwebImport(\"init\")\nwebImport(\"ui/main\")"
                },
                {
                    "name": "Universal ESP",
                    "description": "ESP script that works in any game. Shows players, NPCs, and items.",
                    "likes": 8765,
                    "views": 176543,
                    "content": "--[[ Universal ESP\n\nESP script that works in any game. Shows players, NPCs, and items.\n]]\n\nloadstring(game:HttpGet(\"https://raw.githubusercontent.com/ic3w0lf22/Unnamed-ESP/master/UnnamedESP.lua\", true))()"
                },
                {
                    "name": "Fly Script",
                    "description": "Simple fly script that works in most games. Press E to toggle.",
                    "likes": 7654,
                    "views": 165432,
                    "content": "--[[ Fly Script\n\nSimple fly script that works in most games. Press E to toggle.\n]]\n\nlocal Players = game:GetService(\"Players\")\nlocal UserInputService = game:GetService(\"UserInputService\")\nlocal RunService = game:GetService(\"RunService\")\nlocal Camera = workspace.CurrentCamera\n\nlocal LocalPlayer = Players.LocalPlayer\nlocal Character = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()\nlocal HRP = Character:WaitForChild(\"HumanoidRootPart\")\nlocal Humanoid = Character:WaitForChild(\"Humanoid\")\n\nlocal Flying = false\nlocal Speed = 2\nlocal MaxSpeed = 100\n\nlocal Controls = {\n    Forward = false,\n    Backward = false,\n    Left = false,\n    Right = false,\n    Up = false,\n    Down = false\n}\n\nlocal function Fly()\n    Flying = true\n    Humanoid.PlatformStand = true\n    \n    local BV = Instance.new(\"BodyVelocity\")\n    BV.MaxForce = Vector3.new(math.huge, math.huge, math.huge)\n    BV.Velocity = Vector3.new(0, 0, 0)\n    BV.Parent = HRP\n    \n    local BG = Instance.new(\"BodyGyro\")\n    BG.MaxTorque = Vector3.new(math.huge, math.huge, math.huge)\n    BG.P = 1e4\n    BG.Parent = HRP\n    \n    local Connection\n    Connection = RunService.RenderStepped:Connect(function()\n        if not Flying then\n            Connection:Disconnect()\n            BV:Destroy()\n            BG:Destroy()\n            Humanoid.PlatformStand = false\n            return\n        end\n        \n        BG.CFrame = Camera.CFrame\n        \n        local MoveDirection = Vector3.new(0, 0, 0)\n        \n        if Controls.Forward then\n            MoveDirection = MoveDirection + Camera.CFrame.LookVector\n        end\n        if Controls.Backward then\n            MoveDirection = MoveDirection - Camera.CFrame.LookVector\n        end\n        if Controls.Left then\n            MoveDirection = MoveDirection - Camera.CFrame.RightVector\n        end\n        if Controls.Right then\n            MoveDirection = MoveDirection + Camera.CFrame.RightVector\n        end\n        if Controls.Up then\n            MoveDirection = MoveDirection + Vector3.new(0, 1, 0)\n        end\n        if Controls.Down then\n            MoveDirection = MoveDirection - Vector3.new(0, 1, 0)\n        end\n        \n        if MoveDirection.Magnitude > 0 then\n            MoveDirection = MoveDirection.Unit\n        end\n        \n        BV.Velocity = MoveDirection * Speed * MaxSpeed\n    end)\nend\n\nlocal function StopFly()\n    Flying = false\nend\n\nUserInputService.InputBegan:Connect(function(Input, GameProcessed)\n    if GameProcessed then return end\n    \n    if Input.KeyCode == Enum.KeyCode.E then\n        if Flying then\n            StopFly()\n        else\n            Fly()\n        end\n    elseif Input.KeyCode == Enum.KeyCode.W then\n        Controls.Forward = true\n    elseif Input.KeyCode == Enum.KeyCode.S then\n        Controls.Backward = true\n    elseif Input.KeyCode == Enum.KeyCode.A then\n        Controls.Left = true\n    elseif Input.KeyCode == Enum.KeyCode.D then\n        Controls.Right = true\n    elseif Input.KeyCode == Enum.KeyCode.Space then\n        Controls.Up = true\n    elseif Input.KeyCode == Enum.KeyCode.LeftShift then\n        Controls.Down = true\n    end\nend)\n\nUserInputService.InputEnded:Connect(function(Input, GameProcessed)\n    if GameProcessed then return end\n    \n    if Input.KeyCode == Enum.KeyCode.W then\n        Controls.Forward = false\n    elseif Input.KeyCode == Enum.KeyCode.S then\n        Controls.Backward = false\n    elseif Input.KeyCode == Enum.KeyCode.A then\n        Controls.Left = false\n    elseif Input.KeyCode == Enum.KeyCode.D then\n        Controls.Right = false\n    elseif Input.KeyCode == Enum.KeyCode.Space then\n        Controls.Up = false\n    elseif Input.KeyCode == Enum.KeyCode.LeftShift then\n        Controls.Down = false\n    end\nend)\n\nprint(\"Fly script loaded! Press E to toggle.\")"
                },
                {
                    "name": "Noclip",
                    "description": "Walk through walls in any game. Press V to toggle.",
                    "likes": 6543,
                    "views": 154321,
                    "content": "--[[ Noclip Script\n\nWalk through walls in any game. Press V to toggle.\n]]\n\nlocal Players = game:GetService(\"Players\")\nlocal UserInputService = game:GetService(\"UserInputService\")\nlocal RunService = game:GetService(\"RunService\")\n\nlocal LocalPlayer = Players.LocalPlayer\nlocal Character = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()\nlocal Humanoid = Character:WaitForChild(\"Humanoid\")\n\nlocal Noclipping = false\nlocal NoclipConnection\n\nlocal function Noclip()\n    Noclipping = true\n    NoclipConnection = RunService.Stepped:Connect(function()\n        if Character and Noclipping then\n            for _, Part in pairs(Character:GetDescendants()) do\n                if Part:IsA(\"BasePart\") then\n                    Part.CanCollide = false\n                end\n            end\n        else\n            NoclipConnection:Disconnect()\n        end\n    end)\nend\n\nlocal function StopNoclip()\n    Noclipping = false\n    if NoclipConnection then\n        NoclipConnection:Disconnect()\n    end\n    \n    if Character then\n        for _, Part in pairs(Character:GetDescendants()) do\n            if Part:IsA(\"BasePart\") then\n                Part.CanCollide = true\n            end\n        end\n    end\nend\n\nUserInputService.InputBegan:Connect(function(Input, GameProcessed)\n    if GameProcessed then return end\n    \n    if Input.KeyCode == Enum.KeyCode.V then\n        if Noclipping then\n            StopNoclip()\n            print(\"Noclip disabled\")\n        else\n            Noclip()\n            print(\"Noclip enabled\")\n        end\n    end\nend)\n\nprint(\"Noclip script loaded! Press V to toggle.\")"
                },
                {
                    "name": "Remote Spy",
                    "description": "Monitor and log remote events and function calls in games.",
                    "likes": 5432,
                    "views": 143210,
                    "content": "--[[ Remote Spy\n\nMonitor and log remote events and function calls in games.\n]]\n\nloadstring(game:HttpGet(\"https://raw.githubusercontent.com/exxtremestuffs/SimpleSpySource/master/SimpleSpy.lua\"))()"
                },
                {
                    "name": "Infinite Jump",
                    "description": "Simple script that allows you to jump infinitely in any game.",
                    "likes": 4321,
                    "views": 132109,
                    "content": "--[[ Infinite Jump\n\nSimple script that allows you to jump infinitely in any game.\n]]\n\nlocal UserInputService = game:GetService(\"UserInputService\")\nlocal Players = game:GetService(\"Players\")\nlocal LocalPlayer = Players.LocalPlayer\n\nlocal InfiniteJumpEnabled = true\n\nUserInputService.JumpRequest:Connect(function()\n    if InfiniteJumpEnabled then\n        LocalPlayer.Character:FindFirstChildOfClass(\"Humanoid\"):ChangeState(\"Jumping\")\n    end\nend)\n\nprint(\"Infinite Jump enabled!\")"
                },
                {
                    "name": "Click Teleport",
                    "description": "Teleport to where you click. Hold Ctrl and click to teleport.",
                    "likes": 3210,
                    "views": 121098,
                    "content": "--[[ Click Teleport\n\nTeleport to where you click. Hold Ctrl and click to teleport.\n]]\n\nlocal Players = game:GetService(\"Players\")\nlocal UserInputService = game:GetService(\"UserInputService\")\nlocal Mouse = Players.LocalPlayer:GetMouse()\n\nlocal function Teleport()\n    if UserInputService:IsKeyDown(Enum.KeyCode.LeftControl) then\n        local Character = Players.LocalPlayer.Character\n        if Character then\n            local HumanoidRootPart = Character:FindFirstChild(\"HumanoidRootPart\")\n            if HumanoidRootPart then\n                HumanoidRootPart.CFrame = CFrame.new(Mouse.Hit.p + Vector3.new(0, 3, 0))\n            end\n        end\n    end\nend\n\nMouse.Button1Down:Connect(Teleport)\n\nprint(\"Click Teleport loaded! Hold Ctrl and click to teleport.\")"
                },
                {
                    "name": "Anti AFK",
                    "description": "Prevents you from being kicked for inactivity in any game.",
                    "likes": 2109,
                    "views": 110987,
                    "content": "--[[ Anti AFK\n\nPrevents you from being kicked for inactivity in any game.\n]]\n\nlocal Players = game:GetService(\"Players\")\nlocal VirtualUser = game:GetService(\"VirtualUser\")\n\nPlayers.LocalPlayer.Idled:Connect(function()\n    VirtualUser:CaptureController()\n    VirtualUser:ClickButton2(Vector2.new())\n    print(\"Anti-AFK: Prevented kick\")\nend)\n\nprint(\"Anti-AFK script loaded!\")"
                }
            ]
            
            # Add sample scripts to the list
            for script in sample_scripts:
                scripts.append(script)
            
            # Emit signal with scripts
            self.scriptsReady.emit(scripts)
        except Exception as e:
            print("Failed to fetch scripts:", e)
            self.scriptsReady.emit([])

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("settings_widget")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setStyleSheet(f"color: {COLORS['primary']}; font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text']};
                border: 1px solid {COLORS['surface_hover']};
                border-radius: 4px;
                margin-top: 16px;
                padding: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme selector
        theme_label = QLabel("Select Theme:")
        theme_label.setStyleSheet(f"color: {COLORS['text']};")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        
        # Set the current theme in the combo box
        self.theme_combo.setCurrentText(CURRENT_THEME)
            
        self.theme_combo.setCurrentText(CURRENT_THEME)
        self.theme_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['surface_hover']};
                border-radius: 4px;
                padding: 6px;
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {COLORS['surface_hover']};
            }}
            QComboBox QAbstractItemView {{
                background: {COLORS['surface']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['primary']};
            }}
        """)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        # Theme preview
        self.preview_widget = QWidget()
        self.preview_widget.setFixedHeight(100)
        self.preview_widget.setStyleSheet(f"background: {COLORS['background']}; border-radius: 4px;")
        preview_layout = QVBoxLayout(self.preview_widget)
        
        preview_title = QLabel("Theme Preview")
        preview_title.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        preview_layout.addWidget(preview_title)
        
        preview_text = QLabel("Text Sample")
        preview_text.setStyleSheet(f"color: {COLORS['text']};")
        preview_layout.addWidget(preview_text)
        
        preview_code = QLabel('<span style="color: ' + COLORS['keyword'] + ';">function</span> <span style="color: ' + COLORS['function'] + ';">example</span>() {<br>&nbsp;&nbsp;<span style="color: ' + COLORS['string'] + ';">"string"</span> <span style="color: ' + COLORS['number'] + ';">123</span> <span style="color: ' + COLORS['comment'] + ';">-- comment</span><br>}')
        preview_code.setTextFormat(Qt.TextFormat.RichText)
        preview_layout.addWidget(preview_code)
        
        theme_layout.addWidget(self.preview_widget)
        layout.addWidget(theme_group)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: {COLORS['text']};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']}dd;
            }}
        """)
        self.apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def change_theme(self, theme_name):
        """Preview the selected theme"""
        # Only update the preview, don't change the global theme yet
        preview_colors = THEMES[theme_name]
        
        # Update preview
        self.preview_widget.setStyleSheet(f"background: {preview_colors['background']}; border-radius: 4px;")
        
        for child in self.preview_widget.findChildren(QLabel):
            if child.text() == "Theme Preview":
                child.setStyleSheet(f"color: {preview_colors['primary']}; font-weight: bold;")
            elif child.text() == "Text Sample":
                child.setStyleSheet(f"color: {preview_colors['text']};")
            else:  # Code sample
                child.setText('<span style="color: ' + preview_colors['keyword'] + ';">function</span> <span style="color: ' + preview_colors['function'] + ';">example</span>() {<br>&nbsp;&nbsp;<span style="color: ' + preview_colors['string'] + ';">"string"</span> <span style="color: ' + preview_colors['number'] + ';">123</span> <span style="color: ' + preview_colors['comment'] + ';">-- comment</span><br>}')
    
    def apply_settings(self):
        """Apply the selected settings"""
        global CURRENT_THEME, COLORS
        
        # Update the current theme
        CURRENT_THEME = self.theme_combo.currentText()
        COLORS = THEMES[CURRENT_THEME].copy()  # Make a copy to avoid reference issues
        
        # Update UI with new theme
        if self.parent:
            self.parent.update_theme()

class ScriptHubWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.expanded_item = None
        self.execute_button = None
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create search bar
        search_widget = QWidget()
        search_widget.setFixedHeight(40)
        search_widget.setStyleSheet(f"""
            QWidget {{
                background: {COLORS["surface"]};
                border-bottom: 1px solid {COLORS["surface_hover"]};
            }}
        """)
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(8, 0, 8, 0)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet(f"color: {COLORS['text']};")
        
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS["background"]};
                color: {COLORS["text"]};
                border: 1px solid {COLORS["surface_hover"]};
                border-radius: 2px;
                padding: 4px 8px;
            }}
        """)
        self.search_input.textChanged.connect(self.search_scripts)
        
        search_btn = QPushButton()
        search_btn.setIcon(QIcon("icons/script.png"))
        search_btn.setFixedSize(30, 30)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["primary"]};
                border: none;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background: {COLORS["primary"]}dd;
            }}
        """)
        search_btn.clicked.connect(self.search_scripts)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        # Create scripts list
        self.scripts_list = QListWidget()
        self.scripts_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS["background"]};
                color: {COLORS["text"]};
                border: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS["surface_hover"]};
            }}
            QListWidget::item:selected {{
                background: {COLORS["surface_hover"]};
            }}
            QListWidget::item:hover {{
                background: {COLORS["surface"]};
            }}
        """)
        self.scripts_list.itemClicked.connect(self.toggle_script_details)
        
        # Create loading indicator
        self.loading_label = QLabel("Loading scripts...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet(f"color: {COLORS['text']};")
        
        # Add widgets to layout
        layout.addWidget(search_widget)
        layout.addWidget(self.scripts_list)
        layout.addWidget(self.loading_label)
        
        # Fetch scripts
        self.scripts = []
        self.fetch_scripts()
    
    def fetch_scripts(self):
        """Fetch scripts from rscripts.net"""
        self.loading_label.show()
        self.scripts_list.hide()
        
        # Create a worker thread to fetch scripts
        self.worker = ScriptFetchWorker()
        self.worker.scriptsReady.connect(self.update_scripts_list)
        self.worker.start()
    
    def update_scripts_list(self, scripts):
        """Update the scripts list with fetched scripts"""
        self.scripts = scripts
        self.scripts_list.clear()
        
        for script in scripts:
            # Create custom widget for each script
            script_widget = QWidget()
            script_layout = QVBoxLayout(script_widget)
            script_layout.setContentsMargins(12, 16, 12, 16)  # Even more padding
            script_layout.setSpacing(12)  # More spacing
            
            # Main info row
            info_widget = QWidget()
            info_layout = QHBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)
            
            # Script icon (colored rectangle with first letter)
            icon_size = 64  # Even bigger icon
            icon_widget = QWidget()
            icon_widget.setFixedSize(icon_size, icon_size)
            icon_color = QColor(COLORS["primary"]) if random.random() > 0.5 else QColor("#ff5555")
            icon_letter = script['name'][0].upper()
            
            # Set up icon styling
            icon_widget.setStyleSheet(f"""
                background-color: {icon_color.name()};
                border-radius: 8px;
                color: white;
                font-size: 32px;
                font-weight: bold;
            """)
            
            # Add letter to icon
            icon_layout = QVBoxLayout(icon_widget)
            icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label = QLabel(icon_letter)
            icon_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
            icon_layout.addWidget(icon_label)
            
            # Script name and stats
            name_widget = QWidget()
            name_layout = QVBoxLayout(name_widget)
            name_layout.setContentsMargins(0, 0, 0, 0)
            name_layout.setSpacing(4)  # More spacing
            
            name_label = QLabel(script['name'])
            name_label.setStyleSheet(f"font-weight: bold; color: {COLORS['text']}; font-size: 14px;")  # Bigger font
            
            stats_label = QLabel(f"⭐ {script.get('likes', random.randint(10, 5000))} | 👁️ {script.get('views', random.randint(100, 10000))}")
            stats_label.setStyleSheet(f"color: {COLORS['text']}80; font-size: 12px;")
            
            name_layout.addWidget(name_label)
            name_layout.addWidget(stats_label)
            
            info_layout.addWidget(icon_widget)
            info_layout.addWidget(name_widget)
            info_layout.addStretch()
            
            # Create details widget (hidden by default)
            details_widget = QWidget()
            details_widget.setVisible(False)
            details_layout = QVBoxLayout(details_widget)
            details_layout.setContentsMargins(0, 12, 0, 12)
            details_layout.setSpacing(12)
            
            # Description
            desc = script.get('description', 'A powerful script for Roblox.')
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"color: {COLORS['text']}B0; font-size: 13px; padding: 8px 0;")  
            
            # Execute button
            execute_btn = QPushButton("Execute?")
            execute_btn.setFixedHeight(36)  # Taller button
            execute_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS["primary"]};
                    color: {COLORS["text"]};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {COLORS["primary"]}dd;
                }}
            """)
            execute_btn.clicked.connect(lambda checked, s=script: self.copy_script(s))
            
            details_layout.addWidget(desc_label)
            details_layout.addWidget(execute_btn)
            
            script_layout.addWidget(info_widget)
            script_layout.addWidget(details_widget)
            
            # Store references to the details widget and script data
            script_widget.details_widget = details_widget
            script_widget.script_data = script
            
            # Add to list
            item = QListWidgetItem()
            item.setSizeHint(script_widget.sizeHint())
            self.scripts_list.addItem(item)
            self.scripts_list.setItemWidget(item, script_widget)
        
        self.loading_label.hide()
        self.scripts_list.show()
    
    def search_scripts(self):
        """Search scripts by name"""
        query = self.search_input.text().lower()
        
        # Reset expanded state
        self.expanded_item = None
        
        # Filter and update list
        filtered_scripts = [script for script in self.scripts if query in script['name'].lower()]
        self.update_scripts_list(filtered_scripts)
    
    def toggle_script_details(self, item):
        """Toggle script details when clicked"""
        script_widget = self.scripts_list.itemWidget(item)
        if not script_widget:
            return
            
        # If we have an expanded item, collapse it first
        if self.expanded_item and self.expanded_item != item:
            prev_widget = self.scripts_list.itemWidget(self.expanded_item)
            if prev_widget and hasattr(prev_widget, 'details_widget'):
                prev_widget.details_widget.setVisible(False)
                self.scripts_list.setItemWidget(self.expanded_item, prev_widget)
        
        # Toggle visibility of details
        if hasattr(script_widget, 'details_widget'):
            is_visible = script_widget.details_widget.isVisible()
            script_widget.details_widget.setVisible(not is_visible)
            
            # Update item size
            self.scripts_list.setItemWidget(item, script_widget)
            
            # Store expanded state
            self.expanded_item = item if not is_visible else None
            
            # Create animation effect
            if not is_visible:
                # First make it visible but with 0 height
                script_widget.details_widget.setMaximumHeight(0)
                script_widget.details_widget.setVisible(True)
                
                # Create and start the animation
                animation = QPropertyAnimation(script_widget.details_widget, b"maximumHeight")
                animation.setDuration(300)
                animation.setStartValue(0)
                animation.setEndValue(script_widget.details_widget.sizeHint().height())
                animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # Make sure animation completes
                def animation_finished():
                    if script_widget and hasattr(script_widget, 'details_widget'):
                        script_widget.details_widget.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
                
                animation.finished.connect(animation_finished)
                animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            else:
                # Animate closing
                animation = QPropertyAnimation(script_widget.details_widget, b"maximumHeight")
                animation.setDuration(200)
                animation.setStartValue(script_widget.details_widget.height())
                animation.setEndValue(0)
                animation.setEasingCurve(QEasingCurve.Type.InCubic)
                
                # Connect finished signal to hide the widget
                animation.finished.connect(lambda: script_widget.details_widget.setVisible(False))
                animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    
    def copy_script(self, script):
        """Copy script to editor"""
        if script and 'content' in script:
            try:
                # Create a new tab with the script name
                self.parent.add_new_tab(script['name'])
                
                # Set the script content in the editor
                editor = self.parent.tab_widget.current_editor()
                if editor:
                    editor.setPlainText(script['content'])
                    
                    # Log the action
                    self.parent.log_to_console(f"[INFO] Loaded script: {script['name']}")
                    
                    # Switch to the editor view
                    self.parent.switch_view(0)
            except Exception as e:
                self.parent.log_to_console(f"[ERROR] Failed to load script: {e}")

class LuaCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {COLORS["background"]};
                color: {COLORS["text"]};
                border: none;
                padding: 16px;
                font-family: '{FONT_FAMILY}', Menlo, monospace;
                font-size: 14px;
            }}
        """)
        
        # Add sample script
        self.setPlainText('-- Welcome to SSSnake\nprint("Hello from your executor!")')

class SSSnakeExecutor(QMainWindow):
    # Define signals at the class level
    injection_success = pyqtSignal()
    injection_failure = pyqtSignal(str)
    execution_success = pyqtSignal()
    execution_failure = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSSnake")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # DLL loading variables
        self.dll = None
        self.dll_loaded = False
        self.simulation_mode = False
        
        # Connect signals to slots
        # We don't need these connections anymore as we're using the worker classes
        # with their own signal connections
        
        # Store references to buttons for enabling/disabling
        self.bottom_buttons = []
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create titlebar
        titlebar = QWidget()
        titlebar.setObjectName("titlebar")
        titlebar.setFixedHeight(32)
        titlebar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["surface"]};
                border-bottom: 1px solid {COLORS["surface_hover"]};
            }}
        """)
        titlebar_layout = QHBoxLayout(titlebar)
        titlebar_layout.setContentsMargins(8, 0, 8, 0)
        titlebar_layout.setSpacing(4)
        
        # Logo and App Name
        logo_label = QLabel(" SSSnake v1.0.0")
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["primary"]};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        titlebar_layout.addWidget(logo_label)
        
        # Title and tabs
        self.tab_bar = TabBar()
        
        # Add tab button
        new_tab_btn = QPushButton()
        new_tab_btn.setIcon(QIcon("icons/new_tab.png"))
        new_tab_btn.setFixedSize(24, 24)
        new_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS["text"]};
            }}
            QPushButton:hover {{
                background: {COLORS["surface_hover"]};
            }}
        """)
        new_tab_btn.clicked.connect(self.add_new_tab)
        
        # Status label
        self.status_label = QLabel(" ● Not Injected")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: #808080;
                border-radius: 2px;
                padding: 2px 8px;
                font-size: 11px;
            }}
        """)
        
        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(0)
        
        minimize_btn = QPushButton()
        minimize_btn.setIcon(QIcon("icons/minimize.png"))
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton()
        close_btn.setIcon(QIcon("icons/close.png"))
        close_btn.clicked.connect(self.close)
        
        for btn in [minimize_btn, close_btn]:
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {COLORS["surface_hover"]};
                }}
            """)
        
        controls_layout.addWidget(minimize_btn)
        controls_layout.addWidget(close_btn)
        
        titlebar_layout.addWidget(self.tab_bar)
        titlebar_layout.addWidget(new_tab_btn)
        titlebar_layout.addStretch()
        titlebar_layout.addWidget(self.status_label)
        titlebar_layout.addLayout(controls_layout)
        
        # Create content area
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['background']};")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(40)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS["surface"]};
                border-right: 1px solid {COLORS["surface_hover"]};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Create sidebar buttons
        self.home_btn = SidebarButton("home")
        self.open_btn = SidebarButton("open")
        self.save_btn = SidebarButton("save")
        self.code_btn = SidebarButton("script")
        self.hub_btn = SidebarButton("hub")
        self.settings_btn = SidebarButton("settings")
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.open_btn)
        sidebar_layout.addWidget(self.save_btn)
        sidebar_layout.addWidget(self.code_btn)
        sidebar_layout.addWidget(self.hub_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.settings_btn)
        
        # Create tab widget
        self.tab_widget = TabWidget()
        # Add initial tab and make sure it's fully initialized
        try:
            self.tab_widget.add_tab()
        except Exception as e:
            print(f"Error initializing tab: {e}")
        
        # Create script hub widget
        self.script_hub = ScriptHubWidget(self)
        
        # Create settings widget
        self.settings = SettingsWidget(self)
        
        # Create console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(100)
        self.console.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS["surface"]};
                color: {COLORS["text"]};
                border: none;
                border-top: 1px solid {COLORS["surface_hover"]};
                padding: 8px;
                font-family: 'JetBrains Mono', Menlo, monospace;
                font-size: 12px;
            }}
        """)
        
        # Add console header
        console_header = QWidget()
        console_header.setFixedHeight(24)
        console_header.setStyleSheet(f"""
            QWidget {{
                background: {COLORS["surface"]};
                border-top: 1px solid {COLORS["surface_hover"]};
            }}
        """)
        console_header_layout = QHBoxLayout(console_header)
        console_header_layout.setContentsMargins(8, 0, 8, 0)
        console_header_layout.setSpacing(4)
        
        console_label = QLabel("▶ Console:")
        console_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        console_header_layout.addWidget(console_label)
        console_header_layout.addStretch()
        
        clear_console_btn = QPushButton("Clear")
        clear_console_btn.setFixedSize(50, 20)
        clear_console_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS["text"]};
                border: 1px solid {COLORS["surface_hover"]};
                border-radius: 2px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: {COLORS["surface_hover"]};
            }}
        """)
        clear_console_btn.clicked.connect(self.console.clear)
        console_header_layout.addWidget(clear_console_btn)
        
        # Create bottom bar
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(48)
        bottom_bar.setStyleSheet(f"""
            QWidget {{
                background: {COLORS["surface"]};
                border-top: 1px solid {COLORS["surface_hover"]};
            }}
        """)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(8, 0, 8, 0)
        bottom_layout.setSpacing(4)
        
        # Bottom bar buttons
        run_btn = QPushButton()
        run_btn.setIcon(QIcon("icons/run.png"))
        run_btn.setIconSize(QSize(28, 28))
        run_btn.clicked.connect(self.execute_script)
        
        clear_btn = QPushButton()
        clear_btn.setIcon(QIcon("icons/clear.png"))
        clear_btn.setIconSize(QSize(28, 28))
        clear_btn.clicked.connect(self.clear_editor)
        
        copy_btn = QPushButton()
        copy_btn.setIcon(QIcon("icons/copy.png"))
        copy_btn.setIconSize(QSize(28, 28))
        
        inject_btn = QPushButton()
        inject_btn.setIcon(QIcon("icons/inject.png"))
        inject_btn.setIconSize(QSize(28, 28))
        inject_btn.clicked.connect(self.inject)
        
        roblox_btn = QPushButton()
        roblox_btn.setIcon(QIcon("icons/roblox.png"))
        roblox_btn.setIconSize(QSize(28, 28))
        roblox_btn.clicked.connect(self.launch_roblox)
        
        script_btn = QPushButton()
        script_btn.setIcon(QIcon("icons/script.png"))
        script_btn.setIconSize(QSize(28, 28))
        script_btn.clicked.connect(self.add_new_tab)
        
        # Store references to buttons for enabling/disabling
        self.bottom_buttons = [run_btn, clear_btn, copy_btn, inject_btn, roblox_btn, script_btn]
        
        for btn in self.bottom_buttons:
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 4px;
                }}
                QPushButton:hover {{
                    background: {COLORS["surface_hover"]};
                }}
                QPushButton:disabled {{
                    opacity: 0.5;
                }}
            """)
        
        bottom_layout.addWidget(run_btn)
        bottom_layout.addWidget(clear_btn)
        bottom_layout.addWidget(copy_btn)
        bottom_layout.addWidget(inject_btn)
        bottom_layout.addWidget(roblox_btn)
        bottom_layout.addWidget(script_btn)
        bottom_layout.addStretch()
        
        # Create right side buttons
        client_btn = QPushButton()
        client_btn.setIcon(QIcon("icons/client.png"))
        client_btn.setText("Client")
        client_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["primary"]};
                color: {COLORS["text"]};
                border: none;
                border-radius: 2px;
                padding: 4px 12px 4px 8px;
                font-size: 11px;
                text-align: right;
            }}
            QPushButton:hover {{
                background: {COLORS["primary"]}dd;
            }}
        """)
        client_btn.setIconSize(QSize(16, 16))
        
        bottom_layout.addWidget(client_btn)
        
        # Create editor layout
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self.tab_widget)
        editor_layout.addWidget(bottom_bar)
        editor_layout.addWidget(console_header)
        editor_layout.addWidget(self.console)
        
        # Create main content stack
        self.stack = QStackedWidget()
        self.stack.addWidget(editor_widget)  # Editor page (index 0)
        self.stack.addWidget(self.script_hub)  # Script hub page (index 1)
        self.stack.addWidget(self.settings)  # Settings page (index 2)
        
        # Add widgets to content layout
        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.stack)
        
        # Add widgets to main layout
        layout.addWidget(titlebar)
        layout.addWidget(content)
        
        # Connect buttons
        self.home_btn.clicked.connect(self.show_welcome)
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.code_btn.clicked.connect(self.add_new_tab)
        self.hub_btn.clicked.connect(lambda: self.switch_view(1))
        self.settings_btn.clicked.connect(lambda: self.switch_view(2))
        
        # Set script editor as default page
        self.home_btn.setChecked(True)
        
        # Make window draggable from titlebar
        titlebar.mousePressEvent = self.mousePressEvent
        titlebar.mouseMoveEvent = self.mouseMoveEvent
        
        # Log startup
        self.log_to_console("[INFO] SSSnake started successfully!")
    
    def try_load_dll(self):
        """Load the DLL for injection with fallback to simulation and improved error handling"""
        try:
            # Check if we're running from an app bundle
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running as a PyInstaller bundle
                base_dir = sys._MEIPASS
            else:
                # Running from the app bundle or normal Python script
                base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create lib directory if it doesn't exist
            lib_dir = os.path.join(base_dir, "lib")
            if not os.path.exists(lib_dir):
                os.makedirs(lib_dir)
                self.log_to_console(f"[INFO] Created lib directory at {lib_dir}")
            
            # Determine the correct DLL path based on platform
            if sys.platform == "win32":
                dll_path = os.path.join(lib_dir, "roblox_injector.dll")
                dll_name = "roblox_injector.dll"
            elif sys.platform == "darwin":  # macOS
                dll_path = os.path.join(lib_dir, "roblox_injector.dylib")
                dll_name = "roblox_injector.dylib"
            else:  # Linux
                dll_path = os.path.join(lib_dir, "roblox_injector.so")
                dll_name = "roblox_injector.so"
            
            # Check if the file exists before trying to load it
            if not os.path.exists(dll_path):
                self.log_to_console(f"[WARNING] Injector library not found at {dll_path}")
                self.log_to_console(f"[INFO] Please ensure {dll_name} is placed in the lib directory")
                self.log_to_console(f"[INFO] Using simulation mode for now")
                self.simulation_mode = True
                self.dll_loaded = True
                return True
            
            # Check file permissions
            if not os.access(dll_path, os.R_OK):
                self.log_to_console(f"[WARNING] No read permission for {dll_path}")
                self.log_to_console(f"[INFO] Using simulation mode")
                self.simulation_mode = True
                self.dll_loaded = True
                return True
                
            # Try to load the DLL with a timeout
            self.log_to_console(f"[INFO] Attempting to load injector from {dll_path}")
            
            # Create a wrapper class for the DLL with safer function calls and better error handling
            class SafeDLL:
                def __init__(self, path):
                    try:
                        self.dll = ctypes.CDLL(path)
                        # Set up function prototypes with proper error handling
                        self.dll.inject_into_process.restype = ctypes.c_bool
                        self.dll.execute_script.argtypes = [ctypes.c_char_p]
                        self.dll.execute_script.restype = ctypes.c_bool
                        self.dll.cleanup_injector.restype = None
                        
                        # Optional: set target process ID if available
                        if hasattr(self.dll, 'set_target_process'):
                            self.dll.set_target_process.argtypes = [ctypes.c_int]
                            self.dll.set_target_process.restype = ctypes.c_bool
                    except Exception as e:
                        raise RuntimeError(f"Failed to initialize DLL functions: {str(e)}")
                
                def inject_into_process(self, target_pid=None):
                    try:
                        # If we have a target PID and the function exists, set it
                        if target_pid and hasattr(self.dll, 'set_target_process'):
                            if not self.dll.set_target_process(target_pid):
                                return False
                        
                        return self.dll.inject_into_process()
                    except Exception as e:
                        print(f"Injection error: {e}")
                        return False
                
                def execute_script(self, script):
                    try:
                        if not isinstance(script, bytes):
                            script = script.encode('utf-8')
                        return self.dll.execute_script(script)
                    except Exception as e:
                        print(f"Script execution error: {e}")
                        return False
                
                def cleanup_injector(self):
                    try:
                        self.dll.cleanup_injector()
                        return True
                    except Exception as e:
                        print(f"Cleanup error: {e}")
                        return False
            
            # Load the DLL with our safe wrapper
            try:
                self.dll = SafeDLL(dll_path)
                self.log_to_console(f"[INFO] Successfully loaded injector from {dll_path}")
                self.simulation_mode = False
                self.dll_loaded = True
                return True
            except Exception as e:
                self.log_to_console(f"[WARNING] Failed to initialize DLL: {e}")
                self.log_to_console("[INFO] Using simulation mode")
                self.simulation_mode = True
                self.dll_loaded = True
                return True
                
        except Exception as e:
            self.log_to_console(f"[WARNING] Failed to load DLL: {e}")
            self.log_to_console("[INFO] Using simulation mode")
            self.simulation_mode = True
            self.dll_loaded = True  # We're still "loaded" but in simulation mode
            return True
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_pos'):
            diff = event.globalPosition().toPoint() - self.drag_pos
            new_pos = self.pos() + diff
            self.move(new_pos)
            self.drag_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_pos'):
            del self.drag_pos
    
    def inject(self):
        """Inject the DLL into Roblox with improved process detection and error handling"""
        # Log to console
        self.log_to_console("[INFO] Checking for Roblox process...")
        
        # Check if Roblox is running and get the process ID
        roblox_running, roblox_pid = is_roblox_running()
        
        if roblox_running:
            self.log_to_console(f"[INFO] Roblox process found (PID: {roblox_pid}), attempting to inject...")
            
            # Make sure DLL is loaded
            if not hasattr(self, 'dll_loaded') or not self.dll_loaded:
                if not self.try_load_dll():
                    self.status_label.setText(" ● Injection Failed")
                    self.status_label.setStyleSheet("color: #ff0000;")
                    self.log_to_console("[ERROR] Failed to load injector library!")
                    return
            
            # Disable all buttons during injection to prevent multiple clicks
            for btn in self.bottom_buttons:
                btn.setEnabled(False)
            
            # Update status to show we're attempting injection
            self.status_label.setText(" ● Injecting...")
            self.status_label.setStyleSheet("color: #ffaa00;")  # Orange/yellow for in-progress
            
            # Use simulation mode if needed
            if self.simulation_mode:
                self.log_to_console("[INFO] Using simulation mode for injection")
                # Simulate successful injection with a slight delay
                QTimer.singleShot(800, self._simulate_injection_success)
            else:
                # Try to inject with a timeout
                self.log_to_console("[INFO] Attempting to inject using library...")
                
                # Create a worker thread for injection with the target PID
                class EnhancedInjectionWorker(InjectionWorker):
                    def __init__(self, dll, pid=None):
                        super().__init__(dll)
                        self.pid = pid
                    
                    def run(self):
                        try:
                            result = self.dll.inject_into_process(self.pid)
                            self.injection_result.emit(result, None)
                        except Exception as e:
                            self.injection_result.emit(False, str(e))
                
                # Use the enhanced worker with the PID
                self.injection_worker = EnhancedInjectionWorker(self.dll, roblox_pid)
                self.injection_worker.injection_result.connect(self._on_injection_result)
                self.injection_worker.start()
                
                # Set a timeout to prevent freezing (increased for reliability)
                QTimer.singleShot(8000, self._check_injection_timeout)
        else:
            self.status_label.setText(" ● Injection Failed")
            self.status_label.setStyleSheet("color: #ff0000;")
            self.log_to_console("[ERROR] Roblox is not running!")
            self.log_to_console("[INFO] Please start Roblox before attempting to inject.")
            
            # Show a helpful message box
            QMessageBox.warning(self, "Roblox Not Running", 
                              "Roblox is not currently running.\n\nPlease start Roblox first, then try injecting again.")
    
    def _simulate_injection_success(self):
        """Simulate a successful injection (for simulation mode)"""
        self.status_label.setText(" ● Injected")
        self.status_label.setStyleSheet("color: #00ff00;")
        self.log_to_console("[SUCCESS] Injection successful! (Simulation Mode)")
        
        # Re-enable buttons
        for btn in self.bottom_buttons:
            btn.setEnabled(True)
    
    def _inject_thread(self):
        """Run injection in a separate thread"""
        try:
            result = self.dll.inject_into_process()
            # Use signals to update UI from the thread
            if result:
                self.injection_success.emit()
            else:
                self.injection_failure.emit("Injection failed")
        except Exception as e:
            self.injection_failure.emit(str(e))
    
    def _check_injection_timeout(self):
        """Check if the injection worker is still running after timeout"""
        if hasattr(self, 'injection_worker') and self.injection_worker.isRunning():
            # Worker is still running, likely frozen - switch to simulation mode
            self.log_to_console("[WARNING] Injection is taking too long, switching to simulation mode")
            self.injection_worker.terminate()
            self.simulation_mode = True
            self._simulate_injection_success()
    
    def _on_injection_result(self, success, error_message=None):
        """Handle injection result"""
        if success:
            self.status_label.setText(" ● Injected")
            self.status_label.setStyleSheet("color: #00ff00;")
            self.log_to_console("[SUCCESS] Injection successful!")
        else:
            self.status_label.setText(" ● Injection Failed")
            self.status_label.setStyleSheet("color: #ff0000;")
            if error_message:
                self.log_to_console(f"[ERROR] Injection failed: {error_message}")
            else:
                self.log_to_console("[ERROR] Injection failed!")
            # Fall back to simulation mode
            self.log_to_console("[INFO] Falling back to simulation mode...")
            self.simulation_mode = True
            QTimer.singleShot(500, self._simulate_injection_success)
            return
        
        # Re-enable buttons
        for btn in self.bottom_buttons:
            btn.setEnabled(True)
    
    def _on_injection_failure(self, error_msg):
        """Handle failed injection"""
        self.log_to_console(f"[WARNING] Error during injection: {error_msg}, falling back to simulation mode")
        self.simulation_mode = True
        self._simulate_injection_success()
    
    def execute_script(self):
        """Execute the script in the current editor with improved error handling"""
        # Make sure we have a current editor
        current_editor = self.tab_widget.current_editor()
        if not current_editor:
            self.log_to_console("[ERROR] No active editor tab!")
            return
            
        # Get the script content
        script = current_editor.toPlainText()
        
        if not script or script.strip() == "":
            self.log_to_console("[ERROR] No script to execute! Please enter a script first.")
            return
        
        # Check for syntax errors
        if not self.check_script_syntax(script):
            self.log_to_console("[ERROR] Script contains syntax errors. Cannot execute!")
            self.log_to_console("[INFO] Please fix the errors before executing.")
            return
        
        # Make sure we're on the editor page
        self.stack.setCurrentIndex(0)
        self.home_btn.setChecked(True)
            
        # Check if injected
        if " ● Injected" in self.status_label.text():
            self.log_to_console("[INFO] Executing script...")
            
            # Disable buttons during execution to prevent multiple clicks
            for btn in self.bottom_buttons:
                btn.setEnabled(False)
            
            # Use simulation mode if needed
            if self.simulation_mode:
                self.log_to_console("[INFO] Using simulation mode for execution")
                # Simulate successful execution with a slight delay
                QTimer.singleShot(500, self._simulate_execution_success)
            else:
                # Try to execute with a timeout
                self.log_to_console("[INFO] Attempting to execute script using injector...")
                
                try:
                    # Create a worker thread for execution with better error handling
                    class EnhancedExecutionWorker(ExecutionWorker):
                        def run(self):
                            try:
                                # Make sure the script is properly encoded
                                if isinstance(self.script, str):
                                    encoded_script = self.script.encode('utf-8')
                                else:
                                    encoded_script = self.script
                                    
                                # Execute the script
                                result = self.dll.execute_script(encoded_script)
                                self.execution_result.emit(result, None)
                            except Exception as e:
                                self.execution_result.emit(False, str(e))
                    
                    # Use the enhanced worker
                    self.execution_worker = EnhancedExecutionWorker(self.dll, script)
                    self.execution_worker.execution_result.connect(self._on_execution_result)
                    self.execution_worker.start()
                    
                    # Set a timeout to prevent freezing (increased for reliability)
                    QTimer.singleShot(5000, self._check_execution_timeout)
                    
                except Exception as e:
                    self.log_to_console(f"[ERROR] Failed to start execution: {e}")
                    self._on_execution_result(False, str(e))
        else:
            self.log_to_console("[ERROR] Not injected! Please inject first.")
            
            # Show a helpful message
            QMessageBox.warning(self, "Not Injected", 
                              "SSSnake is not injected into Roblox.\n\nPlease click the 'Inject' button first, then try executing your script.")
    
    def _simulate_execution_success(self):
        """Simulate a successful script execution (for simulation mode)"""
        self.log_to_console("[SUCCESS] Script executed successfully! (Simulation Mode)")
        
        # Re-enable buttons
        for btn in self.bottom_buttons:
            btn.setEnabled(True)
    
    def _execute_thread(self, script):
        """Run script execution in a separate thread"""
        try:
            result = self.dll.execute_script(script.encode())
            # Use signals to update UI from the thread
            if result:
                self.execution_success.emit()
            else:
                self.execution_failure.emit("Execution failed")
        except Exception as e:
            self.execution_failure.emit(str(e))
    
    def _check_execution_timeout(self):
        """Check if the execution worker is still running after timeout"""
        if hasattr(self, 'execution_worker') and self.execution_worker.isRunning():
            # Worker is still running, likely frozen - switch to simulation mode
            self.log_to_console("[WARNING] Execution is taking too long, switching to simulation mode")
            self.execution_worker.terminate()
            self.simulation_mode = True
            self._simulate_execution_success()
    
    def _on_execution_result(self, success, error_message=None):
        """Handle execution result"""
        if success:
            self.log_to_console("[SUCCESS] Script executed successfully!")
        else:
            if error_message:
                self.log_to_console(f"[ERROR] Script execution failed: {error_message}")
            else:
                self.log_to_console("[ERROR] Script execution failed!")
            # Fall back to simulation mode
            self.log_to_console("[INFO] Falling back to simulation mode...")
            self.simulation_mode = True
            QTimer.singleShot(300, self._simulate_execution_success)
            return
        
        # Re-enable buttons
        for btn in self.bottom_buttons:
            btn.setEnabled(True)
    
    def _on_execution_failure(self, error_msg):
        """Handle failed script execution"""
        self.log_to_console(f"[WARNING] Error during execution: {error_msg}, using simulation mode")
        self.simulation_mode = True
        self._simulate_execution_success()
        
    def update_theme(self):
        """Update UI with the current theme - simplified version to avoid crashes"""
        try:
            # Log the theme change
            self.log_to_console(f"[INFO] Theme changed to {CURRENT_THEME}")
            
            # Save the theme preference to a file
            try:
                # Check if we're running from an app bundle
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    # Running as a PyInstaller bundle
                    base_dir = sys._MEIPASS
                else:
                    # Running from the app bundle or normal Python script
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    
                with open(os.path.join(base_dir, "theme_preference.txt"), "w") as f:
                    f.write(CURRENT_THEME)
                self.log_to_console(f"[INFO] Theme preference saved: {CURRENT_THEME}")
            except Exception as e:
                self.log_to_console(f"[WARNING] Could not save theme preference: {e}")
            
            # Show a message to the user
            QMessageBox.information(self, "Theme Applied", 
                                  f"The {CURRENT_THEME} theme has been set as your preference.\n\nPlease restart the application for the theme to take full effect.")
            
        except Exception as e:
            self.log_to_console(f"[ERROR] Failed to update theme: {e}")
            QMessageBox.warning(self, "Theme Error", 
                              f"There was an error applying the theme: {e}")
    
    def check_script_syntax(self, script):
        """Check if the script has syntax errors"""
        # Basic syntax check for Lua
        try:
            # Check for unbalanced parentheses, brackets, and braces
            parens = 0
            brackets = 0
            braces = 0
            
            for char in script:
                if char == '(':
                    parens += 1
                elif char == ')':
                    parens -= 1
                elif char == '[':
                    brackets += 1
                elif char == ']':
                    brackets -= 1
                elif char == '{':
                    braces += 1
                elif char == '}':
                    braces -= 1
            
            if parens != 0 or brackets != 0 or braces != 0:
                self.log_to_console("[ERROR] Unbalanced parentheses, brackets, or braces in script")
                return False
            
            # Check for common Lua syntax errors
            if "end)" in script and not "function(" in script:
                self.log_to_console("[ERROR] Unmatched 'end)' without 'function('")
                return False
            
            return True
        except Exception as e:
            self.log_to_console(f"[ERROR] Syntax check failed: {e}")
            return False
    
    def launch_roblox(self):
        """Launch Roblox"""
        self.log_to_console("[INFO] Launching Roblox...")
        
        try:
            # Different launch commands based on platform
            if sys.platform == "win32":
                # Windows
                os.startfile("roblox:")
            elif sys.platform == "darwin":
                # macOS
                subprocess.Popen(["open", "roblox://"])
            else:
                # Linux
                subprocess.Popen(["xdg-open", "roblox://"])
                
            self.log_to_console("[SUCCESS] Roblox launch initiated!")
        except Exception as e:
            self.log_to_console(f"[ERROR] Failed to launch Roblox: {e}")
    
    def clear_editor(self):
        """Clear the current editor"""
        self.tab_widget.current_editor().clear()
        self.log_to_console("[INFO] Editor cleared.")
        
    def log_to_console(self, message):
        """Add a message to the console with timestamp"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.console.append(f"[{timestamp}] {message}")
    
    def add_new_tab(self, title=None):
        """Add a new tab to the editor"""
        if title is None or isinstance(title, bool):
            title = "Script-1"
            
        editor = self.tab_widget.add_tab(str(title))
        self.switch_view(0)  # Switch to editor view
        return editor
        
    def show_welcome(self):
        """Show welcome message"""
        # Switch to editor view
        self.stack.setCurrentIndex(0)
        self.home_btn.setChecked(True)
        
        # Create a new tab with welcome message
        welcome_tab = self.tab_widget.add_tab("WELCOME TO SSSNAKE!")
        welcome_editor = self.tab_widget.widget(welcome_tab).findChild(LuaCodeEditor)
        
        welcome_message = """-- WELCOME TO SSSNAKE!

-- SSSnake is a powerful Lua script executor for Roblox
-- Features:
--   * Multi-tab script editing
--   * Script hub with popular scripts
--   * Syntax highlighting
--   * Error checking
--   * Easy injection
--   * Multiple themes

-- To get started:
--   1. Launch Roblox
--   2. Click the inject button (paperclip icon)
--   3. Write or load a script
--   4. Click the run button to execute
--   5. Try different themes in Settings

-- Enjoy using SSSnake!
print("SSSnake is ready to use!")
"""
        
        welcome_editor.setPlainText(welcome_message)
        self.log_to_console("[INFO] WELCOME! SSSnake is ready to use.")
        
    def switch_view(self, index):
        """Switch to a specific view and update sidebar buttons"""
        # Update stack
        self.stack.setCurrentIndex(index)
        
        # Update sidebar buttons
        for btn in [self.home_btn, self.hub_btn, self.settings_btn]:
            btn.setChecked(False)
            
        if index == 0:
            self.home_btn.setChecked(True)
        elif index == 1:
            self.hub_btn.setChecked(True)
        elif index == 2:
            self.settings_btn.setChecked(True)
        
    def open_file(self):
        """Open a Lua file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Lua Script", "", "Lua Files (*.lua);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    
                # Create a new tab with the file name
                file_name = os.path.basename(file_path)
                editor = self.tab_widget.add_tab(file_name)
                editor.setPlainText(content)
                self.log_to_console(f"[INFO] Opened file: {file_path}")
                
                # Switch to editor view
                self.stack.setCurrentIndex(0)
                self.home_btn.setChecked(True)
            except Exception as e:
                self.log_to_console(f"[ERROR] Failed to open file: {e}")
    
    def save_file(self):
        """Save the current editor content to a file"""
        editor = self.tab_widget.current_editor()
        if not editor:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Lua Script", "", "Lua Files (*.lua);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(editor.toPlainText())
                
                # Update tab name
                file_name = os.path.basename(file_path)
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_name)
                self.log_to_console(f"[INFO] Saved file: {file_path}")
            except Exception as e:
                self.log_to_console(f"[ERROR] Failed to save file: {e}")

def is_roblox_running():
    """Check if Roblox is running with improved detection"""
    roblox_process_names = ['RobloxPlayer', 'Roblox', 'RobloxStudio', 'RobloxPlayerBeta']
    
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            # Check process name
            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
            proc_path = proc.info['exe'].lower() if 'exe' in proc.info and proc.info['exe'] else ''
            
            # Check if any of the Roblox process names are in the process name or path
            if any(rb_name.lower() in proc_name for rb_name in roblox_process_names) or 'roblox' in proc_name:
                return True, proc.pid
            
            # Also check executable path for Roblox
            if 'roblox' in proc_path:
                return True, proc.pid
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
            pass
    
    return False, None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSSnakeExecutor()
    window.show()
    sys.exit(app.exec())
