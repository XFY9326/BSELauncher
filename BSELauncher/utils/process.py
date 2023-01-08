import os
import traceback
from typing import Optional


def raise_process_error(ex):
    if ex is not KeyboardInterrupt:
        traceback.print_exception(ex)
    else:
        raise ex


def get_default_worker_size(min_size: int, setup_workers: Optional[int]) -> int:
    if setup_workers is None:
        return max(1, min(min_size, os.cpu_count() - 1))
    else:
        return setup_workers
