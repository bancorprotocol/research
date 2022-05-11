from decimal import Decimal, getcontext
from attr import dataclass
from .constants import (
    QDECIMALS,
    MAX_INT,
    PRECISION,
    MODEL,
    VERSION,
    WHITELISTED_TOKENS,
    PRICE_FEEDS_PATH,
    DECIMALS,
    ACTIVE_USERS
)

getcontext().prec = PRECISION


@dataclass
class GlobalSettings:
    timestep = 0
    model = MODEL
    version = VERSION
    eightee_places = QDECIMALS
    max_int = MAX_INT
    precision = PRECISION
    decimals = DECIMALS
    whitelisted_tokens = list = WHITELISTED_TOKENS
    active_users: list = ACTIVE_USERS
    price_feeds_path: str = PRICE_FEEDS_PATH
    cooldown_time: int = 604800
    lower_ema_limit: Decimal = Decimal("0.99").quantize(QDECIMALS)
    upper_ema_limit: Decimal = Decimal("1.01").quantize(QDECIMALS)
    network_fee: Decimal = Decimal("0.2").quantize(QDECIMALS)
    withdrawal_fee: Decimal = Decimal("1.0025").quantize(QDECIMALS)
    bnt_min_liquidity: Decimal = Decimal("100000").quantize(QDECIMALS)
    trading_fee: Decimal = Decimal("1.005").quantize(QDECIMALS)
    bnt_funding_limit: Decimal = Decimal("1000000").quantize(QDECIMALS)
    alpha: Decimal = Decimal("0.2").quantize(QDECIMALS)
