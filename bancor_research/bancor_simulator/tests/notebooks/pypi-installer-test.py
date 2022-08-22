# Databricks notebook source
# MAGIC %pip install bancor-research --force-reinstall --no-cache

# COMMAND ----------

from bancor_research.bancor_simulator.v3.spec.network import *


# COMMAND ----------

from bancor_research import Decimal, pd

bnt_min_liquidity: Decimal = Decimal("10000")
bnt_funding_limit: Decimal = Decimal("40000")
whitelisted_tokens: list = ["bnt", "eth", "wbtc", "link"]


# COMMAND ----------

# Recall from an earlier chapter that we already defined the cooldown period and the exit fees as follows.
cooldown_time: int = 7
iter_limit = 10000
withdrawal_fee: Decimal = Decimal("0.0025")
price_feeds = pd.DataFrame(
    {
        "INDX": [0 for i in range(iter_limit + 1)],
        "bnt": [2.5 for i in range(iter_limit + 1)],
        "link": [15.00 for i in range(iter_limit + 1)],
        "eth": [2500.00 for i in range(iter_limit + 1)],
        "wbtc": [40000.00 for i in range(iter_limit + 1)],
    }
)

network_fee: Decimal = Decimal("0.2")
trading_fee: Decimal = Decimal("0.01")

# There are other possible configuration settings available, however for the present purpose we will use the defaults.
v3 = BancorDapp(
    whitelisted_tokens=whitelisted_tokens,
    network_fee=network_fee,
    trading_fee=trading_fee,
    cooldown_time=cooldown_time,
    withdrawal_fee=withdrawal_fee,
    bnt_min_liquidity=bnt_min_liquidity,
    bnt_funding_limit=bnt_funding_limit,
    price_feeds=price_feeds,
)


# COMMAND ----------

v3.create_user("Alice")
v3.create_user("Bob")
v3.create_user("Charlie")

v3.set_user_balance(user_name="Alice", tkn_name="eth", tkn_amt=101)
v3.set_user_balance(user_name="Charlie", tkn_name="link", tkn_amt=10001)
v3.set_user_balance(user_name="Bob", tkn_name="wbtc", tkn_amt=101)

# COMMAND ----------

# Perform some test deposits.

v3.deposit(tkn_amt=100, tkn_name="eth", user_name="Alice")

v3.deposit(tkn_amt=10000, tkn_name="link", user_name="Charlie")

v3.deposit(tkn_amt=100, tkn_name="wbtc", user_name="Bob")

v3.describe()
