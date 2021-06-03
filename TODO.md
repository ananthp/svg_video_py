# TODO

* setup repo for this
    * [x] github
    * [ ] gitlab
    
* [x] add readme, gitignore, license
* [ ] add copyright notice in readme?

* modularize, split lib and cli tools
* use `logging` in lib (instead of `print`)
* progressbar in cli
* use iterators/generators?

## add setuptools

* `setup.cfg` provides dependency management: https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html
* `requirements.txt` also does the same: https://packaging.python.org/tutorials/installing-packages/#id22 
* which one to use?
    * pip's `requirements.txt` provides both upper and lower bounds for versions, ">=1.0,<2.0", not possible with `setup.cfg`?

## How to distribute to non-developer audience?

* installable with pip, pipx?
* docker?
* ask in stackoverflow or python specific discord

## [Feature] scroll: render only a portion 

* start frame, end frame
* preserve frame number

## [Feature] scroll: infer frame size

Currently we have to manually specify frame size to `Scroller`. There are ways to get the frame size from the SVG file automatically:
* read width and height from svg header.
    - possibility of height/width attributes missing, different units, viewbox, scaling etc makes this tricky. any lib does this already?
* render the page using inkscape (`--export-area-page`) and inspect the generated file.
    - rendering could take time.

## [Refactor] make calculations absolute, not relative to current state

currently, there's a rectangle object pointing to the current frame coordinates, and the progress is made by moving the rectangle successivly and making cuts. This is problematic for the following reasons:
* cumulative error: If we should shift 4.5 px every frame, we end up shifting either 4 or 5 frames.
  these round off errors will accumulate.
* when we want to render only a portion of a video, it's better to directly calculate the necessary frames' coordinates,
  rather than setting advancing internal states.
* relying on mutable internal state make it difficult to parallelize?
