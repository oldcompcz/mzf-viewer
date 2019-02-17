#!/usr/bin/python
# coding: utf-8


# Naming convention in this file:
#
# name starting with f_   ...  Frame widget
#                    l_   ...  Label widget
#                    t_   ...  Text widget
#                    c_   ...  Canvas widget
#                    b_   ...  Button widget
#                   rb_   ...  Radiobutton widget
#                   cb_   ...  Checkbutton widget
#                    s_   ...  Spinbox widget


import tkinter as T
from tkinter import filedialog
import utils


class ViewerApp(T.Frame):
    def __init__(self, master):

        super().__init__(master)
        self.pack()

        self.cgrom = tuple(utils.generate_cgrom())
        self.asc_to_disp = utils.generate_asc_to_disp()
        self.bitmaps = tuple(T.BitmapImage(data=bitmap)
                             for bitmap in utils.generate_bitmaps())
        self.flipped_values = tuple(utils.generate_flipped())

        self.var_filename = T.StringVar()
        self.var_ascii = T.IntVar()
        self.var_charset = T.IntVar()
        self.bmp_columns = T.StringVar()
        self.bmp_block_height = T.StringVar()
        self.bmp_displayed = T.StringVar()
        self.bmp_flipped = T.IntVar()

        b_open = T.Button(self, text="Open file...", command=self.open_file)
        b_open.grid(sticky="e", padx=10, pady=10)

        entry_file = T.Entry(self, textvariable=self.var_filename,
                             state="readonly")
        entry_file.grid(column=1, row=0, columnspan=3, sticky="ew",
                        padx=10, pady=10)

        self.var_filename.set("[no file]")
        self.file_data = b""
        self.position = 0

        # Standard hex dump frame

        f_hexdump = T.Frame(self, borderwidth=3, relief="groove")
        f_hexdump.grid(columnspan=2, sticky="ns",
                       padx=10, pady=5)

        font_textbox = ("Monospace", -14)

        self.t_adr = T.Text(f_hexdump, width=6, height=32, font=font_textbox)
        self.t_adr.grid(padx=10, pady=10)

        self.t_hexdump = T.Text(f_hexdump, width=23, height=32,
                                font=font_textbox)
        self.t_hexdump.grid(column=1, row=0, pady=10)

        self.t_pc_char = T.Text(f_hexdump, width=8, height=32,
                                font=font_textbox)
        self.t_pc_char.grid(column=2, row=0, padx=10, pady=10)

        # Sharp MZ dump frame

        f_mz_dump = T.Frame(self, borderwidth=3, relief="groove")
        f_mz_dump.grid(column=2, row=1, sticky="ns", pady=5)

        self.c_mz_dump = T.Canvas(f_mz_dump, width=208, height=512,
                                  background="#fff", highlightthickness=0)
        self.c_mz_dump.grid(rowspan=15, padx=10, pady=13)

        rb_ascii = T.Radiobutton(f_mz_dump, text="ASCII",
                                 variable=self.var_ascii, value=1,
                                 command=self.refresh_mz)
        rb_ascii.grid(column=1, row=0, sticky="sw", padx=5)

        rb_display = T.Radiobutton(f_mz_dump, text="display",
                                   variable=self.var_ascii, value=0,
                                   command=self.refresh_mz)
        rb_display.grid(column=1, row=1, sticky="nw", padx=5)

        rb_charset1 = T.Radiobutton(f_mz_dump, text="charset 1",
                                    variable=self.var_charset, value=0,
                                    command=self.refresh_mz)
        rb_charset1.grid(column=1, row=2, sticky="sw", padx=5)

        rb_charset2 = T.Radiobutton(f_mz_dump, text="charset 2",
                                    variable=self.var_charset, value=256,
                                    command=self.refresh_mz)
        rb_charset2.grid(column=1, row=3, sticky="nw", padx=5)

        self.var_ascii.set(1)
        self.var_charset.set(0)

        # Bitmap frame

        f_bitmap = T.Frame(self, borderwidth=3, relief="groove")
        f_bitmap.grid(column=3, row=1, columnspan=2, sticky="ns",
                      padx=10, pady=5)

        self.c_bmp = T.Canvas(f_bitmap, width=128, height=512,
                              background="#fff", highlightthickness=0)
        self.c_bmp.grid(rowspan=15, padx=10, pady=13)

        l_bitmap_columns = T.Label(f_bitmap, text="Columns:")
        l_bitmap_columns.grid(column=1, row=0, sticky="ws")

        s_bitmap_columns = T.Spinbox(f_bitmap, width=2, from_=1, to=8,
                                     increment=1,
                                     textvariable=self.bmp_columns,
                                     command=self.refresh_bmp)
        s_bitmap_columns.grid(column=2, row=0, sticky="ws", padx=10)

        l_block_height = T.Label(f_bitmap, text="Block height:")
        l_block_height.grid(column=1, row=1, sticky="nw")

        s_block_height = T.Spinbox(f_bitmap, width=2, from_=1, to=64,
                                   increment=1,
                                   textvariable=self.bmp_block_height,
                                   command=self.refresh_bmp)
        s_block_height.grid(column=2, row=1, sticky="nw", padx=10)

        l_displayed = T.Label(f_bitmap, text="Bytes displayed:")
        l_displayed.grid(column=1, row=2, sticky="nw")

        s_displayed = T.Spinbox(f_bitmap, width=4, from_=256, to=2048,
                                increment=256, textvariable=self.bmp_displayed,
                                command=self.refresh_bmp)
        s_displayed.grid(column=2, row=2, sticky="nw", padx=10)

        cb_flipped = T.Checkbutton(f_bitmap, text="horizontal flip",
                                   variable=self.bmp_flipped,
                                   command=self.refresh_bmp)
        cb_flipped.grid(column=1, row=3, columnspan=2, sticky="nw")

        self.bmp_block_height.set("8")
        self.bmp_flipped.set(0)

        # Navigation buttons

        f_navigate = T.Frame(self, borderwidth=3, relief="groove")
        f_navigate.grid(column=1, columnspan=3, padx=10, pady=10)

        b_char_left = T.Button(f_navigate, text="Char\nLeft",
                               command=lambda: self.move("Left"))
        b_char_left.grid()

        b_line_up = T.Button(f_navigate, text="Line\nUp",
                             command=lambda: self.move("Up"))
        b_line_up.grid(column=1, row=0)

        b_page_up = T.Button(f_navigate, text="Page\nUp",
                             command=lambda: self.move("Prior"))
        b_page_up.grid(column=2, row=0)

        b_home = T.Button(f_navigate, text="Home\n",
                          command=lambda: self.move("Home"))
        b_home.grid(column=3, row=0)

        b_end = T.Button(f_navigate, text="End\n",
                         command=lambda: self.move("End"))
        b_end.grid(column=4, row=0)

        b_page_down = T.Button(f_navigate, text="Page\nDown",
                               command=lambda: self.move("Next"))
        b_page_down.grid(column=5, row=0)

        b_line_down = T.Button(f_navigate, text="Line\nDown",
                               command=lambda: self.move("Down"))
        b_line_down.grid(column=6, row=0)

        b_char_right = T.Button(f_navigate, text="Char\nRight",
                                command=lambda: self.move("Right"))
        b_char_right.grid(column=7, row=0)

        # Exit button

        b_exit = T.Button(self, text="Exit", command=self.master.destroy)
        b_exit.grid(column=4, row=2, sticky="es", padx=10, pady=10)

    def open_file(self, filename=None):

        if not filename:
            dialog = filedialog.Open(self)
            filename = dialog.show()

        if filename:
            self.var_filename.set(filename)

            with open(filename, "rb") as f:
                self.file_data = f.read(0xffff)

            self.mz_from = self.file_data[20] + 256*self.file_data[21]
            self.position = 0
            self.refresh_all()

    def refresh_all(self):

        self.t_adr["state"] = "normal"
        self.t_adr.delete("1.0", "end")
        self.t_hexdump["state"] = "normal"
        self.t_hexdump.delete("1.0", "end")
        self.t_pc_char["state"] = "normal"
        self.t_pc_char.delete("1.0", "end")

        self.c_mz_dump.delete("mz_adr")
        self.c_mz_dump.delete("header_bg")

        contents = self.file_data[self.position:self.position + 256]

        for j in range(32):
            line_hex = ""
            line_pc_char = ""

            for i in range(8):
                if contents[j*8 + i:]:
                    byte = contents[j*8 + i]
                else:
                    break

                line_hex += "{:02X}{}".format(byte, (" " if i < 7 else ""))
                line_pc_char += (chr(byte) if 31 < byte < 127 else " ")

            if line_hex:
                line_adr = self.position + j*8
                self.t_adr.insert("end", "{:#06x}".format(line_adr))

                # when not in header, show MZ address + colon
                if line_adr >= 0x80:
                    mz_adr = "{:04X}:".format(line_adr + self.mz_from - 128)

                    for i5 in range(5):
                        asc = ord(mz_adr[i5])

                        # draw MZ char, regardless of var_ascii and var_charset
                        for i8 in range(8):
                            self.draw_byte(self.c_mz_dump, 16*i5,
                                           16*j + 2*i8,
                                           self.cgrom[self.asc_to_disp[asc]][i8],
                                           0, "mz_adr")

                self.t_hexdump.insert("end", line_hex)
                self.t_pc_char.insert("end", line_pc_char)
            else:
                break

        self.t_adr["state"] = "disabled"
        self.t_hexdump["state"] = "disabled"
        self.t_pc_char["state"] = "disabled"

        self.refresh_mz()
        self.refresh_bmp()

    def refresh_mz(self):

        self.c_mz_dump.delete("mz_char")
        contents = self.file_data[self.position:self.position + 256]

        for j in range(32):
            for i in range(8):
                if contents[j*8 + i:]:
                    byte = contents[j*8 + i]
                else:
                    break

                # draw MZ char according to var_ascii and var_charset
                for i8 in range(8):
                    self.draw_byte(self.c_mz_dump, 16*(i + 5), 16*j + 2*i8,
                                   self.cgrom[(self.asc_to_disp[byte]
                                              if self.var_ascii.get()
                                              else byte)
                                   + self.var_charset.get()][i8], 0, "mz_char")

    def move(self, key):

        jump = {"Left": -1, "Up": -8, "Prior": -256, "Home": -65536,
                "End": 65536, "Next": 256, "Down": 8, "Right": 1}[key]

        if self.file_data:
            self.position += jump

            if self.position < 0:
                self.position = 0
            elif self.position >= len(self.file_data):
                self.position = len(self.file_data) - 1
            self.refresh_all()

    def draw_byte(self, canvas, x, y, byte, flipped, tag):

        if flipped:
            byte = self.flipped_values[byte]

        canvas.create_image((x, y), image=self.bitmaps[byte], anchor="nw",
                            tag=tag)

    def refresh_bmp(self):

        if self.file_data:
            self.c_bmp.delete("graph_bitmap")
            row_length = int(self.bmp_columns.get())
            block_height = int(self.bmp_block_height.get())

            for j in range(int(self.bmp_displayed.get())
                           // (row_length * block_height)):

                for i in range(row_length):

                    for k in range(block_height):
                        index = j*row_length*block_height + i*block_height + k

                        if self.file_data[self.position:][index:]:
                            byte = self.file_data[self.position:][index]
                        else:
                            break

                        self.draw_byte(self.c_bmp, i*16,
                                       2*j*block_height + 2*k, byte,
                                       self.bmp_flipped.get(), "graph_bitmap")


def main():
    root = T.Tk()
    root.wm_title("MZF Viewer")
    app = ViewerApp(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
