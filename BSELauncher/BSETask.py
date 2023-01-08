import os
import json
import random
from typing import Optional, TextIO, List
from multiprocessing import Pool

from .BSEConfig import MarketSessionSpec
from .BSEInterface import _call_market_session_func
from .utils.process import raise_process_error
from .utils import combine_session_avg_balance_csv_files

BSE_MARKET_TASK_CONFIG_VERSION = 1


class BSEMarketTask:

    def __init__(
            self,
            task_id: str,
            spec: MarketSessionSpec,
            output_dir: Optional[str] = None
    ):
        self.task_id: str = task_id
        self.spec: MarketSessionSpec = spec
        self.output_dir: Optional[str] = output_dir

    def _prepare_output_dir(self):
        if self.output_dir is not None:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            elif not os.path.isdir(self.output_dir):
                raise FileExistsError(f"A file with the same name already exists! '{self.output_dir}'")

    def _launch(self, market_session_func: callable, session_id: str, spec_dict: dict, dump_f: TextIO):
        _call_market_session_func(
            market_session_func=market_session_func,
            session_id=session_id,
            spec_dict=spec_dict,
            avg_balance_file=dump_f,
            output_dir=self.output_dir
        )

    def _generate_session_ids(self, session_num: int) -> List[str]:
        session_index_len = len(str(session_num - 1))
        return [f"{self.task_id}_S{i:0{session_index_len}d}" for i in range(session_num)]

    def _generate_avg_balance_path(self, prefix: str) -> str:
        return os.path.join(self.output_dir, f"{prefix}_avg_balance.csv")

    # Use seeds to ensure reproducible results
    def launch(
            self,
            market_session_func: callable,
            session_num: int = 1,
            seed: Optional[int] = None,
            combine_avg_balances: bool = True
    ):
        if session_num <= 0:
            raise ValueError("n <= 0")
        market_params = self.spec.build()
        self._prepare_output_dir()
        if seed is not None:
            random.seed(seed)
        session_ids = self._generate_session_ids(session_num)
        if combine_avg_balances:
            csv_paths = [self._generate_avg_balance_path(self.task_id)]
        else:
            csv_paths = [self._generate_avg_balance_path(session_id) for session_id in session_ids]
        self._save_task_config(session_num, market_params, session_ids, csv_paths, seed)
        if combine_avg_balances:
            with open(csv_paths[0], mode="w", encoding="utf-8") as f:
                for session_id in session_ids:
                    self._launch(market_session_func, session_id, market_params, f)
        else:
            for session_id, csv_path in zip(session_ids, csv_paths):
                with open(csv_path, mode="w", encoding="utf-8") as f:
                    self._launch(market_session_func, session_id, market_params, f)

    def _launch_in_parallel(
            self,
            market_session_func: callable,
            session_id: str,
            spec_dict: dict,
            dump_file_path: str
    ):
        with open(dump_file_path, mode="w", encoding="utf-8") as f:
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
        self._prepare_output_dir()
        session_ids = self._generate_session_ids(session_num)
        csv_paths = [self._generate_avg_balance_path(session_id) for session_id in session_ids]
        self._save_task_config(session_num, market_params, session_ids, csv_paths)
        for session_id, csv_path in zip(session_ids, csv_paths):
            pool.apply_async(
                self._launch_in_parallel,
                args=(market_session_func, session_id, market_params, csv_path,),
                callback=_task_complete_handler,
                error_callback=raise_process_error
            )

    def _save_task_config(
            self,
            session_num: int,
            market_params: dict,
            session_ids: List[str],
            dump_avg_balance: List[str],
            seed: Optional[int] = None
    ):
        task_config = {
            "version": BSE_MARKET_TASK_CONFIG_VERSION,
            "task_id": self.task_id,
            "session_num": session_num,
            "session_ids": session_ids,
            "market_params": market_params,
            "seed": seed,
            "output_dir": self.output_dir,
            "dump_avg_balance": dump_avg_balance
        }
        config_path = os.path.join(self.output_dir, f"{self.task_id}.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(task_config, f, ensure_ascii=False)
