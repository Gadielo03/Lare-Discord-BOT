"""
UI Color Palette Configuration
Global color scheme for all Discord embeds and UI elements
"""
import discord

class ColorPalette:
    """Global color palette for consistent UI design"""
    
    PRIMARY = discord.Color.from_rgb(129, 0, 209)      # #8100D1 - Purple
    SECONDARY = discord.Color.from_rgb(181, 0, 178)    # #B500B2 - Magenta
    ACCENT = discord.Color.from_rgb(255, 82, 160)      # #FF52A0 - Pink
    LIGHT = discord.Color.from_rgb(255, 164, 127)      # #FFA47F - Coral
    
    SUCCESS = PRIMARY          # Success messages - Purple
    INFO = ACCENT             # Information messages - Pink
    WARNING = LIGHT           # Warning messages - Coral
    ERROR = SECONDARY         # Error messages - Magenta
    LOVE = ACCENT             # Love/affection commands - Pink
    
    NOW_PLAYING = PRIMARY     # Currently playing song
    QUEUE = ACCENT           # Queue display
    ADDED = SECONDARY        # Song added to queue
    EMPTY = LIGHT            # Empty queue/no content

def get_color(name: str) -> discord.Color:
    """Get a color from the palette by name"""
    return getattr(ColorPalette, name.upper(), ColorPalette.PRIMARY)
