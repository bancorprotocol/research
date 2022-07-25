# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""System state variables, constants, containers and interface."""
import copy
import logging
import warnings
from dataclasses import field
from decimal import Decimal
from fractions import Fraction
import pandas as pd
import numpy as np
from pydantic.types import Tuple, Any, List, Dict
from pydantic.dataclasses import dataclass
from pydantic.fields import TypeVar
from pydantic.schema import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)
PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")

logger = logging.getLogger(__name__)


# Custom types
class Epoch(int):
    pass


# Non-Configurable Constants
MODEL = "Bancor Network"
VERSION = "1.0.0"
GENESIS_EPOCH = Epoch(0)
SECONDS_PER_DAY = 86400
MAX_UINT112 = 2**112 - 1
PRECISION = 155

# Configurable Genesis Variables
DEFAULT_TIMESTAMP = 0
DEFAULT_WHITELIST = ["dai", "eth", "link", "bnt", "tkn", "wbtc"]
DEFAULT_USERS = ["Alice", "Bob", "Charlie", "Trader"]
DEFAULT_DECIMALS = 18
DEFAULT_QDECIMALS = Decimal(10) ** -DEFAULT_DECIMALS
DEFAULT_PRICE_FEEDS_PATH = (
    "https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.parquet"
)
DEFAULT_EXP_DECAY_DISTRIBUTION = 1
DEFAULT_FLAT_DISTRIBUTION = 0
DEFAULT_WITHDRAWAL_FEE = Decimal("0.0025")
DEFAULT_TRADING_FEE = Decimal("0.01")
DEFAULT_NETWORK_FEE = Decimal("0.2")
DEFAULT_BNT_FUNDING_LIMIT = Decimal("1000000")
DEFAULT_BNT_MIN_LIQUIDITY = Decimal("10000")
DEFAULT_COOLDOWN_TIME = SECONDS_PER_DAY * 7
DEFAULT_ALPHA = Decimal("0.2").quantize(DEFAULT_QDECIMALS)
DEFAULT_LOWER_EMA_LIMIT = Decimal("0.99").quantize(DEFAULT_QDECIMALS)
DEFAULT_UPPER_EMA_LIMIT = Decimal("1.01").quantize(DEFAULT_QDECIMALS)
DEFAULT_NUM_TIMESTAMPS = SECONDS_PER_DAY * 30
DEFAULT_ACCOUNT_BALANCE = Decimal(np.nan)
DEFAULT_PRICE_FEEDS = pd.DataFrame(
    {
        "INDX": (0 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "vbnt": (1.0 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "tkn": (2.5 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "bnt": (2.5 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "link": (15.00 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "eth": (2500.00 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "wbtc": (40000.00 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
    }
)


# Misc dependencies for `State`
class Token(object):
    """
    Represents a token balance with common math operations to increase, decrease, and set the balance.
    """

    def __init__(
        self, balance: Decimal = Decimal("0"), qdecimals: Decimal = DEFAULT_QDECIMALS
    ):
        self.balance = balance
        self.qdecimals = qdecimals

    def add(self, value: Decimal):
        self.validate_balance()
        self.balance += self.validate(value)

    def subtract(self, value: Decimal):
        self.validate_balance()
        self.balance -= self.validate(value)

    def set(self, value: Decimal):
        self.validate_balance()
        self.balance = self.validate(value)

    def validate(self, value) -> Decimal:
        return self.validate_value(value)

    def validate_balance(self):
        if pd.isnull(self.balance):
            self.balance = Decimal("0")

    def validate_value(self, value) -> Decimal:
        if pd.isnull(value):
            value = Decimal("0")
        return Decimal(str(value)).quantize(self.qdecimals)


# Containers
class Config:
    validate_assignment = True
    arbitrary_types_allowed = True


@dataclass(config=Config)
class GlobalSettings:
    """
    Represents the default global settings. These can be overridden by the BancorDapp configuration upon instantiation.
    """

    timestamp: int = DEFAULT_TIMESTAMP
    model: str = MODEL
    version: str = VERSION
    eightee_places: int = DEFAULT_QDECIMALS
    max_uint112: int = MAX_UINT112
    precision: int = PRECISION
    decimals: int = DEFAULT_DECIMALS
    whitelisted_tokens: List[str] = field(default_factory=lambda: DEFAULT_WHITELIST)
    active_users: List[str] = field(default_factory=lambda: DEFAULT_USERS)
    price_feeds_path: str = DEFAULT_PRICE_FEEDS_PATH
    cooldown_time: int = DEFAULT_COOLDOWN_TIME
    network_fee: Decimal = DEFAULT_NETWORK_FEE
    withdrawal_fee: Decimal = DEFAULT_WITHDRAWAL_FEE
    bnt_min_liquidity: Decimal = DEFAULT_BNT_MIN_LIQUIDITY
    trading_fee: Decimal = DEFAULT_TRADING_FEE
    bnt_funding_limit: Decimal = DEFAULT_BNT_FUNDING_LIMIT
    alpha: Decimal = DEFAULT_ALPHA


@dataclass(config=Config)
class Cooldown:
    """
    Represents a pending withdrawal cooldown.
    """

    id: int
    created_at: int
    user_name: str
    tkn_name: str
    is_complete: bool
    tkn: Any = field(default_factory=Token)
    pooltoken: Any = field(default_factory=Token)


@dataclass(config=Config)
class StandardProgram:
    """
    Represents an standard reward program state.
    """

    id: int
    tkn_name: str
    rewards_token: str
    is_enabled: bool
    is_active: bool
    start_time: int
    end_time: int
    last_update_time: int
    reward_rate: Decimal
    remaining_rewards: Any = field(default_factory=Token)
    reward_per_token: Any = field(default_factory=Token)
    total_unclaimed_rewards: Any = field(default_factory=Token)
    staked_reward_amt: Any = field(default_factory=Token)
    pooltoken_amt: Any = field(default_factory=Token)
    providers: list = field(default_factory=list)


@dataclass(config=Config)
class AutocompoundingProgram:
    """
    Represents an autocompounding reward program state.
    """

    id: int
    tkn_name: str
    owner_id: str
    half_life_days: int
    start_time: int
    created_at: int
    _half_life_seconds: int = 0
    total_rewards: Any = field(default_factory=Token)
    remaining_rewards: Any = field(default_factory=Token)
    prev_token_amt_distributed: Any = field(default_factory=Token)
    total_duration_in_seconds: Decimal = Decimal("0")
    distribution_type: str = "exp"
    is_active: bool = False
    is_enabled: bool = False

    @property
    def flat_distribution_rate_per_second(self):
        """
        Returns the rate per second of the distribution.
        """
        return (
            self.total_rewards.balance.quantize(DEFAULT_QDECIMALS)
            / self.total_duration_in_seconds
        )

    @property
    def half_life_seconds(self):
        """
        Returns the half-life of the distribution in seonds.
        """
        return (
            self.half_life_days * SECONDS_PER_DAY
            if self._half_life_seconds == 0
            else self._half_life_seconds
        )

    @half_life_seconds.setter
    def half_life_seconds(self, value):
        """
        Sets the half-life of the distribution in seonds.
        """
        self._half_life_seconds = value


@dataclass(config=Config)
class UserStandardProgram:
    """
    Represents a standard reward program user state
    """

    id: int
    staked_amt: Any = field(default_factory=Token)
    pending_rewards: Any = field(default_factory=Token)
    reward_per_token_paid: Any = field(default_factory=Token)


@dataclass(config=Config)
class User:
    """
    Represents a user agent state.
    """

    user_name: str
    pending_withdrawals: Dict[int, Cooldown] = field(
        default_factory=lambda: defaultdict(Cooldown)
    )
    pending_standard_rewards: Dict[int, UserStandardProgram] = field(
        default_factory=lambda: defaultdict(UserStandardProgram)
    )
    wallet: Dict[str, Token] = field(default_factory=lambda: defaultdict(Token))


@dataclass(config=Config)
class Tokens(GlobalSettings):
    """
    Represents all ledger and other configuration balances associated with a particular token's current state.
    """

    timestamp: int = DEFAULT_TIMESTAMP
    master_vault: Any = field(default_factory=Token)
    staking_ledger: Any = field(default_factory=Token)
    pooltoken_supply: Any = field(default_factory=Token)
    protocol_wallet_pooltokens: Any = field(default_factory=Token)
    vortex_ledger: Any = field(default_factory=Token)
    vbnt_burned: Any = field(default_factory=Token)
    external_protection_vault: Any = field(default_factory=Token)
    standard_rewards_vault: Any = field(default_factory=Token)
    bnt_trading_liquidity: Any = field(default_factory=Token)
    tkn_trading_liquidity: Any = field(default_factory=Token)
    bnt_funding_limit: Decimal = DEFAULT_BNT_FUNDING_LIMIT
    bnt_funding_amt: Any = field(default_factory=Token)
    _vbnt_price: Any = field(default_factory=Token)
    spot_rate: Decimal = Decimal("0")
    inv_spot_rate: Decimal = Decimal("0")
    ema_rate: Decimal = Decimal("0")
    ema_last_updated: Decimal = Decimal("0")
    _inv_ema_rate: Decimal = Decimal("0")
    is_trading_enabled: bool = False

    @property
    def bnt_remaining_funding(self):
        """
        Computes the BNT funding remaining for the pool.
        """
        return self.bnt_funding_limit - self.bnt_funding_amt.balance.quantize(
            DEFAULT_QDECIMALS
        )

    @property
    def vbnt_price(self):
        """
        Returns the price of the current vbnt token. Only valid when name==bnt
        """
        assert (
            self.name == "bnt"
        ), f"vbnt_price attempted to be accessed in {self.name} state, call bnt state instead"
        return self._vbnt_price

    @property
    def is_price_stable(self):
        """
        True if the spot price deviation from the EMA is less than 1% (or other preset threshold amount).
        """
        return (
            Decimal(f"{DEFAULT_LOWER_EMA_LIMIT}") * self.ema_rate
            <= self.spot_rate
            <= Decimal(f"{DEFAULT_UPPER_EMA_LIMIT}") * self.ema_rate
        )

    @property
    def avg_tkn_trading_liquidity(self):
        """
        The tkn trading liquidity adjusted by the ema.
        """
        return (
            self.bnt_trading_liquidity.balance.quantize(DEFAULT_QDECIMALS)
            / self.ema_rate
            if self.ema_rate > 0
            else 0
        )

    @property
    def tkn_excess(self):
        """
        The difference between the master_vault balance and the average trading liquidity.
        """
        return (
            self.master_vault.balance.quantize(DEFAULT_QDECIMALS)
            - self.avg_tkn_trading_liquidity
        )

    @property
    def tkn_excess_bnt_equivalence(self):
        """
        Computes the equivalent bnt value of the non-trading tkn balance of the master_vault.
        """
        return self.tkn_excess * self.ema_rate

    @property
    def bnt_bootstrap_liquidity(self):
        """
        Computes the bnt_min_liquidity multiplied by 2.
        """
        return 2 * self.bnt_min_liquidity

    @property
    def inv_ema_rate(self) -> Decimal:
        """
        The inverse EMA rate.
        """
        return self._inv_ema_rate

    @inv_ema_rate.setter
    def inv_ema_rate(self, val):
        """
        Sets a new inverse EMA rate value.
        """
        self._inv_ema_rate = (self.inv_spot_rate * Decimal(0.2)) + (Decimal(0.8) * val)

    @property
    def inv_ema(self) -> Fraction:
        """
        Returns a fraction as two separate outputs
        """
        return Fraction(self.inv_ema_rate)

    @property
    def ema(self) -> Fraction:
        """
        Returns a fraction as two separate outputs
        """
        return Fraction(self.ema_rate)

    @property
    def ema_descale(self) -> int:
        """
        Used for descaling the ema into at most 112 bits per component.
        """
        return (
            int(max(self.ema.numerator, self.ema.denominator)) + self.max_uint112 - 1
        ) // self.max_uint112

    @property
    def ema_compressed_numerator(self) -> int:
        """
        Used to measure the deviation of solidity fixed point math on v3 calclulations.
        """
        return int(self.ema.numerator / self.ema_descale)

    @property
    def ema_compressed_denominator(self) -> int:
        """
        Used to measure the deviation of solidity fixed point math on v3 calclulations.
        """
        return int(self.ema.denominator / self.ema_descale)

    @property
    def is_ema_update_allowed(self) -> bool:
        """
        Returns True if the moving average has not been updated on the existing block.
        """
        return int(self.timestamp) != int(self.ema_last_updated)

    @property
    def ema_deviation(self) -> Decimal:
        """
        Returns the deviation between these values as emaRate/emaCompressedRate.
        """
        if self.ema_compressed_numerator > 0:
            return self.ema_rate * Decimal(
                self.ema_compressed_denominator / self.ema_compressed_numerator
            )
        else:
            return Decimal("0")


@dataclass(config=Config)
class State(GlobalSettings):
    """
    Represents the system state at the current timestamp. Main interface for all other dataclasses.
    """

    transaction_id: int = 0
    timestamp: int = DEFAULT_TIMESTAMP
    price_feeds: PandasDataFrame = None
    whitelisted_tokens: list = field(default_factory=list)
    tokens: Dict[str, Tokens] = field(default_factory=lambda: defaultdict(Tokens))
    users: Dict[str, User] = field(default_factory=lambda: defaultdict(User))
    standard_reward_programs: Dict[int, StandardProgram] = field(
        default_factory=lambda: defaultdict(StandardProgram)
    )
    autocompounding_reward_programs: Dict[str, AutocompoundingProgram] = field(
        default_factory=lambda: defaultdict(AutocompoundingProgram)
    )
    history: list = field(default_factory=list)
    logger: Any = logger
    json_export: dict = field(default_factory=dict)

    @property
    def valid_rewards_programs(self):
        """
        Returns all valid autocompounding programs for the current state.
        """
        return [
            p
            for p in self.autocompounding_reward_programs
            if self.autocompounding_reward_programs[p].is_active
            and self.autocompounding_reward_programs[p].is_enabled
        ]

    @property
    def usernames(self):
        """
        Returns a list of all current users
        """
        return [user for user in self.users]

    @property
    def withdrawal_ids(self):
        """
        Returns a list of all withdrawal_ids
        """
        return sum([len(self.users[user].pending_withdrawals) for user in self.users])

    @property
    def autocompounding_programs_count(self) -> int:
        """
        Returns the count of active autocompounding reward programs
        """
        return len(
            [
                self.autocompounding_reward_programs[tkn_name]
                for tkn_name in self.autocompounding_reward_programs
                if self.autocompounding_reward_programs[tkn_name].is_active
            ]
        )

    @property
    def active_autocompounding_programs(self) -> list:
        """
        Returns the active autocompounding reward programs
        """
        return [
            tkn_name
            for tkn_name in self.autocompounding_reward_programs
            if self.autocompounding_reward_programs[tkn_name].is_active
        ]

    @property
    def active_standard_programs(self) -> list:
        """
        Returns the active standard reward programs
        """
        return [
            tkn_name
            for tkn_name in self.whitelisted_tokens
            if self.standard_reward_programs[tkn_name].is_active
        ]

    @property
    def standard_programs_count(self) -> int:
        """
        Returns the count of active standard reward programs
        """
        return len(
            [
                self.standard_reward_programs[tkn_name]
                for tkn_name in self.whitelisted_tokens
                if self.standard_reward_programs[tkn_name].is_active
            ]
        )

    @property
    def bnt_price(self) -> Decimal:
        """
        Returns the bnt price feed at the current timestamp.
        """
        return Decimal(self.price_feeds.at[self.timestamp, "bnt"])

    @property
    def bnt_virtual_balance(self) -> Decimal:
        """
        Returns the inverse of the bnt price feed at the current timestamp
        """
        return Decimal("1") / self.bnt_price

    @property
    def bnbnt_rate(self) -> Decimal:
        """
        Returns the inverse of the bnt price feed at the current timestamp
        """
        if (
            self.tokens["bnt"].staking_ledger.balance.quantize(DEFAULT_QDECIMALS) == 0
            and self.tokens["bnt"].pooltoken_supply.balance.quantize(DEFAULT_QDECIMALS)
            == 0
        ):
            bnbnt_rate = Decimal("1")
        else:
            bnbnt_rate = Decimal(
                self.tokens["bnt"].pooltoken_supply.balance.quantize(DEFAULT_QDECIMALS)
                / self.tokens["bnt"].staking_ledger.balance.quantize(DEFAULT_QDECIMALS)
            )
        return bnbnt_rate

    def step(self):
        """
        Incriments the current timestamp.
        """
        self.timestamp += 1

    def add_user_to_standard_reward_providers(self, id: int, user_name: str):
        """
        Add a user to a given standard reward program providers list.
        """
        self.standard_reward_programs[id].providers.append(user_name)

    def remove_user_from_standard_reward_program(self, id: int, user_name: str):
        """
        Remove a user from a given standard reward program providers list.
        """
        self.standard_reward_programs[id].providers.remove(user_name)

    def set_standard_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Set standard rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].standard_rewards_vault.set(value)

    def set_user_pending_standard_rewards(
        self, user_name: str, id: int, value: Decimal
    ):
        """
        Set standard rewards vault balance by a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].pending_rewards.set(value)

    def increase_standard_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Increase standard rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].standard_rewards_vault.add(value)

    def decrease_standard_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease standard rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].standard_rewards_vault.subtract(value)

    def decrease_pooltoken_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease staked_amt supply balance by a given amount.
        """
        self.tokens[tkn_name].pooltoken_supply.subtract(value)

    def increase_pooltoken_balance(self, tkn_name: str, value: Decimal):
        """
        Increase staked_amt supply balance by a given amount.
        """
        self.tokens[tkn_name].pooltoken_supply.add(value)

    def increase_user_standard_rewards_stakes(
        self, id: int, user_name: str, value: Decimal
    ):
        """
        Increase user standard rewards staked_reward_amt pooltokens by a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].staked_amt.add(value)

    def decrease_user_standard_rewards_stakes(
        self, id: int, user_name: str, value: Decimal
    ):
        """
        Increase user standard rewards staked_reward_amt pooltokens by a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].staked_amt.subtract(value)

    def set_user_standard_rewards_stakes(self, id: int, user_name: str, value: Decimal):
        """
        Set user standard rewards staked_reward_amt pooltokens to a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].staked_amt.set(value)

    def decrease_bnt_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Decrease bnt_trading_liquidity balance by a given amount.
        """
        self.tokens[tkn_name].bnt_trading_liquidity.subtract(value)

    def increase_bnt_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Increase bnt_trading_liquidity balance by a given amount.
        """
        self.tokens[tkn_name].bnt_trading_liquidity.add(value)

    def decrease_tkn_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Decrease tkn_trading_liquidity balance by a given amount.
        """
        self.tokens[tkn_name].tkn_trading_liquidity.subtract(value)

    def increase_tkn_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Increase tkn_trading_liquidity balance by a given amount.
        """
        self.tokens[tkn_name].tkn_trading_liquidity.add(value)

    def decrease_bnt_funding_amt(self, tkn_name: str, value: Decimal):
        """
        Decrease bnt_funding_amt balance by a given amount.
        """
        self.tokens[tkn_name].bnt_funding_amt.subtract(value)

    def increase_bnt_funding_amt(self, tkn_name: str, value: Decimal):
        """
        Increase bnt_funding_amt balance by a given amount.
        """
        self.tokens[tkn_name].bnt_funding_amt.add(value)

    def decrease_protocol_wallet_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease protocol wallet balance by a given amount.
        """
        self.tokens[tkn_name].protocol_wallet_pooltokens.subtract(value)

    def increase_protocol_wallet_balance(self, tkn_name: str, value: Decimal):
        """
        Increase protocol wallet balance by a given amount.
        """
        self.tokens[tkn_name].protocol_wallet_pooltokens.add(value)

    def decrease_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease master_vault balance by a given amount.
        """
        self.tokens[tkn_name].master_vault.subtract(value)

    def increase_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Increase master_vault balance by a given amount.
        """
        self.tokens[tkn_name].master_vault.add(value)

    def decrease_staked_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease staked_reward_amt balance by a given amount.
        """
        self.tokens[tkn_name].staking_ledger.subtract(value)

    def increase_staked_balance(self, tkn_name: str, value: Decimal):
        """
        Increase staked_reward_amt balance by a given amount.
        """
        self.tokens[tkn_name].staking_ledger.add(value)

    def decrease_external_protection_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease external protection balance by a given amount.
        """
        self.tokens[tkn_name].external_protection.subtract(value)

    def increase_external_protection_balance(self, tkn_name: str, value: Decimal):
        """
        Increase external protection balance by a given amount.
        """
        self.tokens[tkn_name].external_protection.add(value)

    def decrease_user_balance(self, user_name: str, tkn_name: str, value: Decimal):
        """
        Decrease user balance by a given amount.
        """
        self.users[user_name].wallet[tkn_name].subtract(value)

    def increase_user_balance(self, user_name: str, tkn_name: str, value: Decimal):
        """
        Increase user balance by a given amount.
        """
        self.users[user_name].wallet[tkn_name].add(value)

    def set_vortex_balance(self, tkn_name: str, value: Decimal):
        """
        Set vortex_ledger balance to a given amount.
        """
        self.tokens[tkn_name].vortex_ledger.set(value)

    def decrease_vbnt_burned(self, tkn_name: str, value: Decimal):
        """
        Decrease vbnt amount burned.
        """
        self.tokens[tkn_name].vbnt_burned.subtract(value)

    def increase_vbnt_burned(self, tkn_name: str, value: Decimal):
        """
        Increase vbnt amount burned.
        """
        self.tokens[tkn_name].vbnt_burned.add(value)

    def set_vbnt_burned(self, tkn_name: str, value: Decimal):
        """
        Set vbnt amount burned.
        """
        self.tokens[tkn_name].vbnt_burned.set(value)

    def increase_vortex_balance(self, tkn_name: str, value: Decimal):
        """
        Increase vortex_ledger balance by a given amount.
        """
        self.tokens[tkn_name].vortex_ledger.add(value)

    def decrease_vortex_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease vortex_ledger balance by a given amount.
        """
        self.tokens[tkn_name].vortex_ledger.subtract(value)

    def increase_standard_reward_program_stakes(self, id: int, value: Decimal):
        """
        Increase the standard reward program staked_reward_amt balance by a given amount.
        """
        self.standard_reward_programs[id].staked_reward_amt.add(value)

    def decrease_standard_reward_program_stakes(self, id: int, value: Decimal):
        """
        Decrease the standard reward program staked_reward_amt balance by a given amount.
        """
        self.standard_reward_programs[id].staked_reward_amt.subtract(value)

    def set_standard_rewards_per_token(self, id: int, value: Decimal):
        """
        Set the standard reward program rewards per token.
        """
        self.standard_reward_programs[id].reward_per_token.set(value)

    def set_standard_rewards_last_update_time(self, id: int, value: int):
        """
        Set the standard reward program last updated time.
        """
        self.standard_reward_programs[id].last_update_time = value

    def set_provider_reward_per_token_paid(
        self, user_name: str, id: int, value: Decimal
    ):
        """
        Set the user's rewards per token paid for a given program.
        """
        self.users[user_name].pending_standard_rewards[id].reward_per_token_paid.set(
            value
        )

    def set_provider_pending_standard_rewards(
        self, user_name: str, id: int, value: Decimal
    ):
        """
        Set the user's pending standard rewards for a given program.
        """
        self.users[user_name].pending_standard_rewards[id].pending_rewards.set(value)

    def set_trading_fee(self, tkn_name: str, value: Decimal):
        """
        Set the trading fee for a given tkn_name.
        """
        self.tokens[tkn_name].trading_fee = value

    def set_bnt_funding_limit(self, tkn_name: str, value: Decimal):
        """
        Set the bnt funding limit for a given tkn_name.
        """
        self.tokens[tkn_name].bnt_funding_limit = value

    def set_bnt_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Set the bnt_trading_liquidity balance to a given amount.
        """
        self.tokens[tkn_name].bnt_trading_liquidity.set(value)

    def set_standard_program_end_time(self, id: int, value: int):
        """
        Set the end time of the standard program.
        """
        self.standard_reward_programs[id].end_time = value

    def set_standard_program_is_active(self, id: int, value: bool):
        """
        Set the is_active status of a standard program.
        """
        self.standard_reward_programs[id].is_active = value

    def set_tkn_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Set the tkn_trading_liquidity balance to a given amount.
        """
        self.tokens[tkn_name].tkn_trading_liquidity.set(value)

    def set_withdrawal_fee(self, tkn_name: str, value: Decimal):
        """
        Set the withdrawal_fee to a given amount.
        """
        self.tokens[tkn_name].withdrawal_fee = value

    def set_prev_token_amt_distributed(self, tkn_name: str, value: Decimal):
        """
        Set the prev_token_amt_distributed to a given value.
        """
        self.autocompounding_reward_programs[tkn_name].prev_token_amt_distributed.set(
            value
        )

    def set_is_trading_enabled(self, tkn_name: str, value: bool):
        """
        Set the set_is_trading_enabled to a given status.
        """
        self.tokens[tkn_name].is_trading_enabled = value

    def set_spot_rate(self, tkn_name: str, value: Decimal):
        """
        Set the spot_rate to a given value.
        """
        self.tokens[tkn_name].spot_rate = value

    def set_bnt_funding_amt(self, tkn_name: str, value: Decimal):
        """
        Set the bnt_funding_amt to a given status.
        """
        self.tokens[tkn_name].bnt_funding_amt.set(value)

    def set_initial_rates(self, tkn_name: str, bootstrap_rate: Decimal):
        self.tokens[tkn_name].spot_rate = self.tokens[
            tkn_name
        ].ema_rate = bootstrap_rate

    def set_staked_balance(self, tkn_name: str, value: Decimal):
        """
        Set the staked_reward_amt balance to a given amount.
        """
        self.tokens[tkn_name].staking_ledger.set(value)

    def set_protocol_wallet_balance(self, tkn_name: str, value: Decimal):
        """
        Set the protocol_wallet balance to a given amount.
        """
        self.tokens[tkn_name].protocol_wallet_pooltokens.set(value)

    def set_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Set the master_vault balance to a given amount.
        """
        self.tokens[tkn_name].master_vault.set(value)

    def set_user_balance(self, user_name: str, tkn_name: str, value: Decimal):
        """
        Set the user balance to a given amount.
        """
        self.users[user_name].wallet[tkn_name].set(value)

    def set_ema_rate(self, tkn_name: str, value: Decimal):
        """
        Set the ema rate to a given amount.
        """
        self.tokens[tkn_name].ema_rate = value

    def set_network_fee(self, tkn_name: str, value: Decimal):
        """
        Set the network fee to a given amount.
        """
        self.tokens[tkn_name].network_fee = value

    def set_pooltoken_balance(self, tkn_name: str, value: Decimal):
        """
        Set the staked_reward_amt balance to a given amount.
        """
        self.tokens[tkn_name].pooltoken_supply.set(value)

    def set_standard_remaining_rewards(self, id: int, value: Decimal):
        """
        Set the remaining_rewards balance to a given amount.
        """
        self.standard_reward_programs[id].remaining_rewards.set(value)

    def set_autocompounding_remaining_rewards(self, tkn_name: str, value: Decimal):
        """
        Set the remaining_rewards balance to a given amount.
        """
        self.autocompounding_reward_programs[tkn_name].remaining_rewards.set(value)

    def set_token_amt_to_distribute(self, tkn_name: str, value: Decimal):
        """
        Set the token_amt_to_distribute balance to a given amount.
        """
        self.autocompounding_reward_programs[tkn_name].token_amt_to_distribute.set(
            value
        )

    def set_program_is_active(self, tkn_name: str, value: bool):
        """
        Set the rewards is_active flag to a given status.
        """
        self.autocompounding_reward_programs[tkn_name].is_active = value

    def set_inv_spot_rate(self, tkn_name: str, value: Decimal):
        """
        Set the inv_spot_rate to a given value.
        """
        self.tokens[tkn_name].inv_spot_rate = value

    def set_pending_withdrawals_status(
        self, user_name: str, tkn_name: str, id_number: int, status: bool
    ):
        """
        Set pending_withdrawal to a given status.
        """
        self.users[user_name].wallet[tkn_name].pending_withdrawals[
            id_number
        ].is_complete = status

    def create_whitelisted_tkn(self, tkn_name: str):
        """
        Adds a new tkn_name to the whitelisted_tokens
        """
        if tkn_name not in self.whitelisted_tokens:
            self.whitelisted_tokens.append(tkn_name)

    def create_user(self, user_name: str):
        """
        Creates a new system user agent.
        """
        if user_name not in self.usernames:
            self.users[user_name] = User(user_name=user_name)

        for tkn_name in self.whitelisted_tokens:
            if tkn_name not in self.users[user_name].wallet:
                self.users[user_name].wallet[tkn_name] = Token(
                    balance=DEFAULT_ACCOUNT_BALANCE
                )
            if get_pooltoken_name(tkn_name) not in self.users[user_name].wallet:
                self.users[user_name].wallet[get_pooltoken_name(tkn_name)] = Token(
                    balance=DEFAULT_ACCOUNT_BALANCE
                )
            if tkn_name == "bnt":
                if "vbnt" not in self.users[user_name].wallet:
                    self.users[user_name].wallet["vbnt"] = Token(
                        balance=DEFAULT_ACCOUNT_BALANCE
                    )

    def update_inv_spot_rate(self, tkn_name: str):
        """
        Updates the inverse spot rate.
        """
        bnt_trading_liquidity = get_bnt_trading_liquidity(self, tkn_name)
        tkn_trading_liquidity = get_tkn_trading_liquidity(self, tkn_name)
        if bnt_trading_liquidity == 0 and tkn_trading_liquidity == 0:
            inv_spot_rate = Decimal(0)
        else:
            inv_spot_rate = bnt_trading_liquidity / tkn_trading_liquidity
        self.set_inv_spot_rate(tkn_name, inv_spot_rate)

    def update_spot_rate(self, tkn_name: str):
        """
        Updates the spot rate.
        """
        bnt_trading_liquidity = get_bnt_trading_liquidity(self, tkn_name)
        tkn_trading_liquidity = get_tkn_trading_liquidity(self, tkn_name)
        if bnt_trading_liquidity == 0 and tkn_trading_liquidity == 0:
            spot_rate = Decimal(0)
        else:
            spot_rate = bnt_trading_liquidity / tkn_trading_liquidity
        self.set_spot_rate(tkn_name, spot_rate)
        self.update_inv_spot_rate(tkn_name)

    def next_standard_program_id(self) -> int:
        """
        Returns the next standard program ID.
        """
        return len(self.standard_reward_programs) + 1

    def copy(self):
        return copy.deepcopy(self)


def get_vault_tvl(state: State) -> Decimal:
    """
    Computes the vault tvl for all tkns.
    """
    return sum(
        [
            (
                get_tkn_price(state, tkn_name)
                * state.tokens[tkn_name].master_vault.balance
            )
            for tkn_name in state.whitelisted_tokens
        ]
    )


def get_unclaimed_rewards(state: State, tkn_name: str) -> Decimal:
    """
    Returns the rewards vault balance for a given tkn_name.
    """
    return state.tokens[tkn_name].standard_rewards_vault.balance.quantize(
        DEFAULT_QDECIMALS
    )


def get_total_standard_rewards_staked(state, id: int) -> Decimal:
    """
    Returns the total standard rewards staked_reward_amt for a given program id.
    """
    providers = [
        state.users[user_name]
        for user_name in state.standard_reward_programs[id].providers
    ]
    return sum(
        [
            provider.pending_standard_rewards[id].staked_reward_amt.balance.quantize(
                DEFAULT_QDECIMALS
            )
            for provider in providers
        ]
    )


def get_tkn_virtual_balance(state: State, tkn_name: str) -> Decimal:
    """
    Return the reciprocal of the price of bnt or tkn.
    """
    return Decimal("1") / get_tkn_price(state, tkn_name)


def get_virtual_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns bnt_virtual_balance / tkn_token_virtual_balance
    """
    return get_bnt_virtual_balance(state) / get_tkn_virtual_balance(state, tkn_name)


def get_bnt_virtual_balance(state: State) -> Decimal:
    """
    Returns bnt_virtual_balance via the common get interface for consistency
    """
    return state.bnt_virtual_balance


def get_tkn_bootstrap_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The tkn equivalnce of twice the bnt min liquidity (i.e. the bnt bootstrap liquidity)
    """
    return state.tokens[tkn_name].bnt_bootstrap_liquidity / get_virtual_rate(
        state, tkn_name
    )


def get_bnt_bootstrap_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    Returns the current state bnt bootstrap liquidity via get interface for consistency
    """
    return state.tokens[tkn_name].bnt_bootstrap_liquidity


def get_staked_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current balance of the staking ledger for a given tkn_name.
    """
    return state.tokens[tkn_name].staking_ledger.balance.quantize(DEFAULT_QDECIMALS)


def get_vault_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current balance of the master master_vault for a given tkn_name.
    """
    return state.tokens[tkn_name].master_vault.balance.quantize(DEFAULT_QDECIMALS)


def get_bnt_trading_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The current bnt trading liquidity for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_trading_liquidity.balance.quantize(
        DEFAULT_QDECIMALS
    )


def get_standard_reward_providers(state: State, id: int) -> list:
    """
    Get the standard reward providers for a given program id.
    """
    return state.standard_reward_programs[id].providers


def get_standard_reward_tkn_name(state: State, id: int) -> Tuple[str, str]:
    """
    Get the standard reward tkn_name for a given id.
    """
    return (
        state.standard_reward_programs[id].tkn_name,
        state.standard_reward_programs[id].rewards_token,
    )


def get_standard_reward_per_token(state: State, id: int) -> Decimal:
    pass


def get_standard_reward_end_time(state: State, id: int) -> int:
    pass


def get_standard_reward_start_time(state: State, id: int) -> int:
    pass


def get_standard_reward_last_update_time(state: State, id: int) -> int:
    pass


def get_standard_reward_rate(state: State, id: int) -> int:
    pass


def get_user_pending_rewards_staked_balance(
    state: State, id: int, user_name: str
) -> Decimal:
    return (
        state.users[user_name]
        .pending_standard_rewards[id]
        .staked.balance.quantize(DEFAULT_QDECIMALS)
    )


def get_user_pending_standard_rewards(state: State, id: int, user_name: str) -> Decimal:
    return (
        state.users[user_name]
        .pending_standard_rewards[id]
        .pending_rewards.balance.quantize(DEFAULT_QDECIMALS)
    )


def get_user_reward_per_token_paid(state: State, id: int, user_name: str) -> Decimal:
    return (
        state.users[user_name]
        .pending_standard_rewards[id]
        .reward_per_token_paid.balance.quantize(DEFAULT_QDECIMALS)
    )


def get_user_wallet_tokens(state: State, user_name: str) -> list:
    """
    List of all tokens for a given user.
    """
    return [
        state.users[user_name].wallet[tkn_name].balance.quantize(DEFAULT_QDECIMALS)
        for tkn_name in state.whitelisted_tokens
        if state.users[user_name].wallet[tkn_name].balance.quantize(DEFAULT_QDECIMALS)
        > 0
    ]


def get_tkn_trading_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The current tkn trading liquidity for a given tkn_name.
    """
    return state.tokens[tkn_name].tkn_trading_liquidity.balance.quantize(
        DEFAULT_QDECIMALS
    )


def get_bnt_funding_amt(state: State, tkn_name: str) -> Decimal:
    """
    The current bnt amount funded for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_funding_amt.balance.quantize(DEFAULT_QDECIMALS)


def get_external_protection_vault(state: State, tkn_name: str) -> Decimal:
    """
    The current external protection master_vault balance for a given tkn_name.
    """
    return state.tokens[tkn_name].external_protection_vault.balance.quantize(
        DEFAULT_QDECIMALS
    )


def get_pooltoken_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current erc20 contracts staked_amt supply for a given tkn_name.
    """
    return state.tokens[tkn_name].pooltoken_supply.balance.quantize(DEFAULT_QDECIMALS)


def get_protocol_wallet_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current protocol owned liquidity (when tkn_name==bnt) or the current autocompounding rewards remaining.
    """
    return state.tokens[tkn_name].protocol_wallet_pooltokens.balance.quantize(
        DEFAULT_QDECIMALS
    )


def get_vortex_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current vortex_ledger balance for a given tkn_name.
    """
    return state.tokens[tkn_name].vortex_ledger.balance.quantize(DEFAULT_QDECIMALS)


def get_user_balance(state: State, user_name: str, tkn_name: str) -> Decimal:
    """
    The current external protection master_vault balance for a given tkn_name.
    """
    return state.users[user_name].wallet[tkn_name].balance.quantize(DEFAULT_QDECIMALS)


def get_bnbnt_rate(state: State) -> Decimal:
    """
    The current bnbnt rate.
    """
    return state.bnbnt_rate.quantize(DEFAULT_QDECIMALS)


def get_total_rewards(state: State, tkn_name: str) -> Decimal:
    """
    The initial balance for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[
        tkn_name
    ].total_rewards.balance.quantize(DEFAULT_QDECIMALS)


def get_distribution_type(state: State, tkn_name: str) -> str:
    """
    The type of distribution for an autocompounding rewards program (either flat or exponential "exp")
    """
    return state.autocompounding_reward_programs[tkn_name].distribution_type


def get_prev_token_amt_distributed(state: State, tkn_name: str) -> Decimal:
    """
    The previous distribution amount for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[
        tkn_name
    ].prev_token_amt_distributed.balance.quantize(DEFAULT_QDECIMALS)


def get_autocompounding_start_time(state: State, tkn_name: str) -> int:
    """
    The start time for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[tkn_name].start_time


def get_half_life_seconds(state: State, tkn_name: str) -> int:
    """
    The half life in seconds for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[tkn_name].half_life_seconds


def get_timestamp(state: State) -> int:
    """
    The current state timestamp.
    """
    return state.timestamp


def get_avg_tkn_trading_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The average trading liquidity for a given tkn_name.
    """
    return state.tokens[tkn_name].avg_tkn_trading_liquidity


def get_tkn_excess_bnt_equivalence(state: State, tkn_name: str) -> Decimal:
    """
    Returns the equivalent bnt value of the non-trading tkn balance of the master_vault.
    """
    return state.tokens[tkn_name].tkn_excess_bnt_equivalence


def get_tkn_excess(state: State, tkn_name: str) -> Decimal:
    """
    The difference between the master_vault balance and the average trading liquidity.
    """
    return state.tokens[tkn_name].tkn_excess


def get_is_trading_enabled(state: State, tkn_name: str) -> bool:
    """
    Returns True if trading is enabled for a given tkn_name.
    """
    return state.tokens[tkn_name].is_trading_enabled


def get_is_price_stable(state: State, tkn_name: str) -> bool:
    """
    Returns True if the spot_price vs EMA deviation is less than 1%.
    """
    return state.tokens[tkn_name].is_price_stable


def get_bnt_remaining_funding(state: State, tkn_name: str) -> Decimal:
    """
    Returns the bnt funding remaining for a given tkn_name relative to the limit.
    """
    return state.tokens[tkn_name].bnt_remaining_funding


def get_flat_distribution_rate_per_second(state: State, tkn_name: str) -> Decimal:
    """
    Returns the flat distribution rate per second for a given tkn_name based on the program duration.
    """
    return state.autocompounding_reward_programs[
        tkn_name
    ].flat_distribution_rate_per_second


def get_spot_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns the bnt funding remaining for a given tkn_name relative to the limit.
    """
    return state.tokens[tkn_name].spot_rate


def get_inv_spot_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns the inverse spot rate for a given tkn_name.
    """
    return state.tokens[tkn_name].inv_spot_rate


def get_ema_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns spot rate for a given tkn_name.
    """
    return state.tokens[tkn_name].ema_rate


def get_ema_last_updated(state: State, tkn_name: str) -> Decimal:
    """
    Returns the timestamp of the last EMA update of a given tkn_name.
    """
    return state.tokens[tkn_name].ema_last_updated


def get_whitelisted_tokens(state: State) -> List[str]:
    """
    Returns the current state whitelisted tokens.
    """
    return state.whitelisted_tokens


def get_usernames(state: State) -> List[str]:
    """
    Returns the current state users by usernames.
    """
    return state.usernames


def get_trading_fee(state: State, tkn_name: str) -> Decimal:
    """
    Returns the trading fee for a given tkn_name.
    """
    return state.tokens[tkn_name].trading_fee


def get_bnt_funding_limit(state: State, tkn_name: str) -> Decimal:
    """
    Returns the bnt funding limit for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_funding_limit


def get_withdrawal_id(state: State) -> int:
    """
    Generate withdraw id.
    """
    return state.withdrawal_ids


def get_tkn_price(state: State, tkn_name: str) -> Decimal:
    """
    Gets the tkn price from the price feed.
    """
    return (
        state.tokens[tkn_name].vbnt_price.quantize(DEFAULT_QDECIMALS)
        if tkn_name == "vbnt"
        else Decimal(state.price_feeds.at[state.timestamp, tkn_name])
    )


def get_user_pending_withdrawals(state: State, user_name: str, tkn_name: str) -> list:
    """
    Returns a given user's pending withdrawals for a given tkn_name
    """
    return [
        id
        for id in state.users[user_name].pending_withdrawals
        if state.users[user_name].pending_withdrawals[id].tkn_name == tkn_name
        and state.users[user_name].pending_withdrawals[id].is_complete
    ]


def get_prices(state: State, tkn_name: str) -> Tuple[Decimal, Decimal]:
    """
    Returns tkn & bnt price from the price feed.
    """
    return get_tkn_price(state, tkn_name), get_tkn_price(state, "bnt")


def get_is_ema_update_allowed(state: State, tkn_name: str) -> bool:
    """
    Returns the is_ema_update_allowed state for a given tkn_name.
    """
    return state.tokens[tkn_name].is_ema_update_allowed


def get_total_bnt_trading_liquidity(state: State) -> Decimal:
    """
    Returns the total sum of bnt_trading_liquidity across all whitelisted tokens
    """
    return sum(
        [
            state.tokens[name].bnt_trading_liquidity.balance.quantize(DEFAULT_QDECIMALS)
            for name in state.whitelisted_tokens
            if name != "bnt"
        ]
    )


def get_bnt_min_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    Returns the bnt_min_liquidity state for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_min_liquidity


def get_rate_report(state: State, tkn_name: str, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [
        f"Spot Rate={state.tokens[tkn_name].spot_rate.quantize(qdecimals)}, "
        f"EMA Rate={state.tokens[tkn_name].ema_rate.quantize(qdecimals)}"
    ]


def get_trading_liquidity_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [
        f"bnt={get_bnt_trading_liquidity(state, tkn_name).quantize(qdecimals)} {tkn_name}="
        + str(get_tkn_trading_liquidity(state, tkn_name).quantize(qdecimals))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_vault_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnt={get_vault_balance(state, 'bnt').quantize(qdecimals)}"] + [
        f"{tkn_name}=" + str(get_vault_balance(state, tkn_name).quantize(qdecimals))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_staking_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnt={get_staked_balance(state, 'bnt').quantize(qdecimals)}"] + [
        f"{tkn_name}=" + str(get_staked_balance(state, tkn_name).quantize(qdecimals))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_pooltoken_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnbnt={get_pooltoken_balance(state, 'bnt').quantize(qdecimals)}"] + [
        f"bn{tkn_name}="
        + str(get_pooltoken_balance(state, tkn_name).quantize(qdecimals))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_vortex_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return ["bnt=" + str(get_vortex_balance(state, "bnt").quantize(qdecimals))] + [
        "" for x in range(len(state.whitelisted_tokens[:-1]))
    ]


def get_external_protection_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [
        f"{tkn_name}="
        + str(get_external_protection_vault(state, tkn_name).quantize(qdecimals))
        for tkn_name in state.whitelisted_tokens
    ]


def get_protocol_wallet_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [
        f"bnbnt=" + str(get_protocol_wallet_balance(state, "bnt").quantize(qdecimals))
    ] + ["" for tkn_name in state.whitelisted_tokens[:-1]]


def get_description(state: State, qdecimals: Decimal) -> dict:
    """
    Builds a dictionary to be used as a description for current state information display.
    """
    return {
        "Trading Liquidity": get_trading_liquidity_description(state, qdecimals),
        "Vault": get_vault_description(state, qdecimals),
        "Staking": get_staking_description(state, qdecimals),
        "ERC20 Contracts": get_pooltoken_description(state, qdecimals),
        "Vortex": get_vortex_description(state, qdecimals),
        "External Protection": get_external_protection_description(state, qdecimals),
        "Protocol WalletState": get_protocol_wallet_description(state, qdecimals),
    }


def get_total_holdings(state: State, user_name: str) -> Decimal:
    """
    Returns the total number of holdings for a given wallet name.
    """
    return state.users[user_name].total_holdings(state)


def get_pooltoken_name(tkn_name: str) -> str:
    """
    Returns the pool token name for a given token name.
    """
    return f"bn{tkn_name}"


def get_json_virtual_balances(state: State, tkn_name: str) -> dict:
    """
    Return the virtual balances for a given token name for a json test scenario.
    """
    return {
        "bntVirtualBalance": state.price_feeds[tkn_name].values[0],
        "baseTokenVirtualBalance": state.price_feeds["bnt"].values[0],
    }


def get_max_bnt_deposit(
    state: State,
    user_bnt: Decimal,
) -> Decimal:
    """
    Used in simulation only.
    """
    return max(get_pooltoken_balance(state, "bnt"), user_bnt)


def get_network_fee(state: State, tkn_name: str) -> Decimal:
    """
    Gets the network fee for a given tkn_name.
    """
    return state.tokens[tkn_name].network_fee


def get_trade_inputs(
    state: State, tkn_name: str
) -> Tuple[str, Decimal, Decimal, Decimal, Decimal]:
    """
    Gets all input data required to process trade action.
    """
    return (
        tkn_name,
        get_bnt_trading_liquidity(state, tkn_name),
        get_tkn_trading_liquidity(state, tkn_name),
        get_trading_fee(state, tkn_name),
        get_network_fee(state, tkn_name),
    )


def get_autocompounding_remaining_rewards(state: State, tkn_name: str) -> Decimal:
    """
    Get the remaining rewards for a given program.
    """
    return state.autocompounding_reward_programs[
        tkn_name
    ].remaining_rewards.balance.quantize(DEFAULT_QDECIMALS)


def get_remaining_standard_rewards(state: State, id: int) -> Decimal:
    """
    Get the remaining rewards for a given program.
    """
    return state.standard_reward_programs[id].remaining_rewards.balance.quantize(
        DEFAULT_QDECIMALS
    )


def get_standard_program(state: State, tkn_name: str) -> Decimal:
    """
    Get the remaining rewards for a given program.
    """
    return state.autocompounding_reward_programs[
        tkn_name
    ].remaining_rewards.balance.quantize(DEFAULT_QDECIMALS)
