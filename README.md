# ep-skimage-mcubes-mni

[![Version](https://img.shields.io/docker/v/fnndsc/ep-skimage-mcubes-mni?sort=semver)](https://hub.docker.com/r/fnndsc/ep-skimage-mcubes-mni)
[![MIT License](https://img.shields.io/github/license/fnndsc/ep-skimage-mcubes-mni)](https://github.com/FNNDSC/ep-skimage-mcubes-mni/blob/main/LICENSE)
[![Build](https://github.com/FNNDSC/ep-skimage-mcubes-mni/actions/workflows/build.yml/badge.svg)](https://github.com/FNNDSC/ep-skimage-mcubes-mni/actions)

`ep-skimage-mcubes-mni` is a _ChRIS_ _ds_ plugin that performs the
[marching-cubes](https://scikit-image.org/docs/stable/auto_examples/edges/plot_marching_cubes.html)
algorithm on binary `.mnc` masks, producing surfaces in the `.obj` file format.
