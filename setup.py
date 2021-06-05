from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension('PMD\\*', ['PMD\\*.pyx'],
        include_dirs=[np.get_include()]
        ),
    Extension('event_processing\\*', ['event_processing\\*.pyx'],
        include_dirs=[np.get_include()]
        )
]
setup(
    name = 'async-cv',
    ext_modules = cythonize(extensions, annotate=True)
)