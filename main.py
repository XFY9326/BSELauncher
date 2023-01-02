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
