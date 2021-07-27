
from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension('async_cv.event_processing.draw_events',
        [
            'async_cv/event_processing/draw_events.pyx'
        ],
        include_dirs = [
            np.get_include()
        ],
        define_macros = [
            ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')
        ]
    ),
    Extension('async_cv.PMD.PyPMD', 
        [
            'async_cv/PMD/PyPMD.pyx',
            'async_cv/PMD/PersistentMotionDetector.cpp',
            'async_cv/PMD/EventHandler.cpp',
            'async_cv/PMD/EventBuffer.cpp',
            'async_cv/PMD/ClusterBuffer.cpp',
            'async_cv/PMD/ClusterSorter.cpp',
            'async_cv/PMD/ClusterAnalyzer.cpp'
        ],
        include_dirs = [
            np.get_include(), 
            '../CTPL'
        ],
        language = 'c++',    
        define_macros = [
            ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'), 
            ('USE_THREADS', 0)
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