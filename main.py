import os
import time
import shutil

from BSELauncher import *
from BSE import market_session

OUTPUT_DIR = "outputs_test"
TASKS_AMOUNT = 5
SESSIONS_AMOUNT = 50

if __name__ == '__main__':
    start_time = 0
    end_time = 60 * 10
    market_spec = MarketSessionSpec(
        session_time=(start_time, end_time),
        sellers=[TraderSpec(Trader.ZIP, 10), TraderSpec(Trader.ZIC, 10), TraderSpec(Trader.SHVR, 10)],
        buyers=[TraderSpec(Trader.ZIP, 10), TraderSpec(Trader.ZIC, 10), TraderSpec(Trader.SHVR, 10)],
        orders_spec=OrderSpec(
            supply=[
                OrderStrategy(
                    time=(start_time, end_time),
                    ranges=[PriceStrategy(80, 320)],
                    step_mode=StepMode.FIXED
                )
            ],
            demand=[
                OrderStrategy(
                    time=(start_time, end_time),
                    ranges=[PriceStrategy(80, 320)],
                    step_mode=StepMode.FIXED
                )
            ],
            interval=30,
            time_mode=TimeMode.PERIODIC
        )
    )

    # Before Cython
    # i7-8750H + 16GB
    # 100%|██████████| 5/5 [01:58<00:00, 23.76s/it]
    # launch_market_tasks: 118.82856316200001s
    # 100%|██████████| 250/250 [01:51<00:00,  2.25it/s]
    # launch_market_tasks_in_parallel: 111.276186845s

    # After Cython
    # i7-8750H + 16GB
    # 100%|██████████| 5/5 [01:02<00:00, 12.44s/it]
    # launch_market_tasks: 62.283330947s
    # 100%|██████████| 250/250 [00:52<00:00,  4.78it/s]
    # launch_market_tasks_in_parallel: 52.34778339s

    tasks = [
        BSEMarketTask(f"Test_{i}", market_spec, f"{OUTPUT_DIR}/{i}")
        for i in range(TASKS_AMOUNT)
    ]

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    start = time.perf_counter()
    launch_market_tasks(market_session, *tasks, n=SESSIONS_AMOUNT)
    print(f"launch_market_tasks: {time.perf_counter() - start}s")

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    start = time.perf_counter()
    launch_market_tasks_in_parallel(market_session, *tasks, n=SESSIONS_AMOUNT)
    print(f"launch_market_tasks_in_parallel: {time.perf_counter() - start}s")
