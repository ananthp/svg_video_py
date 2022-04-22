from pytest import approx
import sys, math
from pathlib import Path

from svgvid.scroll import export_area, Scroller, calculate_advance


SVG_SAMPLE = Path("tests/test.svg")

# values of yellow bar copied from inkscape
# units: pixels
yellow_bar = {
    "x1": 156.055,
    "y1": 1119.626,
    "w": 159.408,
    "h": 3058.242,
}
# coordinates of the bottom right of the drawing
yellow_bar["x2"] = yellow_bar["x1"] + yellow_bar["w"]
yellow_bar["y2"] = yellow_bar["y1"] + yellow_bar["h"]


def test_sample_file_exists():
    assert SVG_SAMPLE.exists()


def test_sample_file_size():
    scroller = Scroller(SVG_SAMPLE, "/tmp", 1920, 1080, 30, 1)
    N_FRAMES = 118  # need these many frames to fully scroll the above.

    def test_height_includes_free_space_above():
        assert scroller.get_svg_height() == math.ceil(yellow_bar["y2"])
        assert scroller.estimate_frames() == N_FRAMES

    test_height_includes_free_space_above()

    def test_frame_0_always_starts_at_origin():
        first_rect = scroller.get_frame_rect(0)
        x1, y1 = first_rect.top_left().unpack()
        x2, y2 = first_rect.bottom_right().unpack()
        assert x1 == 0
        assert y1 == 0
        assert x2 == first_rect.width
        assert y2 == first_rect.height

    test_frame_0_always_starts_at_origin()

    def test_fully_scrolls_the_image_sans_residue():
        last_rect = scroller.get_frame_rect(N_FRAMES - 1)
        x1, y1 = last_rect.top_left().unpack()
        x2, y2 = last_rect.bottom_right().unpack()
        assert y1 > yellow_bar["y2"]


def test_calculate_advance():
    assert calculate_advance(100, 1, 1) == 100
    assert calculate_advance(100, 10, 1) == 10
    assert calculate_advance(100, 1, 10) == 10
