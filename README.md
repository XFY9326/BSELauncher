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

## Progress bar by seconds

By default, the progress bar of BSE Launcher shows the progress of Task or Task and Sessions.

It is not very useful when a single task takes a very long time.

If you want to display the overall progress in seconds, you can use this function:

```python
from BSELauncher.utils import show_seconds_progress
```

The specific usage can be viewed in `seconds_progress.py`

## Need to run faster?

You can speed up BSE with [Cython](https://cython.org/)

Cython speeds up operation by compiling Python files into native library files supported by the platform

Related tools have been stored in the BSEUtils folder

1. Download the 'BSE.py' file from [GitHub Mirror](https://raw.githubusercontent.com/XFY9326/BristolStockExchange/master/BSE.py).
2. Install Cython using command `python -m pip install cython mypy`.
3. Install the relevant compiler tools required by Cython. e.g. VC++ or GCC
4. Compile 'BSE.py' file using command `python setup.py build_ext --inplace`.
5. (Optional) Create 'BSE.pyi' interface using command `stubgen --parse-only --no-import --output . BSE.py`.
6. Copy 'BSE.XXXX.pyd' or 'BSE.XXXX.so' to the directory at the same level as the project python file.
7. Import BSE as usual.

After testing, it can reduce the time consumption by about one-third.

## Attention

This BSE.py script is based on commit '29b943e'.

The BSE used here adds the parameter specifying the output file path and set `verbose=False` in `Trader_PRZI`.

