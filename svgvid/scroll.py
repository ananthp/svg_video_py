#!/bin/env python3

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import math
import os
import subprocess
import sys
import tempfile

from PIL import Image
from matplotlib import pyplot as plt
import numpy as np


@dataclass
class Point:
    """a 2D Point"""
    x: float
    y: float

    def unpack(self):
        return self.x, self.y


ORIGIN = Point(0, 0)


class Caching(Enum):
    MEMORY = auto(),
    PNG = auto(),


class Rect:
    def __init__(self, top_left: Point, width_px, height_px):
        self.x1 = top_left.x
        self.y1 = top_left.y
        self.x2 = self.x1 + width_px
        self.y2 = self.y1 + height_px
        self.width = width_px
        self.height = height_px

    def top_left(self):
        return Point(self.x1, self.y1)

    def bottom_right(self):
        return Point(self.x2, self.y2)

    def shift_down(self, by_px):
        self.y1 += by_px
        self.y2 += by_px


def export_area(rect, source, png):
    x1, y1 = rect.top_left().unpack()
    x2, y2 = rect.bottom_right().unpack() #inclusive
    if isinstance(source, np.ndarray):
        x1 = round(x1)
        y1 = round(y1)
        # due to semi-open intervals in np ranges, the second point is not inclusive.
        x2 = x1 + rect.width + 1
        y2 = y1 + rect.height + 1
        frame = source[y1:y2, x1:x2]
        plt.imsave(png, frame)
    elif str(source).endswith('.png'):
        frame = Image.open(source).crop((x1, y1, x2, y2))
        frame.save(png)
    elif str(source).endswith('.svg'):
        coords = f"{x1}:{y1}:{x2}:{y2}"
        result = subprocess.run(["inkscape", "--export-area", coords, "-o", png, source], capture_output=True, check=True)
        try:
            result.check_returncode()
        except subprocess.CalledProcessError:
            print(result.stdout.decode("UTF-8"))
            print(result.stderr.decode("UTF-8"))
            sys.exit(f"Exporting {rect} of {source} to {png} failed.\n")


def calculate_advance(height, pace, fps):
    shift_px_per_sec = height / pace
    return shift_px_per_sec / fps


class Scroller:
    def __init__(self, svg, outpath, frame_width_px, frame_height_px, fps, pace, caching=Caching.MEMORY):
        """
        svg: input SVG file path.
        outpath: directory to render output frames.
        frame_width_px, frame_height_px: width and height of the video frame.
        bottom_px: Y coordinate of the bottom of the SVG drawing in px. Decides how far to scroll.

        pace: Number of seconds to scroll one screen full. float.
        caching:
            None - no caching. each frame gets rendered directly from svg.
            Caching.MEMORY - default. renders the whole image once and caches in memory.
                             fastest, but uses more memory.
            Caching.PNG - renders the whole image once as a png file and exports each frame from it.
                          slightly faster than `None`.
        """
        self.svg = Path(svg)
        self.outpath = Path(outpath)
        self.rect = Rect(ORIGIN, frame_width_px, frame_height_px)
        self.fps = fps
        self.caching = caching
        # number of pixels to shift down for each frame
        self.advance_px = calculate_advance(height=frame_height_px, pace=pace, fps=fps)

    def render(self):
        self.validate_input()
        self.create_outpath_if_required()

        source = self.svg
        if self.caching:
            tmpdir = tempfile.TemporaryDirectory()
            source = self.cache(tmpdir)

        total_height = self.get_svg_height()

        estimated_frames = math.ceil(total_height / self.advance_px) + 1
        for current_frame in range(estimated_frames):
            print(f"Rendering Frame {current_frame+1} / {estimated_frames}")
            export_area(rect=self.rect,
                    source=source,
                    png=self.output_file_path(current_frame))
            self.advance()

    def cache(self, tmpdir):
        # we have to cache the full image + one screen full of the botom portion
        # to fully scroll away the contents.
        full_height = self.get_svg_height() + self.rect.height
        full_image_png = Path(tmpdir.name)/"full.png"
        export_area(rect=Rect(ORIGIN, self.rect.width, full_height),
                source=self.svg,
                png=full_image_png)

        if self.caching == Caching.PNG:
            return full_image_png
        elif self.caching == Caching.MEMORY:
            return plt.imread(full_image_png)

    def advance(self):
        self.rect.shift_down(self.advance_px)

    def output_file_path(self, frame_number):
        result = self.outpath / f"{frame_number:06}.png"
        return result.resolve()

    def validate_input(self):
        # TODO
        pass

    def create_outpath_if_required(self):
        if not self.outpath.exists():
            os.makedirs(self.outpath.resolve())

    def get_svg_height(self):
        """
        gets the height of the drawing using inkscape.
        This is nothing to do with the page size.
        """
        result = subprocess.run(["inkscape", "--query-height", self.svg], capture_output=True, check=True)
        try:
            height = float(result.stdout)

            # The image may start at the middle or
            # bottom of the page. The space above the first chunk
            # is not accounted.
            # adding a frame height ensures video scrolls fully
            return math.ceil(height + self.rect.height)
        except ValueError:
            print(result.stdout.decode("UTF-8"))
            print(result.stderr.decode("UTF-8"))
            sys.exit("Getting dimensions from SVG failed.\n")


if __name__ == '__main__':
    # os.getcwd() gives the current working directory,
    # not necessarily the dir where the script is located.
    script_path = sys.path[0]
    svg = Path(script_path).parent / "examples" / "scrolling_titles.svg"
    rendered = Path(tempfile.gettempdir()) / "rendered"
    scroller = Scroller(svg=svg,
                        outpath=rendered,
                        frame_width_px=1920, frame_height_px=1080,
                        fps=30, pace=8,
                        )
    scroller.render()
