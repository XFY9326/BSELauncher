# BSE Launcher

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

Advanced Parallel Run Tool for [davecliff/BristolStockExchange](https://github.com/davecliff/BristolStockExchange)

Meet your pursuit of execution speed and high CPU usage 😊

## Features

- Perfect parameter prompt
- Multiple ways to run in parallel for speed
- Only one dependency: tqdm

## Usage

1. Install ‘tqdm’ first:

    ```bash
    python -m pip install tqdm
    ```

2. Download 'BSELauncher' folder to your project root path

3. Import code:

    ```python
    from BSELauncher import *
    ```

4. For more usage methods, you can view the test code in main.py

## Need to run faster?

You can speed up BSE with [Cython](https://cython.org/)

Cython speeds up operation by compiling Python files into native library files supported by the platform

Related tools have been stored in the BSEUtils folder

1. Download the 'BSE.py' file using the 'downloadBSE' script supported by the platform or download it manually.
2. Install Cython using command `python -m pip install cython`.
3. Install the relevant compiler tools required by Cython. e.g. VC++ or GCC
4. Compile 'BSE.py' file using the 'build' script supported by the platform or execute it manually.
5. Copy 'BSE.XXXX.pyd' to the directory at the same level as the project python file.
6. (Optional) Rename 'BSE.XXXX.pyd' to 'BSE.pyd'.
7. Import BSE as usual.

After testing, it can reduce the time consumption by about one-third.

## Attention

This BSE.py script is based on commit '29b943e'.

The BSE used here adds the parameter specifying the output file path.

