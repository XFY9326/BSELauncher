import os
import io
from typing import Union, Optional, Tuple, List, Iterable


def _all_file_exists(files_path: Iterable[str]) -> bool:
    for file_path in files_path:
        if not os.path.isfile(file_path):
            return False
    return True


def get_task_config_files(output_dir: str, task_id: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(task_id, str):
        task_id = [task_id]
    result = []
    for i in task_id:
        f_path = os.path.join(output_dir, f"{i}.json")
        if os.path.isfile(f_path):
            result.append(f_path)
    return result


def _generate_task_config_files(output_dir: str, task_id: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(task_id, str):
        task_id = [task_id]
    return [os.path.join(output_dir, f"{i}.json") for i in task_id]


def _get_session_csv_files(output_dir: str, task_id: str, file_end: str) -> List[Tuple[str, int]]:
    f_start = f"{task_id}_S"
    return [
        (f, int(f[len(f_start):-len(file_end)]))
        for f in os.listdir(output_dir)
        if f.startswith(f_start) and f.endswith(file_end)
    ]


def get_session_avg_balance_csv_files(output_dir: str, task_id: str) -> List[Tuple[str, int]]:
    return _get_session_csv_files(output_dir, task_id, "_avg_balance.csv")


def get_session_lob_frames_csv_files(output_dir: str, task_id: str) -> List[Tuple[str, int]]:
    return _get_session_csv_files(output_dir, task_id, "_LOB_frames.csv")


def get_session_strategies_csv_files(output_dir: str, task_id: str) -> List[Tuple[str, int]]:
    return _get_session_csv_files(output_dir, task_id, "_strats.csv")


def combine_session_avg_balance_csv_files(output_dir: str, task_id: str) -> str:
    avg_balance_files = get_session_avg_balance_csv_files(output_dir, task_id)
    avg_balance_files = sorted(avg_balance_files, key=lambda x: x[1])
    dump_file_path = os.path.join(output_dir, f"{task_id}_avg_balance.csv")
    with open(dump_file_path, mode="wb") as f_in:
        for f_name, _ in avg_balance_files:
            with open(os.path.join(output_dir, f_name), mode="rb") as f_out:
                f_in.write(f_out.read())
    return dump_file_path


def tail_file(file_path: str, n: int, encoding: Optional[str] = None) -> str:
    f_size = os.path.getsize(file_path)
    if f_size == 0:
        return ""
    f_cursor = f_size - 1
    line = 0
    with io.BytesIO() as buffer:
        with open(file_path, "rb") as f:
            while f_cursor >= 0 and line <= n:
                f.seek(f_cursor)
                b = f.read(1)
                f_cursor -= 1

                if b == b'\n':
                    line += 1
                if line <= n:
                    buffer.write(b)
        buffer_bytes = buffer.getvalue()[::-1]
        if encoding is None:
            return buffer_bytes.decode()
        else:
            return buffer_bytes.decode(encoding=encoding)
