# Naming convention in this file:
#
# name starting with f_   ...  Frame widget
#                    l_   ...  Label widget
#                    t_   ...  Text widget
#                    c_   ...  Canvas widget
#                    b_   ...  Button widget
#                   rb_   ...  Radiobutton widget
#                   cb_   ...  Checkbutton widget
#                   sb_   ...  Spinbox widget
#                    m_   ...  Menu widget


from collections import defaultdict
from functools import lru_cache
import itertools
from pathlib import Path
import pickle
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import font

from mzfviewer import constants
from mzfviewer import utils


class ViewerApp(tk.Tk):    # pylint: disable=too-many-ancestors
    def __init__(self):
        super().__init__()
        self.tk_setPalette(constants.MAIN_BG)

        with open(constants.DATA_DIR / 'charset_zoom_2.pickle', 'rb') as f:
            charset_zoom_2 = pickle.load(f)
        with open(constants.DATA_DIR / 'charset_zoom_3.pickle', 'rb') as f:
            charset_zoom_3 = pickle.load(f)

        self.charsets = {
            2: tuple(tk.BitmapImage(data=bitmap, foreground=constants.WHITE)
                     for bitmap in charset_zoom_2),
            3: tuple(tk.BitmapImage(data=bitmap, foreground=constants.WHITE)
                     for bitmap in charset_zoom_3),
        }
        self.charsets_active = {
            2: tuple(tk.BitmapImage(data=bitmap, **constants.ACTIVE)
                     for bitmap in charset_zoom_2),
            3: tuple(tk.BitmapImage(data=bitmap, **constants.ACTIVE)
                     for bitmap in charset_zoom_3),
        }

        with open(constants.DATA_DIR / 'bitmaps_zoom_2.pickle', 'rb') as f:
            bitmaps_zoom_2 = pickle.load(f)
        with open(constants.DATA_DIR / 'bitmaps_zoom_3.pickle', 'rb') as f:
            bitmaps_zoom_3 = pickle.load(f)

        self.bmps = {
            2: tuple(tk.BitmapImage(data=bitmap, foreground=constants.WHITE)
                     for bitmap in bitmaps_zoom_2),
            3: tuple(tk.BitmapImage(data=bitmap, foreground=constants.WHITE)
                     for bitmap in bitmaps_zoom_3)
        }
        self.bmps_blue = {
            2: tuple(tk.BitmapImage(data=bitmap, foreground=constants.LITE_BLUE)
                     for bitmap in bitmaps_zoom_2),
            3: tuple(tk.BitmapImage(data=bitmap, foreground=constants.LITE_BLUE)
                     for bitmap in bitmaps_zoom_3)
        }
        self.bmps_active = {
            2: tuple(tk.BitmapImage(data=bitmap, **constants.ACTIVE)
                     for bitmap in bitmaps_zoom_2),
            3: tuple(tk.BitmapImage(data=bitmap, **constants.ACTIVE)
                     for bitmap in bitmaps_zoom_3)
        }

        with open(constants.DATA_DIR / 'flipped.pickle', 'rb') as f:
            self.flipped_values = pickle.load(f)
        with open(constants.DATA_DIR / 'asc_to_disp.pickle', 'rb') as f:
            self.asc_to_disp = pickle.load(f)
        self.fn_id_cache = defaultdict(lambda: {'<Enter>': {}, '<Leave>': {}})

        # variables to be directly connected with widgets
        self.zoom = tk.IntVar()
        self.filename = tk.StringVar()

        self.asc_code = tk.BooleanVar()
        self.asc_code.set(True)

        self.alt_charset = tk.BooleanVar()
        self.alt_charset.set(False)

        self.bmp_columns = tk.IntVar()

        self.bmp_block_height = tk.IntVar()
        self.bmp_block_height.set('8')

        self.bmp_displayed = tk.IntVar()

        self.bmp_flipped = tk.BooleanVar()
        self.bmp_flipped.set(False)

        self.mono_font = font.Font(name='TkFixedFont', exists=True)
        self.draw_gui()

        self.file_data = None
        self.zoom.set(2)
        self.set_zoom()

        self.bind_keyboard_events()
        self.bind_mouse_events()

        # if possible, open a file from a command line argument
        if sys.argv[1:] and Path(sys.argv[1]).is_file():
            self.open_file(sys.argv[1])
        else:
            self.filename.set('')
            self.show_filename_in_title()
            self.open_dir = './sample_mzf/'
            self.file_data = b''
            self.position = 0
            self.visible_data = b''

    def draw_gui(self):
        self['menu'] = self.get_menu_bar()

        # Standard hex dump frame

        f_hexdump = tk.Frame(self, borderwidth=3, relief='groove')
        f_hexdump.grid(columnspan=5, row=15, sticky='ns', padx=10, pady=5)

        self.t_adr = tk.Text(f_hexdump, background=constants.WHITE,
                             width=6, height=32, cursor='arrow',
                             font=self.mono_font)
        self.t_adr.grid(padx=10, pady=10)

        self.t_hexdump = tk.Text(f_hexdump, background=constants.WHITE,
                                 width=23, height=32, cursor='arrow',
                                 font=self.mono_font)
        self.t_hexdump.grid(column=1, row=0, pady=10)

        self.t_pc_char = tk.Text(f_hexdump, background=constants.WHITE,
                                 width=8, height=32, cursor='arrow',
                                 font=self.mono_font)
        self.t_pc_char.grid(column=2, row=0, padx=10, pady=10)

        # Sharp MZ dump frame

        f_mz_dump = tk.Frame(self, borderwidth=3, relief='groove')
        f_mz_dump.grid(column=5, columnspan=5, row=15, sticky='ns', pady=5)

        self.c_mz_dump = tk.Canvas(f_mz_dump, background=constants.BLUE,
                                   highlightthickness=0)
        self.c_mz_dump.grid(rowspan=15, padx=10, pady=13)

        rb_ascii = tk.Radiobutton(f_mz_dump, text='ASCII',
                                  variable=self.asc_code, value=True,
                                  command=self.redraw_mz_chars)
        rb_ascii.grid(column=1, row=0, sticky='sw', padx=5)

        rb_display = tk.Radiobutton(f_mz_dump, text='Display',
                                    variable=self.asc_code, value=False,
                                    command=self.redraw_mz_chars)
        rb_display.grid(column=1, row=1, sticky='nw', padx=5)

        rb_charset1 = tk.Radiobutton(f_mz_dump, text='Charset 1',
                                     variable=self.alt_charset, value=False,
                                     command=self.redraw_mz_chars)
        rb_charset1.grid(column=1, row=2, sticky='sw', padx=5)

        rb_charset2 = tk.Radiobutton(f_mz_dump, text='Charset 2',
                                     variable=self.alt_charset, value=True,
                                     command=self.redraw_mz_chars)
        rb_charset2.grid(column=1, row=3, sticky='nw', padx=5)

        # Bitmap frame

        f_bitmap = tk.Frame(self, borderwidth=3, relief='groove')
        f_bitmap.grid(column=10, columnspan=5, row=15, sticky='ns',
                      padx=10, pady=5)

        self.c_bmp = tk.Canvas(f_bitmap, background=constants.GREY_BLUE,
                               highlightthickness=0)
        self.c_bmp.grid(column=3, rowspan=15, padx=10, pady=13)

        l_bitmap_columns = tk.Label(f_bitmap, text='Columns:')
        l_bitmap_columns.grid(column=1, row=0, sticky='ws')

        # TODO:
        #  `Columns` and `Block height` spinboxes: Explore spinbox
        #  value validation and how to use it when values are edited
        #  from keyboard. Can MouseWheel events be used to control
        #  these spinboxes?

        sb_bitmap_columns = tk.Spinbox(f_bitmap, width=2, from_=1, to=32,
                                       increment=1,
                                       textvariable=self.bmp_columns,
                                       command=self.redraw_bitmap)
        sb_bitmap_columns.grid(column=2, row=0, sticky='ws', padx=10)

        l_block_height = tk.Label(f_bitmap, text='Block height:')
        l_block_height.grid(column=1, row=1, sticky='nw')

        sb_block_height = tk.Spinbox(f_bitmap, width=2, from_=1, to=64,
                                     increment=1,
                                     textvariable=self.bmp_block_height,
                                     command=self.redraw_bitmap)
        sb_block_height.grid(column=2, row=1, sticky='nw', padx=10)

        l_disp = tk.Label(f_bitmap, text='Bytes displayed:')
        l_disp.grid(column=1, row=2, sticky='nw')

        # TODO:
        #  `Bytes displayed` widget: Change to a roll-down list?
        #  (currently only 8 possible values)

        sb_disp = tk.Spinbox(f_bitmap, width=4, from_=256, to=2048,
                             increment=256, textvariable=self.bmp_displayed,
                             command=self.redraw_bitmap)
        sb_disp.grid(column=2, row=2, sticky='nw', padx=10)

        cb_flipped = tk.Checkbutton(f_bitmap, text='Horizontal flip',
                                    variable=self.bmp_flipped,
                                    command=self.redraw_bitmap)
        cb_flipped.grid(column=1, row=3, columnspan=2, sticky='nw')

    def get_menu_bar(self):
        m_main = tk.Menu(self)

        # File menu
        self.m_file = tk.Menu(m_main, tearoff=False)
        self.m_file.add('command', label='Open...', underline=0,
                        accelerator='Ctrl+O', command=self.open_file)
        self.m_file.add('separator')
        self.m_file.add('command', label='Quit', underline=0,
                        accelerator='Ctrl+Q', command=self.close)

        # View menu
        self.m_view = tk.Menu(m_main, tearoff=False)
        self.m_view.add('radiobutton', label='Double zoom (200%)', underline=0,
                        variable=self.zoom, value=2,
                        accelerator='Ctrl+D', command=self.set_zoom)
        self.m_view.add('radiobutton', label='Triple zoom (300%)', underline=0,
                        variable=self.zoom, value=3,
                        accelerator='Ctrl+T', command=self.set_zoom)

        # Navigate menu
        self.m_navigate = tk.Menu(m_main, tearoff=False)
        self.m_navigate.add('command', label='Char left', accelerator='Left',
                            command=lambda: self.move('Left'))
        self.m_navigate.add('command', label='Char right', accelerator='Right',
                            command=lambda: self.move('Right'))
        self.m_navigate.add('separator')
        self.m_navigate.add('command', label='Line up', accelerator='Up',
                            command=lambda: self.move('Up'))
        self.m_navigate.add('command', label='Line down', accelerator='Down',
                            command=lambda: self.move('Down'))
        self.m_navigate.add('separator')
        self.m_navigate.add('command', label='Page up', accelerator='PageUp',
                            command=lambda: self.move('Prior'))
        self.m_navigate.add('command', label='Page down',
                            accelerator='PageDown',
                            command=lambda: self.move('Next'))
        self.m_navigate.add('separator')
        self.m_navigate.add('command', label='To beginning', accelerator='Home',
                            command=lambda: self.move('Home'))
        self.m_navigate.add('command', label='To end', accelerator='End',
                            command=lambda: self.move('End'))

        m_main.add('cascade', label='File', underline=0, menu=self.m_file)
        m_main.add('cascade', label='View', underline=0, menu=self.m_view)
        m_main.add('cascade', label='Navigate', underline=0,
                   menu=self.m_navigate)
        return m_main

    def bind_keyboard_events(self):
        self.bind('<Control-o>', lambda event: self.m_file.invoke(0))
        self.bind('<Control-q>', lambda event: self.m_file.invoke(2))

        self.bind('<Control-d>', lambda event: self.m_view.invoke(0))
        self.bind('<Control-t>', lambda event: self.m_view.invoke(1))

        self.bind('<Left>', lambda event: self.m_navigate.invoke(0))
        self.bind('<Right>', lambda event: self.m_navigate.invoke(1))
        self.bind('<Up>', lambda event: self.m_navigate.invoke(3))
        self.bind('<Down>', lambda event: self.m_navigate.invoke(4))
        self.bind('<Prior>', lambda event: self.m_navigate.invoke(6))
        self.bind('<Next>', lambda event: self.m_navigate.invoke(7))
        self.bind('<Home>', lambda event: self.m_navigate.invoke(9))
        self.bind('<End>', lambda event: self.m_navigate.invoke(10))

    def bind_mouse_events(self):
        # mouse wheel events (Windows)
        self.t_adr.bind('<MouseWheel>', self.move)
        self.t_hexdump.bind('<MouseWheel>', self.move)
        self.t_pc_char.bind('<MouseWheel>', self.move)
        self.c_mz_dump.bind('<MouseWheel>', self.move)
        self.c_bmp.bind('<MouseWheel>', self.move)

        # mouse wheel events (Linux)
        self.t_adr.bind('<Button-4>', self.move)
        self.t_adr.bind('<Button-5>', self.move)
        self.t_hexdump.bind('<Button-4>', self.move)
        self.t_hexdump.bind('<Button-5>', self.move)
        self.t_pc_char.bind('<Button-4>', self.move)
        self.t_pc_char.bind('<Button-5>', self.move)
        self.c_mz_dump.bind('<Button-4>', self.move)
        self.c_mz_dump.bind('<Button-5>', self.move)
        self.c_bmp.bind('<Button-4>', self.move)
        self.c_bmp.bind('<Button-5>', self.move)

        # mouse over and out events
        self.bind_mouse_to_canvas_tags(self.c_mz_dump)
        self.bind_mouse_to_canvas_tags(self.c_bmp)

    def open_file(self, filename=None):

        if not filename:
            dialog = filedialog.Open(self, initialdir=self.open_dir,
                                     filetypes=(('MZF files', '*.mzf'),
                                                ('MZ* files', '*.mz*'),
                                                ('All files', '*')))
            filename = dialog.show()

        if filename:
            self.filename.set(filename)
            self.show_filename_in_title()
            self.open_dir = Path(filename).resolve().parent

            with open(filename, 'rb') as f:
                self.file_data = f.read()

            self.mz_from = int.from_bytes(self.file_data[20:22], 'little')
            self.position = 0
            self.visible_data = self.file_data[:256]
            self.redraw_main()
            self.redraw_mz_chars()
            self.redraw_bitmap()

    def show_filename_in_title(self):
        filename = self.filename.get()
        if filename:
            self.wm_title(f'{Path(filename).name} - {constants.APP_NAME}')
        else:
            self.wm_title(constants.APP_NAME)

    def move(self, arg):
        jumps = {'Left': -1, 'Right': 1, 'Up': -8, 'Down': 8,
                 'Prior': -256, 'Next': 256,
                 'Home': -len(self.file_data), 'End': len(self.file_data),
                 'ScrollUp': -32, 'ScrollDown': 32}

        # if `arg` is not one of the strings above, it is a mouse wheel event
        if arg not in jumps:

            # mouse wheel on Windows
            if str(arg.type) in ('38', 'MouseWheel'):
                arg = 'ScrollDown' if arg.delta < 0 else 'ScrollUp'

            # mouse wheel on Linux
            elif arg.type == '4':
                arg = {4: 'ScrollUp', 5: 'ScrollDown'}[arg.num]

        if self.file_data:
            old_position = self.position
            self.position += jumps[arg]

            if self.position < 0:
                self.position = 0
            elif self.position >= len(self.file_data):
                self.position = len(self.file_data) - 1

            if self.position != old_position:
                self.visible_data = self.file_data[self.position:][:256]
                self.redraw_main()
                self.redraw_mz_chars()
                self.redraw_bitmap()

    def set_zoom(self):
        zoom = self.zoom.get()

        # monospaced font for the text widgets
        self.mono_font['size'] = self.get_mono_font_size(zoom)

        self.charset = self.charsets[zoom]
        self.charset_active = self.charsets_active[zoom]
        self.bitmaps = self.bmps[zoom]
        self.bitmaps_blue = self.bmps_blue[zoom]
        self.bitmaps_active = self.bmps_active[zoom]

        self.c_mz_dump['width'] = zoom * 13 * 8
        self.c_mz_dump['height'] = zoom * 32 * 8
        self.c_bmp['width'] = zoom * self.bmp_columns.get() * 8
        self.c_bmp['height'] = zoom * 32 * 8

        if self.file_data:
            self.redraw_main()
            self.redraw_mz_chars()
            self.redraw_bitmap()

    @lru_cache
    def get_mono_font_size(self, zoom):
        """Search for a font size with line height exactly zoom * 8 px.

        Return zoom * 5 pt if unsuccessful.
        """
        for size in range(zoom * 9, -zoom * 9, -1):
            self.mono_font['size'] = size
            if self.mono_font.metrics()['linespace'] == zoom * 8:
                result = size
                break
        else:
            result = zoom * 5

        return result

    def redraw_main(self):
        """Update the contents of the 't_adr', 't_hexdump', 't_pc_char' text
        widgets, and redraw addresses and header highlight on the 'c_mz_dump'
        canvas.
        """
        q = 8 * self.zoom.get()

        self.t_adr['state'] = 'normal'
        self.t_adr.delete('1.0', 'end')
        self.t_hexdump['state'] = 'normal'
        self.t_hexdump.delete('1.0', 'end')
        self.t_hexdump.tag_delete(*self.t_hexdump.tag_names())
        self.t_pc_char['state'] = 'normal'
        self.t_pc_char.delete('1.0', 'end')
        self.t_pc_char.tag_delete(*self.t_pc_char.tag_names())

        self.c_mz_dump.delete('all')

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

                tag = 'item{}'.format(index)
                self.t_hexdump.insert('end', '{:02X}'.format(byte), tag)
                if i < 7:
                    self.t_hexdump.insert('end', ' ')

                self.t_pc_char.insert('end',
                                      chr(byte) if 31 < byte < 127 else ' ',
                                      tag)

                self.rebind_mouse_to_text_tag(self.t_hexdump, tag)
                self.rebind_mouse_to_text_tag(self.t_pc_char, tag)

            if not line_empty:
                line_adr = self.position + j*8
                self.t_adr.insert('end', '{:#06x}'.format(line_adr))

                # when not in header, show MZ address + colon
                if line_adr >= 0x80:
                    mz_adr = '{:04X}:'.format(line_adr + self.mz_from - 128)

                    for x, asc in enumerate(bytes(mz_adr, 'ascii')):
                        # draw MZ char, regardless of asc_code and alt_charset
                        self.c_mz_dump.create_image(q * x, q * j,
                                                    image=self.charset
                                                    [self.asc_to_disp[asc]],
                                                    anchor='nw')
            else:
                break

        self.t_adr['state'] = 'disabled'
        self.t_hexdump['state'] = 'disabled'
        self.t_pc_char['state'] = 'disabled'

    def redraw_mz_chars(self):
        """Redraw ascii chars (but not addresses) on the 'c_mz_dump' canvas."""

        q = 8 * self.zoom.get()

        self.c_mz_dump.delete('chr')

        for index in range(256):
            if self.visible_data[index:]:
                byte = self.visible_data[index]
            else:
                break

            # draw MZ char according to asc_code and alt_charset
            byte = (self.asc_to_disp[byte]
                    if self.asc_code.get() else byte)
            if self.alt_charset.get():
                byte += 256
            tag = 'item{}'.format(index)
            self.c_mz_dump.create_image(q * (index % 8 + 5), q * (index // 8),
                                        image=self.charset[byte],
                                        activeimage=self.charset_active[byte],
                                        anchor='nw',
                                        tags='{} chr'.format(tag))

    def redraw_bitmap(self):
        """Redraw the contents of the 'c_bmp' bitmap canvas."""

        zoom = self.zoom.get()
        columns = self.bmp_columns.get()
        block_height = self.bmp_block_height.get()

        # cannot use self.visible_data here, as there can be more data
        # displayed on this canvas
        visible_data = self.file_data[self.position:][:self.bmp_displayed.get()]

        # update canvas width - necessary when called by the
        # 'sb_bitmap_columns' spinbox
        self.c_bmp['width'] = 8 * zoom * columns

        self.c_bmp.delete('all')

        for i, (row, column, k) in enumerate(itertools.product(
                                             range(32*8 // block_height),
                                             range(columns),
                                             range(block_height))):
            try:
                byte = visible_data[i]
            except IndexError:
                break

            # draw a single 8x1 bitmap
            if self.bmp_flipped.get():
                byte = self.flipped_values[byte]
            tag = 'item{}'.format(i)

            self.c_bmp.create_image(8 * zoom * column,
                                    zoom * (row*block_height + k),
                                    image=(self.bitmaps[byte]
                                           if (column + row) % 2
                                           else self.bitmaps_blue[byte]),
                                    activeimage=self.bitmaps_active[byte],
                                    anchor='nw', tag=tag)

    def mouse_enter(self, event):
        try:
            # event caught by Canvas widget
            current_tags = event.widget.gettags('current')
        except AttributeError:
            # event caught by Text widget
            current_tags = event.widget.tag_names('current')

        tag = utils.get_tag(current_tags)
        self.previous_tag = tag
        self.previous_char = None
        self.previous_bmp = None

        self.t_hexdump.tag_configure(tag, background=constants.ORANGE)
        self.t_pc_char.tag_configure(tag, background=constants.ORANGE)

        if event.widget is not self.c_mz_dump:
            self.previous_char = self.c_mz_dump.itemcget(tag, 'image')
            active_char = self.c_mz_dump.itemcget(tag, 'activeimage')
            self.c_mz_dump.itemconfigure(tag, image=active_char)

        if event.widget is not self.c_bmp and self.c_bmp.gettags(tag):
            # byte exists on c_bmp canvas
            self.previous_bmp = self.c_bmp.itemcget(tag, 'image')
            active_bmp = self.c_bmp.itemcget(tag, 'activeimage')
            self.c_bmp.itemconfigure(tag, image=active_bmp)

    def mouse_leave(self, event):    # pylint: disable=unused-argument
        tag = self.previous_tag

        if tag in self.t_hexdump.tag_names():
            self.t_hexdump.tag_configure(tag, background='')
            self.t_pc_char.tag_configure(tag, background='')
        if self.previous_char:
            self.c_mz_dump.itemconfigure(tag, image=self.previous_char)
        if self.previous_bmp:
            self.c_bmp.itemconfigure(tag, image=self.previous_bmp)

    def rebind_mouse_to_text_tag(self, widget, tag):
        cache = self.fn_id_cache[widget]['<Enter>']
        if tag in cache:
            widget.tag_unbind(tag, '<Enter>', cache[tag])
        cache[tag] = widget.tag_bind(tag, '<Enter>', self.mouse_enter)

        cache = self.fn_id_cache[widget]['<Leave>']
        if tag in cache:
            widget.tag_unbind(tag, '<Leave>', cache[tag])
        cache[tag] = widget.tag_bind(tag, '<Leave>', self.mouse_leave)

    def bind_mouse_to_canvas_tags(self, widget):
        for i in range(256):
            tag = f'item{i}'
            widget.tag_bind(tag, '<Enter>', self.mouse_enter)
            widget.tag_bind(tag, '<Leave>', self.mouse_leave)

    def close(self, *args):    # pylint: disable=unused-argument
        """Close the application window.

        Called with one <tkinter.Event> argument when using the Alt+X shortcut,
        or without this argument when using the Exit button.
        """

        self.destroy()


def main():
    app = ViewerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
