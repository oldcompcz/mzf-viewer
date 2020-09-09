from unittest.mock import patch, Mock

from mzfviewer.__main__ import ViewerApp


@patch('mzfviewer.__main__.utils.generate_cgrom')
def test_generate_cgrom_called_once(generate_cgrom_mock: Mock):
    ViewerApp()
    assert generate_cgrom_mock.called_once()


bitmap_dummy = '''#define byte0_width 8
#define byte0_height 1
static unsigned char byte0_bits[] = { 0x0 }'''


@patch('mzfviewer.__main__.utils.generate_charset',
       return_value=[bitmap_dummy] * 512)
def test_generate_charset_call_count_and_args(generate_charset_mock: Mock):
    ViewerApp()
    assert generate_charset_mock.call_count == 2

    # test values of the `zoom` parameter
    assert [a.args[1] for a in generate_charset_mock.call_args_list] == [2, 3]


@patch('mzfviewer.__main__.utils.generate_bitmaps',
       return_value=[bitmap_dummy] * 256)
def test_generate_bitmaps_call_count_and_args(generate_bitmaps_mock: Mock):
    ViewerApp()
    assert generate_bitmaps_mock.call_count == 2

    # test values of the `zoom` parameter
    assert [a.args[0] for a in generate_bitmaps_mock.call_args_list] == [2, 3]


@patch('mzfviewer.__main__.utils.zoomed',
       side_effect=lambda byte, zoom: b' ' * zoom**2)
def test_zoomed_call_count_and_args(zoomed_mock: Mock):
    ViewerApp()
    assert zoomed_mock.call_count == 512*8*2 + 256*2

    # test all combinations of `byte` and `zoom` parameters
    assert set(a.args[:2] for a in zoomed_mock.call_args_list) \
           == set((n, zoom) for n in range(256) for zoom in (2, 3))
