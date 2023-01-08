import os
import time
import shutil

from BSELauncher import *
from BSE import market_session

TASK_ID = "Test"
OUTPUT_DIR = "outputs"
SESSIONS_AMOUNT = 30
START_TIME = 0
END_TIME = 60 * 30
TASKS_SIZE = 5

if __name__ == '__main__':
    trader_spec = [
        TraderSpec(Trader.ZIP, 10),
        TraderSpec(Trader.ZIC, 10),
        TraderSpec(Trader.SHVR, 10),
        TraderSpec(Trader.PRDE, 10, {'k': 4, 's_min': -1.0, 's_max': +1.0})
    ]
    order_spec = [
        OrderStrategy(
            time=(START_TIME, END_TIME),
            ranges=[PriceStrategy(180, 200)],
            step_mode=StepMode.RANDOM
        )
    ]
    market_spec = MarketSessionSpec(
        session_time=(START_TIME, END_TIME),
        sellers=trader_spec,
        buyers=trader_spec,
        orders_spec=OrderSpec(
            supply=order_spec,
            demand=order_spec,
            interval=5,
            time_mode=TimeMode.DRIP_POISSON
        )
    )

    tasks = [
        BSEMarketTask(f"{TASK_ID}_{i}", market_spec, OUTPUT_DIR)
        for i in range(0, TASKS_SIZE)
    ]

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    start = time.perf_counter()
    launch_tasks_sessions_in_parallel(
        market_session,
        *tasks,
        session_num=SESSIONS_AMOUNT,
        combine_avg_balances=True
    )
    print(f"launch_market_tasks_in_parallel: {time.perf_counter() - start}s")
