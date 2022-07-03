---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.7
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Data Structures

The following data structures are built with [pydantic dataclass](https://pydantic-docs.helpmanual.io/usage/dataclasses/) objects.

*Note*: The definitions below are ordered topologically to facilitate execution of the BIP15 spec.

## Misc dependencies

### `Config`

Global dataclass config settings inherited by all dataclasses.

```python
class Config:
    validate_assignment = True
    arbitrary_types_allowed = True
```

### `GlobalSettings`

```python
@dataclass(config=Config)
class GlobalSettings:
    """
    Represents the default global settings. These can be overridden by the BancorNetwork configuration upon instantiation.
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
```

### `Cooldown`

```python
@dataclass(config=Config)
class Cooldown:
    """
    Represents a pending withdrawal cooldown state.
    """
    id: int
    created_at: int
    user_name: str
    tkn_name: str
    is_complete: bool
    tkn: Any = field(default_factory=Token)
    pooltoken: Any = field(default_factory=Token)
```

### `StandardProgram`

```python
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
```

### `AutocompoundingProgram`

```python
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
        return self.total_rewards.balance.quantize(DEFAULT_QDECIMALS) / self.total_duration_in_seconds

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
```

### `UserStandardProgram`

```python
@dataclass(config=Config)
class UserStandardProgram:
    """
    Represents a standard reward program user state
    """
    id: int
    staked_amt: Any = field(default_factory=Token)
    pending_rewards: Any = field(default_factory=Token)
    reward_per_token_paid: Any = field(default_factory=Token)

```

### `User`

```python
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
```

### `Tokens`

```python
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
        return self.bnt_funding_limit - self.bnt_funding_amt.balance.quantize(DEFAULT_QDECIMALS)

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
            self.bnt_trading_liquidity.balance.quantize(DEFAULT_QDECIMALS) / self.ema_rate
            if self.ema_rate > 0
            else 0
        )

    @property
    def tkn_excess(self):
        """
        The difference between the master_vault balance and the average trading liquidity.
        """
        return self.master_vault.balance.quantize(DEFAULT_QDECIMALS) - self.avg_tkn_trading_liquidity

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
```

## System State

### `State`

```python
@dataclass(config=Config)
class State(GlobalSettings):
    """
    Represents the system state at the current timestamp. Main interface for all other dataclasses.
    """
    transaction_id: int = 0
    timestamp: int = DEFAULT_TIMESTAMP
    price_feeds: PandasDataFrame = None
    whitelisted_tokens: list = field(default_factory=list)
    tokens: Dict[str, Tokens] = field(
        default_factory=lambda: defaultdict(Tokens)
    )
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
        return [tkn_name for tkn_name in self.autocompounding_reward_programs if
                self.autocompounding_reward_programs[tkn_name].is_active]

    @property
    def active_standard_programs(self) -> list:
        """
        Returns the active standard reward programs
        """
        return [tkn_name for tkn_name in self.whitelisted_tokens if self.standard_reward_programs[tkn_name].is_active]

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
                and self.tokens["bnt"].pooltoken_supply.balance.quantize(DEFAULT_QDECIMALS) == 0
        ):
            bnbnt_rate = Decimal("1")
        else:
            bnbnt_rate = Decimal(
                self.tokens["bnt"].pooltoken_supply.balance.quantize(DEFAULT_QDECIMALS) / self.tokens[
                    "bnt"].staking_ledger.balance.quantize(DEFAULT_QDECIMALS)
            )
        return bnbnt_rate
```
