#!/usr/bin/env python

import os
import subprocess as sp
from argparse import ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Sequence

import nibabel as nib
from bicpl import PolygonObj
from chris_plugin import chris_plugin, PathMapper
from civet.minc import Mask
from loguru import logger
from nibabel.affines import apply_affine
from skimage import measure

parser = ArgumentParser(description='scikit-image marching-cubes + mincblur ChRIS plugin')
parser.add_argument('-l', '--level', default=None, type=float,
                    help='Contour value to search for isosurfaces in volume.'
                         'If not given or None, the average of the min and max'
                         ' of vol is used.')
parser.add_argument('--spacing', default='1,1,1',
                    help='Voxel spacing in spatial dimensions corresponding'
                         ' to numpy array indexing dimensions (M, N, P).')
parser.add_argument('-s', '--step-size', default=1, type=int,
                    help='Step size in voxels. '
                         'Larger steps yield faster but coarser results. '
                         'The result will always be topologically correct though.')
parser.add_argument('-m', '--method', default='lewiner',
                    choices=('lewiner', 'lorensen'),
                    help='Specify which of Lewiner et al. or Lorensen et al.'
                         ' method will be used.')
parser.add_argument('-p', '--pattern', default='**/*.mnc',
                    help='pattern for file names to include')
parser.add_argument('-f', '--fwhm', type=float, default=3.0,
                    help='Amount of blurring (mincblur -fwhm) to do as preprocessing. '
                         'A value of 0 skips blurring.')


def __quiet_shell(cmd: Sequence[str | os.PathLike]) -> None:
    sp.run(cmd, check=True, stdout=sp.DEVNULL, stderr=sp.STDOUT)


@contextmanager
def mincblur(mask_path: Path, fwhm: float) -> str:
    if fwhm == 0:
        yield str(mask_path)
        return
    with NamedTemporaryFile(suffix='.mnc') as tmp:
        Mask(mask_path).resamplef64().mincblur(fwhm=fwhm).save(tmp.name, shell=__quiet_shell)
        yield tmp.name


def mcubes(mask_path: Path, surface_path: Path,
           fwhm: float,
           level: float,
           spacing: tuple[float, float, float],
           step_size: int,
           method: str):
    with mincblur(mask_path, fwhm) as blurred:
        blurred_mask = nib.load(blurred)
    data = blurred_mask.get_fdata()
    verts, faces, normals, values = measure.marching_cubes(
        data, level=level, spacing=spacing, step_size=step_size, method=method, allow_degenerate=False
    )
    transformed_verts = apply_affine(blurred_mask.affine, verts)
    obj = PolygonObj.from_data(transformed_verts, faces, normals)
    obj.save(surface_path)
    logger.info('Completed: {} => {}', mask_path, surface_path)


@chris_plugin(
    parser=parser,
    title='Scikit-Image Marching Cubes',
    category='Surface Extraction',
    min_memory_limit='200Mi',
    min_cpu_limit='1000m',
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    spacing = tuple(float(n) for n in options.spacing.split(','))

    logger.info('scikit-image marching_cubes: fwhm={} spacing={} step_size={} method={}',
                options.fwhm, spacing, options.step_size, options.method)

    results = []
    with ThreadPoolExecutor(max_workers=len(os.sched_getaffinity(0))) as pool:
        mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix='.obj')
        for mnc, obj in mapper:
            results.append(pool.submit(mcubes, mnc, obj,
                                       options.fwhm, options.level, spacing,
                                       options.step_size, options.method))

    for future in results:
        e = future.exception()
        if e is not None:
            raise e


if __name__ == '__main__':
    main()
