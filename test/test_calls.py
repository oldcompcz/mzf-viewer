from unittest.mock import patch, Mock

import pytest

from mzfviewer.__main__ import ViewerApp


@patch('mzfviewer.__main__.utils.generate_cgrom')
def test_generate_cgrom_not_called(generate_cgrom_mock: Mock):
    ViewerApp()
    generate_cgrom_mock.assert_not_called()


@patch('mzfviewer.__main__.utils.generate_charset')
def test_generate_charset_not_called(generate_charset_mock: Mock):
    ViewerApp()
    generate_charset_mock.assert_not_called()


@patch('mzfviewer.__main__.utils.generate_bitmaps')
def test_generate_bitmaps_not_called(generate_bitmaps_mock: Mock):
    ViewerApp()
    generate_bitmaps_mock.assert_not_called()


@pytest.mark.xfail
@patch('mzfviewer.__main__.utils.generate_flipped')
def test_generate_flipped_not_called(generate_flipped_mock: Mock):
    ViewerApp()
    generate_flipped_mock.assert_not_called()


@patch('mzfviewer.__main__.utils.zoomed')
def test_zoomed_not_called(zoomed_mock: Mock):
    ViewerApp()
    zoomed_mock.assert_not_called()
