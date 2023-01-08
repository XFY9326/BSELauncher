import sys
from typing import Optional
from multiprocessing import Pool

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("Dependency 'tqdm' is required! Please run 'python -m pip install tqdm' to install it!")
    sys.exit(1)

from .BSEMarketTask import BSEMarketTask
from .utils.process import raise_process_error, get_default_worker_size


# Create a process for each task and run it in parallel
# Note: Running multiple processes does not produce any output on the console
def launch_tasks_in_parallel(
        market_session_func: callable,
        *tasks: BSEMarketTask,
        session_num: int = 1,
        seed: Optional[int] = None,
        workers: Optional[int] = None
):
    if session_num < 1:
        raise ValueError
    tasks_size = len(tasks)
    if tasks_size == 1:
        tasks[0].launch(session_num, seed)
    else:
        workers = get_default_worker_size(tasks_size, workers)
        with tqdm(total=len(tasks)) as pbar:
            with Pool(processes=workers) as p:
                for task in tasks:
                    p.apply_async(
                        task.launch,
                        args=(market_session_func, session_num, seed,),
                        callback=lambda _: pbar.update(),
                        error_callback=raise_process_error
                    )
                p.close()
                p.join()


# Create a process for each session in each task and run it in parallel
# Since the random number seed cannot be customized, the result cannot be completely reproduced
# Faster than 'launch_market_tasks_in_parallel' only when the amount of tasks is small but the amount of sessions is large
# Note: Running multiple processes does not produce any output on the console
def launch_tasks_sessions_in_parallel(
        market_session_func: callable,
        *tasks: BSEMarketTask,
        session_num: int = 1,
        combine_avg_balances: bool = True,
        workers: Optional[int] = None
):
    if session_num < 1:
        raise ValueError
    if session_num == 1:
        launch_tasks_in_parallel(
            market_session_func=market_session_func,
            *tasks,
            session_num=session_num,
            workers=workers
        )
    else:
        tasks_size = len(tasks) * session_num
        workers = get_default_worker_size(tasks_size, workers)
        with tqdm(total=tasks_size) as pbar:
            with Pool(processes=workers) as p:
                for task in tasks:
                    task.launch_in_pool(market_session_func, session_num, p, combine_avg_balances, pbar.update)
                p.close()
                p.join()
