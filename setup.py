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
            'PMD\\EventBuffer.cpp'
        ],
        include_dirs=[np.get_include()],
        language="c++",    
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
    )
]
setup(
    name = 'async-cv',
    ext_modules = cythonize(
        extensions, 
        annotate = True,
        compiler_directives = {
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True
        }
    )
)