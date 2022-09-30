# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""System state variables, constants, containers and interface."""
import copy, logging, pandas
from dataclasses import field
from pydantic.types import Tuple, Any, List, Dict
from pydantic.dataclasses import dataclass
from pydantic.schema import defaultdict

from bancor_research import DEFAULT, Decimal, PandasDataFrame

logger = logging.getLogger(__name__)


# Configurable Genesis Variables
DEFAULT_TIMESTAMP = DEFAULT.TIMESTAMP
DEFAULT_USERS = DEFAULT.USERS
DEFAULT_DECIMALS = DEFAULT.DECIMALS
DEFAULT_WITHDRAWAL_FEE = Decimal(DEFAULT.WITHDRAWAL_FEE[:-1]) / 100
DEFAULT_TRADING_FEE = Decimal(DEFAULT.TRADING_FEE[:-1]) / 100
DEFAULT_NETWORK_FEE = Decimal(DEFAULT.NETWORK_FEE[:-1]) / 100
DEFAULT_BNT_FUNDING_LIMIT = Decimal(DEFAULT.BNT_FUNDING_LIMIT)
DEFAULT_BNT_MIN_LIQUIDITY = Decimal(DEFAULT.BNT_MIN_LIQUIDITY)
DEFAULT_COOLDOWN_TIME = DEFAULT.COOLDOWN_TIME
DEFAULT_ALPHA = Decimal("0.2")
DEFAULT_LOWER_EMA_LIMIT = Decimal("0.99")
DEFAULT_UPPER_EMA_LIMIT = Decimal("1.01")
DEFAULT_ACCOUNT_BALANCE = Decimal("0")


# Misc dependencies for `State`
class Token(object):
    """
    Represents a token balance with common math operations to increase, decrease, and set the balance.
    """

    def __init__(self, balance: Decimal = Decimal("0")):
        self.balance = balance

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
        if pandas.isnull(self.balance):
            self.balance = Decimal("0")

    def validate_value(self, value) -> Decimal:
        if pandas.isnull(value):
            value = Decimal("0")
        return Decimal(str(value))


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
    whitelisted_tokens: dict = field(default_factory=dict)
    active_users: List[str] = field(default_factory=lambda: DEFAULT_USERS)
    cooldown_time: int = DEFAULT_COOLDOWN_TIME
    network_fee: Decimal = DEFAULT_NETWORK_FEE
    withdrawal_fee: Decimal = DEFAULT_WITHDRAWAL_FEE
    bnt_min_liquidity: Decimal = DEFAULT_BNT_MIN_LIQUIDITY
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


@dataclass(config=Config)
class AutocompoundingProgram:
    """
    Represents an autocompounding reward program state.
    """

    id: int
    created_at: int
    tkn_name: str
    distribution_type: str
    start_time: int
    total_duration: int = 0
    half_life: int = 0
    total_rewards: Any = field(default_factory=Token)
    remaining_rewards: Any = field(default_factory=Token)
    prev_token_amt_distributed: Any = field(default_factory=Token)
    is_active: bool = False
    is_enabled: bool = False

    @property
    def flat_distribution_rate_per_second(self):
        """
        Returns the rate per second of the distribution.
        """
        return self.total_rewards.balance / self.total_duration


@dataclass(config=Config)
class UserStandardProgram:
    """
    Represents a standard reward program user state
    """

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

    tkn_name: str = None
    decimals: int = DEFAULT_DECIMALS
    master_vault: Any = field(default_factory=Token)
    staking_ledger: Any = field(default_factory=Token)
    pooltoken_supply: Any = field(default_factory=Token)
    protocol_wallet_pooltokens: Any = field(default_factory=Token)
    vortex_ledger: Any = field(default_factory=Token)
    vbnt_burned: Any = field(default_factory=Token)
    external_protection_vault: Any = field(default_factory=Token)
    external_rewards_vault: Any = field(default_factory=Token)
    bnt_trading_liquidity: Any = field(default_factory=Token)
    tkn_trading_liquidity: Any = field(default_factory=Token)
    bnt_funding_amt: Any = field(default_factory=Token)
    spot_rate: Decimal = Decimal("0")
    ema_rate: Decimal = Decimal("0")
    inv_spot_rate: Decimal = Decimal("0")
    inv_ema_rate: Decimal = Decimal("0")
    ema_last_updated: Decimal = Decimal("0")
    is_trading_enabled: bool = False
    bnt_funding_limit: Decimal = DEFAULT_BNT_FUNDING_LIMIT
    trading_fee: Decimal = DEFAULT_TRADING_FEE

    @property
    def bnt_remaining_funding(self):
        """
        Computes the BNT funding remaining for the pool.
        """
        return self.bnt_funding_limit - self.bnt_funding_amt.balance

    @property
    def is_price_stable(self):
        """
        True if the spot price deviation from the EMA is less than 1% (or other preset threshold amount).
        """
        # changed due to contract implementation
        # should probably use `ema_rate` and `inv_ema_rate` instead
        ema_rate = self.updated_ema_rate
        inv_ema_rate = self.updated_inv_ema_rate
        return (
            DEFAULT_LOWER_EMA_LIMIT * ema_rate
            <= self.spot_rate
            <= DEFAULT_UPPER_EMA_LIMIT * ema_rate
            and DEFAULT_LOWER_EMA_LIMIT * inv_ema_rate
            <= self.inv_spot_rate
            <= DEFAULT_UPPER_EMA_LIMIT * inv_ema_rate
        )

    @property
    def updated_ema_rate(self) -> Decimal:
        """
        Computes the ema as a lagging average only once per block, per pool.
        """
        return self.alpha * self.spot_rate + (1 - self.alpha) * self.ema_rate

    @property
    def updated_inv_ema_rate(self) -> Decimal:
        """
        Computes the inverse ema as a lagging average only once per block, per pool.
        """
        return self.alpha * self.inv_spot_rate + (1 - self.alpha) * self.inv_ema_rate

    @property
    def bnt_bootstrap_liquidity(self):
        """
        Computes the minimum between bnt_min_liquidity multiplied by 2 and bnt_funding_limit.
        """
        return min(2 * self.bnt_min_liquidity, self.bnt_funding_limit)

    @property
    def vbnt_price(self):
        """
        Returns the price of the current vbnt token. Only valid when name==bnt
        """
        assert (
            self.tkn_name == "bnt"
        ), f"vbnt_price attempted to be accessed in {self.tkn_name} state, call bnt state instead"
        return self._vbnt_price


@dataclass(config=Config)
class State(GlobalSettings):
    """
    Represents the system state at the current timestamp. Main interface for all other dataclasses.
    """

    transaction_id: int = 0
    price_feeds: PandasDataFrame = None
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
    whitelisted_tokens: dict = field(default_factory=dict)
    rolling_trade_fees: dict = field(default_factory=dict)

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
            for tkn_name in self.standard_reward_programs
            if self.standard_reward_programs[tkn_name].is_active
        ]

    @property
    def standard_programs_count(self) -> int:
        """
        Returns the count of active standard reward programs
        """
        return len(self.active_standard_programs())

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
        pooltoken_supply = self.tokens["bnt"].pooltoken_supply.balance
        staking_ledger = self.tokens["bnt"].staking_ledger.balance
        if pooltoken_supply != staking_ledger:
            return Decimal(pooltoken_supply) / Decimal(staking_ledger)
        return Decimal("1")

    def step(self):
        """
        Incriments the current timestamp.
        """
        self.timestamp += 1

    def set_external_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Set external rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].external_rewards_vault.set(value)

    def map_user_standard_program(self, user_name: str, id: int):
        """
        Map a user standard program if needed.
        """
        if id not in self.users[user_name].pending_standard_rewards:
            self.users[user_name].pending_standard_rewards[id] = UserStandardProgram()

    def set_user_pending_standard_rewards(
        self, user_name: str, id: int, value: Decimal
    ):
        """
        Set standard rewards vault balance by a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].pending_rewards.set(value)

    def increase_external_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Increase external rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].external_rewards_vault.add(value)

    def decrease_external_rewards_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease external rewards vault balance by a given amount.
        """
        self.tokens[tkn_name].external_rewards_vault.subtract(value)

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
        self.standard_reward_programs[id].staked_reward_amt.add(value)

    def decrease_user_standard_rewards_stakes(
        self, id: int, user_name: str, value: Decimal
    ):
        """
        Increase user standard rewards staked_reward_amt pooltokens by a given amount.
        """
        self.users[user_name].pending_standard_rewards[id].staked_amt.subtract(value)
        self.standard_reward_programs[id].staked_reward_amt.subtract(value)

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

    def decrease_master_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Decrease master_vault balance by a given amount.
        """
        self.tokens[tkn_name].master_vault.subtract(value)

    def increase_master_vault_balance(self, tkn_name: str, value: Decimal):
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
        self.tokens[tkn_name].external_protection_vault.subtract(value)

    def increase_external_protection_balance(self, tkn_name: str, value: Decimal):
        """
        Increase external protection balance by a given amount.
        """
        self.tokens[tkn_name].external_protection_vault.add(value)

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

    def set_vault_balance(self, tkn_name: str, value: Decimal):
        """
        Set master vault balance.
        """
        self.tokens[tkn_name].master_vault.set(value)

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

    def set_bnt_min_liquidity(self, tkn_name: str, value: Decimal):
        """
        Set the min trading liquidity for a given tkn_name.
        """
        self.tokens[tkn_name].bnt_min_liquidity = value

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
        Set the spot rate to a given value.
        """
        self.tokens[tkn_name].spot_rate = value

    def set_ema_rate(self, tkn_name: str, value: Decimal):
        """
        Set the ema rate to a given amount.
        """
        self.tokens[tkn_name].ema_rate = value

    def set_inv_spot_rate(self, tkn_name: str, value: Decimal):
        """
        Set the inverse spot rate to a given value.
        """
        self.tokens[tkn_name].inv_spot_rate = value

    def set_inv_ema_rate(self, tkn_name: str, value: Decimal):
        """
        Set the inverse ema rate to a given value.
        """
        self.tokens[tkn_name].inv_ema_rate = value

    def set_bnt_funding_amt(self, tkn_name: str, value: Decimal):
        """
        Set the bnt_funding_amt to a given status.
        """
        self.tokens[tkn_name].bnt_funding_amt.set(value)

    def set_initial_rates(self, tkn_name: str, bootstrap_rate: Decimal):
        self.tokens[tkn_name].spot_rate = bootstrap_rate
        self.tokens[tkn_name].ema_rate = bootstrap_rate
        self.tokens[tkn_name].inv_spot_rate = bootstrap_rate**-1
        self.tokens[tkn_name].inv_ema_rate = bootstrap_rate**-1

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

    def set_user_balance(self, user_name: str, tkn_name: str, value: Decimal):
        """
        Set the user balance to a given amount.
        """
        self.users[user_name].wallet[tkn_name].set(value)

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

    def set_pending_withdrawals_status(
        self, user_name: str, id_number: int, status: bool
    ):
        """
        Set pending_withdrawal to a given status.
        """
        self.users[user_name].pending_withdrawals[id_number].is_complete = status

    def create_whitelisted_tkn(self, tkn_name: str):
        """
        Adds a new tkn_name to the whitelisted_tokens
        """
        if tkn_name not in self.whitelisted_tokens:
            self.whitelisted_tokens[tkn_name] = {
                "decimals": 18,
                "trading_fee": DEFAULT_TRADING_FEE,
                "bnt_funding_limit": DEFAULT_BNT_FUNDING_LIMIT,
                "ep_vault_balance": DEFAULT.EP_VAULT_BALANCE,
            }
        return self

    def create_user(self, user_name: str):
        """
        Creates a new system user agent.
        """
        if user_name not in self.users:
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
        if "bnt" not in self.users[user_name].wallet:
            self.users[user_name].wallet["bnt"] = Token(balance=DEFAULT_ACCOUNT_BALANCE)
        if "vbnt" not in self.users[user_name].wallet:
            self.users[user_name].wallet["vbnt"] = Token(
                balance=DEFAULT_ACCOUNT_BALANCE
            )
        return self

    def update_spot_rate(self, tkn_name: str):
        """
        Updates the spot rate and the inverse spot rate.
        """
        bnt_trading_liquidity = get_bnt_trading_liquidity(self, tkn_name)
        tkn_trading_liquidity = get_tkn_trading_liquidity(self, tkn_name)
        if bnt_trading_liquidity == 0 and tkn_trading_liquidity == 0:
            spot_rate = Decimal(0)
            inv_spot_rate = Decimal(0)
        else:
            spot_rate = bnt_trading_liquidity / tkn_trading_liquidity
            inv_spot_rate = tkn_trading_liquidity / bnt_trading_liquidity
        self.set_spot_rate(tkn_name, spot_rate)
        self.set_inv_spot_rate(tkn_name, inv_spot_rate)

    def next_standard_program_id(self) -> int:
        """
        Returns the next standard program ID.
        """
        return len(self.standard_reward_programs) + 1

    def copy(self):
        return copy.deepcopy(self)


def get_total_standard_rewards_staked(state, id: int) -> Decimal:
    """
    Returns the total standard rewards staked_reward_amt for a given program id.
    """
    return state.standard_reward_programs[id].staked_reward_amt.balance


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
    return state.tokens[tkn_name].staking_ledger.balance


def get_master_vault_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current balance of the master_vault for a given tkn_name.
    """
    return state.tokens[tkn_name].master_vault.balance


def get_bnt_trading_liquidity(state: State, tkn_name: str) -> Decimal:
    """
    The current bnt trading liquidity for a given tkn_name.
    """
    return state.tokens[tkn_name].bnt_trading_liquidity.balance


def get_standard_reward_pool_token_name(state: State, id: int) -> str:
    """
    Get the standard reward pool token name for a given id.
    """
    return get_pooltoken_name(state.standard_reward_programs[id].tkn_name)


def get_standard_reward_per_token(state: State, id: int) -> Decimal:
    """
    Get the standard reward per token for a given id.
    """
    return state.standard_reward_programs[id].reward_per_token.balance


def get_standard_reward_end_time(state: State, id: int) -> int:
    """
    Get the standard reward end time for a given id.
    """
    return state.standard_reward_programs[id].end_time


def get_standard_reward_start_time(state: State, id: int) -> int:
    """
    Get the standard reward start time for a given id.
    """
    return state.standard_reward_programs[id].start_time


def get_standard_reward_last_update_time(state: State, id: int) -> int:
    """
    Get the standard reward last update time for a given id.
    """
    return state.standard_reward_programs[id].last_update_time


def get_standard_reward_rate(state: State, id: int) -> int:
    """
    Get the standard reward rate for a given id.
    """
    return state.standard_reward_programs[id].reward_rate


def get_user_pending_rewards_staked_balance(
    state: State, id: int, user_name: str
) -> Decimal:
    return state.users[user_name].pending_standard_rewards[id].staked_amt.balance


def get_user_pending_standard_rewards(state: State, id: int, user_name: str) -> Decimal:
    return state.users[user_name].pending_standard_rewards[id].pending_rewards.balance


def get_user_reward_per_token_paid(state: State, id: int, user_name: str) -> Decimal:
    return (
        state.users[user_name]
        .pending_standard_rewards[id]
        .reward_per_token_paid.balance
    )


def get_bnt_per_tkn(state: State, tkn_name: str):
    tkn_price = get_tkn_price(state, tkn_name)
    bnt_price = get_tkn_price(state, "bnt")
    return tkn_price / bnt_price


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


def get_external_protection_vault_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current external protection vault balance for a given tkn_name.
    """
    return state.tokens[tkn_name].external_protection_vault.balance


def get_external_rewards_vault_balance(state: State, tkn_name: str) -> Decimal:
    """
    The current external rewards vault balance for a given tkn_name.
    """
    return state.tokens[tkn_name].external_rewards_vault.balance


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


def get_user_balance(state: State, user_name: str, tkn_name: str) -> Decimal:
    """
    The user balance for a given tkn_name.
    """
    return state.users[user_name].wallet[tkn_name].balance


def get_bnbnt_rate(state: State) -> Decimal:
    """
    The current bnbnt rate.
    """
    return state.bnbnt_rate


def get_total_rewards(state: State, tkn_name: str) -> Decimal:
    """
    The initial balance for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[tkn_name].total_rewards.balance


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
    ].prev_token_amt_distributed.balance


def get_autocompounding_start_time(state: State, tkn_name: str) -> int:
    """
    The start time for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[tkn_name].start_time


def get_half_life(state: State, tkn_name: str) -> int:
    """
    The half life for a given autocompounding rewards program.
    """
    return state.autocompounding_reward_programs[tkn_name].half_life


def get_timestamp(state: State) -> int:
    """
    The current state timestamp.
    """
    return state.timestamp


def get_avg_tkn_trading_liquidity(
    state: State, tkn_name: str, rate: Decimal
) -> Decimal:
    """
    The average trading liquidity for a given tkn_name.
    """
    return get_bnt_trading_liquidity(state, tkn_name) / rate


def get_updated_ema_rate(state: State, tkn_name: str) -> Decimal:
    """
    The ema as a lagging average only once per block, per pool.
    """
    if state.tokens[tkn_name].ema_last_updated == state.tokens[tkn_name].timestamp:
        return state.tokens[tkn_name].ema_rate
    return state.tokens[tkn_name].updated_ema_rate


def get_updated_inv_ema_rate(state: State, tkn_name: str) -> Decimal:
    """
    The inverse ema as a lagging average only once per block, per pool.
    """
    if state.tokens[tkn_name].ema_last_updated == state.tokens[tkn_name].timestamp:
        return state.tokens[tkn_name].inv_ema_rate
    return state.tokens[tkn_name].updated_inv_ema_rate


def get_tkn_excess_bnt_equivalence(
    state: State, tkn_name: str, rate: Decimal
) -> Decimal:
    """
    Returns the equivalent bnt value of the non-trading tkn balance of the master_vault.
    """
    return get_tkn_excess(state, tkn_name) * rate


def get_tkn_excess(state: State, tkn_name: str) -> Decimal:
    """
    The difference between the master_vault balance and the average trading liquidity.
    """
    return get_master_vault_balance(state, tkn_name) - get_tkn_trading_liquidity(
        state, tkn_name
    )


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
    Returns the spot rate for a given tkn_name.
    """
    return state.tokens[tkn_name].spot_rate


def get_ema_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns the ema rate for a given tkn_name.
    """
    return state.tokens[tkn_name].ema_rate


def get_inv_spot_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns the inverse spot rate for a given tkn_name.
    """
    return state.tokens[tkn_name].inv_spot_rate


def get_inv_ema_rate(state: State, tkn_name: str) -> Decimal:
    """
    Returns the inverse ema rate for a given tkn_name.
    """
    return state.tokens[tkn_name].inv_ema_rate


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
        state.tokens[tkn_name].vbnt_price
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
        f"Spot Rate={state.tokens[tkn_name].spot_rate}"
        f"EMA Rate={state.tokens[tkn_name].ema_rate}"
        f"Inverse Spot Rate={state.tokens[tkn_name].inv_spot_rate}"
        f"Inverse EMA Rate={state.tokens[tkn_name].inv_ema_rate}"
    ]


def get_trading_liquidity_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [
        f"bnt={get_bnt_trading_liquidity(state, tkn_name)} {tkn_name}="
        + str(get_tkn_trading_liquidity(state, tkn_name))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_master_vault_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnt={get_master_vault_balance(state, 'bnt')}"] + [
        f"{tkn_name}=" + str(get_master_vault_balance(state, tkn_name))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_staking_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnt={get_staked_balance(state, 'bnt')}"] + [
        f"{tkn_name}=" + str(get_staked_balance(state, tkn_name))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_pooltoken_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnbnt={get_pooltoken_balance(state, 'bnt')}"] + [
        f"bn{tkn_name}=" + str(get_pooltoken_balance(state, tkn_name))
        for tkn_name in state.whitelisted_tokens
        if tkn_name != "bnt"
    ]


def get_vortex_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return ["bnt=" + str(get_vortex_balance(state, "bnt"))] + [
        "" for x in range(len(state.whitelisted_tokens[:-1]))
    ]


def get_external_protection_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [
        f"{tkn_name}=" + str(get_external_protection_vault_balance(state, tkn_name))
        for tkn_name in state.whitelisted_tokens
    ]


def get_protocol_wallet_description(state: State, qdecimals: Decimal) -> list:
    """
    Builds a structured list for current state information display.
    """
    return [f"bnbnt=" + str(get_protocol_wallet_balance(state, "bnt"))] + [
        "" for tkn_name in state.whitelisted_tokens[:-1]
    ]


def get_description(state: State, qdecimals: Decimal) -> dict:
    """
    Builds a dictionary to be used as a description for current state information display.
    """
    return {
        "Trading Liquidity": get_trading_liquidity_description(state, qdecimals),
        "Vault": get_master_vault_description(state, qdecimals),
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
    Get the remaining rewards for a given auto-compounding program.
    """
    return state.autocompounding_reward_programs[tkn_name].remaining_rewards.balance


def get_standard_remaining_rewards(state: State, id: int) -> Decimal:
    """
    Get the remaining rewards for a given standard program.
    """
    return state.standard_reward_programs[id].remaining_rewards.balance
