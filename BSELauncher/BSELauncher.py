import os
import math
import random
from typing import Optional, TextIO, List
from multiprocessing import Pool, cpu_count

try:
    from tqdm import tqdm
except ImportError:
    raise ImportError("Dependency 'tqdm' is required! Please run 'python -m pip install tqdm' to install it!")

from .BSE import market_session
from .BSEConfig import MarketSessionSpec


# For internal usage only
def _raise_error(ex):
    raise ex


# For internal usage only
def _launch_market_session(session_id: str, spec_dict: dict, avg_balance_file: TextIO, output_dir: Optional[str] = None):
    market_session(sess_id=session_id, avg_bals=avg_balance_file, dump_dir=output_dir, **spec_dict)


# Simple spec wrapper
# Not recommended if there is no special need
def launch_market_session(session_id: str, spec: MarketSessionSpec, avg_balance_file: TextIO, output_dir: Optional[str] = None):
    _launch_market_session(session_id=session_id, spec_dict=spec.build(), avg_balance_file=avg_balance_file, output_dir=output_dir)


# Build faster with new_market_task
class BSEMarketTask:
    def __init__(self, session_id: str, spec: MarketSessionSpec, output_dir: Optional[str] = None):
        self.session_id: str = session_id
        self.spec: MarketSessionSpec = spec
        self.output_dir: Optional[str] = output_dir

    @staticmethod
    def _prepare_output_dir(output_dir: Optional[str]):
        if output_dir is not None:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            elif not os.path.isdir(output_dir):
                raise FileExistsError(f"A file with the same name already exists but is not a folder! '{output_dir}'")

    def _launch(self, index: int, spec_dict: dict, dump_f: TextIO):
        _launch_market_session(f"{self.session_id}_S{index}", spec_dict, dump_f, self.output_dir)

    # Use seeds to ensure reproducible results
    def launch(self, n: int = 1, seed: Optional[int] = None):
        if n <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir(self.output_dir)
        if seed is not None:
            random.seed(seed)
        with open(os.path.join(self.output_dir, f"{self.session_id}_avg_balance.csv"), "w") as f:
            for i in range(n):
                self._launch(i, market_params, f)

    def _launch_in_parallel(self, index: int, spec_dict: dict):
        with open(os.path.join(self.output_dir, f"{self.session_id}_S{index}_avg_balance.csv"), "w") as f:
            self._launch(index, spec_dict, f)

    def _combine_avg_balance(self):
        f_start = f"{self.session_id}_S"
        f_end = "_avg_balance.csv"
        avg_balance_files = [
            (f, int(f[len(f_start):-len(f_end)]))
            for f in os.listdir(self.output_dir)
            if f.startswith(f_start) and f.endswith(f_end)
        ]
        sorted(avg_balance_files, key=lambda x: x[1])
        with open(os.path.join(self.output_dir, f"{self.session_id}_avg_balance.csv"), "wb") as f_in:
            for f_name, _ in avg_balance_files:
                with open(os.path.join(self.output_dir, f_name), "rb") as f_out:
                    f_in.write(f_out.read())

    # Running in parallel can speed things up, but using the specified seed results in exactly the same output
    # So here you can't set the random seed but use the default
    def launch_in_pool(self, n: int, pool: Pool, complete_callback: Optional[callable] = None):
        task_counter = 0

        def combine_outputs(_):
            nonlocal task_counter
            task_counter += 1
            if task_counter == n:
                self._combine_avg_balance()
            if complete_callback is not None:
                complete_callback()

        if n <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir(self.output_dir)
        for i in range(n):
            pool.apply_async(self._launch_in_parallel, args=(i, market_params,), callback=combine_outputs, error_callback=_raise_error)


# Create a process for each task and run it in parallel
# Note: Running multiple processes does not produce any output on the console
def launch_market_tasks(tasks: List[BSEMarketTask], n: int = 1, seed: Optional[int] = None, workers: Optional[int] = None):
    if len(tasks) == 1:
        tasks[0].launch(n, seed)
    else:
        p = None
        workers = int(math.ceil(cpu_count() / 2)) if workers is None else workers
        try:
            with tqdm(total=len(tasks)) as pbar:
                p = Pool(processes=workers)
                for task in tasks:
                    p.apply_async(task.launch, args=(n, seed,), callback=lambda _: pbar.update(), error_callback=_raise_error)
                p.close()
                p.join()
        finally:
            if p is not None:
                p.terminate()


# Create a process for each session in each task and run it in parallel
# Since the random number seed cannot be customized, the result cannot be completely reproduced
# Faster than 'launch_market_tasks' only when the amount of tasks is small but the amount of sessions is large
# Note: Running multiple processes does not produce any output on the console
def launch_market_tasks_in_parallel(tasks: List[BSEMarketTask], n: int, workers: Optional[int] = None):
    p = None
    workers = int(math.ceil(cpu_count() / 2)) if workers is None else workers
    try:
        with tqdm(total=len(tasks) * n) as pbar:
            p = Pool(processes=workers)
            for task in tasks:
                task.launch_in_pool(n, p, lambda: pbar.update())
            p.close()
            p.join()
    finally:
        if p is not None:
            p.terminate()
