#!/usr/bin/env python3

from pathlib import Path
import subprocess

class VideoRenderer:
    """Converts sequence of frames stored as images to video."""

    def __init__(self, args):
        self.args = args
        self.validate_indir()
        self.validate_output()
        
    def validate_indir(self):
        indir = Path(self.args.indir)
        if not indir.exists():
            exit("Input path does not exist")

        if not indir.is_dir():
            exit(f"{args.indir} is not a directory")

    def validate_output(self):
        if self.args.output:
            self.output = self.args.output
            # TODO: create dirs if necessary
        else:
            self.output = str((Path(self.args.indir) / 'rendered.mp4').resolve())

# ffmpeg -i out/audio-track.flac -r 30 -i out/blender-%04d.png -c:v libx264 -vf yadif,format=yuv420p -force_key_frames "expr:gte(t,n_forced*0.5)" -crf 18 -bf 2 -use_editlist 0 -movflags +faststart -c:a aac -strict -2 -b:a 384k -ac 2 -ar 48000 out/rendered.mp4
    def generate_ffmpg_params(self):
        ffmpeg_params = ["ffmpeg"]

        ffmpeg_params.append('-r')
        ffmpeg_params.append(str(self.args.fps))

        prefix=self.args.prefix
        digits=self.args.digits
        indir = Path(self.args.indir) / f"{prefix}%{digits:02}d.png"
        pngs = str(indir.resolve())
        ffmpeg_params.append('-i')
        ffmpeg_params.append(pngs)

        ffmpeg_params.append('-c:v')
        ffmpeg_params.append('libx264')
        ffmpeg_params.append('-vf')
        ffmpeg_params.append('yadif,format=yuv420p')

        # ffmpeg_params.append('-force_key_frames')
        # ffmpeg_params.append('"expr:gte(t,n_forced*0.5)"')
        ffmpeg_params.append('-crf')
        ffmpeg_params.append('18')
        ffmpeg_params.append('-bf')
        ffmpeg_params.append('2')
        ffmpeg_params.append('-use_editlist')
        ffmpeg_params.append('0')
        ffmpeg_params.append('-movflags')
        ffmpeg_params.append('+faststart')
        ffmpeg_params.append(self.output)

        print(ffmpeg_params)
        return ffmpeg_params

    def render(self):
        # We are using ffmpeg cli tool.
        # ffmpeg C library and wrappers also available.
        # see:
        # * https://github.com/leandromoreira/ffmpeg-libav-tutorial/
        # * https://github.com/kkroening/ffmpeg-python
        command = self.generate_ffmpg_params()
        subprocess.run(command)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description="Renders seqeunce of images as video",
            epilog="""
                Some tools generate video sequences as sequentially numbered images. E.g. blender, other tools
                in this project.

                This script combines the images and renders them as video. The format and settings used in the video
                are based on the recommendations by youtube.

                If the images are like `/my/path/render0001.png`, use `--prefix render -d 4`
            """
            )
    parser.add_argument('indir', help="directory where PNG frames are stored")
    parser.add_argument('--output', '-o', help="video file name to render. defaults to indir/rendered.mp4")
    parser.add_argument('--fps', type=int, default=30, help="video frames per second. Ideally, it should be same as the setting used to generate images")
    parser.add_argument('--audio', help="TODO: audio file to mix with the video")
    parser.add_argument('--prefix', default='', help="Common prefix of the png files, such as render_ or frame-... Defaults is empty")
    parser.add_argument('--digits', '-d', type=int, default=6, help="number of zero-padded digits used in png sequence. Defaults to 6")
    args = parser.parse_args()

    renderer = VideoRenderer(args)
    renderer.render()
