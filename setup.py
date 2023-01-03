import os
from setuptools import setup
from Cython.Build import cythonize

if __name__ == '__main__':
    setup(
        name="BSE",
        ext_modules=cythonize(
            "BSE.py",
            nthreads=max(1, int(os.cpu_count() / 2)),
            language_level=3,
            build_dir="build",
            quiet=True
        )
    )
