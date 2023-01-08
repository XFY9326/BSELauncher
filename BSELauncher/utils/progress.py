import os
import sys
import time
import json
from typing import Optional, Dict, Union, Iterable

from .files import _generate_task_config_files, tail_file, _all_file_exists

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("Dependency 'tqdm' is required! Please run 'python -m pip install tqdm' to install it!")
    sys.exit(1)


def _get_avg_balance_progress(csv_path: str) -> Optional[int]:
    if os.path.exists(csv_path):
        # noinspection PyBroadException
        try:
            last_line = tail_file(csv_path, 1)
            if "," in last_line:
                cols = last_line.split(",")
                if len(cols) >= 1:
                    return int(cols[1])
        except:  # pylint: disable=bare-except
            pass
        return None
    return 0


def _get_all_avg_balance_progress(
        avg_balance_csv_files: Iterable[str],
        last_status: Optional[Dict[str, int]] = None
) -> Dict[str, int]:
    result = {}
    path_list = [p for p in avg_balance_csv_files if os.path.isfile(p)]
    for f_path in path_list:
        progress = _get_avg_balance_progress(f_path)
        if progress is None:
            if last_status is not None and f_path in last_status:
                result[f_path] = last_status[f_path]
            else:
                result[f_path] = 0
        else:
            result[f_path] = progress
    return result


def show_seconds_progress_by_avg_balance(
        avg_balance_csv_files: Union[str, Iterable[str]],
        total_seconds: int,
        refresh_seconds: float = 1.0
):
    if isinstance(avg_balance_csv_files, str):
        avg_balance_csv_files = [avg_balance_csv_files]
    last_progress = _get_all_avg_balance_progress(avg_balance_csv_files)
    last_num = sum(last_progress.values())

    with tqdm(initial=last_num, total=total_seconds) as pbar:
        try:
            while last_num < total_seconds:
                time.sleep(refresh_seconds)

                current_progress = _get_all_avg_balance_progress(avg_balance_csv_files, last_progress)
                current_num = sum(current_progress.values())

                pbar.update(current_num - last_num)

                last_progress = current_progress
                last_num = current_num
        except KeyboardInterrupt:
            pass


def show_seconds_progress_by_config(
        task_config: Union[str, Iterable[str]],
        wait_all_configs: bool = False,
        refresh_seconds: float = 1.0
):
    if isinstance(task_config, str):
        task_config = [task_config]
    if wait_all_configs and not _all_file_exists(task_config):
        print("Waiting for task configs ...")
        while not _all_file_exists(task_config):
            time.sleep(refresh_seconds)

    avg_balance_csv_files = []
    session_nums = 0
    end_times = 0
    task_nums = 0
    for config_path in task_config:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        session_nums += config["session_num"]
        end_times += config["market_params"]["endtime"]
        avg_balance_csv_files += config["dump_avg_balance"]
        task_nums += 1
    show_seconds_progress_by_avg_balance(
        avg_balance_csv_files,
        session_nums * end_times * task_nums,
        refresh_seconds
    )


def show_seconds_progress(
        output_dir: str,
        task_id: Union[str, Iterable[str]],
        wait_all_configs: bool = False,
        refresh_seconds: float = 1.0
):
    if wait_all_configs and not os.path.isdir(output_dir):
        print("Waiting for output dir ...")
        while not os.path.isdir(output_dir):
            time.sleep(refresh_seconds)
    task_configs = _generate_task_config_files(output_dir, task_id)
    show_seconds_progress_by_config(
        task_config=task_configs,
        wait_all_configs=wait_all_configs,
        refresh_seconds=refresh_seconds
    )
