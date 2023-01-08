from BSELauncher.utils import show_seconds_progress

TASK_ID = "Test"
OUTPUT_DIR = "outputs"
TASKS_SIZE = 5
TASK_IDS = [f"{TASK_ID}_{i}" for i in range(0, TASKS_SIZE)]

if __name__ == '__main__':
    show_seconds_progress(
        output_dir=OUTPUT_DIR,
        task_id=TASK_IDS,
        wait_all_configs=True,
        refresh_seconds=1.0
    )
