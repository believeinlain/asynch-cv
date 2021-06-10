from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension('PMD\\*', 
        [
            'PMD\\PyPMD.pyx',
            'PMD\\PersistentMotionDetector.cpp',
            'PMD\\Partition.cpp',
            'PMD\\EventHandler.cpp',
            'PMD\\EventBuffer.cpp',
            'PMD\\ClusterBuffer.cpp',
            'PMD\\ClusterPrioritizer.cpp',
            'PMD\\ClusterAnalyzer.cpp'
        ],
        include_dirs = [np.get_include()],
        language = 'c++',    
        define_macros = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'), ('USE_THREADS', 1)]
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