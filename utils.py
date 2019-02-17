def generate_cgrom():

    with open("data/cg_rom.bin", 'rb') as f:

        while True:
            chunk = f.read(8)
            if chunk:
                yield chunk
            else:
                break


def generate_asc_to_disp():

    with open("data/asc_to_disp.bin", 'rb') as f:
        return f.read()


def generate_bitmaps():

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

    for n in range(256):
        bin_string_reversed = "{:08b}".format(n)[::-1]
        yield int(bin_string_reversed, 2)
