from setuptools import setup

setup(
    name             = 'ep-skimage-mcubes-mni',
    version          = '1.0.0',
    description      = 'Marching-cubes implementation from scikit-image',
    author           = 'Jennings Zhang',
    author_email     = 'Jennings.Zhang@childrens.harvard.edu',
    url              = 'https://github.com/jennydaman/ep-skimage-mcubes-mni',
    py_modules       = ['skimc'],
    install_requires = ['chris_plugin', 'pybicpl', 'nibabel', 'scikit-image', 'h5py', 'loguru'],
    license          = 'MIT',
    python_requires  = '>=3.10.2',
    entry_points     = {
        'console_scripts': [
            'skimc = skimc:main'
            ]
        },
    classifiers      = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
