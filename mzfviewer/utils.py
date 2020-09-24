import base64
from functools import lru_cache
import pickle
import re

from mzfviewer import constants


def get_tag(sequence_of_strings):
    """Return first string that matches the 'item{number}' pattern."""

    for tag in sequence_of_strings:
        if re.match(r"^item\d+$", tag):
            return tag


def generate_cgrom():
    """Generate a sequence representing the original Sharp MZ font.

    Each yielded item is an 8-tuple of 0-255 integers.
    """
    itr = iter(base64.b64decode(constants.CG_ROM))

    for chunk in zip(*[itr]*8):
        yield chunk


def generate_charset(cgrom, zoom):
    """Generate the original Sharp MZ font as a sequence of 16x16px or 24x24px
    bitmaps, in the format required by the tkinter.BitmapImage constructor.
    """
    format_string = """#define byte{n}_width {w}
#define byte{n}_height {w}
static unsigned char byte{n}_bits[] = {{ {data} }}"""

    for i, chunk in enumerate(cgrom):
        hex_strings = []

        for byte in chunk:
            hex_strings.extend(hex(i) for i in zoomed(byte, zoom))

        joined_hex = ",".join(hex_strings)

        yield format_string.format(n=i, w=8*zoom, data=joined_hex)


def generate_bitmaps(zoom):
    """Generate a sequence of 16x2px or 24x3px bitmaps, in the format required
    by the tkinter.BitmapImage constructor.
    """
    format_string = """#define byte{n}_width {w}
#define byte{n}_height {h}
static unsigned char byte{n}_bits[] = {{ {data} }}"""

    for i in range(256):
        joined_hex = ",".join(hex(i) for i in zoomed(i, zoom))

        yield format_string.format(n=i, w=8*zoom, h=zoom, data=joined_hex)


def generate_flipped():
    """Generate a sequence of bitwise mirrored 8-bit values."""

    for n in range(256):
        bin_string_reversed = "{:08b}".format(n)[::-1]
        yield int(bin_string_reversed, 2)


@lru_cache(maxsize=512)
def zoomed(byte, zoom):
    """Return a sequence of bytes that represent a "bitwise zoom" of 'byte'.

    'zoom' must be 2 or 3.
    """
    zoomed_bits = {2: (3, 12, 48, 192, 768, 3072, 12288, 49152),
                   3: (7, 56, 448, 3584,
                       28672, 229376, 1835008, 14680064)}[zoom]

    result = sum(zoomed_bit
                 for bit, zoomed_bit in zip((1, 2, 4, 8, 16, 32, 64, 128),
                                            zoomed_bits)
                 if byte & bit)

    return result.to_bytes(zoom, "little") * zoom


def generate_and_pickle_data():
    cgrom = tuple(generate_cgrom())

    charset_zoom_2 = tuple(generate_charset(cgrom, 2))
    with open(constants.DATA_DIR / 'charset_zoom_2.pickle', 'wb') as f:
        pickle.dump(charset_zoom_2, f)

    charset_zoom_3 = tuple(generate_charset(cgrom, 3))
    with open(constants.DATA_DIR / 'charset_zoom_3.pickle', 'wb') as f:
        pickle.dump(charset_zoom_3, f)

    bitmaps_zoom_2 = tuple(generate_bitmaps(2))
    with open(constants.DATA_DIR / 'bitmaps_zoom_2.pickle', 'wb') as f:
        pickle.dump(bitmaps_zoom_2, f)

    bitmaps_zoom_3 = tuple(generate_bitmaps(3))
    with open(constants.DATA_DIR / 'bitmaps_zoom_3.pickle', 'wb') as f:
        pickle.dump(bitmaps_zoom_3, f)


if __name__ == '__main__':
    generate_and_pickle_data()
