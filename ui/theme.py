"""
Titanium Downloader - Theme & Design System
Bảng màu, font, spacing cho giao diện hiện đại.
"""


class Colors:
    """Bảng màu chính - Dark theme hiện đại."""
    
    # Background layers
    BG_DARKEST = "#0a0a0f"       # Sidebar background
    BG_DARK = "#0f0f17"          # Main background
    BG_CARD = "#161625"          # Card background
    BG_CARD_HOVER = "#1c1c30"    # Card hover
    BG_INPUT = "#1a1a2e"         # Input field background
    BG_ELEVATED = "#1e1e35"      # Elevated surfaces
    
    # Primary - Vibrant Blue/Purple gradient feel
    PRIMARY = "#6C63FF"          # Main action color
    PRIMARY_HOVER = "#5A52E0"    # Hover state
    PRIMARY_LIGHT = "#8B85FF"    # Light variant
    PRIMARY_GLOW = "#2a2847"     # Glow effect (pre-blended)
    
    # Secondary - Cyan accent  
    SECONDARY = "#00D4FF"        # Accent color
    SECONDARY_HOVER = "#00B8E0"
    
    # Status colors
    SUCCESS = "#00E676"          # Green
    SUCCESS_BG = "#0a1f14"
    WARNING = "#FFB74D"          # Orange
    WARNING_BG = "#1f1a10"
    ERROR = "#FF5252"            # Red
    ERROR_BG = "#1f0f0f"
    
    # Text
    TEXT_PRIMARY = "#EAEAFF"     # Main text
    TEXT_SECONDARY = "#8888AA"   # Secondary text
    TEXT_MUTED = "#555570"       # Muted text
    TEXT_ACCENT = "#6C63FF"      # Accent text
    
    # Borders
    BORDER = "#2a2a45"
    BORDER_FOCUS = "#6C63FF"
    
    # Special
    MP3_COLOR = "#FF6B9D"        # Pink for MP3 mode
    MP3_HOVER = "#E0558A"
    MP4_COLOR = "#6C63FF"        # Purple for MP4 mode
    MP4_HOVER = "#5A52E0"
    
    # Progress bar
    PROGRESS_BG = "#1a1a2e"
    PROGRESS_FILL = "#6C63FF"
    
    # Sidebar
    SIDEBAR_BG = "#0a0a14"
    SIDEBAR_ACTIVE = "#1a1830"
    SIDEBAR_HOVER = "#141420"


class Fonts:
    """Font definitions."""
    # Sử dụng font có sẵn trên Windows
    FAMILY = "Segoe UI"
    MONO = "Consolas"
    
    # Sizes
    TITLE = (FAMILY, 28, "bold")
    HEADING = (FAMILY, 18, "bold")
    SUBHEADING = (FAMILY, 14, "bold")
    BODY = (FAMILY, 13)
    BODY_BOLD = (FAMILY, 13, "bold")
    SMALL = (FAMILY, 11)
    SMALL_BOLD = (FAMILY, 11, "bold")
    TINY = (FAMILY, 10)
    
    # Special
    LOGO = (FAMILY, 26, "bold")
    BUTTON_LARGE = (FAMILY, 15, "bold")
    BUTTON = (FAMILY, 13, "bold")
    CONSOLE = (MONO, 11)
    STAT_NUMBER = (FAMILY, 22, "bold")


class Spacing:
    """Spacing & sizing constants."""
    # Padding
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 12
    PAD_LG = 16
    PAD_XL = 20
    PAD_XXL = 24
    
    # Gaps
    GAP_SM = 6
    GAP_MD = 10
    GAP_LG = 16
    
    # Sizing
    SIDEBAR_WIDTH = 260
    INPUT_HEIGHT = 48
    BUTTON_HEIGHT = 50
    BUTTON_HEIGHT_SM = 38
    CORNER_RADIUS = 12
    CORNER_RADIUS_SM = 8
    CORNER_RADIUS_LG = 16
    
    # Progress bar
    PROGRESS_HEIGHT = 8
