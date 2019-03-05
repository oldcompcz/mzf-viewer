def generate_cgrom():
    """Generate a sequence of 8-byte chunks representing chars of the original
    Sharp MZ font.
    """

    with open("data/cg_rom.bin", 'rb') as f:

        while True:
            chunk = f.read(8)
            if chunk:
                yield chunk
            else:
                break


def generate_charset(scale):
    """Generate the original Sharp MZ font as a sequence of 16x16px or 24x24px
    bitmaps, in the format required by the tkinter.BitmapImage constructor.
    """

    format_string = """#define byte{n}_width {w}
#define byte{n}_height {w}
static unsigned char byte{n}_bits[] = {{ {data} }}"""

    for i, chunk in enumerate(generate_cgrom()):
        hex_strings = []

        for byte in chunk:
            hex_strings.extend([hex(i) for i in zoomed(byte, scale)])

        joined_hex = ",".join(hex_strings)

        yield format_string.format(n=i, w=8*scale, data=joined_hex)


def generate_asc_to_disp():
    """Return a byte sequence serving as conversion table from ascii code
    to display (video-RAM) code.
    """

    with open("data/asc_to_disp.bin", 'rb') as f:
        return f.read()


def generate_bitmaps(scale):
    """Generate a sequence of 16x2px or 24x3px bitmaps, in the format required
    by the tkinter.BitmapImage contructor.
    """

    format_string = """#define byte{n}_width {w}
#define byte{n}_height {h}
static unsigned char byte{n}_bits[] = {{ {data} }}"""

    for i in range(256):
        joined_hex = ",".join([hex(i) for i in zoomed(i, scale)])

        yield format_string.format(n=i, w=8*scale, h=scale, data=joined_hex)


def generate_flipped():
    """Generate a sequence of bitwise mirrored 8-bit values.
    """

    for n in range(256):
        bin_string_reversed = "{:08b}".format(n)[::-1]
        yield int(bin_string_reversed, 2)


def zoomed(byte, scale):
    """Return a sequence of bytes that represent a "bitwise zoom" of 'byte'.
    """

    zoomed_bits = {2: (3, 12, 48, 192, 768, 3072, 12288, 49152),
                   3: (7, 56, 448, 3584,
                       28672, 229376, 1835008, 14680064)}[scale]

    result = sum(zoomed_bit
                 for bit, zoomed_bit in zip((1, 2, 4, 8, 16, 32, 64, 128),
                                            zoomed_bits)
                 if byte & bit)

    return result.to_bytes(scale, "little") * scale
