from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules = cythonize('src\\event_processing\\draw_events.pyx', annotate=False),
    include_dirs=[np.get_include()]
)