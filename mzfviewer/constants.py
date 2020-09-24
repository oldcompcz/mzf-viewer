from pathlib import Path


# Colors

MAIN_BG = '#a0b0b0'

WHITE = '#f8f8f8'
LITE_BLUE = '#60c8f8'
ORANGE = '#ffc040'

BLUE = '#282870'
GREY_BLUE = '#285870'

ACTIVE = {'foreground': ORANGE, 'background': '#000000'}


# Paths

PACKAGE_DIR = Path(__file__).parent
DATA_DIR = PACKAGE_DIR / 'data'
ICON_DIR = PACKAGE_DIR / 'icons'

ICON_CHARLEFT = ICON_DIR / 'charleft.png'
ICON_LINEUP = ICON_DIR / 'lineup.png'
ICON_PAGEUP = ICON_DIR / 'pageup.png'
ICON_HOME = ICON_DIR / 'home.png'
ICON_END = ICON_DIR / 'end.png'
ICON_PAGEDOWN = ICON_DIR / 'pagedown.png'
ICON_LINEDOWN = ICON_DIR / 'linedown.png'
ICON_CHARRIGHT = ICON_DIR / 'charright.png'
