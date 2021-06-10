# svgvid

Utilities to produce videos using SVG files.

## Scrolling Titles
    
`svgvid.scroll.Scroller` generates videos like end-credits in movies. It takes an SVG file, and generates video frames as a sequence of PNG files.

Demo:

Running `examples/scrolling_titles.py` produces this video:

https://user-images.githubusercontent.com/494398/119168712-d5c47600-ba7e-11eb-95ed-b4e1d58456d0.mp4




Note: `Scroller` Requires [inkscape](https://inkscape.org) to be installed on the system.

## Combining Images

`render.py` creates `mp4` video by combining seqeunce of individual frames stored as images. For instance,
you can use `Scroll` to generate the images, and finally produce the video with this script. (Other video tools, notably blender, also generate image sequences).

`svgvid/render.py --help` for detailed usage info.

Notes:

* Ideally, `--fps` should match the value used to generate the image sequence.
* Requires [ffmpeg](https://ffmpeg.org) to be installed on the system.
