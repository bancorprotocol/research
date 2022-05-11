from decimal import *

MODEL = "Bancor V3"
VERSION = "1.0.0"
WHITELISTED_TOKENS: list = ["dai", "eth", "link", "bnt", "tkn", "wbtc"]
ACTIVE_USERS: list = ['Alice', 'Bob', 'Charlie', 'Trader']
DECIMALS: int = 18
QDECIMALS = Decimal(10) ** -DECIMALS
TIMESTEP: int = 0
MAX_INT: int = 2**112 - 1
PRECISION: int = 155
PRICE_FEEDS_PATH: str = (
    "https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.parquet"
)
