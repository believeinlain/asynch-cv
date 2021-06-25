
import os
from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np
from distutils.dir_util import copy_tree, remove_tree

if not os.path.isdir('PMD'):
    os.mkdir('PMD')
if not os.path.isdir('event_processing'):
    os.mkdir('event_processing')

extensions = [
    Extension('event_processing.basic_consumer',
        [
            'src/event_processing/basic_consumer.pyx'
        ],
        include_dirs = [
            np.get_include()
        ],
        define_macros = [
            ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')
        ]
    ),
    Extension('PMD/*', 
        [
            'src/PMD/PyPMD.pyx',
            'src/PMD/PersistentMotionDetector.cpp',
            'src/PMD/EventHandler.cpp',
            'src/PMD/EventBuffer.cpp',
            'src/PMD/ClusterBuffer.cpp',
            'src/PMD/ClusterSorter.cpp',
            'src/PMD/ClusterAnalyzer.cpp'
        ],
        include_dirs = [
            np.get_include(), 
            '../CTPL'
        ],
        language = 'c++',    
        define_macros = [
            ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'), 
            ('USE_THREADS', 1)
        ]
    )
]
setup(
    name = 'async-cv',
    ext_modules = cythonize(
        extensions, 
        annotate = False,
        compiler_directives = {
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True
        }
    )
)

# cython places modules in the wrong directory, so move them to src
copy_tree('PMD', 'src/PMD')
remove_tree('PMD')
copy_tree('event_processing', 'src/event_processing')
remove_tree('event_processing')