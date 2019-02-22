# MZF Viewer
A tool for inspecting contents of .mzf files ([Sharp MZ-700 and MZ-800](https://en.wikipedia.org/wiki/Sharp_MZ) casette tape files).

The tool is primarily aimed at digging out sprites and other graphics from Sharp MZ-800 games and programs, but can be used to view other files as well (e.g. ZX Spectrum games, see screenshots/cyclone.png).

To do:
- make spinboxes "Columns" and "Block height" editable from keyboard, including confirming by Enter
- change binary data files to Base64 text files
- when a byte is hovered by mouse cursor in one of the "content widgets" (i.e. hex dump text, ascii char text, mz canvas, bitmap canvas), highlight the corresponding byte in the other three widgets as well
