from enum import Enum
from typing import List, Tuple, Dict, Union, Callable, Optional


class Trader(str, Enum):
    # Give away
    GVWY = "GVWY"
    # Zero Intelligence - Constraint
    ZIC = "ZIC"
    # Shaver
    SHVR = "SHVR"
    # Sniper
    SNPR = "SNPR"
    # Zero Intelligence - Plus
    ZIP = "ZIP"
    # Parameterised-Response Zero Intelligence
    PRZI = "PRZI"
    # PRZI-Stochastic-Hillclimber
    PRSH = "PRSH"
    # Parameterized-Response zero-intelligence with Differential Evolution
    PRDE = "PRDE"


class StepMode(str, Enum):
    FIXED = "fixed"
    JITTERED = "jittered"
    RANDOM = "random"


class TimeMode(str, Enum):
    PERIODIC = "periodic"
    DRIP_FIXED = "drip-fixed"
    DRIP_JITTER = "drip-jitter"
    DRIP_POISSON = "drip-poisson"


class TraderSpec:
    def __init__(
            self,
            trader: Union[Trader, str],
            amount: int,
            args: Optional[dict] = None
    ):
        self.trader: Union[Trader, str] = trader
        self.amount: int = amount
        self.args: Optional[dict] = args

    def build(self) -> tuple:
        assert self.amount >= 0, f"Trader amount error! Value: {self.amount}"
        if isinstance(self.trader, Trader):
            trader = self.trader.value
        else:
            trader = str(self.trader)
        if self.args is None or len(self.args) == 0:
            return trader, self.amount
        else:
            return trader, self.amount, self.args

    def __repr__(self) -> str:
        return str(self.build())


class PriceStrategy:
    def __init__(self, start: int, end: int):
        self.start: int = start
        self.end: int = end
        self._offset_functions: List[Callable[[int], int]] = []

    def set_offset_function(self, offset: Callable[[int], int]):
        self._offset_functions = [offset]

    def set_min_max_offset_functions(self, min_offset: Callable[[int], int], max_offset: Callable[[int], int]):
        self._offset_functions = [min_offset, max_offset]

    def build(self) -> tuple:
        assert self.end >= self.start >= 0, f"OrderStrategy range error! Value: [{self.start} {self.end}]"
        if len(self._offset_functions) == 0:
            return self.start, self.end
        elif len(self._offset_functions) == 1:
            return self.start, self.end, self._offset_functions[0]
        elif len(self._offset_functions) == 2:
            return self.start, self.end, self._offset_functions[0], self._offset_functions[1]
        else:
            raise ValueError("There can only be at most two offset functions!")

    def __repr__(self) -> str:
        return str(self.build())


class OrderStrategy:
    def __init__(
            self,
            time: Tuple[int, int],
            ranges: List[PriceStrategy],
            step_mode: Union[StepMode, str]
    ):
        self.time: Tuple[int, int] = time
        self.ranges: List[PriceStrategy] = ranges
        self.mode: Union[StepMode, str] = step_mode

    def build(self) -> Dict[str, Union[int, List[Tuple[int, int]], str]]:
        assert self.time[1] >= self.time[0] >= 0, f"OrderStrategy time error! Value: {self.time}"
        assert len(self.ranges) > 0, "OrderStrategy ranges empty!"
        if isinstance(self.mode, StepMode):
            mode = self.mode.value
        else:
            mode = str(self.mode)
        return {
            "from": self.time[0],
            "to": self.time[1],
            "ranges": [i.build() for i in self.ranges],
            "stepmode": mode
        }

    def __repr__(self) -> str:
        return str(self.build())


class OrderSpec:
    def __init__(
            self,
            supply: List[OrderStrategy],
            demand: List[OrderStrategy],
            interval: int,
            time_mode: Union[TimeMode, str]
    ):
        self.interval: int = interval
        self.mode: Union[TimeMode, str] = time_mode
        self.supply: List[OrderStrategy] = supply
        self.demand: List[OrderStrategy] = demand

    def set_supply_and_demand(self, strategy: List[OrderStrategy]):
        self.supply = strategy
        self.demand = strategy

    def build(self) -> Dict[str, Union[List[OrderStrategy], int, str]]:
        assert self.interval >= 0, f"OrderSpec interval error! Value: {self.interval}"
        if isinstance(self.mode, TimeMode):
            mode = self.mode.value
        else:
            mode = str(self.mode)
        return {
            "sup": [i.build() for i in self.supply],
            "dem": [i.build() for i in self.demand],
            "interval": self.interval,
            "timemode": mode
        }

    def __repr__(self) -> str:
        return str(self.build())


class MarketSessionSpec:
    def __init__(
            self,
            session_time: Tuple[int, int],
            sellers: List[TraderSpec],
            buyers: List[TraderSpec],
            orders_spec: OrderSpec,
            dump_all: bool = True,
            verbose: bool = False
    ):
        # start_time, end_time
        self.session_time: Tuple[int, int] = session_time
        # traders_spec
        self.sellers: List[TraderSpec] = sellers
        self.buyers: List[TraderSpec] = buyers
        # orders_spec
        self.orders_spec: OrderSpec = orders_spec
        # dump
        self.dump_all: bool = dump_all
        self.verbose: bool = verbose

    def set_sellers_and_buyers(self, traders: List[TraderSpec]):
        self.sellers = traders
        self.buyers = traders

    def _build_traders_spec(self) -> Dict[str, List[Tuple[str, int]]]:
        return {
            "sellers": [i.build() for i in self.sellers],
            "buyers": [i.build() for i in self.buyers]
        }

    def build(self) -> Dict[str, Union[int, dict, bool]]:
        assert self.session_time[1] >= self.session_time[0] >= 0, f"Market session time error! Value: {self.session_time}"
        return {
            "starttime": self.session_time[0],
            "endtime": self.session_time[1],
            "trader_spec": self._build_traders_spec(),
            "order_schedule": self.orders_spec.build(),
            "dump_all": self.dump_all,
            "verbose": self.verbose
        }

    def __repr__(self) -> str:
        return str(self.build())
