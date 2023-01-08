from BSELauncher.utils import show_seconds_progress

TASK_ID = "Test"
OUTPUT_DIR = "outputs"
SESSIONS_AMOUNT = 30
START_TIME = 0
END_TIME = 60 * 30
TASKS_SIZE = 5

if __name__ == '__main__':
    show_seconds_progress(
        output_dir=OUTPUT_DIR,
        task_id=[f"{TASK_ID}_{i}" for i in range(0, TASKS_SIZE)],
        total_seconds=END_TIME * SESSIONS_AMOUNT * TASKS_SIZE
    )
