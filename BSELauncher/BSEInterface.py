import inspect
from typing import Optional, TextIO
from .BSEConfig import MarketSessionSpec


def _check_market_session_func(market_session_func: callable):
    spec = inspect.getfullargspec(market_session_func)
    if "dump_dir" not in spec.args:
        raise TypeError("The 'market_session' function expects a parameter named 'dump_dir'!")


def _call_market_session_func(
        market_session_func: callable,
        session_id: str,
        spec_dict: dict,
        avg_balance_file: TextIO,
        output_dir: Optional[str] = None
):
    _check_market_session_func(market_session_func)
    market_session_func(
        sess_id=session_id,
        avg_bals=avg_balance_file,
        dump_dir=output_dir,
        **spec_dict
    )


# Simple spec wrapper
# Not recommended if there is no special need
def launch_market_session(
        market_session_func: callable,
        session_id: str,
        spec: MarketSessionSpec,
        avg_balance_file: TextIO,
        output_dir: Optional[str] = None
):
    _call_market_session_func(
        market_session_func=market_session_func,
        session_id=session_id,
        spec_dict=spec.build(),
        avg_balance_file=avg_balance_file,
        output_dir=output_dir
    )
