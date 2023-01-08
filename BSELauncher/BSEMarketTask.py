import os
import random
from typing import Optional, TextIO
from multiprocessing import Pool

from .BSEConfig import MarketSessionSpec
from .BSEInterface import _call_market_session_func
from .utils.process import raise_process_error
from .utils import combine_session_avg_balance_csv_files


class BSEMarketTask:
    def __init__(
            self,
            task_id: str,
            spec: MarketSessionSpec,
            output_dir: Optional[str] = None,
            overwrite_output: bool = False
    ):
        self.task_id: str = task_id
        self.spec: MarketSessionSpec = spec
        self.output_dir: Optional[str] = output_dir
        self.overwrite_output: bool = overwrite_output

    def _prepare_output_dir(self, output_dir: Optional[str]):
        if output_dir is not None:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            elif not os.path.isdir(output_dir):
                raise FileExistsError(f"A file with the same name already exists but is not a folder! '{output_dir}'")
            elif not self.overwrite_output:
                raise FileExistsError(f"Output dir '{output_dir}' already exists!")

    def _launch(self, market_session_func: callable, session_id: str, spec_dict: dict, dump_f: TextIO):
        _call_market_session_func(
            market_session_func=market_session_func,
            session_id=session_id,
            spec_dict=spec_dict,
            avg_balance_file=dump_f,
            output_dir=self.output_dir
        )

    # Use seeds to ensure reproducible results
    def launch(self, market_session_func: callable, session_num: int = 1, seed: Optional[int] = None):
        if session_num <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir(self.output_dir)
        if seed is not None:
            random.seed(seed)
        dump_file_path = os.path.join(self.output_dir, f"{self.task_id}_avg_balance.csv")
        with open(dump_file_path, mode="w", encoding="utf-8") as f:
            session_index_len = len(str(session_num - 1))
            for i in range(session_num):
                session_id = f"{self.task_id}_S{i:0{session_index_len}d}"
                self._launch(market_session_func, session_id, market_params, f)

    def _launch_in_parallel(self, market_session_func: callable, session_id: str, spec_dict: dict):
        dump_file_dir = os.path.join(self.output_dir, f"{session_id}_avg_balance.csv")
        with open(dump_file_dir, mode="w", encoding="utf-8") as f:
            self._launch(market_session_func, session_id, spec_dict, f)

    # Running in parallel can speed things up, but using the specified seed results in exactly the same output
    # So here you can't set the random seed but use the default
    def launch_in_pool(
            self,
            market_session_func: callable,
            session_num: int,
            pool: Pool,
            combine_avg_balances: bool = True,
            task_complete_callback: Optional[callable] = None
    ):
        task_counter = 0

        def _task_complete_handler(_):
            nonlocal task_counter
            task_counter += 1
            if task_complete_callback is not None:
                task_complete_callback()
            if task_counter == session_num and combine_avg_balances:
                combine_session_avg_balance_csv_files(
                    output_dir=self.output_dir,
                    task_id=self.task_id
                )

        if session_num <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir(self.output_dir)
        session_index_len = len(str(session_num - 1))
        for i in range(session_num):
            session_id = f"{self.task_id}_S{i:0{session_index_len}d}"
            pool.apply_async(
                self._launch_in_parallel,
                args=(market_session_func, session_id, market_params,),
                callback=_task_complete_handler,
                error_callback=raise_process_error
            )