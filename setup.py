from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules = cythonize('src\\event_processing\\draw_events.pyx', annotate=False),
    include_dirs=[np.get_include()]
)

extensions = [
    Extension('PMD', ['src\\PMD\\*.pyx'],
        include_dirs=[np.get_include()]
        ),
    Extension("draw_events", ['src\\event_processing\\draw_events.pyx'],
        include_dirs=[np.get_include()]
        ),
]
setup(
    name="Async CV",
    ext_modules=cythonize(extensions, annotate=True),
)