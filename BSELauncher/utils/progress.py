import os
import sys
import time
import itertools as it
from typing import Optional, Dict, Union, Iterable

from .files import tail_file, get_session_avg_balance_csv_files

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("Dependency 'tqdm' is required! Please run 'python -m pip install tqdm' to install it!")
    sys.exit(1)


def _get_csv_progress(csv_path: str) -> Optional[int]:
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


def _get_all_csv_progress(
        output_dir: str,
        task_id: Union[str, Iterable[str]],
        last_status: Optional[Dict[str, int]] = None
) -> Dict[str, int]:
    result = {}
    if os.path.exists(output_dir):
        if isinstance(task_id, str):
            task_id = [task_id]
        f_name_list = [
            get_session_avg_balance_csv_files(output_dir, i)
            for i in task_id
        ]
        for f_name, _ in it.chain.from_iterable(f_name_list):
            progress = _get_csv_progress(os.path.join(output_dir, f_name))
            if progress is None:
                if last_status is not None and f_name in last_status:
                    result[f_name] = last_status[f_name]
                else:
                    result[f_name] = 0
            else:
                result[f_name] = progress
    return result


def show_seconds_progress(
        output_dir: str,
        task_id: Union[str, Iterable[str]],
        total_seconds: int,
        refresh_seconds: float = 1.0
):
    last_progress = _get_all_csv_progress(output_dir, task_id)
    last_num = sum(last_progress.values())

    with tqdm(initial=last_num, total=total_seconds) as pbar:
        try:
            while last_num < total_seconds:
                time.sleep(refresh_seconds)

                current_progress = _get_all_csv_progress(output_dir, task_id, last_progress)
                current_num = sum(current_progress.values())

                pbar.update(current_num - last_num)

                last_progress = current_progress
                last_num = current_num
        except KeyboardInterrupt:
            pass
