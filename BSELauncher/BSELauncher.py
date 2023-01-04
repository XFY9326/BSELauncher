import os
import sys
import math
import random
import traceback
from typing import Optional, TextIO
from multiprocessing import Pool, cpu_count

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("Dependency 'tqdm' is required! Please run 'python -m pip install tqdm' to install it!")
    sys.exit(1)

from .BSEConfig import MarketSessionSpec


# For internal usage only
def _raise_error(ex):
    if ex is not KeyboardInterrupt:
        traceback.print_exception(ex)
    else:
        raise ex


# For internal usage only
def _launch_market_session(
        market_session_func: callable,
        session_id: str,
        spec_dict: dict,
        avg_balance_file: TextIO,
        output_dir: Optional[str] = None
):
    market_session_func(
        sess_id=session_id,
        avg_bals=avg_balance_file,
        dump_dir=output_dir,
        **spec_dict
    )


# Simple spec wrapper
# Not recommended if there is no special need
def launch_market_session(
        market_session_func: callable,
        session_id: str,
        spec: MarketSessionSpec,
        avg_balance_file: TextIO,
        output_dir: Optional[str] = None
):
    _launch_market_session(
        market_session_func=market_session_func,
        session_id=session_id,
        spec_dict=spec.build(),
        avg_balance_file=avg_balance_file,
        output_dir=output_dir
    )


# Build faster with new_market_task
class BSEMarketTask:
    def __init__(
            self,
            session_id: str,
            spec: MarketSessionSpec,
            output_dir: Optional[str] = None
    ):
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

    def _launch(self, market_session_func: callable, index: int, spec_dict: dict, dump_f: TextIO):
        _launch_market_session(
            market_session_func=market_session_func,
            session_id=f"{self.session_id}_S{index}",
            spec_dict=spec_dict,
            avg_balance_file=dump_f,
            output_dir=self.output_dir
        )

    # Use seeds to ensure reproducible results
    def launch(self, market_session_func: callable, n: int = 1, seed: Optional[int] = None):
        if n <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir(self.output_dir)
        if seed is not None:
            random.seed(seed)
        dump_file_path = os.path.join(self.output_dir, f"{self.session_id}_avg_balance.csv")
        with open(dump_file_path, mode="w", encoding="utf-8") as f:
            for i in range(n):
                self._launch(market_session_func, i, market_params, f)

    def _launch_in_parallel(self, market_session_func: callable, index: int, spec_dict: dict):
        dump_file_dir = os.path.join(self.output_dir, f"{self.session_id}_S{index}_avg_balance.csv")
        with open(dump_file_dir, mode="w", encoding="utf-8") as f:
            self._launch(market_session_func, index, spec_dict, f)

    # Running in parallel can speed things up, but using the specified seed results in exactly the same output
    # So here you can't set the random seed but use the default
    def launch_in_pool(self, market_session_func: callable, n: int, pool: Pool, complete_callback: Optional[callable] = None):
        if n <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir(self.output_dir)
        for i in range(n):
            pool.apply_async(
                self._launch_in_parallel,
                args=(market_session_func, i, market_params,),
                callback=lambda _: complete_callback(),
                error_callback=_raise_error
            )


def combine_avg_balance_csv_files(output_dir: str, session_id: str):
    f_start = f"{session_id}_S"
    f_end = "_avg_balance.csv"
    avg_balance_files = [
        (f, int(f[len(f_start):-len(f_end)]))
        for f in os.listdir(output_dir)
        if f.startswith(f_start) and f.endswith(f_end)
    ]
    avg_balance_files = sorted(avg_balance_files, key=lambda x: x[1])
    dump_file_path = os.path.join(output_dir, f"{session_id}_avg_balance.csv")
    with open(dump_file_path, mode="wb") as f_in:
        for f_name, _ in avg_balance_files:
            with open(os.path.join(output_dir, f_name), mode="rb") as f_out:
                f_in.write(f_out.read())


# Create a process for each task and run it in parallel
# Note: Running multiple processes does not produce any output on the console
def launch_market_tasks(
        market_session_func: callable,
        *tasks: BSEMarketTask,
        n: int = 1,
        seed: Optional[int] = None,
        workers: Optional[int] = None
):
    if n < 1:
        raise ValueError
    tasks_size = len(tasks)
    if tasks_size == 1:
        tasks[0].launch(n, seed)
    else:
        p = None
        workers = min(tasks_size, int(math.ceil(cpu_count() / 2)) if workers is None else workers)
        try:
            with tqdm(total=len(tasks)) as pbar:
                p = Pool(processes=workers)
                for task in tasks:
                    p.apply_async(
                        task.launch,
                        args=(market_session_func, n, seed,),
                        callback=lambda _: pbar.update(),
                        error_callback=_raise_error
                    )
                p.close()
                p.join()
        except KeyboardInterrupt:
            pass
        finally:
            if p is not None:
                p.terminate()


# Create a process for each session in each task and run it in parallel
# Since the random number seed cannot be customized, the result cannot be completely reproduced
# Faster than 'launch_market_tasks' only when the amount of tasks is small but the amount of sessions is large
# Note: Running multiple processes does not produce any output on the console
def launch_market_tasks_in_parallel(
        market_session_func: callable,
        *tasks: BSEMarketTask,
        n: int = 1,
        combine_avg_balances: bool = True,
        workers: Optional[int] = None
):
    if n < 1:
        raise ValueError
    if n == 1:
        launch_market_tasks(market_session_func=market_session_func, *tasks, n=n, workers=workers)
    else:
        tasks_size = len(tasks) * n
        p = None
        workers = min(tasks_size, int(math.ceil(cpu_count() / 2)) if workers is None else workers)
        try:
            with tqdm(total=tasks_size) as pbar:
                p = Pool(processes=workers)
                for task in tasks:
                    task.launch_in_pool(market_session_func, n, p, pbar.update)
                p.close()
                p.join()
                if combine_avg_balances:
                    for task in tasks:
                        combine_avg_balance_csv_files(task.output_dir, task.session_id)
        except KeyboardInterrupt:
            pass
        finally:
            if p is not None:
                p.terminate()
