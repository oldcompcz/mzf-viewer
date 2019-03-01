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


import sys
import os
import tkinter as T
from tkinter import filedialog
from tkinter import font
import utils
import constants


class ViewerApp(T.Frame):
    def __init__(self, master):

        super().__init__(master)
        self.config(background=constants.MAIN_BG)
        self.pack()

        self.scale = 2
        self.charset = tuple(T.BitmapImage(data=bitmap,
                                           foreground=constants.WHITE)
                             for bitmap in utils.generate_charset(self.scale))
        self.charset_active = tuple(T.BitmapImage(data=bitmap,
                                                  **constants.ACTIVE)
                                    for bitmap in utils.generate_charset(
                                                        self.scale))

        self.bitmaps = tuple(T.BitmapImage(data=bitmap,
                                           foreground=constants.WHITE)
                             for bitmap in utils.generate_bitmaps(self.scale))
        self.bitmaps_active = tuple(T.BitmapImage(data=bitmap,
                                                  **constants.ACTIVE)
                                    for bitmap in utils.generate_bitmaps(
                                                        self.scale))
        self.flipped_values = tuple(utils.generate_flipped())
        self.asc_to_disp = utils.generate_asc_to_disp()

        # monospaced font for the text widgets
        # (search for a font size with line height exactly scale*8 px,
        # set to scale*5 if unsuccessful)
        self.font_textbox = font.Font(name="TkFixedFont", exists=True)

        for size in range(self.scale * 9, -self.scale * 9, -1):
            self.font_textbox.config(size=size)
            if self.font_textbox.metrics()["linespace"] == self.scale * 8:
                break
        else:
            self.font_textbox.config(size=self.scale * 5)

        # variables directly connected with widgets
        self.var_filename = T.StringVar()

        self.var_ascii = T.IntVar()
        self.var_ascii.set(1)

        self.alt_charset = T.BooleanVar()
        self.alt_charset.set(False)

        self.bmp_columns = T.IntVar()

        self.bmp_block_height = T.IntVar()
        self.bmp_block_height.set("8")

        self.bmp_displayed = T.IntVar()

        self.bmp_flipped = T.BooleanVar()
        self.bmp_flipped.set(False)

        # icons for navigation buttons
        self.img_char_left = T.PhotoImage(file="icons/charleft.png")
        self.img_line_up = T.PhotoImage(file="icons/lineup.png")
        self.img_page_up = T.PhotoImage(file="icons/pageup.png")
        self.img_home = T.PhotoImage(file="icons/home.png")
        self.img_end = T.PhotoImage(file="icons/end.png")
        self.img_page_down = T.PhotoImage(file="icons/pagedown.png")
        self.img_line_down = T.PhotoImage(file="icons/linedown.png")
        self.img_char_right = T.PhotoImage(file="icons/charright.png")

        self.draw_gui()

        # keyboard events
        self.master.bind("<Left>", self.move)
        self.master.bind("<Up>", self.move)
        self.master.bind("<Prior>", self.move)
        self.master.bind("<Home>", self.move)
        self.master.bind("<End>", self.move)
        self.master.bind("<Next>", self.move)
        self.master.bind("<Down>", self.move)
        self.master.bind("<Right>", self.move)

        self.master.bind("<Alt-x>", self.close)

        # mouse events
        self.t_adr.bind("<MouseWheel>", self.move)
        self.t_hexdump.bind("<MouseWheel>", self.move)
        self.t_pc_char.bind("<MouseWheel>", self.move)
        self.c_mz_dump.bind("<MouseWheel>", self.move)
        self.c_bmp.bind("<MouseWheel>", self.move)

        # if possible, open a file from a command line argument
        if sys.argv[1:] and os.path.isfile(sys.argv[1]):
            self.open_file(sys.argv[1])
        else:
            self.var_filename.set("[no file]")
            self.open_dir = "./sample_mzf/"
            self.file_data = b""
            self.position = 0
            self.visible_data = b""

        self.open_file("sample_mzf/renegade.mzf")

    def draw_gui(self):

        # Topmost widgets

        b_open = T.Button(self, text="Open file...", command=self.open_file)
        b_open.grid(sticky="e", padx=10, pady=10)

        l_filename = T.Label(self, textvariable=self.var_filename, anchor="w")
        l_filename.grid(column=1, row=0, columnspan=3, sticky="ew",
                        padx=10, pady=10)

        # Standard hex dump frame

        f_hexdump = T.Frame(self, borderwidth=3, relief="groove")
        f_hexdump.grid(columnspan=2, sticky="ns", padx=10, pady=5)

        self.t_adr = T.Text(f_hexdump, background=constants.WHITE,
                            width=6, height=32, font=self.font_textbox)
        self.t_adr.grid(padx=10, pady=10)

        self.t_hexdump = T.Text(f_hexdump, background=constants.WHITE,
                                width=23, height=32, font=self.font_textbox)
        self.t_hexdump.grid(column=1, row=0, pady=10)

        self.t_pc_char = T.Text(f_hexdump, background=constants.WHITE,
                                width=8, height=32, font=self.font_textbox)
        self.t_pc_char.grid(column=2, row=0, padx=10, pady=10)

        # Sharp MZ dump frame

        f_mz_dump = T.Frame(self, borderwidth=3, relief="groove")
        f_mz_dump.grid(column=2, row=1, sticky="ns", pady=5)

        self.c_mz_dump = T.Canvas(f_mz_dump, width=self.scale * 13 * 8,
                                  height=self.scale * 32 * 8,
                                  background=constants.BLUE,
                                  highlightthickness=0)
        self.c_mz_dump.grid(rowspan=15, padx=10, pady=13)

        rb_ascii = T.Radiobutton(f_mz_dump, text="ASCII",
                                 variable=self.var_ascii, value=1,
                                 command=self.redraw_mz_chars)
        rb_ascii.grid(column=1, row=0, sticky="sw", padx=5)

        rb_display = T.Radiobutton(f_mz_dump, text="display",
                                   variable=self.var_ascii, value=0,
                                   command=self.redraw_mz_chars)
        rb_display.grid(column=1, row=1, sticky="nw", padx=5)

        rb_charset1 = T.Radiobutton(f_mz_dump, text="charset 1",
                                    variable=self.alt_charset, value=False,
                                    command=self.redraw_mz_chars)
        rb_charset1.grid(column=1, row=2, sticky="sw", padx=5)

        rb_charset2 = T.Radiobutton(f_mz_dump, text="charset 2",
                                    variable=self.alt_charset, value=True,
                                    command=self.redraw_mz_chars)
        rb_charset2.grid(column=1, row=3, sticky="nw", padx=5)

        # Bitmap frame

        f_bitmap = T.Frame(self, borderwidth=3, relief="groove")
        f_bitmap.grid(column=3, row=1, columnspan=2, sticky="ns",
                      padx=10, pady=5)

        self.c_bmp = T.Canvas(f_bitmap, width=self.scale * 8 * 8,
                              height=self.scale * 32 * 8,
                              background=constants.GREEN_BLUE,
                              highlightthickness=0)
        self.c_bmp.grid(rowspan=15, padx=10, pady=13)

        l_bitmap_columns = T.Label(f_bitmap, text="Columns:")
        l_bitmap_columns.grid(column=1, row=0, sticky="ws")

        s_bitmap_columns = T.Spinbox(f_bitmap, width=2, from_=1, to=8,
                                     increment=1,
                                     textvariable=self.bmp_columns,
                                     command=self.redraw_bitmap)
        s_bitmap_columns.grid(column=2, row=0, sticky="ws", padx=10)

        l_block_height = T.Label(f_bitmap, text="Block height:")
        l_block_height.grid(column=1, row=1, sticky="nw")

        s_block_height = T.Spinbox(f_bitmap, width=2, from_=1, to=64,
                                   increment=1,
                                   textvariable=self.bmp_block_height,
                                   command=self.redraw_bitmap)
        s_block_height.grid(column=2, row=1, sticky="nw", padx=10)

        l_displayed = T.Label(f_bitmap, text="Bytes displayed:")
        l_displayed.grid(column=1, row=2, sticky="nw")

        s_displayed = T.Spinbox(f_bitmap, width=4, from_=256, to=2048,
                                increment=256, textvariable=self.bmp_displayed,
                                command=self.redraw_bitmap)
        s_displayed.grid(column=2, row=2, sticky="nw", padx=10)

        cb_flipped = T.Checkbutton(f_bitmap, text="horizontal flip",
                                   variable=self.bmp_flipped,
                                   command=self.redraw_bitmap)
        cb_flipped.grid(column=1, row=3, columnspan=2, sticky="nw")

        # Navigation buttons

        f_navigate = T.Frame(self, borderwidth=3, relief="groove")
        f_navigate.grid(column=1, columnspan=3, padx=10, pady=10)

        b_char_left = T.Button(f_navigate, text="Char\nLeft",
                               image=self.img_char_left, compound="top",
                               command=lambda: self.move("Left"))
        b_char_left.grid()

        b_line_up = T.Button(f_navigate, text="Line\nUp",
                             image=self.img_line_up, compound="top",
                             command=lambda: self.move("Up"))
        b_line_up.grid(column=1, row=0)

        b_page_up = T.Button(f_navigate, text="Page\nUp",
                             image=self.img_page_up, compound="top",
                             command=lambda: self.move("Prior"))
        b_page_up.grid(column=2, row=0)

        b_home = T.Button(f_navigate, text="Home\n",
                          image=self.img_home, compound="top",
                          command=lambda: self.move("Home"))
        b_home.grid(column=3, row=0)

        b_end = T.Button(f_navigate, text="End\n",
                         image=self.img_end, compound="top",
                         command=lambda: self.move("End"))
        b_end.grid(column=4, row=0)

        b_page_down = T.Button(f_navigate, text="Page\nDown",
                               image=self.img_page_down, compound="top",
                               command=lambda: self.move("Next"))
        b_page_down.grid(column=5, row=0)

        b_line_down = T.Button(f_navigate, text="Line\nDown",
                               image=self.img_line_down, compound="top",
                               command=lambda: self.move("Down"))
        b_line_down.grid(column=6, row=0)

        b_char_right = T.Button(f_navigate, text="Char\nRight",
                                image=self.img_char_right, compound="top",
                                command=lambda: self.move("Right"))
        b_char_right.grid(column=7, row=0)

        # Exit button

        b_exit = T.Button(self, text="Exit", command=self.close)
        b_exit.grid(column=4, row=2, sticky="es", padx=10, pady=10)

    def open_file(self, filename=None):

        if not filename:
            dialog = filedialog.Open(self, initialdir=self.open_dir,
                                     filetypes=(("MZF files", "*.mzf"),
                                                ("MZ* files", "*.mz*"),
                                                ("All files", "*")))
            filename = dialog.show()

        if filename:
            self.var_filename.set(filename)
            self.open_dir = os.path.split(os.path.abspath(filename))[0]

            with open(filename, "rb") as f:
                self.file_data = f.read()

            self.mz_from = int.from_bytes(self.file_data[20:22], "little")
            self.position = 0
            self.visible_data = self.file_data[:256]
            self.redraw_main()
            self.redraw_mz_chars()
            self.redraw_bitmap()

    def move(self, arg):
        jumps = {"Left": -1, "Right": 1, "Up": -8, "Down": 8,
                 "Prior": -256, "Next": 256,
                 "Home": -len(self.file_data), "End": len(self.file_data),
                 "ScrollUp": -32, "ScrollDown": 32}

        # if 'arg' is not one of the strings above, 'arg' is an event
        if arg not in jumps:

            if str(arg.type) in ("2", "KeyPress"):
                arg = arg.keysym

            elif str(arg.type) in ("38", "MouseWheel"):
                arg = "ScrollDown" if arg.delta < 0 else "ScrollUp"

        if self.file_data:
            old_position = self.position
            self.position += jumps[arg]

            if self.position < 0:
                self.position = 0
            elif self.position >= len(self.file_data):
                self.position = len(self.file_data) - 1

            if self.position != old_position:
                self.visible_data = self.file_data[self.position:
                                                   self.position + 256]
                self.redraw_main()
                self.redraw_mz_chars()
                self.redraw_bitmap()

    def redraw_main(self):
        """Update the contents of the 't_adr', 't_hexdump', 't_pc_char' text
        widgets, and redraw addresses and header highlight on the 'c_mz_dump'
        canvas.
        """
        q = 8 * self.scale

        self.t_adr["state"] = "normal"
        self.t_adr.delete("1.0", "end")
        self.t_hexdump["state"] = "normal"
        self.t_hexdump.delete("1.0", "end")
        self.t_pc_char["state"] = "normal"
        self.t_pc_char.delete("1.0", "end")

        self.c_mz_dump.delete("all")

        for j in range(32):
            line_empty = True

            for i in range(8):
                index = j*8 + i
                if self.visible_data[index:]:
                    byte = self.visible_data[index]
                    line_empty = False
                else:
                    break

                # different color for MZ header
                if self.position + index < 0x80:
                    self.c_mz_dump.create_rectangle(q*(i + 5), q*j,
                                                    q*(i + 6), q*(j + 1),
                                                    fill=constants.GREY_BLUE,
                                                    width=0)

                self.t_hexdump.insert("end", "{:02X}".format(byte))
                if i < 7:
                    self.t_hexdump.insert("end", " ")

                self.t_pc_char.insert("end",
                                      chr(byte) if 31 < byte < 127 else " ")

            if not line_empty:
                line_adr = self.position + j*8
                self.t_adr.insert("end", "{:#06x}".format(line_adr))

                # when not in header, show MZ address + colon
                if line_adr >= 0x80:
                    mz_adr = "{:04X}:".format(line_adr + self.mz_from - 128)

                    for i5 in range(5):
                        asc = ord(mz_adr[i5])

                        # draw MZ char, regardless of var_ascii and alt_charset
                        self.c_mz_dump.create_image(q * i5, q * j,
                                                    image=self.charset
                                                    [self.asc_to_disp[asc]],
                                                    anchor="nw")
            else:
                break

        self.t_adr["state"] = "disabled"
        self.t_hexdump["state"] = "disabled"
        self.t_pc_char["state"] = "disabled"

    def redraw_mz_chars(self):
        """Redraw ascii chars (but not addresses) on the 'c_mz_dump' canvas.
        """
        q = 8 * self.scale

        self.c_mz_dump.delete("chr")

        for j in range(32):
            for i in range(8):
                index = j*8 + i
                if self.visible_data[index:]:
                    byte = self.visible_data[index]
                else:
                    break

                # draw MZ char according to var_ascii and alt_charset
                byte = (self.asc_to_disp[byte]
                        if self.var_ascii.get() else byte)
                if self.alt_charset.get():
                    byte += 256
                tag = "item{}".format(index)
                self.c_mz_dump.create_image(q*(i + 5), q*j,
                                            image=self.charset[byte],
                                            activeimage=self.charset_active[byte],
                                            anchor="nw",
                                            tags="{} chr".format(tag))
                self.c_mz_dump.tag_bind(tag, "<Enter>", self.mouse_enter)
                self.c_mz_dump.tag_bind(tag, "<Leave>", self.mouse_leave)

    def mouse_enter(self, event):
        current_tags = event.widget.itemconfigure("current", "tags")[4]
        index = int(current_tags.strip(constants.NON_DIGITS))

        self.backup_char = self.c_mz_dump.itemconfigure("item{}".format(index),
                                                        "image")[4]
        active_char = self.c_mz_dump.itemconfigure("item{}".format(index),
                                                   "activeimage")[4]
        self.c_mz_dump.itemconfigure("item{}".format(index),
                                     image=active_char)

        self.backup_bmp = self.c_bmp.itemconfigure("item{}".format(index),
                                                   "image")[4]
        active_bmp = self.c_bmp.itemconfigure("item{}".format(index),
                                              "activeimage")[4]
        self.c_bmp.itemconfigure("item{}".format(index),
                                 image=active_bmp)

        self.backup_index = index

    def mouse_leave(self, event):
        self.c_mz_dump.itemconfigure("item{}".format(self.backup_index),
                                     image=self.backup_char)
        self.c_bmp.itemconfigure("item{}".format(self.backup_index),
                                 image=self.backup_bmp)

    def redraw_bitmap(self):
        """Redraw the contents of the 'c_bmp' bitmap canvas.
        """

        self.c_bmp.delete("all")
        row_length = int(self.bmp_columns.get())
        block_height = int(self.bmp_block_height.get())

        for j in range(int(self.bmp_displayed.get())
                       // (row_length * block_height)):

            for i in range(row_length):

                for k in range(block_height):
                    index = j*row_length*block_height + i*block_height + k

                    if self.file_data[self.position:][index:]:
                        # 'visible_data' not used here, as there can be
                        # much more data displayed on this canvas
                        byte = self.file_data[self.position:][index]
                    else:
                        break

                    # draw a single 8x1 bitmap
                    if self.bmp_flipped.get():
                        byte = self.flipped_values[byte]
                    tag = "item{}".format(index)
                    self.c_bmp.create_image(i * 8 * self.scale,
                                            self.scale*(j*block_height + k),
                                            image=self.bitmaps[byte],
                                            activeimage=self.bitmaps_active[byte],
                                            anchor="nw", tag=tag)
                    self.c_bmp.tag_bind(tag, "<Enter>", self.mouse_enter)
                    self.c_bmp.tag_bind(tag, "<Leave>", self.mouse_leave)

    def close(self, *args):
        """Close the application window. Called with one <tkinter.Event>
        argument when using the Alt+X shortcut, or without this argument when
        using the Exit button.
        """

        self.master.destroy()


def main():
    root = T.Tk()
    root.wm_title("MZF Viewer")
    app = ViewerApp(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
