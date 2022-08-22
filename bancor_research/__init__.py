# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Spec, simulation, & emulation modules for Bancor v3."""

import warnings, decimal, pandas
from pydantic.fields import TypeVar

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    warnings.simplefilter("ignore", DeprecationWarning)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

decimal.getcontext().prec = len(str(2 ** 512 - 1))
decimal.getcontext().rounding = decimal.ROUND_DOWN

Decimal = decimal.Decimal

DataFrame = pandas.DataFrame

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")

class DEFAULT:
    TIMESTAMP = 0

    DECIMALS = 18

    TRADING_FEE    = "1%"
    NETWORK_FEE    = "20%"
    WITHDRAWAL_FEE = "0.25%"

    BNT_FUNDING_LIMIT = "1000000"
    BNT_MIN_LIQUIDITY = "10000"
    EP_VAULT_BALANCE  = "0"

    COOLDOWN_TIME  = 7 * 24 * 60 * 60
    NUM_TIMESTAMPS = 30 * 24 * 60 * 60

    PRICE_FEEDS_PATH = "https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.parquet"

    PRICE_FEEDS = DataFrame({
        "INDX": (    0.00 for _ in range(NUM_TIMESTAMPS)),
        "vbnt": (    1.00 for _ in range(NUM_TIMESTAMPS)),
        "tkn" : (    2.50 for _ in range(NUM_TIMESTAMPS)),
        "bnt" : (    2.50 for _ in range(NUM_TIMESTAMPS)),
        "link": (   15.00 for _ in range(NUM_TIMESTAMPS)),
        "eth" : ( 2500.00 for _ in range(NUM_TIMESTAMPS)),
        "wbtc": (40000.00 for _ in range(NUM_TIMESTAMPS)),
    })

    USERS = [
        "Alice",
        "Bob",
        "Charlie",
        "Trader",
    ]

    TOKENS = [
        "eth",
        "link",
        "tkn",
        "wbtc",
    ]

DEFAULT.WHITELIST = {
    TOKEN : {
        "decimals": DEFAULT.DECIMALS,
        "trading_fee": DEFAULT.TRADING_FEE,
        "bnt_funding_limit": DEFAULT.BNT_FUNDING_LIMIT,
        "ep_vault_balance": DEFAULT.EP_VAULT_BALANCE,
    }
    for TOKEN in DEFAULT.TOKENS
}

def read_price_feeds(price_feeds_path: str):
    price_feeds = pandas.read_parquet(price_feeds_path)
    price_feeds.columns = [col.lower() for col in price_feeds.columns]
    return price_feeds

__version__ = "2.0.3"
