#!/bin/env python3

"""
Renders frames for a scrolling titles example video.
"""

from pathlib import Path
import sys
import tempfile


# os.getcwd() gives the current working directory,
# not necessarily the dir where the script is located.
script_path = Path(sys.path[0])

sys.path.append(str(script_path / ".."))
from svgvid.scroll import Scroller

svg = script_path /  "scrolling_titles.svg"
outpath = Path(tempfile.gettempdir()) / "rendered"
scroller = Scroller(
               svg=svg,
               outpath=outpath,
               frame_width_px=1920, frame_height_px=1080,
               fps=30, pace=8,
           )
scroller.render()

print(f"Generated video frames to {str(outpath)}")
print("Next step: combine the images with render.py")
