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


def generate_charset():
    """Generate the original Sharp MZ font as a sequence of 16x16px (double
    sized 8x8px) bitmaps, in the format required by the tkinter.BitmapImage
    contructor.
    """

    format_string = """#define byte{n}_width 16
#define byte{n}_height 16
static unsigned char byte{n}_bits[] = {{ {data} }}"""

    for i, chunk in enumerate(generate_cgrom()):
        hex_strings = []

        for byte in chunk:
            hex_strings.extend([hex(i) for i in zoomed(byte)])

        joined_hex = ",".join(hex_strings)

        yield format_string.format(n=i, data=joined_hex)


def generate_asc_to_disp():
    """Return a byte sequence serving as conversion table from ascii code
    to display (video-RAM) code.
    """

    with open("data/asc_to_disp.bin", 'rb') as f:
        return f.read()


def generate_bitmaps():
    """Generate a sequence of 16x2px (double sized 8x1px) bitmaps, in the
    format required by the tkinter.BitmapImage contructor.
    """

    for number in range(256):
        double_byte = 0

        for bit, double_bit in zip((1, 2, 4, 8, 16, 32, 64, 128),
                                   (3, 12, 48, 192, 768, 3072, 12288, 49152)):
            if number & bit:
                double_byte += double_bit

        lsb_hex = hex(double_byte & 0xff)
        msb_hex = hex(double_byte >> 8)

        bitmap_code = """#define byte{n}_width 16
#define byte{n}_height 2
static unsigned char byte{n}_bits[] = {{
{lsb}, {msb}, {lsb}, {msb}}}""".format(n=number, lsb=lsb_hex, msb=msb_hex)

        yield bitmap_code


def generate_flipped():
    """Generate a sequence of bitwise mirrored 8-bit values.
    """

    for n in range(256):
        bin_string_reversed = "{:08b}".format(n)[::-1]
        yield int(bin_string_reversed, 2)


def zoomed(byte, little_endian=True):
    """Return a list of four values that represent a "bitwise zoom" of 'byte'.
    """

    double_byte = sum(double_bit
                      for bit, double_bit in zip((1, 2, 4, 8,
                                                  16, 32, 64, 128),
                                                 (3, 12, 48, 192,
                                                 768, 3072, 12288, 49152))
                      if byte & bit)

    if little_endian:
        return [double_byte & 0xff, double_byte >> 8] * 2
    else:
        return [double_byte >> 8, double_byte & 0xff] * 2
