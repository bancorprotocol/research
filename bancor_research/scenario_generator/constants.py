# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Simulation constants and default state variables."""
from decimal import Decimal
from bancor_research import DEFAULT
DEFAULT_TRADING_FEE = DEFAULT.TRADING_FEE
DEFAULT_BNT_FUNDING_LIMIT = DEFAULT.BNT_FUNDING_LIMIT
DEFAULT_NETWORK_FEE = DEFAULT.NETWORK_FEE
DEFAULT_WITHDRAWAL_FEE = DEFAULT.WITHDRAWAL_FEE
    
SIMULATION_TARGET_TVL: Decimal = Decimal("160000000")
SIMULATION_TARGET_TRADE_VOLUME: Decimal = Decimal("20000000")
SIMULATION_WHALE_THRESHOLD: Decimal = Decimal("1000000")
SIMULATION_TARGET_NUM_TRADES_PER_DAY: int = 200
SIMULATION_TARGET_NUM_DEPOSITS_PER_DAY: int = 200
SIMULATION_TARGET_NUM_WITHDRAWALS_PER_DAY: int = 200
SIMULATION_NUM_TRADERS = 2
SIMULATION_NUM_LPs = 2


SIMULATION_WHITELISTED_TOKENS = {
    "eth": {
        "trading_fee": DEFAULT_TRADING_FEE,
        "bnt_funding_limit": DEFAULT_BNT_FUNDING_LIMIT,
    },
    "link": {
        "trading_fee": DEFAULT_TRADING_FEE,
        "bnt_funding_limit": DEFAULT_BNT_FUNDING_LIMIT,
    },
    "tkn": {
        "trading_fee": DEFAULT_TRADING_FEE,
        "bnt_funding_limit": DEFAULT_BNT_FUNDING_LIMIT,
    },
    "wbtc": {
        "trading_fee": DEFAULT_TRADING_FEE,
        "bnt_funding_limit": DEFAULT_BNT_FUNDING_LIMIT,
    },
}
SIMULATION_MAX_STEPS = 100
SIMULATION_OUTPUT_PATH: str = "examples/studies/limit_max_on_curve_liquidity/data/simulation_output.csv"
