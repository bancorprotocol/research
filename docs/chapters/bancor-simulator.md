# Bancor Simulator

<p align="center">
<img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
</p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

**Bancor Simulator** is an open-source python package developed by the **Bancor Research Team**. It aims to assist the design, testing, and validation of Bancor v3 tokenomics.

See [official documentation](https://simulator.bancor.network/chapters/bancor-research.html) for complete details.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
**Warning**: This documentation is a work in progress with potentially broken links, unfinished sections, and commands for including code segments. Moreover, the entirety of the codebase and documentation is subject to change without warning.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


## Introduction

All state transition functions and accompanying data structures described in the product specification [BIP15: Proposing Bancor 3](https://docs.google.com/document/d/11UeMYaI_1CWdf_Nu6veUO-vNB5uX-FcVRqTSU-ziDRk/edit?usp=sharing) are the core system level operations of this library. 

## Organization

This is the project directory structure:

```
bancor_analytics/            <------- Tableau Dashboard Project
bancor_emulator/             <------- Solidity Emulation Project
bancor_simulator/            <------- ** Spec & Simulation Project **
├── v3/                      <------- Current Version
│   └── simulation/          <------- Agent-based simulation module
│   │     └── agents.py      <------- Mesa Agent-based implementations of the Bancor protocol.
│   │     └── batch_run.py   <------- Script used to perform a parameter sweep.
│   │     └── model.py       <------- Main Bancor Simulation module interface.
│   │     └── random_walk.py <------- Generalized behavior for random walking
│   │     └── run.py         <------- Runs the simulation server with browser-based UI
│   │     └── server.py      <------- Configures the browser-based interface.
│   │     └── utils.py       <------- Misc utility functions
│   │ 
│   └── spec/                <------- State transition functions and data structures described in BIP15.
│         └── actions.py     <------- Deposit, trade, & withdrawal algorithm logic.
│         └── emulation.py   <------- Verifies solidity result parity.
│         └── network.py     <------- Main BancorDapp application interface.
│         └── rewards.py     <------- Autocompounding and standard rewards logic.
│         └── state.py       <------- State variables, constants, data structures, and CRUD interfaces.
│         └── utils.py       <------- Misc utility functions
│ 
└── main.py                  <------- Application

** These docs apply.
```

## Notation

Code snippets appearing in `this style` are to be interpreted as Python 3 code.

## Formatting & Style

Code is formatted according to [PEP8](https://peps.python.org/pep-0008/), which is the official Python style guide. In order to overcome the burden on the developers to fix formatting, we use [Black](https://black.readthedocs.io/en/stable/) which reports on format errors and automatically fixes them.

## Types

### Standard Types

Python `decimals.Decimal(precision=155)`is used for all floating-point values for reason of obtaining theoretical accuracy. After a theoretical result is produced, the emulator module provides a python-based solidity contract replica result in order to assess any fixed-point math and/or other implementation deviations.

### Custom Types

We define the following Python custom types for type hinting and readability:

| Name | Type | Description |
| - | - | - |
| `Epoch` | `int64` | an epoch number |

## Constants

### Non-Configurable Constants

The following values are (non-configurable) constants used throughout the specification.

```
MODEL = "Bancor Network"
VERSION = "1.0.0"
GENESIS_EPOCH = Epoch(0)
SECONDS_PER_DAY = 86400
MAX_UINT112 = 2 ** 112 - 1
PRECISION = 155
```

### Configurable Genesis Variables

The following values are (configurable) genesis variables used throughout the specification.

*Note*: Where applicable, the default values correspond to those used in BIP15 examples, or are otherwise expected to be those values which are actually implemented on the Bancor dApp.

```
DEFAULT_TIMESTAMP = 0
DEFAULT_WHITELIST = ["dai", "eth", "link", "bnt", "tkn", "wbtc"]
DEFAULT_USERS = ["alice", "bob", "charlie", "trader", "user", "protocol"]
DEFAULT_DECIMALS = 18
DEFAULT_QDECIMALS = Decimal(10) ** -DEFAULT_DECIMALS
DEFAULT_PRICE_FEEDS_PATH = "https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.parquet"
DEFAULT_EXP_DECAY_DISTRIBUTION = 1
DEFAULT_FLAT_DISTRIBUTION = 0
DEFAULT_WITHDRAWAL_FEE = Decimal('0.002')
DEFAULT_TRADING_FEE = Decimal('0.0025')
DEFAULT_NETWORK_FEE = Decimal('0.0025')
DEFAULT_BNT_FUNDING_LIMIT = Decimal('1000000')
DEFAULT_BNT_MIN_LIQUIDITY = Decimal('10000')
DEFAULT_COOLDOWN_TIME = 604800
DEFAULT_ALPHA = Decimal("0.2").quantize(DEFAULT_QDECIMALS)
DEFAULT_LOWER_EMA_LIMIT = Decimal("0.99").quantize(DEFAULT_QDECIMALS)
DEFAULT_UPPER_EMA_LIMIT = Decimal("1.01").quantize(DEFAULT_QDECIMALS)
DEFAULT_NUM_TIMESTAMPS = SECONDS_PER_DAY * 30
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
```

## Misc dependencies

### `Token`

The following object represents token values in the system. Supported operations include **add, subtract, and set** which are anologous to **credit, debit, and overwrite** in traditional book-keeping parlance.

```python
class Token(object):
    """
    Represents a token balance with common math operations to increase, decrease, and set the balance.
    """

    def __init__(self, balance: Decimal = Decimal('0'), qdecimals: Decimal = DEFAULT_QDECIMALS):
        self.balance = balance
        self.qdecimals = qdecimals

    def add(self, value: Decimal):
        self.balance += self.validate(value)

    def subtract(self, value: Decimal):
        self.balance -= self.validate(value)

    def set(self, value: Decimal):
        self.balance = self.validate(value)

    def validate(self, value) -> Decimal:
        return Decimal(str(value)).quantize(self.qdecimals)
```

## Data Structures

The following data structures are built with [pydantic dataclass](https://pydantic-docs.helpmanual.io/usage/dataclasses/) objects.

*Note*: The definitions below are ordered topologically to facilitate execution of the BIP15 spec.

### Misc dependencies

#### `Config`

Global dataclass config settings inherited by all dataclasses.

```python
class Config:
    validate_assignment = True
    arbitrary_types_allowed = True
```

#### `GlobalSettings`

```python
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
```

#### `Cooldown`

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

#### `StandardProgram`

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

#### `AutocompoundingProgram`

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

#### `UserStandardProgram`

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

#### `User`

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

#### `Tokens`

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

### System State

#### `State`

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


## State Helper (CRUD) Functions

### Get Values

These functions get the current state variable value.

* `get_autocompounding_remaining_rewards(state, tkn_name)`
* `get_autocompounding_start_time(state, tkn_name)`
* `get_avg_tkn_trading_liquidity(state, tkn_name)`
* `get_bnbnt_rate(state, tkn_name)`
* `get_bnt_bootstrap_liquidity(state, tkn_name)`
* `get_bnt_funding_amt(state, tkn_name)`
* `get_bnt_funding_limit(state, tkn_name)`
* `get_bnt_min_liquidity(state, tkn_name)`
* `get_bnt_remaining_funding(state, tkn_name)`
* `get_bnt_trading_liquidity(state, tkn_name)`
* `get_bnt_virtual_balance(state, tkn_name)`
* `get_description(state, tkn_name)`
* `get_distribution_type(state, tkn_name)`
* `get_ema_last_updated(state, tkn_name)`
* `get_ema_rate(state, tkn_name)`
* `get_external_protection_description(state, tkn_name)`
* `get_external_protection_vault(state, tkn_name)`
* `get_flat_distribution_rate_per_second(state, tkn_name)`
* `get_half_life_seconds(state, tkn_name)`
* `get_inv_spot_rate(state, tkn_name)`
* `get_is_ema_update_allowed(state, tkn_name)`
* `get_is_price_stable(state, tkn_name)`
* `get_is_trading_enabled(state, tkn_name)`
* `get_json_virtual_balances(state, tkn_name)`
* `get_max_bnt_deposit(state, tkn_name)`
* `get_network_fee(state, tkn_name)`
* `get_pooltoken_balance(state, tkn_name)`
* `get_pooltoken_description(state, tkn_name)`
* `get_pooltoken_name(state, tkn_name)`
* `get_prev_token_amt_distributed(state, tkn_name)`
* `get_prices(state, tkn_name)`
* `get_protocol_wallet_balance(state, tkn_name)`
* `get_protocol_wallet_description(state, tkn_name)`
* `get_rate_report(state, tkn_name)`
* `get_remaining_standard_rewards(state, tkn_name)`
* `get_spot_rate(state, tkn_name)`
* `get_staked_balance(state, tkn_name)`
* `get_staking_description(state, tkn_name)`
* `get_standard_program(state, tkn_name)`
* `get_standard_reward_end_time(state, tkn_name)`
* `get_standard_reward_last_update_time(state, tkn_name)`
* `get_standard_reward_per_token(state, tkn_name)`
* `get_standard_reward_providers(state, tkn_name)`
* `get_standard_reward_rate(state, tkn_name)`
* `get_standard_reward_start_time(state, tkn_name)`
* `get_standard_reward_tkn_name(state, tkn_name)`
* `get_timestamp(state, tkn_name)`
* `get_tkn_bootstrap_liquidity(state, tkn_name)`
* `get_tkn_excess(state, tkn_name)`
* `get_tkn_excess_bnt_equivalence(state, tkn_name)`
* `get_tkn_price(state, tkn_name)`
* `get_tkn_trading_liquidity(state, tkn_name)`
* `get_tkn_virtual_balance(state, tkn_name)`
* `get_total_bnt_trading_liquidity(state, tkn_name)`
* `get_total_holdings(state, user_name, tkn_name)`
* `get_total_rewards(state, tkn_name)`
* `get_total_standard_rewards_staked(state, tkn_name)`
* `get_trade_inputs(state, tkn_name)`
* `get_trading_fee(state, tkn_name)`
* `get_trading_liquidity_description(state, tkn_name)`
* `get_unclaimed_rewards(state, tkn_name)`
* `get_user_balance(state, user_name, tkn_name)`
* `get_user_pending_rewards_staked_balance(state, user_name, tkn_name)`
* `get_user_pending_standard_rewards(state, user_name, tkn_name)`
* `get_user_pending_withdrawals(state, user_name, tkn_name)`
* `get_user_reward_per_token_paid(state, user_name, tkn_name)`
* `get_user_wallet_tokens(state, user_name, tkn_name)`
* `get_usernames(state, tkn_name)`
* `get_vault_balance(state, tkn_name)`
* `get_vault_description(state, tkn_name)`
* `get_vault_tvl(state, tkn_name)`
* `get_virtual_rate(state, tkn_name)`
* `get_vortex_balance(state)`
* `get_vortex_description(state, tkn_name)`
* `get_whitelisted_tokens(state, tkn_name)`
* `get_withdrawal_id(state, tkn_name)`

 ### Example 

```
v3 = BancorDapp()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"

balance = get_user_balance(state, user_name, tkn_name)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

balance = get_user_balance(state, user_name, pooltoken_name)
```


### Modify State
The following methods provide an interface to modify `State`.

*Note:* For reason of readability and clarity, the following operations are handled by methods of the `State` class, whereas the above *get* operations above are handled by functions. Thus, we include the `state.` prefix for each method below, where typing is assumed `state: State`

### Set Values

 * `state.set_autocompounding_remaining_rewards(tkn_name, value)`
 * `state.set_bnt_funding_amt(tkn_name, value)`
 * `state.set_bnt_funding_limit(tkn_name, value)`
 * `state.set_bnt_trading_liquidity(tkn_name, value)`
 * `state.set_ema_rate(tkn_name, value)`
 * `state.set_initial_rates(tkn_name, value)`
 * `state.set_inv_spot_rate(tkn_name, value)`
 * `state.set_is_trading_enabled(tkn_name, value)`
 * `state.set_network_fee(tkn_name, value)`
 * `state.set_pending_withdrawals_status(tkn_name, value)`
 * `state.set_pooltoken_balance(tkn_name, value)`
 * `state.set_prev_token_amt_distributed(tkn_name, value)`
 * `state.set_program_is_active(tkn_name, value)`
 * `state.set_protocol_wallet_balance(tkn_name, value)`
 * `state.set_provider_pending_standard_rewards(tkn_name, value)`
 * `state.set_provider_reward_per_token_paid(tkn_name, value)`
 * `state.set_spot_rate(tkn_name, value)`
 * `state.set_staked_balance(tkn_name, value)`
 * `state.set_standard_program_end_time(tkn_name, value)`
 * `state.set_standard_program_is_active(tkn_name, value)`
 * `state.set_standard_remaining_rewards(tkn_name, value)`
 * `state.set_standard_rewards_last_update_time(tkn_name, value)`
 * `state.set_standard_rewards_per_token(tkn_name, value)`
 * `state.set_standard_rewards_vault_balance(tkn_name, value)`
 * `state.set_tkn_trading_liquidity(tkn_name, value)`
 * `state.set_token_amt_to_distribute(tkn_name, value)`
 * `state.set_trading_fee(tkn_name, value)`
 * `state.set_user_balance(user_name, tkn_name, value)`
 * `state.set_user_pending_standard_rewards(user_name, tkn_name, value)`
 * `state.set_user_standard_rewards_stakes(user_name, tkn_name, value)`
 * `state.set_vault_balance(tkn_name, value)`
 * `state.set_vbnt_burned(tkn_name, value)`
 * `state.set_vortex_balance(tkn_name, value)`
 * `state.set_withdrawal_fee(tkn_name, value)`
 
 ### Example 

```
v3 = BancorDapp()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"
value = 100

state.set_user_balance(user_name, tkn_name, value)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

state.set_user_balance(user_name, pooltoken_name, value)
```

### Decrease Values

 * `state.decrease_bnt_funding_amt(tkn_name, value)`
 * `state.decrease_bnt_trading_liquidity(tkn_name, value)`
 * `state.decrease_external_protection_balance(tkn_name, value)`
 * `state.decrease_pooltoken_balance(tkn_name, value)`
 * `state.decrease_protocol_wallet_balance(tkn_name, value)`
 * `state.decrease_staked_balance(tkn_name, value)`
 * `state.decrease_standard_reward_program_stakes(tkn_name, value)`
 * `state.decrease_standard_rewards_vault_balance(tkn_name, value)`
 * `state.decrease_tkn_trading_liquidity(tkn_name, value)`
 * `state.decrease_user_balance(user_name, tkn_name, value)`
 * `state.decrease_user_standard_rewards_stakes(user_name, tkn_name, value)`
 * `state.decrease_vault_balance(tkn_name, value)`
 * `state.decrease_vbnt_burned(tkn_name, value)`
 * `state.decrease_vortex_balance(tkn_name, value)`

### Example 

```
v3 = BancorDapp()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"

# Amount to be subtracted from the current state
value = 100         

state.decrease_user_balance(user_name, tkn_name, value)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

state.decrease_user_balance(user_name, pooltoken_name, value)
```

### Increase Values

 * `state.increase_bnt_funding_amt(tkn_name, value)`
 * `state.increase_bnt_trading_liquidity(tkn_name, value)`
 * `state.increase_external_protection_balance(tkn_name, value)`
 * `state.increase_pooltoken_balance(tkn_name, value)`
 * `state.increase_protocol_wallet_balance(tkn_name, value)`
 * `state.increase_staked_balance(tkn_name, value)`
 * `state.increase_standard_reward_program_stakes(tkn_name, value)`
 * `state.increase_standard_rewards_vault_balance(tkn_name, value)`
 * `state.increase_tkn_trading_liquidity(tkn_name, value)`
 * `state.increase_user_balance(user_name, tkn_name, value)`
 * `state.increase_user_standard_rewards_stakes(user_name, tkn_name, value)`
 * `state.increase_vault_balance(tkn_name, value)`
 * `state.increase_vbnt_burned(tkn_name, value)`
 * `state.increase_vortex_balance(tkn_name, value)`

### Example 

```
v3 = BancorDapp()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"

# Amount to be added to the current balance
value = 100         

state.increase_user_balance(user_name, tkn_name, value)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

state.increase_user_balance(user_name, pooltoken_name, value)
```


## Network

The `BancorDapp` class provides the top level interface through which the entire codebase is made to simulate real-world scenarios in a practical sense. An instance of this class is analogous to the **Environment** in common agent-oriented-programming jargon, and more practically, can be thought of like an instance of the **Bancor dApp** where Traders can perform trades, LPs can make deposits, withdraws, and participate in DAO votes which change the system's tuneable fee (and other) parameters. 

 * `v3.begin_cooldown`
 * `v3.burn`
 * `v3.claim_standard_rewards`
 * `v3.create_autocompounding_program`
 * `v3.create_user`
 * `v3.dao_msig_init_pools`
 * `v3.deposit`
 * `v3.describe`
 * `v3.describe_rates`
 * `v3.distribute_autocompounding_program`
 * `v3.export`
 * `v3.export_test_scenarios`
 * `v3.get_state`
 * `v3.join_standard_rewards`
 * `v3.leave_standard_rewards`
 * `v3.next_transaction`
 * `v3.revert_state`
 * `v3.set_state`
 * `v3.set_user_balance`
 * `v3.show_history`
 * `v3.trade`
 * `v3.update_state`
 * `v3.whitelist_token`
 * `v3.withdraw`
 * `v3.set_trading_fee`
 * `v3.set_network_fee`
 * `v3.set_withdrawal_fee`
 * `v3.set_bnt_funding_limit`

### Example 

```
v3 = BancorDapp()

tkn_name = 'wbtc'
value = .005

v3.set_trading_fee(tkn_name=tkn_name, value=value)
```

## Simulation

The library currently supports a limited random walker style simulation scenario.

### Parameter Sweeps (Batch Runs)
Parameters sweeps can be done via the [mesa](https://github.com/projectmesa/mesa) BatchRunner instance defined at the bottom of file *batch_run.py* in the simulation directory. This instance is for collecting data on parameter sweeps. It is not meant to be run with run.py, since run.py starts up a server for visualization, which isn't necessary for the BatchRunner. To run a parameter sweep, call batch_run.py in the command line from the project directory as follows:

```
python bancor_simulator/v3/simulation/batch_run.py
```

The BatchRunner is set up to collect step by step data of the model. It does this by collecting the DataCollector object in a model_reporter (i.e. the DataCollector is collecting itself every step).

The end result of the batch run will be a CSV file created in the same directory from which Python was run. The CSV file will contain the data from every step of every run.

### GUI Visualization (Single Runs)

To run the model interactively, run the following command from the project directory:
```
mesa runserver
```
Then open your browser to http://127.0.0.1:8521/, select the model parameters, press Reset, then Start.

