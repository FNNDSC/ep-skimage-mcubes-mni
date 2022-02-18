#!/usr/bin/env python

import os
import nibabel as nib
from nibabel.affines import apply_affine
from skimage import measure
from bicpl import PolygonObj

from pathlib import Path
from argparse import ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from chris_plugin import chris_plugin, PathMapper

parser = ArgumentParser(description='cli description')
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


def mcubes(mask_path: Path, surface_path: Path,
           spacing: tuple[float, float, float],
           step_size: int,
           method: str):
    mask = nib.load(mask_path)
    data = mask.get_fdata()
    verts, faces, normals, values = measure.marching_cubes(
        data, spacing=spacing, step_size=step_size, method=method, allow_degenerate=False
    )
    transformed_verts = apply_affine(mask.affine, verts)
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

    logger.info('scikit-image marching_cubes: spacing={} step_size={} method={}',
                spacing, options.step_size, options.method)

    results = []
    with ThreadPoolExecutor(max_workers=len(os.sched_getaffinity(0))) as pool:
        mapper = PathMapper(inputdir, outputdir, glob=options.pattern, suffix='.obj')
        for mnc, obj in mapper:
            results.append(pool.submit(mcubes, mnc, obj, spacing, options.step_size, options.method))

    for future in results:
        future.exception()


if __name__ == '__main__':
    main()
