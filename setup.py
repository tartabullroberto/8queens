from setuptools import setup
from Cython.Build import cythonize

setup(
    name='NQueensSolver',
    ext_modules=cythonize(
        "nqueens_cython.pyx",
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'initializedcheck': False,
            'nonecheck': False
        }
    ),
)