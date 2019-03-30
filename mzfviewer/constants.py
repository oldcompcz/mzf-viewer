import os


# Colors

MAIN_BG = "#a0b0b0"

WHITE = "#f8f8f8"
ORANGE = "#ffc040"

BLUE = "#282870"
GREY_BLUE = "#285870"
GREEN_BLUE = "#287070"

ACTIVE = {"foreground": ORANGE, "background": "#000000"}


# Other

NON_DIGITS = "_ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# Resources

package_path = os.path.dirname(__file__)

ICON_SCALE2 = os.path.join(package_path, 'icons/scale2.png')
ICON_SCALE3 = os.path.join(package_path, 'icons/scale3.png')
ICON_CHARLEFT = os.path.join(package_path, 'icons/charleft.png')
ICON_LINEUP = os.path.join(package_path, 'icons/lineup.png')
ICON_PAGEUP = os.path.join(package_path, 'icons/pageup.png')
ICON_HOME = os.path.join(package_path, 'icons/home.png')
ICON_END = os.path.join(package_path, 'icons/end.png')
ICON_PAGEDOWN = os.path.join(package_path, 'icons/pagedown.png')
ICON_LINEDOWN = os.path.join(package_path, 'icons/linedown.png')
ICON_CHARRIGHT = os.path.join(package_path, 'icons/charright.png')


# Base64 data

cg_rom = b"""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
ICAgQEBAQICQkGA=="""

asc_to_disp = b"""8PDw8PDw8PDw8PDw8PDw8PDBwsPExcbw8PDw8PDw8PAAYWJjZGVmZ2hpa2ov
Ki4tICEiIyQlJicoKU8sUStXSVUBAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGlJZVFBFx8jJysvMzc
7P3+fo5ens7dDR0tPU1dbX2Nna29zd3sBAvZ2xtbm0nrK2ur6fs7e7v6OFpKWmlIeInIKYhJKQg5GB
mpeTlYmhr4uGlqKrqoqOsK2Np6ipj4yurJugmby4gDs6cDxxWj1DVj8eShxdPlwfX143e382en4zS0
wdbFt4QTU0dDA4dTlNb24yd3Zyc0d8UzFObUhGfUQbWHlCYA=="""
