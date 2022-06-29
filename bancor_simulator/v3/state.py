# coding=utf-8
import logging
import warnings
from collections import defaultdict
from dataclasses import field
from decimal import Decimal
from fractions import Fraction
from typing import Dict, List, Any, Tuple
from typing import TypeVar
import pandas as pd
from pydantic.dataclasses import dataclass

warnings.filterwarnings("ignore", category=RuntimeWarning)
PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")

MODEL = "Bancor V3"
VERSION = "1.0.0"
WHITELISTED_TOKENS = ["dai", "eth", "link", "bnt", "tkn", "wbtc"]
ACTIVE_USERS = ["Alice", "Bob", "Charlie", "Trader"]
DECIMALS = 18
SECONDS_PER_DAY = Decimal("86400")
QDECIMALS = Decimal(10) ** -DECIMALS
MAX_UINT112 = 2 ** 112 - 1
PRECISION = 155
PRICE_FEEDS_PATH = "https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.parquet"
EXP_DECAY_DISTRIBUTION = 1
FLAT_DISTRIBUTION = 0

logger = logging.getLogger(__name__)


@dataclass
class Token:
    """
    Represents a token balance with common math operations to increase, decrease, and set the balance.
    """
    balance: Decimal

    def add(self, value: Decimal):
        self.balance += self.validate(value)

    def subtract(self, value: Decimal):
        self.balance -= self.validate(value)

    def set(self, value: Decimal):
        self.balance = self.validate(value)

    def validate(self, value) -> Decimal:
        if "Decimal" in str(value):
            return value
        else:
            return Decimal(str(value))


@dataclass
class GlobalSettings:
    """
    Represents the default global settings. These can be overridden by the BancorNetwork configuration upon instantiation.
    """
    unix_timestamp: int = 0
    model: str = MODEL
    version: str = VERSION
    eightee_places: int = QDECIMALS
    max_uint112: int = MAX_UINT112
    precision: int = PRECISION
    decimals: int = DECIMALS
    whitelisted_tokens: List[str] = field(default_factory=lambda: WHITELISTED_TOKENS)
    active_users: List[str] = field(default_factory=lambda: ACTIVE_USERS)
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

    class Config:
        validate_assignment = True


@dataclass
class CooldownState:
    """
    Represents a pending withdrawal cooldown.
    """
    id: int
    created_at: int
    user_name: str
    tkn_name: str
    is_complete: bool
    tkn: Token = Token(balance=Decimal("0"))
    pooltoken: Token = Token(balance=Decimal("0"))

    class Config:
        validate_assignment = True


@dataclass
class StandardProgramState(GlobalSettings):
    """
    Represents an standard reward program state.
    """
    id: int
    tkn_name: str
    rewards_token: str
    is_enabled: bool
    start_time: int
    end_time: int
    last_update_time: int
    reward_rate: Decimal
    remaining_rewards: Token
    reward_per_token: Token
    total_unclaimed_rewards: Token
    staked_reward_amt: Token
    pooltoken_amt: Token
    providers: list = field(default_factory=list)

    class Config:
        validate_assignment = True


@dataclass
class AutocompoundingProgramState:
    """
    Represents an autocompounding reward program state.
    """
    id: int
    tkn_name: str
    owner_id: str
    total_rewards: Token
    remaining_rewards: Token
    half_life_days: int = 0
    _half_life_seconds: int = 0
    start_time: int = 0
    created_at: int = 0
    prev_token_amt_distributed: Token = Token(balance=Decimal("0"))
    total_duration_in_seconds: Decimal = Decimal("0")
    distribution_type: str = "exp"
    is_active: bool = False
    is_enabled: bool = False

    @property
    def flat_distribution_rate_per_second(self):
        """
        Returns the rate per second of the distribution.
        """
        return self.total_rewards.balance / self.total_duration_in_seconds

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

    class Config:
        validate_assignment = True


@dataclass
class StandardProgramUserState(GlobalSettings):
    """
    Represents a standard reward program user state
    """
    id: int
    staked_amt: Token
    pending_rewards: Token
    reward_per_token_paid: Token

    class Config:
        validate_assignment = True


@dataclass
class UserState:
    """
    Represents a user agent state.
    """
    user_name: str
    pending_withdrawals: Dict[int, CooldownState] = field(
        default_factory=lambda: defaultdict(CooldownState)
    )
    pending_standard_rewards: Dict[int, StandardProgramUserState] = field(
        default_factory=lambda: defaultdict(StandardProgramUserState)
    )
    wallet: Dict[str, Token] = field(default_factory=lambda: defaultdict(Token))

    class Config:
        validate_assignment = True


@dataclass
class TokenState(GlobalSettings):
    """
    Represents all ledger and other configuration balances associated with a particular token's current state.
    """
    name: str = None
    master_vault: Token = Token(balance=Decimal("0"))
    staking_ledger: Token = Token(balance=Decimal("0"))
    pooltoken_supply: Token = Token(balance=Decimal("0"))
    protocol_wallet_pooltokens: Token = Token(balance=Decimal("0"))
    vortex_ledger: Token = Token(balance=Decimal("0"))
    external_protection_vault: Token = Token(balance=Decimal("0"))
    standard_rewards_vault: Token = Token(balance=Decimal("0"))
    bnt_trading_liquidity: Token = Token(balance=Decimal("0"))
    tkn_trading_liquidity: Token = Token(balance=Decimal("0"))
    bnt_funding_limit: Decimal = Decimal("1000000")
    bnt_funding_amt: Token = Token(balance=Decimal("0"))
    _vbnt_price: Token = Token(balance=Decimal("0"))
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
        return self.bnt_funding_limit - self.bnt_funding_amt.balance

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
                Decimal("0.99") * self.ema_rate
                <= self.spot_rate
                <= Decimal("1.01") * self.ema_rate
        )

    @property
    def avg_tkn_trading_liquidity(self):
        """
        The tkn trading liquidity adjusted by the ema.
        """
        return (
            self.bnt_trading_liquidity.balance / self.ema_rate
            if self.ema_rate > 0
            else 0
        )

    @property
    def tkn_excess(self):
        """
        The difference between the master_vault balance and the average trading liquidity.
        """
        return self.master_vault.balance - self.avg_tkn_trading_liquidity

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
        return int(self.unix_timestamp) != int(self.ema_last_updated)

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

    class Config:
        validate_assignment = True


@dataclass
class State(GlobalSettings):
    """
    Represents the system state at the current timestamp. Main interface for all other dataclasses.
    """
    transaction_id: int = 0
    unix_timestamp: int = 0
    price_feeds: PandasDataFrame = None
    whitelisted_tokens: list = field(default_factory=list)
    history: list = field(default_factory=list)
    logger: Any = logger
    json_export: dict = field(default_factory=dict)
    tokens: Dict[str, TokenState] = field(
        default_factory=lambda: defaultdict(TokenState)
    )
    users: Dict[str, UserState] = field(default_factory=lambda: defaultdict(UserState))
    standard_programs: Dict[id, StandardProgramState] = field(
        default_factory=lambda: defaultdict(StandardProgramState)
    )
    autocompounding_programs: Dict[str, AutocompoundingProgramState] = field(
        default_factory=lambda: defaultdict(AutocompoundingProgramState)
    )

    @property
    def valid_rewards_programs(self):
        """
        Returns all valid autocompounding programs for the current state.
        """
        return [
            p
            for p in self.autocompounding_programs
            if self.autocompounding_programs[p].is_active
               and self.autocompounding_programs[p].is_enabled
        ]

    def step(self):
        """
        Incriments the current timestamp.
        """
        self.unix_timestamp += 1

    @property
    def usernames(self):
        """
        Returns a list of all current users
        """
        return [user for user in self.users]

    @property
    def autocompounding_programs_count(self) -> int:
        """
        Returns the count of active autocompounding reward programs
        """
        return len(
            [
                self.autocompounding_programs[tkn_name]
                for tkn_name in self.whitelisted_tokens
                if self.autocompounding_programs[tkn_name].is_active
            ]
        )

    @property
    def active_autocompounding_programs(self) -> list:
        """
        Returns the active autocompounding reward programs
        """
        return [tkn_name for tkn_name in self.whitelisted_tokens if self.autocompounding_programs[tkn_name].is_active]

    @property
    def active_standard_programs(self) -> list:
        """
        Returns the active standard reward programs
        """
        return [tkn_name for tkn_name in self.whitelisted_tokens if self.standard_programs[tkn_name].is_active]

    @property
    def standard_programs_count(self) -> int:
        """
        Returns the count of active standard reward programs
        """
        return len(
            [
                self.standard_programs[tkn_name]
                for tkn_name in self.whitelisted_tokens
                if self.standard_programs[tkn_name].is_active
            ]
        )

    @property
    def bnt_price(self) -> Decimal:
        """
        Returns the bnt price feed at the current timestamp.
        """
        return Decimal(self.price_feeds.at[self.unix_timestamp, "bnt"])

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
                self.tokens["bnt"].staking_ledger.balance == 0
                and self.tokens["bnt"].pooltoken_supply.balance == 0
        ):
            bnbnt_rate = Decimal("1")
        else:
            bnbnt_rate = Decimal(
                self.tokens["bnt"].pooltoken_supply.balance / self.tokens["bnt"].staking_ledger.balance
            )
        return bnbnt_rate

    def add_user_to_standard_reward_providers(self, id: int, user_name: str):
        """
        Add a user to a given standard reward program providers list.
        """
        self.standard_programs[id].providers.append(user_name)

    def remove_user_from_standard_reward_program(self, id: int, user_name: str):
        """
        Remove a user from a given standard reward program providers list.
        """
        self.standard_programs[id].providers.remove(user_name)

    def set_standard_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Set standard rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].standard_rewards_vault.set(value)

    def set_user_pending_standard_rewards(self, user_name: str, id: int, value: Decimal):
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

    def increase_user_standard_rewards_stakes(self, id: int, user_name: str, value: Decimal):
        """
        Increase user standard rewards staked_reward_amt pooltokens by a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].staked_amt.add(value)

    def decrease_user_standard_rewards_stakes(self, id: int, user_name: str, value: Decimal):
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
        self.standard_programs[id].staked_reward_amt.add(value)

    def decrease_standard_reward_program_stakes(self, id: int, value: Decimal):
        """
        Decrease the standard reward program staked_reward_amt balance by a given amount.
        """
        self.standard_programs[id].staked_reward_amt.subtract(value)

    def set_standard_rewards_per_token(self, id: int, value: Decimal):
        """
        Set the standard reward program rewards per token.
        """
        self.standard_programs[id].reward_per_token.set(value)

    def set_standard_rewards_last_update_time(self, id: int, value: int):
        """
        Set the standard reward program last updated time.
        """
        self.standard_programs[id].last_update_time = value

    def set_provider_reward_per_token_paid(self, user_name: str, id: int, value: Decimal):
        """
        Set the user's rewards per token paid for a given program.
        """
        self.users[user_name].pending_standard_rewards[id].reward_per_token_paid.set(value)

    def set_provider_pending_standard_rewards(self, user_name: str, id: int, value: Decimal):
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
        self.standard_programs[id].end_time = value

    def set_standard_program_is_active(self, id: int, value: bool):
        """
        Set the is_active status of a standard program.
        """
        self.standard_programs[id].is_active = value

    def set_tkn_trading_liquidity(self, tkn_name: str, value: Decimal):
        """
        Set the tkn_trading_liquidity balance to a given amount.
        """
        self.tokens[tkn_name].tkn_trading_liquidity.set(value)

    def set_prev_token_amt_distributed(self, tkn_name: str, value: Decimal):
        """
        Set the prev_token_amt_distributed to a given value.
        """
        self.autocompounding_programs[tkn_name].prev_token_amt_distributed.set(value)

    def set_is_trading_enabled(self, tkn_name: str, value: bool):
        """
        Set the set_is_trading_enabled to a given status.
        """
        self.tokens[tkn_name].is_trading_enabled = value

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

    def set_user_balance(self, tkn_name: str, user_name: str, value: Decimal):
        """
        Set the user balance to a given amount.
        """
        self.users[user_name].wallet[tkn_name].set(value)

    def set_pooltoken_balance(self, tkn_name: str, value: Decimal):
        """
        Set the staked_reward_amt balance to a given amount.
        """
        self.tokens[tkn_name].pooltoken_supply.set(value)

    def set_standard_remaining_rewards(self, id: int, value: Decimal):
        """
        Set the remaining_rewards balance to a given amount.
        """
        self.standard_programs[id].remaining_rewards.set(value)

    def set_autocompounding_remaining_rewards(self, tkn_name: str, value: Decimal):
        """
        Set the remaining_rewards balance to a given amount.
        """
        self.autocompounding_programs[tkn_name].remaining_rewards.set(value)

    def set_token_amt_to_distribute(self, tkn_name: str, value: Decimal):
        """
        Set the token_amt_to_distribute balance to a given amount.
        """
        self.autocompounding_programs[tkn_name].token_amt_to_distribute.set(value)

    def set_program_is_active(self, tkn_name: str, value: bool):
        """
        Set the rewards is_active flag to a given status.
        """
        self.autocompounding_programs[tkn_name].is_active = value

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
            self.users[user_name] = UserState(user_name=user_name)
            for tkn_name in self.whitelisted_tokens:
                self.users[user_name].wallet[tkn_name] = Token(balance=Decimal("0"))
                self.users[user_name].wallet[get_pooltoken_name(tkn_name)] = Token(
                    balance=Decimal("0")
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
        return len(self.standard_programs) + 1

    class Config:
        validate_assignment = True


def get_unclaimed_rewards(state: State, tkn_name: str) -> Decimal:
    """
    Returns the rewards vault balance for a given tkn_name.
    """
    return state.tokens[tkn_name].standard_rewards_vault.balance


def get_total_standard_rewards_staked(state, id: int) -> Decimal:
    """
    Returns the total standard rewards staked_reward_amt for a given program id.
    """
    providers = [state.users[user_name] for user_name in state.standard_programs[id].providers]
    return sum([provider.pending_standard_rewards[id].staked_reward_amt.balance for provider in providers])


def get_tkn_virtual_balance(state: State, tkn_name: str) -> Decimal:
    """
    Return the reciprocal of the price of bnt or tkn.
    """
    return Decimal("1") / get_tkn_price(state, tkn_name)


def get_virtual_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns bnt_virtual_balance / tkn_token_virtual_balance
    """
    return get_bnt_virtual_balance(state, tkn_name) / get_tkn_virtual_balance(
        state, tkn_name
    )


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
    return state.tokens[tkn_name].staking_ledger.balance


def get_vault_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current balance of the master master_vault for a given tkn_name.
    """
    return state.tokens[tkn_name].master_vault.balance


def get_bnt_trading_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The current bnt trading liquidity for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_trading_liquidity.balance


def get_standard_reward_providers(state: State, id: int) -> list:
    """
    Get the standard reward providers for a given program id.
    """
    return state.standard_programs[id].providers


def get_standard_reward_tkn_name(state: State, id: int) -> Tuple[str, str]:
    """
    Get the standard reward tkn_name for a given id.
    """
    return state.standard_programs[id].tkn_name, state.standard_programs[id].rewards_token


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


def get_user_pending_rewards_staked_balance(state: State, id: int, user_name: str) -> Decimal:
    return state.users[user_name].pending_standard_rewards[id].staked.balance


def get_user_pending_standard_rewards(state: State, id: int, user_name: str) -> Decimal:
    return state.users[user_name].pending_standard_rewards[id].pending_rewards.balance


def get_user_reward_per_token_paid(state: State, id: int, user_name: str) -> Decimal:
    return state.users[user_name].pending_standard_rewards[id].reward_per_token_paid.balance


def get_user_wallet_tokens(state: State, user_name: str) -> list:
    """
    List of all tokens for a given user.
    """
    return [state.users[user_name].wallet[tkn_name].balance for tkn_name in state.whitelisted_tokens if
            state.users[user_name].wallet[tkn_name].balance > 0]


def get_tkn_trading_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The current tkn trading liquidity for a given tkn_name.
    """
    return state.tokens[tkn_name].tkn_trading_liquidity.balance


def get_bnt_funding_amt(state: State, tkn_name: str) -> Decimal:
    """
    The current bnt amount funded for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_funding_amt.balance


def get_external_protection_vault(state: State, tkn_name: str) -> Decimal:
    """
    The current external protection master_vault balance for a given tkn_name.
    """
    return state.tokens[tkn_name].external_protection_vault.balance


def get_pooltoken_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current erc20 contracts staked_amt supply for a given tkn_name.
    """
    return state.tokens[tkn_name].pooltoken_supply.balance


def get_protocol_wallet_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current protocol owned liquidity (when tkn_name==bnt) or the current autocompounding rewards remaining.
    """
    return state.tokens[tkn_name].protocol_wallet_pooltokens.balance


def get_vortex_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current vortex_ledger balance for a given tkn_name.
    """
    return state.tokens[tkn_name].vortex_ledger.balance


def get_user_balance(state: State, tkn_name: str, user_name: str) -> Decimal:
    """
    The current external protection master_vault balance for a given tkn_name.
    """
    return state.users[user_name].wallet[tkn_name].balance


def get_total_rewards(state: State, tkn_name: str) -> Decimal:
    """
    The initial balance for a given autocompounding rewards program.
    """
    return state.autocompounding_programs[tkn_name].total_rewards.balance


def get_distribution_type(state: State, tkn_name: str) -> str:
    """
    The type of distribution for an autocompounding rewards program (either flat or exponential "exp")
    """
    return state.autocompounding_programs[tkn_name].distribution_type


def get_prev_token_amt_distributed(state: State, tkn_name: str) -> Decimal:
    """
    The previous distribution amount for a given autocompounding rewards program.
    """
    return state.autocompounding_programs[tkn_name].prev_token_amt_distributed.balance


def get_autocompounding_start_time(state: State, tkn_name: str) -> int:
    """
    The start time for a given autocompounding rewards program.
    """
    return state.autocompounding_programs[tkn_name].start_time


def get_half_life_seconds(state: State, tkn_name: str) -> Decimal:
    """
    The half life in seconds for a given autocompounding rewards program.
    """
    return state.autocompounding_programs[tkn_name].half_life_seconds


def get_unix_timestamp(state: State) -> int:
    """
    The current state timestamp.
    """
    return state.unix_timestamp


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
    return state.autocompounding_programs[tkn_name].flat_distribution_rate_per_second


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
    return len(state.withdrawal_ids)


def get_tkn_price(state: State, tkn_name: str) -> Decimal:
    """
    Gets the tkn price from the price feed.
    """
    return (
        state.tokens[tkn_name].balance
        if tkn_name == "vbnt"
        else Decimal(state.price_feeds.at[state.unix_timestamp, tkn_name])
    )


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
            state.tokens[name].bnt_trading_liquidity.balance
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
    return max(state.erc20contracts_bnbnt, user_bnt)


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


def get_program(
        state: State, program_id: str
) -> StandardProgramState or AutocompoundingProgramState:
    """
    Pre-parses the dataclass for convenience and clarity
    """
    return state.standard_reward_programs[program_id]


def get_provider(state: State, provider_id: str) -> UserState:
    """
    Pre-parses the dataclass for convenience and clarity
    """
    return state.users[provider_id]


def get_program_and_provider_state(
        state: State, provider_id: str, program_id: str
) -> Tuple[StandardProgramState or AutocompoundingProgramState, UserState]:
    """
    Gets pre-parsed dataclasses for convenience and clarity
    """
    return get_program(state, program_id), get_provider(state, provider_id)


def set_program(
        state: State,
        program: StandardProgramState or AutocompoundingProgramState,
        program_id: str,
) -> State:
    state.standard_reward_programs[program_id] = program
    return state


def set_provider(state: State, provider: UserState, provider_id: str) -> State:
    state.users[provider_id] = provider
    return state


def set_program_and_provider_state(
        state: State,
        provider_id: str,
        program_id: str,
        provider: UserState,
        program: StandardProgramState or AutocompoundingProgramState,
) -> State:
    """
    Updates the state with the new program state and provider state.
    """
    state = set_provider(state, provider, provider_id)
    state = set_program(state, program, program_id)
    return state


def check_if_program_enabled(start_time: int, end_time: int, unix_timestamp: int):
    return start_time <= unix_timestamp <= end_time


def get_dao_msig_init_pools_logging_inputs(state, tkn_name: str):
    return tkn_name, Decimal("0"), "Enable Trading (DAO msig)", "Protocol", state.transaction_id, state


def get_whitelist_token_logging_inputs(state: State, tkn_name: str):
    return tkn_name, Decimal("0"), f"whitelist_{tkn_name}", "NA", state.transaction_id, state


def get_create_user_logging_inputs(state: State, user_name: str) -> Tuple[str, Decimal, str, str, int, State]:
    return "NA", Decimal("0"), f"create_{user_name}", "NA", state.transaction_id, state


def check_pool_shutdown(state: State, tkn_name: str) -> bool:
    """
    Checks that the bnt_min_trading_liquidity threshold has not been breached.
    """
    trading_enabled = get_is_trading_enabled(state, tkn_name)
    bnt_min_liquidity = get_bnt_min_liquidity(state, tkn_name)
    bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
    if bnt_trading_liquidity < bnt_min_liquidity and trading_enabled:
        return True
    return False


def check_is_bootstrap_reqs_met(
        state: State, tkn_name: str, bootstrap_liquidity: Decimal
) -> bool:
    """
    CHecks if the bootstrap requirements are met for a given tkn_name.
    """
    vault_balance = get_vault_balance(state, tkn_name)
    return vault_balance >= bootstrap_liquidity


def compute_pooltoken_amt(state: State, tkn_name: str, tkn_amt: Decimal) -> Decimal:
    """
    Returns the pool_token_amt for a given tkn_name, tkn_amt.
    """
    staked_amt = get_staked_balance(state, tkn_name)
    pool_token_supply = get_pooltoken_balance(state, tkn_name)
    if staked_amt > 0:
        pool_token_amt = (lambda a, b, c: a * b / c)(
            pool_token_supply, tkn_amt, staked_amt
        )
    else:
        pool_token_amt = Decimal("0")
    return pool_token_amt


def compute_bntkn_amt(state: State, tkn_name: str, tkn_amt: Decimal) -> Decimal:
    return compute_bntkn_rate(state, tkn_name) * tkn_amt


def compute_bnbnt_amt(state: State, bnt_amt: Decimal) -> Decimal:
    return state.bnbnt_rate * bnt_amt


def compute_ema(
        last_spot: Decimal, last_ema: Decimal, alpha: Decimal = Decimal("0.2")
) -> Decimal:
    """
    Computes the ema as a lagging average only once per block, per pool.
    """
    return alpha * last_spot + (1 - alpha) * last_ema


def compute_bntkn_rate(state, tkn_name):
    """
    Computes the bntkn issuance rate for tkn deposits, based on the staking ledger and the current bntkn supply
    """
    pool_token_supply = get_pooltoken_balance(state, tkn_name)
    staked_tkn = get_staked_balance(state, tkn_name)
    if pool_token_supply == 0 and staked_tkn == 0:
        bntkn_rate = Decimal("1")
    else:
        bntkn_rate = pool_token_supply / staked_tkn
    return bntkn_rate


def compute_ema_deviation(
        new_ema: Decimal,
        new_ema_compressed_numerator: Decimal,
        new_ema_compressed_denominator: Decimal,
) -> Decimal:
    """
    Computes the deviation between these values as ema_rate/ema_compressed_rate.
    """
    return (
            new_ema
            * Decimal(new_ema_compressed_denominator)
            / Decimal(new_ema_compressed_numerator)
    )


def compute_changed_bnt_trading_liquidity(
        a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return a * (b + d * x * (1 - e)) / (b + x)
    elif direction == "bnt":
        return (a * (a + x) + d * (1 - e) * (a * x + x ** 2)) / (a + d * x)


def compute_changed_tkn_trading_liquidity(
        a: Decimal, b: Decimal, d: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return b + x
    elif direction == "bnt":
        return b * (a + d * x) / (a + x)


def compute_target_amt(
        a: Decimal, b: Decimal, d: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return a * x * (1 - d) / (b + x)
    elif direction == "bnt":
        return b * x * (1 - d) / (a + x)


def compute_bootstrap_rate(
        state, tkn_name: str, tkn_virtual_balance: Decimal
) -> Decimal:
    return get_bnt_virtual_balance(state, tkn_name) / tkn_virtual_balance


def compute_vault_tvl(vault_balance: Decimal, token_price: Decimal) -> Decimal:
    return vault_balance * token_price


def compute_max_tkn_deposit(
        vault_tvl: Decimal, target_tvl: Decimal, user_funds: Decimal
) -> Decimal:
    return max(target_tvl - vault_tvl, user_funds)


def format_json(val: Any, integer: bool = False, percentage: bool = False) -> Any:
    """
    Formats data when generating JSON test scenarios.
    """
    if integer:
        return str(val).replace("0E-18", "0", 10)
    elif percentage:
        return str(round(float(str(val)))).replace("0E-18", "0") + "%"
    else:
        if type(val) == dict:
            return val
        else:
            return str(val.quantize(QDECIMALS)).replace("0E-18", "0")


def enable_trading(state: State, tkn_name: str) -> State:
    """
    Enables trading if the minimum bnt equivalent of tkn exists to justify bootstrapping.
    """

    bootstrap_liquidity = get_tkn_bootstrap_liquidity(state, tkn_name)

    if check_is_bootstrap_reqs_met(state, tkn_name, bootstrap_liquidity):
        log = f"Bootstrap requirements met for {tkn_name}"
        print(log)
        state.logger.info(log)

        state.set_is_trading_enabled(tkn_name, True)

        tkn_virtual_balance = get_tkn_virtual_balance(state, tkn_name)
        bootstrap_rate = compute_bootstrap_rate(state, tkn_name, tkn_virtual_balance)
        state.set_initial_rates(tkn_name, bootstrap_rate)

        bnt_bootstrap_liquidity = get_bnt_bootstrap_liquidity(state, tkn_name)
        state.set_bnt_trading_liquidity(tkn_name, bnt_bootstrap_liquidity)
        state.set_bnt_funding_amt(tkn_name, bnt_bootstrap_liquidity)

        tkn_bootstrap_liquidity = get_tkn_bootstrap_liquidity(state, tkn_name)
        state.set_tkn_trading_liquidity(tkn_name, tkn_bootstrap_liquidity)

        state.set_protocol_wallet_balance("bnt", bnt_bootstrap_liquidity)

    return state


def dao_msig_init_pools(state: State, pools: list) -> State:
    """
    DAO msig initilizes new tokens to allow trading once specified conditions are met.
    """
    for token_name in pools:
        if token_name != "bnt":
            state = enable_trading(state, token_name)
    return state


def mint_protocol_bnt(state: State, tkn_amt: Decimal) -> State:
    """
    Handles adjustments to the system resulting from the v3 minting BNT.
    """
    bnbnt_amt = compute_bnbnt_amt(state, tkn_amt)
    state.increase_vault_bnt("bnt", tkn_amt)
    state.increase_pooltoken_balance("bnt", bnbnt_amt)
    state.increase_staked_bnt("bnt", tkn_amt)
    state.increase_protocol_wallet("bnt", bnbnt_amt)
    return state


def shutdown_pool(state: State, tkn_name: str) -> State:
    """
    Shutdown pool when the bnt_min_trading_liquidity threshold is breached.
    """

    bnt_trading_liquidity = state.tokens[tkn_name].bnt_trading_liquidity.balance
    bnbnt_renounced = compute_bnbnt_amt(state, bnt_trading_liquidity)

    # adjust balances
    state.decrease_staked_balance("bnt", bnt_trading_liquidity)
    state.decrease_vault_balance("bnt", bnt_trading_liquidity)
    state.decrease_pooltoken_balance("bnt", bnbnt_renounced)
    state.decrease_protocol_wallet_balance("bnt", bnbnt_renounced)
    state.decrease_bnt_funding_amt(tkn_name, bnt_trading_liquidity)

    # set balances
    state.set_is_trading_enabled(tkn_name, False)
    state.set_bnt_trading_liquidity(tkn_name, Decimal("0"))
    state.set_tkn_trading_liquidity(tkn_name, Decimal("0"))
    state.set_spot_rate(tkn_name, Decimal("0"))
    state.set_inv_spot_rate(tkn_name, Decimal("0"))
    state.set_ema_rate(tkn_name, Decimal("0"))
    return state


def compute_pool_depth_adjustment(
        state: State, tkn_name: str, case: str = "none"
) -> Tuple[str, Decimal, Decimal]:
    """
    Computes the quantities of bnt and tkn to add to the pool trading liquidity during a deposit.
    """
    bnt_increase = tkn_increase = Decimal("0")
    is_trading_enabled = get_is_trading_enabled(state, tkn_name)
    is_price_stable = get_is_price_stable(state, tkn_name)
    bnt_remaining_funding = get_bnt_remaining_funding(state, tkn_name)
    if is_trading_enabled and is_price_stable and bnt_remaining_funding > 0:
        avg_tkn_trading_liquidity = get_avg_tkn_trading_liquidity(state, tkn_name)
        tkn_excess = get_tkn_excess(state, tkn_name)
        tkn_excess_bnt_equivalence = get_tkn_excess_bnt_equivalence(state, tkn_name)
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)

        if (
                avg_tkn_trading_liquidity <= tkn_excess
                and bnt_trading_liquidity <= bnt_remaining_funding
        ):
            case = "case1"
            bnt_increase = bnt_trading_liquidity
            tkn_increase = avg_tkn_trading_liquidity

        elif (
                avg_tkn_trading_liquidity <= tkn_excess
                and bnt_trading_liquidity > bnt_remaining_funding
                or avg_tkn_trading_liquidity > tkn_excess
                and tkn_excess_bnt_equivalence >= bnt_remaining_funding
        ):
            case = "case2"
            bnt_increase = bnt_remaining_funding
            tkn_increase = bnt_remaining_funding / state.tokens[tkn_name].ema_rate

        elif (
                tkn_excess < avg_tkn_trading_liquidity
                and bnt_trading_liquidity <= bnt_remaining_funding
                or avg_tkn_trading_liquidity > tkn_excess
                and bnt_trading_liquidity
                > bnt_remaining_funding
                > tkn_excess_bnt_equivalence
        ):
            case = "case3"
            bnt_increase = tkn_excess_bnt_equivalence
            tkn_increase = tkn_excess

        else:
            raise ValueError("Something went wrong, pool adjustment case not found...")

    return case, bnt_increase, tkn_increase


def vortex_collection(
        a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return a * d * e * x / (b + x)
    elif direction == "bnt":
        return d * e * x * (a + x) / (a + d * x)


def swap_fee_collection(
        a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the swap fees according to the swap algorithm.
    """
    if direction == "tkn":
        return a * d * x * (1 - e) / (b + x)
    elif direction == "bnt":
        return b * d * x * (1 - e) / (a + x)


def external_protection(
        bnt_trading_liquidity,
        average_tkn_trading_liquidity,
        withdrawal_fee,
        bnt_sent_to_user,
        external_protection_tkn_balance,
        tkn_withdraw_value,
        tkn_sent_to_user,
        trading_enabled,
):
    """
    This replaces any BNT that would have been received by the user with TKN.
    """
    a = bnt_trading_liquidity
    b = average_tkn_trading_liquidity
    n = withdrawal_fee
    T = bnt_sent_to_user
    w = external_protection_tkn_balance
    x = tkn_withdraw_value
    S = tkn_sent_to_user

    if not trading_enabled:
        bnt_sent_to_user = Decimal("0")
        external_protection_compensation = min(w, x * (1 - n) - S)

    elif T and w:
        if T * b > w * a:
            bnt_sent_to_user = (T * b - w * a) / b
            external_protection_compensation = w
        else:
            bnt_sent_to_user = Decimal("0")
            external_protection_compensation = T * b / a
    else:
        bnt_sent_to_user = T
        external_protection_compensation = Decimal("0")
    return bnt_sent_to_user, external_protection_compensation


def init_protocol(
        state: State,
        whitelisted_tokens: List[str],
        usernames: List[str],
        cooldown_time: int,
        network_fee: Decimal,
        trading_fee: Decimal,
        bnt_min_liquidity: Decimal,
        bnt_funding_limit: Decimal,
        withdrawal_fee: Decimal,
) -> State:
    """
    Initialize user wallets upon system genesis.
    """

    for tkn_name in whitelisted_tokens:
        if tkn_name not in state.whitelisted_tokens:
            state.create_whitelisted_tkn(tkn_name)

    for tkn_name in whitelisted_tokens:

        # Get tokens not yet initialized.
        if tkn_name not in state.tokens:
            # initialize tokens
            state.tokens[tkn_name] = TokenState(
                whitelisted_tokens=whitelisted_tokens,
                active_users=usernames,
                cooldown_time=cooldown_time,
                network_fee=network_fee,
                trading_fee=trading_fee,
                bnt_min_liquidity=bnt_min_liquidity,
                bnt_funding_limit=bnt_funding_limit,
                withdrawal_fee=withdrawal_fee,
            )

    for usr in usernames:

        # Get users not yet initialized.
        if usr not in state.usernames:
            # initialize users.
            state.create_user(usr)

    state.whitelisted_tokens = whitelisted_tokens
    state.active_users = usernames
    return state


def init_json_simulation(state: State) -> State:
    """This method uploads a pre-formatted JSON file containing simulation modules to run and report on."""

    tkn_name = [tkn for tkn in state.whitelisted_tokens if tkn != "bnt"][0]

    if len(state.json_export["users"]) == 0:
        state.json_export["tradingFee"] = format_json(
            state.trading_fee, percentage=True
        )
        state.json_export["networkFee"] = format_json(
            state.network_fee, percentage=True
        )
        state.json_export["withdrawalFee"] = format_json(
            state.withdrawal_fee, percentage=True
        )
        state.json_export["epVaultBalance"] = format_json(
            state.tokens[tkn_name].external_protection_vault.balance
        )

        if tkn_name in state.standard_reward_programs:
            state.json_export["tknRewardsamt"] = format_json(
                state.standard_reward_programs[tkn_name].total_staked.balance
            )
            state.json_export["tknRewardsDuration"] = format_json(
                state.standard_reward_programs[tkn_name].end_time, integer=True
            )
            state.json_export["bntRewardsamt"] = format_json(
                state.standard_reward_programs["bnt"].total_staked.balance
            )
            state.json_export["bntRewardsDuration"] = format_json(
                state.standard_reward_programs["bnt"].end_time, integer=True
            )

        state.json_export["tknDecimals"] = format_json(state.decimals, integer=True)
        state.json_export["bntMinLiquidity"] = format_json(state.bnt_min_liquidity)
        state.json_export["bntFundingLimit"] = format_json(state.bnt_funding_limit)
        users = []
        for user_name in state.usernames:
            user = {}
            user["id"] = user_name
            for tkn_name in state.whitelisted_tokens:
                user[f"{tkn_name}Balance"] = format_json(
                    state.users[user_name].wallet[tkn_name].balance
                )
            users.append(user)

        state.json_export["users"] = users
    return state


def handle_logging(
        tkn_name: str,
        tkn_amt: Decimal,
        action_name: str,
        user_name: str,
        transaction_id: int,
        state: State,
) -> State:
    """
    Logs the system state history after each action.
    """
    state.iter_transaction_id = transaction_id
    for tkn_name in state.whitelisted_tokens:
        state_variables = {
            "unix_timestamp": [state.unix_timestamp],
            "latest_action": [action_name],
            "latest_amt": [tkn_amt],
            "latest_user_name": [user_name],
            "tkn_name": [tkn_name],
            "vault_tkn": [get_vault_balance(state, tkn_name)],
            "erc20contracts_bntkn": [get_pooltoken_balance(state, tkn_name)],
            "staked_tkn": [get_staked_balance(state, tkn_name)],
            "is_trading_enabled": [get_is_trading_enabled(state, tkn_name)],
            "bnt_trading_liquidity": [get_bnt_trading_liquidity(state, tkn_name)],
            "tkn_trading_liquidity": [get_tkn_trading_liquidity(state, tkn_name)],
            "trading_fee": [get_trading_fee(state, tkn_name)],
            "bnt_funding_limit": [get_bnt_funding_limit(state, tkn_name)],
            "bnt_remaining_funding": [get_bnt_remaining_funding(state, tkn_name)],
            "bnt_funding_amt": [get_bnt_funding_amt(state, tkn_name)],
            "external_protection_vault": [
                get_external_protection_vault(state, tkn_name)
            ],
            "spot_rate": [get_spot_rate(state, tkn_name)],
            "ema_rate": [get_ema_rate(state, tkn_name)],
            "ema_descale": [state.tokens[tkn_name].ema_descale],
            "ema_compressed_numerator": [
                state.tokens[tkn_name].ema_compressed_numerator
            ],
            "ema_compressed_denominator": [
                state.tokens[tkn_name].ema_compressed_denominator
            ],
            "ema_deviation": [state.tokens[tkn_name].ema_deviation],
            "ema_last_updated": [state.tokens[tkn_name].ema_last_updated],
            "network_fee": [state.network_fee],
            "withdrawal_fee": [state.withdrawal_fee],
            "bnt_min_liquidity": [state.bnt_min_liquidity],
            "cooldown_time": [state.cooldown_time],
            "protocol_wallet_bnbnt": [get_protocol_wallet_balance(state, "bnt")],
            "vortex_bnt": [get_vortex_balance(state, "bnt")],
            "erc20contracts_bnbnt": [get_pooltoken_balance(state, "bnt")],
            "vault_bnt": [get_vault_balance(state, "bnt")],
            "staked_bnt": [get_staked_balance(state, "bnt")],
            "bnbnt_rate": [state.bnbnt_rate],
        }
        state.history.append(pd.DataFrame(state_variables))
    return state


def handle_vandalism_attack(state: State, tkn_name):
    """
    Checks if a vandalism attack has occured and adjusts the system state accordingly.
    """
    staked_tkn = get_staked_balance(state, tkn_name)
    bntkn = get_pooltoken_balance(state, tkn_name)
    if staked_tkn > 0 and bntkn == 0:
        state.set_staked_balance(tkn_name, Decimal("0"))
        state.shutdown_pool(tkn_name)
    return state


def handle_ema(state: State, tkn_name: str) -> State:
    """
    Handles the updating of the ema_rate, called before a swap is performed.
    """
    last_spot = get_spot_rate(state, tkn_name)
    last_ema = get_ema_rate(state, tkn_name)
    update_allowed = get_is_ema_update_allowed(state, tkn_name)
    if update_allowed:
        new_ema = compute_ema(last_spot, last_ema)
        state.tokens[tkn_name].ema_last_updated = state.tokens[tkn_name].unix_timestamp
        state.tokens[tkn_name].ema_rate = new_ema
        state.logger.info(f"EMA updated | old EMA = {last_ema} | new EMA = {new_ema}")
    return state


def describe_rates(state: State, qdecimals: Decimal, report={}) -> pd.DataFrame:
    """
    Return a dataframe of the current system EMA & spot rates.
    """
    for tkn in state.whitelisted_tokens:
        if state.tokens[tkn].spot_rate == Decimal(0):
            state.tokens[tkn].spot_rate = state.tokens[tkn].ema_rate
        report[tkn] = get_rate_report(state, tkn, qdecimals)
    return pd.DataFrame(report).T.reset_index()


def describe(state: State, rates: bool = False, decimals=6) -> pd.DataFrame:
    """
    Builds a dataframe of the current system/ledger state.
    """
    qdecimals = Decimal(10) ** -decimals
    if rates:
        return describe_rates(state, decimals=qdecimals)

    description = get_description(state, qdecimals)
    max_rows = max([len(description[key]) for key in description])

    # fill-in the description spacing for display purposes
    for col in description:
        while len(description[col]) < max_rows:
            description[col].append("")

    return pd.DataFrame(description)


def get_autocompounding_remaining_rewards(state: State, tkn_name: str) -> Decimal:
    """
    Get the remaining rewards for a given program.
    """
    return state.autocompounding_programs[tkn_name].remaining_rewards.balance


def get_remaining_standard_rewards(state: State, id: int) -> Decimal:
    """
    Get the remaining rewards for a given program.
    """
    return state.standard_programs[id].remaining_rewards.balance


def get_standard_program(state: State, tkn_name: str) -> Decimal:
    """
    Get the remaining rewards for a given program.
    """
    return state.autocompounding_programs[tkn_name].remaining_rewards.balance


def get_emulator_expected_results(
        state: State,
        tkn_name: str,
        tkn_amt: Decimal,
        transaction_type: str,
        user_name: str,
        unix_timestamp: int) -> dict:
    """
    Get the expected results for a given transaction.
    """
    json_operation = build_json_operation(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)
    return json_operation['expected']


def build_json_operation(
        state: State,
        tkn_name: str,
        tkn_amt: Decimal,
        transaction_type: str,
        user_name: str,
        unix_timestamp: int,
) -> dict:
    if "tkn" in state.autocompounding_programs:
        program_wallet_bntkn = get_protocol_wallet_balance(state, tkn_name)
        tkn_remaining_rewards = get_autocompounding_remaining_rewards(state, tkn_name)
    else:
        program_wallet_bntkn = Decimal("0")
        tkn_remaining_rewards = Decimal("0")

    if "bnt" in state.autocompounding_programs:
        bnt_remaining_rewards = get_autocompounding_remaining_rewards(state, "bnt")
    else:
        bnt_remaining_rewards = Decimal("0")

    if "tkn" in state.standard_reward_programs:
        er_vault_tkn = state.tokens[tkn_name].protocol_wallet_pooltokens.balance
    else:
        er_vault_tkn = Decimal("0")

    if "bnt" in state.autocompounding_programs:
        er_vault_bnt = state.tokens["bnt"].protocol_wallet_pooltokens.balance
    else:
        er_vault_bnt = Decimal("0")

    if "User" not in state.users:
        print("User not found, therefore JSON export will not be created.")
        return {}

    json_operation = {
        "type": transaction_type,
        "userId": user_name,
        "elapsed": unix_timestamp,
        "amt": format_json(tkn_amt) if str(tkn_amt) != "NA" else tkn_amt,
        "expected": {
            "tknBalances": {
                "User": format_json(get_user_balance(state, tkn_name, user_name)),
                "masterVault": format_json(get_vault_balance(state, tkn_name)),
                "erVault": format_json(er_vault_tkn),
                "epVault": format_json(get_external_protection_vault(state, tkn_name)),
            },
            "bntBalances": {
                "User": format_json(get_user_balance(state, "bnt", user_name)),
                "masterVault": format_json(get_vault_balance(state, "bnt")),
                "erVault": format_json(er_vault_bnt),
            },
            "bntknBalances": {
                "User": format_json(
                    get_user_balance(state, f"bn{tkn_name}", user_name)
                ),
                "TKNProgramWallet": format_json(program_wallet_bntkn),
            },
            "bnbntBalances": {
                "User": format_json(get_user_balance(state, "bnbnt", user_name)),
                "bntPool": format_json(get_protocol_wallet_balance(state, "bnt")),
            },
            "tknRewardsRemaining": format_json(tkn_remaining_rewards),
            "bntRewardsRemaining": format_json(bnt_remaining_rewards),
            "bntCurrentPoolFunding": format_json(get_bnt_funding_amt(state, tkn_name)),
            "tknStakedBalance": format_json(get_staked_balance(state, tkn_name)),
            "bntStakedBalance": format_json(get_staked_balance(state, "bnt")),
            "tknTradingLiquidity": format_json(
                get_tkn_trading_liquidity(state, tkn_name)
            ),
            "bntTradingLiquidity": format_json(
                get_bnt_trading_liquidity(state, tkn_name)
            ),
            "averageRateN": format_json(
                state.tokens[tkn_name].ema.numerator, integer=True
            ),
            "averageRateD": format_json(
                state.tokens[tkn_name].ema.denominator, integer=True
            ),
            "averageInvRateN": format_json(
                state.tokens[tkn_name].inv_ema.numerator, integer=True
            ),
            "averageInvRateD": format_json(
                state.tokens[tkn_name].inv_ema.denominator, integer=True
            ),
        },
    }
    return json_operation


def log_json_operation(state, transaction_type, user_name, amt, unix_timestamp):
    """Logs the latest operation for json testing."""

    tkn_name = [tkn for tkn in state.whitelisted_tokens if tkn != "bnt"][0]
    json_operation = build_json_operation(
        state, tkn_name, amt, transaction_type, user_name, unix_timestamp
    )

    if transaction_type == "createAutocompoundingRewardProgramTKN":
        json_operation["amt"] = {}
        json_operation["amt"]["tknRewardsTotalamt"] = format_json(
            state.autocompounding_programs["tkn"].total_rewards
        )
        json_operation["amt"]["tknRewardsStartTime"] = format_json(
            state.autocompounding_programs["tkn"].start_time, integer=True
        )
        json_operation["amt"]["tknRewardsType"] = str(
            state.autocompounding_programs["tkn"].distribution_type
        )
        json_operation["amt"]["tknHalfLifeInDays"] = format_json(
            state.autocompounding_programs["tkn"].half_life_days, integer=True
        )

    if transaction_type == "createAutocompoundingRewardProgramBNT":
        state.json_export["bntRewardsTotalamt"] = format_json(
            state.autocompounding_programs["bnt"].total_rewards
        )
        state.json_export["bntRewardsStartTime"] = format_json(
            state.autocompounding_programs["bnt"].start_time, integer=True
        )
        state.json_export["bntRewardsType"] = str(
            state.autocompounding_programs["bnt"].distribution_type
        )
        state.json_export["bntHalfLifeInDays"] = format_json(
            state.autocompounding_programs["bnt"].half_life_days, integer=True
        )

    return json_operation


def validate_input(
        state: State,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        unix_timestamp: int = None,
):
    """
    Validates the input for all agent actions.
    """

    try:
        tkn_name = tkn_name.lower()
    except ValueError("tkn_name must be type String") as e:
        print(e)

    try:
        tkn_amt = Decimal(tkn_amt)
    except ValueError("tkn_amt must be convertable to type Decimal") as e:
        print(e)

    try:
        wallet_test = state.users[user_name].wallet
    except ValueError(
            "user_name not found. Create a new user by calling the .create_user(user_name) method"
    ) as e:
        print(e)

    if unix_timestamp is not None:
        state.unix_timestamp = unix_timestamp
        state.tokens[tkn_name].unix_timestamp = unix_timestamp
    else:
        state.unix_timestamp = 0
        state.tokens[tkn_name].unix_timestamp = 0

    return state
