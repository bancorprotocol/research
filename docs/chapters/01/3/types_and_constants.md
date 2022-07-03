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

# Types and Constants

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
DEFAULT_PRICE_FEEDS = pd.DataFrame({'INDX': [0 for _ in range(100000)],
                                    'vbnt': [1.0 for _ in range(100000)],
                                    'tkn': [2.5 for _ in range(100000)],
                                    'bnt': [2.5 for _ in range(100000)],
                                    'link': [15.00 for _ in range(100000)],
                                    'eth': [2500.00 for _ in range(100000)],
                                    'wbtc': [40000.00 for _ in range(100000)]})
```

