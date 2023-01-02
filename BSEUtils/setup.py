from distutils.core import setup
from Cython.Build import cythonize

if __name__ == '__main__':
    setup(
        name="BSE",
        ext_modules=cythonize("BSE.py", language_level=3)
    )
