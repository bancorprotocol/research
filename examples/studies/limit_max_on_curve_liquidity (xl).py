# Databricks notebook source
# MAGIC %md
# MAGIC # **Bancor Simulator - Demo & Tutorial**

# COMMAND ----------

# MAGIC %md
# MAGIC <p align="center">
# MAGIC <img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
# MAGIC </p>

# COMMAND ----------

# MAGIC %md
# MAGIC # Proposal: Limit on-curve liquidity to max(520 x 7 day fees, 100k BNT)
# MAGIC 
# MAGIC In the [Bancor Governance Forum](https://vote.bancor.network/), the BancorDAO (Decentralized Autonomous Organization) proposes and discusses token Whitelistings, Trading liquidity limits, Fee changes, Bancor Improvement Proposals, and others. To facilitate community participation, we have created this demo and tutorial notebook covering some relevant concepts for using the Bancor simulator for related analysis.
# MAGIC 
# MAGIC Please head on to the [Information and Templates](https://gov.bancor.network/c/information-and-templates/16) category for more information on the DAO process.
# MAGIC 
# MAGIC Voting happens on the [BancorDAO Snapshot Page](https://vote.bancor.network/).
# MAGIC 
# MAGIC The notebook presents an introduction to Bancor simulations, describing the structure and elements of the dataset(s), some relevant statistical properties, as well as running a baseline simulation and providing an example modified simulation model based on proposed changes discussed in **Proposal: Limit on-curve liquidity to max(520 x 7 day fees, 100k BNT)**.

# COMMAND ----------

# MAGIC %md
# MAGIC ## TLDR:
# MAGIC 
# MAGIC -   We pay IL on 100% of TKN available for trading
# MAGIC -   We get diminishing returns on new fees per unit of trading liquidity
# MAGIC -   If IL > fees then the protocol dies (and is already in crisis due to existing deficits)
# MAGIC -   B3 has the unique ability to set a cap on trading liquidity
# MAGIC -   Taking capital off-curve has a dual benefit of limiting IL exposure AND making it available to other revenue opportunities (native staking etc.)
# MAGIC -   Currently the protocol deficit increases when ETH price increases by ~1.5x annually relative to BNT, making some assumptions, we could lift this to the protocol being profitable up to a ~4x ETH annual moon relative to BNT by limiting the on-curve trading liquidity to 520x 7 day trading fees + implementing some modest staking model (or similar)
# MAGIC -   We should set a simple cap based on the data we have and commission a more sophisticated model in the near future

# COMMAND ----------

# MAGIC %md
# MAGIC ## Proposal:
# MAGIC 
# MAGIC When we look at the IL curve:
# MAGIC 
# MAGIC ![image](https://aws1.discourse-cdn.com/standard20/uploads/bancordao/optimized/2X/e/e0d10c4f716b77cc23de68cb160db8c6e9dc28e1_2_690x387.png)
# MAGIC 
# MAGIC 
# MAGIC We see that the losses due to IL are a % of all the capital deployed on the trading curve.
# MAGIC 
# MAGIC If TKN moons 2x relative to BNT then the IL is ~10%, a 4x moon has ~20% IL, etc.
# MAGIC 
# MAGIC Meanwhile there are only so many fees due to trade volume across all of defi and almost all trades through bancor currently are based on arbitrage and aggregators only. That is to say, there is negligible trading being done directly on bancor due to retail etc. as that market is largely monopolized by aggregators and a few platforms that take the lion's share of human traders such as uniswap.
# MAGIC 
# MAGIC In considering this proposal, please consider mainly how **arb bots and aggregators** will respond, not human traders, as the former is 10x+ the latter in terms of protocol fee generation.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dataset description:
# MAGIC 
# MAGIC Datasets:
# MAGIC   * **[price_feeds.csv](https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.csv)** - Dataset consists of token price feeds at daily resolution.
# MAGIC   * **[historical_actions.csv](https://bancorml.s3.us-east-2.amazonaws.com/historical_actions.csv)** - Dataset consists of Trade, Deposit, and Withdrawal actions performed on Bancor v3 since its launch in April.
# MAGIC   * **[fees_vs_liquidity.csv](https://bancorml.s3.us-east-2.amazonaws.com/fees_vs_liquidity.csv)** - Dataset consists of historical trading fees per token joined with on-curve liquidity snapshots.

# COMMAND ----------

# MAGIC %md
# MAGIC **Bancor Simulator** is an open-source python package developed by **Bancor Research**. It aims to assist the design, testing, and validation of Bancor v3 tokenomics.
# MAGIC 
# MAGIC See [official documentation](https://simulator.bancor.network/chapters/bancor-simulator.html) for complete details.
# MAGIC 
# MAGIC In order to run the simulation software described herein, follow the setup and installation instructions below.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Project setup
# MAGIC 
# MAGIC If you don't already have one, create a virtualenv
# MAGIC using [these instructions](https://docs.python.org/3/library/venv.html)
# MAGIC 
# MAGIC ## Install
# MAGIC 
# MAGIC **Bancor Research** is available for Python 3.6+
# MAGIC 
# MAGIC To install using [pypi](https://pypi.org/project/bancor-simulation/), run this command:
# MAGIC 
# MAGIC ````{tab} PyPI
# MAGIC $ pip install --upgrade bancor-research
# MAGIC ````
# MAGIC 
# MAGIC Note, if running this command inside a jupyter notebook, use this instead:
# MAGIC 
# MAGIC ````{tab} PyPI
# MAGIC $ ! pip install --upgrade bancor-research
# MAGIC ````

# COMMAND ----------

# MAGIC %pip install bancor-research --force-reinstall

# COMMAND ----------

# MAGIC %md
# MAGIC If you experience numpy related errors after installation, try reinstalling numpy as follows:

# COMMAND ----------

# MAGIC %pip install --upgrade numpy

# COMMAND ----------

# MAGIC %md
# MAGIC Import the dependencies we will use.

# COMMAND ----------

from bancor_research import DEFAULT
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.utils import shuffle
from decimal import Decimal
import pprint
import plotly.express as px
from bancor_research.bancor_simulator.v3.spec import get_is_trading_enabled, get_bnt_funding_limit, get_vault_balance, \
    get_staked_balance, get_tkn_trading_liquidity, get_bnt_trading_liquidity, get_ema_rate, get_tkn_price

from typing import Tuple, Any

from bancor_research.bancor_simulator.v3.spec import get_prices, State, get_bnt_trading_liquidity, \
    get_tkn_trading_liquidity, get_trading_fee, get_user_balance, get_is_trading_enabled, get_network_fee, get_ema_rate, \
    get_spot_rate, get_vault_balance, get_pooltoken_balance, get_staked_balance, get_external_protection_vault, \
    get_protocol_wallet_balance, get_vortex_balance, get_bnt_funding_limit, get_bnbnt_rate, get_max_bnt_deposit, \
    get_user_pending_withdrawals, Token, get_bnt_min_liquidity, get_is_price_stable, get_pooltoken_name
from bancor_research.bancor_simulator.v3.spec.actions import (
    unpack_withdrawal_cooldown,
    vortex_burner,
)
from bancor_research.bancor_simulator.v3.spec.network import BancorDapp
from bancor_research.bancor_simulator.v3.spec.utils import (
    compute_user_total_holdings,
    compute_ema,
    compute_bntkn_rate,
    compute_max_tkn_deposit,
    compute_vault_tkn_tvl, check_pool_shutdown, shutdown_pool,
)
import random

# COMMAND ----------

# MAGIC %md
# MAGIC Define the constants we will use:

# COMMAND ----------

default_trading_fee = '1%'
default_bnt_funding_limit = 1000000
target_tvl = Decimal("160000000")
pool_freq_dist = {}
whitelisted_tokens = {}
action_freq_dist = {}
historical_action_distribution_dic = {}
arbitrage_percentage = .99
bnt_min_liquidity = 20000
constant_multiplier = 520
n_periods = 7
price_feeds_path = 'https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.csv'
historical_actions_path = 'https://bancorml.s3.us-east-2.amazonaws.com/historical_actions.csv'
fees_vs_liquidity_path = 'https://bancorml.s3.us-east-2.amazonaws.com/fees_vs_liquidity.csv'
global_username = 'global user'

num_simulation_days = 90
num_timestamps_per_day = 60 * 24 # minutes / day (same resolution as price feeds)
save_results_path = f'/dbfs/FileStore/tables/research/limit_max_on_curve_liquidity_results_{constant_multiplier}_{n_periods}_{num_simulation_days}.csv'
save_results_path

# COMMAND ----------

# MAGIC %md
# MAGIC ## Loading the data

# COMMAND ----------

# MAGIC %md
# MAGIC Load the price feed data:

# COMMAND ----------

price_feeds = pd.read_csv(price_feeds_path)

for n in range(10):
    price_feeds = shuffle(price_feeds)
    
price_feeds['indx'] = [i for i in range(len(price_feeds))]
price_feeds

# COMMAND ----------

# MAGIC %md
# MAGIC Load the historical actions data:

# COMMAND ----------

historical_actions = pd.read_csv(historical_actions_path)
historical_actions

# COMMAND ----------

# MAGIC %md
# MAGIC Load the fees vs liquidity data and do some preprocessing:

# COMMAND ----------

fees_vs_liquidity = pd.read_csv(fees_vs_liquidity_path).drop('Unnamed: 0', axis=1)
fees_vs_liquidity['tknTradingLiquidity_real_bnt'] = fees_vs_liquidity['tknTradingLiquidity_real'] * fees_vs_liquidity['price']

# COMMAND ----------

# MAGIC %md
# MAGIC Find which tokens are included in all three datasets (we will focus on these in our simulations):

# COMMAND ----------

price_feed_tokens = price_feeds.T.reset_index().rename({'index':'tkn_name'}, axis=1)['tkn_name'].unique()
simulation_tokens = [tkn for tkn in historical_actions['poolSymbol'].unique() if tkn in price_feed_tokens]
print(simulation_tokens)

# COMMAND ----------

# MAGIC %md
# MAGIC Filter the actions to include only those we have price and liquidity data for:

# COMMAND ----------

historical_actions = historical_actions[historical_actions['poolSymbol'].isin(simulation_tokens)]

# COMMAND ----------

# MAGIC %md
# MAGIC Get the distribution of historical actions:

# COMMAND ----------

c = historical_actions.event_name.value_counts(dropna=False)
p = historical_actions.event_name.value_counts(dropna=False, normalize=True)
historical_action_distribution = pd.concat([c,p], axis=1, keys=['counts', '%'])
historical_action_distribution

# COMMAND ----------

# MAGIC %md
# MAGIC Get the distribution of all historical actions by token:

# COMMAND ----------

c = historical_actions.poolSymbol.value_counts(dropna=False)
p = historical_actions.poolSymbol.value_counts(dropna=False, normalize=True)
historical_action_tkn_distribution = pd.concat([c,p], axis=1, keys=['counts', '%'])
historical_action_tkn_distribution

# COMMAND ----------

# MAGIC %md
# MAGIC We can solve for a reasonable starting balance per token for a single global user as described in detail below.

# COMMAND ----------

user_initial_balances = historical_actions
user_initial_balances['user_id'] = [global_username for _ in range(len(user_initial_balances))]
user_initial_balances = historical_actions[
    ['user_id','poolSymbol','tokenAmount_real_usd']].groupby(['user_id','poolSymbol']).sum()
user_initial_balances = user_initial_balances.reset_index()
user_initial_balances = user_initial_balances[user_initial_balances['poolSymbol'].isin(simulation_tokens)]
user_initial_balances = user_initial_balances[user_initial_balances['tokenAmount_real_usd'] > 0]
user_initial_balances

# COMMAND ----------

# MAGIC %md
# MAGIC ## `MonteCarloGenerator` Simulation Setup

# COMMAND ----------

h = historical_action_distribution.reset_index()
h

# COMMAND ----------

# MAGIC %md
# MAGIC Create the `action_freq_dist` which tells the simulator how often it should randomly generate specific actions (e.g. trades, deposits, etc...). You can either manually specify these amounts, or use a data-based approach like we use here:

# COMMAND ----------

a = historical_action_distribution.reset_index()
all_actions = h['index'].unique()
for action in all_actions:
    action_freq_dist[action] = a[a['index']==action]['%'].values[0]
    
# Prints formatted action_freq_dist dictionary
pprint.pprint(action_freq_dist)

# COMMAND ----------

# MAGIC %md
# MAGIC Create the `pool_freq_dist` which tells the simulator how often it should randomly select specific pools (e.g. ETH, DAI, etc...) when performing an action. You can either manually specify this, or use a data-based approach like we use here. Note that in the loop below we're also building the `whitelisted_tokens` parameter which tells the simulator which pools to use as well as their initial `trading_fee` and `bnt_funding_limit` parameters.

# COMMAND ----------

d = historical_action_tkn_distribution.reset_index()
for tkn in simulation_tokens:
    pool_freq_dist[tkn] = d[d['index']==tkn]['%'].values[0]
    whitelisted_tokens[tkn] = {'trading_fee': default_trading_fee, 
                               'bnt_funding_limit': default_bnt_funding_limit, 
                               'decimals':18,
                               'ep_vault_balance': 0
                              }
    
# Prints formatted pool_freq_dist dictionary
pprint.pprint(pool_freq_dist)

# COMMAND ----------

# MAGIC %md
# MAGIC Print the formatted `whitelisted_tokens` dictionary for reference.

# COMMAND ----------

pprint.pprint(whitelisted_tokens)

# COMMAND ----------

# MAGIC %md
# MAGIC We can solve for the average number of events per day `mean_events_per_day`. This will tell us how often we should update the `bnt_funding_limit` parameter. Note: you can manually override this value to speed-up the simulation.

# COMMAND ----------

from datetime import datetime

date_time_str = '01/07/22 00:00:00'
date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
time = historical_actions.copy()
time['date'] = [datetime.strptime(str(i), '%Y-%m-%d') for i in pd.to_datetime(time['time']).dt.date.values]
time = time[time['date'] > date_time_obj]
mean_events_per_day = time.groupby('date').count()['event_name'].mean()

# mean_events_per_day = 50
print(f'mean_events_per_day={mean_events_per_day}')

# COMMAND ----------

# MAGIC %md
# MAGIC Below we set the `num_simulation_days` parameter in order to tell the simulator how long we want to run the simulation. The units of this are in `days` in order to allow us to convert the proposal's `rolling 7 day average trade fees` into some number of simulated actions.
# MAGIC 
# MAGIC Note that the simulator uses `timestamps` throughout the codebase. In the current simulation, every timestamp iteration corresponds to 1 action.

# COMMAND ----------

# MAGIC %md
# MAGIC The `simulation_step_count` specifies the number of sequential actions we will simulate. By our definitions above, this number of actions we would expect to see over a time period of `180 days` based on the average number of actions per day.

# COMMAND ----------

num_timesteps = num_simulation_days * num_timestamps_per_day
assert len(price_feeds) > num_timesteps, "the number of timesteps must be less than the length of the price feeds table"
simulation_actions_count = int(round(mean_events_per_day * num_simulation_days, 0))

print(simulation_actions_count, num_timesteps)

# COMMAND ----------

# MAGIC %md
# MAGIC The `transact(...)` function below is the main logic which specifies the Monte-Carlo transaction (deposit, trade, etc...) frequency distributions.

# COMMAND ----------

def transact(self, is_proposal):
    self.latest_amt = None
    self.latest_tkn_name = None
    self.user_name = global_username

    latest_action = None
    timestamp = self.timestamp
    
    i = self.random.randint(0, self.num_timesteps)
    
    deposit_range = self.simulation_actions_count * self.action_freq_dist['deposit']
    trade_range = deposit_range + self.simulation_actions_count * self.action_freq_dist['trade'] * (1 - arbitrage_percentage)
    arb_range = trade_range + self.simulation_actions_count * self.action_freq_dist['trade'] * arbitrage_percentage
    withdraw_initiated = arb_range + self.simulation_actions_count * self.action_freq_dist['withdraw_initiated']
    withdraw_completed = withdraw_initiated + self.simulation_actions_count * self.action_freq_dist['withdraw_completed']
    withdraw_canceled = withdraw_completed + self.simulation_actions_count * self.action_freq_dist['withdraw_canceled']
    withdraw_pending = withdraw_canceled + self.simulation_actions_count * self.action_freq_dist['withdraw_pending']

    if i < deposit_range:
        latest_action = "deposit"
        self.perform_random_deposit()

    elif deposit_range <= i < trade_range:
        latest_action = "trade"
        self.perform_random_trade()

    elif trade_range <= i < arb_range:
        latest_action = "arbitrage_trade"
        self.perform_random_arbitrage_trade()

    elif arb_range <= i < withdraw_initiated:
        latest_action = "cooldown"
        self.perform_random_begin_cooldown()

    elif withdraw_initiated <= i < withdraw_completed:
        latest_action = "withdrawal"
        self.perform_random_withdrawal()
        
    else:
        latest_action = "skip"
    
    if latest_action != 'skip':
        state = self.protocol.global_state
        state.timestamp = timestamp
        for tkn_name in self.whitelisted_tokens:
            if not get_is_trading_enabled(state, tkn_name):
                self.protocol.enable_trading(tkn_name=tkn_name, timestamp=timestamp)

        # The code below creates a new dataframe which collects the data we want to analyze about the simulation.
        df = {}
        df['timestamp'] = [timestamp]
        df['latest_action'] = [latest_action]
        df['latest_amt'] = [self.latest_amt]
        df['latest_tkn_name'] = [self.latest_tkn_name]
        total_def = Decimal('0')
        total_def_bnt = Decimal('0')
        total_def_usd = Decimal('0')

        for tkn in self.whitelisted_tokens:
            if tkn != 'bnt':
                ema_rate = get_ema_rate(state, tkn)
                bntprice = get_tkn_price(state, 'bnt')
                df[f'{tkn}_bnt_funding_limit'] = [get_bnt_funding_limit(state, tkn)]
                df[f'{tkn}_vault'] = [get_vault_balance(state, tkn)]
                df[f'{tkn}_staking'] = [get_staked_balance(state, tkn)]
                df[f'{tkn}_surplus'] = [df[f'{tkn}_vault'][0] - df[f'{tkn}_staking'][0]]
                df[f'{tkn}_surplus_bnt'] = [df[f'{tkn}_surplus'][0] * ema_rate]
                df[f'{tkn}_surplus_usd'] = [df[f'{tkn}_surplus_bnt'][0] * bntprice]
                total_def += df[f'{tkn}_surplus'][0]
                total_def_bnt += df[f'{tkn}_surplus_bnt'][0]
                total_def_usd += df[f'{tkn}_surplus_usd'][0]
                df[f'{tkn}_tkn_trading_liquidity'] = [get_tkn_trading_liquidity(state, tkn)]
                df[f'{tkn}_bnt_trading_liquidity'] = [get_bnt_trading_liquidity(state, tkn)]

        df[f'total_surplus'] = [total_def]
        df[f'total_surplus_bnt'] = [total_def_bnt]
        df[f'total_surplus_usd'] = [total_def_usd]
        df = pd.DataFrame(df)
        self.logger.append(df)

# COMMAND ----------

# MAGIC %md
# MAGIC Next we define a few helper functions which allow us to simulate specific actions.

# COMMAND ----------

def trade_tkn_to_ema(
        bnt_trading_liquidity: Decimal,
        tkn_trading_liquidity: Decimal,
        trading_fee: Decimal,
        network_fee: Decimal,
        future_ema: Decimal,
) -> Decimal:
    """
    Outputs the tkn_amt that should be traded to force the ema and the spot price together on a given pool.
    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    d = trading_fee
    e = network_fee
    f = future_ema
    tkn_amt = (
                      (a * d * (Decimal("1") - e) - Decimal("2") * f * b)
                      + (
                              a
                              * (
                                      Decimal("4") * f * b * (Decimal("1") - d * (Decimal("1") - e))
                                      + a * d ** Decimal("2") * (Decimal("1") - e) ** Decimal("2")
                              )
                      )
                      ** (Decimal("1") / Decimal("2"))
              ) / (Decimal("2") * f)
    return tkn_amt



def trade_bnt_to_ema(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        future_ema,
):
    """
    Analyze the state of any pool and create a swap that drives the ema and the spot price together.
    """

    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    d = trading_fee
    e = network_fee
    f = future_ema
    x = (
                -Decimal("2") * a
                + b * d * f
                + (
                        (Decimal("2") * a - b * d * f) ** Decimal("2")
                        - Decimal("4") * a * (a - b * f)
                )
                ** (Decimal("1") / Decimal("2"))
        ) / Decimal("2")
    a_recursion = (
                          a * (a + x) + d * (Decimal("1") - e) * (a * x + x ** Decimal("2"))
                  ) / (a + d * x)
    b_recursion = b * (a + d * x) / (a + x)
    n = 0
    p = Decimal("0.001")
    while a_recursion / b_recursion < f:
        n += 1
        p += Decimal("0.0001")
        x += x * (f ** p - (a_recursion / b_recursion) ** p) / f
        a_recursion = (
                              a * (a + x) + d * (Decimal("1") - e) * (a * x + x ** Decimal("2"))
                      ) / (a + d * x)
        b_recursion = b * (a + d * x) / (a + x)
        if n > 20000:
            break
    bnt_amt = x
    return bnt_amt

def process_arbitrage_trade(
        tkn_name: str,
        tkn_token_virtual_balance: Decimal,
        bnt_virtual_balance: Decimal,
        bnt_trading_liquidity: Decimal,
        tkn_trading_liquidity: Decimal,
        trading_fee: Decimal,
        user_tkn: Decimal,
        user_bnt: Decimal,
) -> Tuple[Decimal, str, str, bool]:
    """
    Computes the appropriate arbitrage trade on the tkn_name pool.
    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    m = trading_fee
    p = bnt_virtual_balance
    q = tkn_token_virtual_balance

    bnt_trade_amt = (
                            -Decimal("2") * a * q
                            + b * m * p
                            + (
                                    (Decimal("2") * a * q - b * m * p) ** Decimal("2")
                                    - Decimal("4") * a * q * (a * q - b * p)
                            )
                            ** (Decimal("1") / Decimal("2"))
                    ) / (Decimal("2") * q)

    tkn_trade_amt = (
                            -Decimal("2") * b * p
                            + a * m * q
                            + (
                                    (Decimal("2") * b * p - a * m * q) ** Decimal("2")
                                    - Decimal("4") * b * p * (b * p - a * q)
                            )
                            ** (Decimal("1") / Decimal("2"))
                    ) / (Decimal("2") * p)

    if bnt_trade_amt > 0:
        source_token = "bnt"
        target_token = tkn_name
        trade_amt = bnt_trade_amt
        user_capability = user_bnt > bnt_trade_amt
        return trade_amt, source_token, target_token, user_capability

    elif tkn_trade_amt > 0:
        source_token = tkn_name
        target_token = "bnt"
        trade_amt = tkn_trade_amt
        user_capability = user_tkn > tkn_trade_amt
        return trade_amt, source_token, target_token, user_capability

# COMMAND ----------

# MAGIC %md
# MAGIC Finally, we define the main logical class `MonteCarloGenerator` which we will use to run our simulation.

# COMMAND ----------

class MonteCarloGenerator(object):
    """
    Generates Monte Carlo scenarios.
    """

    def __init__(
            self,
            target_tvl: Decimal,
            whitelisted_tokens: dict,
            price_feed: pd.DataFrame,
            user_initial_balances: pd.DataFrame,
            simulation_actions_count: int,
            num_timesteps: int,
            pool_freq_dist: dict,
            action_freq_dist: dict,
            bnt_min_liquidity: Any = 10000,
            
    ):

        # all users/agents use a single BancorDapp instance
        v3 = BancorDapp(whitelisted_tokens=whitelisted_tokens,
                        bnt_min_liquidity=bnt_min_liquidity,
                        price_feeds=price_feed)

        # set the initial balances for each user.
        for user_id in user_initial_balances['user_id'].unique():
            v3.create_user(user_id)

            user_balances = user_initial_balances[user_initial_balances['user_id'] == user_id]
            for tkn_name in user_balances['poolSymbol'].unique():

                user_balance = user_balances[user_balances['poolSymbol'] == tkn_name]['tokenAmount_real_usd'].values[0]
                v3.set_user_balance(user_name=user_id, tkn_name=tkn_name, tkn_amt=user_balance, timestamp=0)

                pooltkn_name = get_pooltoken_name(tkn_name)
                if pooltkn_name not in v3.global_state.users[user_id].wallet:
                    v3.global_state.users[user_id].wallet[pooltkn_name] = Token(
                        balance=Decimal('0')
                    )

        self.protocol = v3
        self.random = random
        self.logger = []
        self.timestamp = 0
        self.target_tvl = target_tvl
        self.simulation_actions_count = simulation_actions_count
        self.whitelisted_tokens = whitelisted_tokens
        self.daily_trade_volume = 0
        self.latest_amt = 0
        self.latest_tkn_name = None
        self.rolling_trade_fees = {}
        self.action_freq_dist = action_freq_dist
        self.num_timesteps = num_timesteps

        random_tkn_names = []
        
        # create a list of tokens which occur at the desired frequency
        for tkn in pool_freq_dist:
            self.rolling_trade_fees[tkn] = []
            freq = int(round(float(pool_freq_dist[tkn] * simulation_actions_count), 0))
            for i in range(freq):
                random_tkn_names.append(tkn)

        # randomly shuffle the list of tokens that we will select from
        random.seed(1)
        for i in range(50):
            random.shuffle(random_tkn_names)
        self.pool_freq_dist_list = random_tkn_names

    def get_random_amt(self, amt: Decimal) -> Decimal:
        if self.random.randint(0, 1000) != 0:
            max_amt, min_amt = amt * Decimal("0.0001"), amt * Decimal("0.000001")
        else:
            max_amt, min_amt = amt * Decimal("0.01"), amt * Decimal("0.001")
        return Decimal(self.random.uniform(float(min_amt), float(max_amt)))

    def perform_random_trade(self):
        """
        Performs a random trade on the server.
        """
        state = self.protocol.global_state
        timestamp = self.timestamp
        user_name = self.user_name
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        source_liquidity = get_tkn_trading_liquidity(state, tkn_name)
        bnt_min_liquidity = get_bnt_min_liquidity(state, tkn_name)
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
        delta = bnt_trading_liquidity - bnt_min_liquidity
        user_funds = get_user_balance(state, user_name, tkn_name)
        is_trading_enabled_source = get_is_trading_enabled(state, tkn_name)
        is_trading_enabled_target = get_is_trading_enabled(state, target_tkn)
        amt = 0
#         if is_trading_enabled_source and is_trading_enabled_target:
        swap_amt = self.get_random_amt(source_liquidity)
        if pd.isnull(user_funds):
            user_funds = Decimal('0')

        if pd.isnull(swap_amt):
            swap_amt = Decimal('0')
        if user_funds > swap_amt:
            amt = swap_amt
        else:
            amt = user_funds

        if amt > 0:
            self.protocol.trade(
                tkn_amt=str(amt),
                source_token=tkn_name,
                target_token=target_tkn,
                user_name=user_name,
                timestamp=timestamp,
            )
        if target_tkn == 'bnt':
            tkn = tkn_name
        else:
            tkn = target_tkn
        trading_fee = get_trading_fee(state, tkn)
        fees_earned = trading_fee * amt
        if fees_earned > 0:
            self.rolling_trade_fees[tkn].append(fees_earned)
        self.daily_trade_volume += amt
        self.latest_tkn_name = tkn_name + "_" + target_tkn
        self.latest_amt = amt
        return self

    def arbitrage_trade(self, state: State, tkn_name: str, target_tkn: str, user_name: str):
        """
        Computes the appropriate arbitrage trade on the tkn_name pool.
        """
        timestamp = self.timestamp
        tkn_price, bnt_price = get_prices(state, tkn_name)
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
        tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
        trading_fee = get_trading_fee(state, tkn_name)
        user_tkn = get_user_balance(state, user_name, tkn_name)
        user_bnt = get_user_balance(state, user_name, "bnt")
        is_trading_enabled_source = get_is_trading_enabled(state, tkn_name)
        is_trading_enabled_target = get_is_trading_enabled(state, target_tkn)
        trade_amt = Decimal('0')
        source_token = tkn_name
        target_token = target_tkn
#         if is_trading_enabled_source and is_trading_enabled_target:
        x = process_arbitrage_trade(
            tkn_name,
            tkn_price,
            bnt_price,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            user_tkn,
            user_bnt,
        )
        if x is not None:
            (
                trade_amt,
                source_token,
                target_token,
                user_capability,
            ) = x
            if user_capability:
                if trade_amt > 0:
                    self.protocol.trade(
                        str(trade_amt), source_token, target_token, user_name, timestamp
                    )
        self.daily_trade_volume += trade_amt
        self.latest_tkn_name = source_token + "_" + target_token
        self.latest_amt = trade_amt
        if target_token == 'bnt':
            tkn = source_token
        else:
            tkn = target_token
        trading_fee = get_trading_fee(state, tkn)
        fees_earned = trading_fee * trade_amt
        if fees_earned > 0:
            self.rolling_trade_fees[tkn].append(fees_earned)

    def perform_random_arbitrage_trade(self):
        """
        Performs a random arbitrage trade.
        """
        state = self.protocol.global_state
        user_name = self.random.choice([usr for usr in state.users if usr != 'protocol'])
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        self.arbitrage_trade(state, tkn_name, target_tkn, user_name)
        return self

    def process_force_moving_average(
            self, tkn_name: str, user_tkn: Decimal, user_bnt: Decimal
    ) -> Tuple[Decimal, str, str, bool]:
        """
        Process the trade amount to force the ema and the spot price together.
        """
        state = self.protocol.global_state
        tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
        trading_fee = get_trading_fee(state, tkn_name)
        network_fee = get_network_fee(state, tkn_name)
        ema_rate = get_ema_rate(state, tkn_name)
        spot_rate = get_spot_rate(state, tkn_name)
        future_ema = compute_ema(spot_rate, ema_rate)
        if ema_rate < spot_rate:
            source_tkn = tkn_name
            target_tkn = "bnt"
            trade_amt = trade_tkn_to_ema(
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
                future_ema,
            )
            user_capability = user_tkn > trade_amt
        elif ema_rate > spot_rate:
            source_tkn = "bnt"
            target_tkn = tkn_name
            trade_amt = trade_bnt_to_ema(
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
                future_ema,
            )
            user_capability = user_bnt > trade_amt
        else:
            source_tkn = tkn_name
            target_tkn = tkn_name
            trade_amt = Decimal("0")
            user_capability = False
        self.latest_tkn_name = source_tkn + "_" + target_tkn
        self.latest_amt = trade_amt
        return trade_amt, source_tkn, target_tkn, user_capability

    def force_moving_average(
            self, state: State, tkn_name: str, user_name: str, timestamp: int
    ):
        """
        Analyze the state of a pool and creates a swap that drives the ema and the spot price together.
        """
        user_tkn = get_user_balance(state, user_name, tkn_name)
        user_bnt = get_user_balance(state, user_name, "bnt")
        if get_is_trading_enabled(state, tkn_name):
            (
                tkn_amt,
                source_token,
                target_token,
                user_capability,
            ) = self.process_force_moving_average(tkn_name, user_tkn, user_bnt)
            if user_capability:
                self.protocol.trade(
                    tkn_amt, source_token, target_token, user_name, timestamp
                )
                self.daily_trade_volume += tkn_amt
                self.latest_tkn_name = source_token + "_" + target_token
                self.latest_amt = tkn_amt
        return self

    def perform_random_ema_force_trade(self):
        state = self.protocol.global_state
        timestamp = self.timestamp
        user_name = self.random.choice(state.usernames)
        tokens = [token for token in state.whitelisted_tokens if token != "bnt"]
        tkn_name = self.random.choice(tokens)
        if get_is_trading_enabled(state, tkn_name):
            self.force_moving_average(state, tkn_name, user_name, timestamp)
        return self

    def get_random_tkn_names(self, state: State) -> Tuple[str, str]:
        source_tkn, target_tkn = 'None', 'None'
        while source_tkn == target_tkn:
            source_tkn, target_tkn = self.random.sample(self.pool_freq_dist_list, 2)
        if source_tkn == target_tkn:
            target_tkn  = self.random.sample(self.pool_freq_dist_list.remove(source_tkn), 1)
        return source_tkn, target_tkn

    def get_average_trading_fee(self):
        state = self.protocol.global_state
        return np.average(
            [
                float(state.tokens[tkn_name].trading_fee)
                for tkn_name in state.whitelisted_tokens
            ]
        )

    def get_random_trading_fee(self, trading_fee: Decimal) -> Decimal:
        min_trading_fee, max_trading_fee = max(
            trading_fee / Decimal("3"), Decimal("0.001")
        ), min(trading_fee * Decimal("3"), Decimal("0.05"))
        return Decimal(
            self.random.uniform(float(min_trading_fee), float(max_trading_fee))
        )

    def get_random_network_fee(self, network_fee: Decimal) -> Decimal:
        min_fee, max_fee = max(network_fee / Decimal("2"), Decimal("0.05")), min(
            network_fee * Decimal("2"), Decimal("0.25")
        )
        return Decimal(self.random.uniform(float(min_fee), float(max_fee)))

    def get_random_withdrawal_fee(self, withdrawal_fee: Decimal) -> Decimal:
        min_fee, max_fee = max(withdrawal_fee / Decimal("2"), Decimal("0.001")), min(
            withdrawal_fee * Decimal("2"), Decimal("0.01")
        )
        return Decimal(self.random.uniform(float(min_fee), float(max_fee)))

    def get_random_bnt_funding_limit(self, bnt_funding_amt: Decimal) -> Decimal:
        min_bnt_funding_limit = bnt_funding_amt * Decimal("1.5")
        max_bnt_funding_limit = bnt_funding_amt * Decimal("3.0")
        bnt_funding_limit = Decimal(
            self.random.uniform(
                float(min_bnt_funding_limit), float(max_bnt_funding_limit)
            )
        )
        return bnt_funding_limit

    def set_random_trading_fee(self):
        state = self.protocol.global_state
        for i in range(self.random.randint(1, 3)):
            tkn_name = self.random.choice([tkn for tkn in state.whitelisted_tokens])
            trading_fee = get_trading_fee(state, tkn_name)
            trading_fee = self.get_random_trading_fee(trading_fee)
            state.set_trading_fee(tkn_name, trading_fee)
            self.protocol.set_state(state)
        return self

    def set_random_network_fee(self):
        state = self.protocol.global_state
        tkn_name = self.random.choice([tkn for tkn in state.whitelisted_tokens])
        network_fee = get_network_fee(state, tkn_name)
        network_fee = self.get_random_network_fee(network_fee)
        state.set_network_fee(tkn_name, network_fee)
        self.protocol.set_state(state)
        return self

    def set_random_withdrawal_fee(self):
        state = self.protocol.global_state
        withdrawal_fee = state.withdrawal_fee
        tkn_name = self.random.choice([tkn for tkn in state.whitelisted_tokens])
        withdrawal_fee = self.get_random_withdrawal_fee(withdrawal_fee)
        state.set_withdrawal_fee(tkn_name, withdrawal_fee)
        self.protocol.set_state(state)
        return self

    def set_random_bnt_funding_limit(self):
        state = self.protocol.global_state
        tkn_name = self.random.choice([tkn for tkn in state.whitelisted_tokens])
        bnt_funding_limit = get_bnt_funding_limit(state, tkn_name)
        updated_bnt_funding_limit = self.get_random_bnt_funding_limit(bnt_funding_limit)
        state.set_bnt_funding_limit(tkn_name, updated_bnt_funding_limit)
        self.protocol.set_state(state)
        return self

    def perform_random_enable_trading(self):
        state = self.protocol.global_state
        for tkn in [tkn for tkn in state.whitelisted_tokens]:
            self.protocol.enable_trading(tkn)
        return self

    def get_random_withdrawal_amt(self, tkn_name: str) -> Decimal:
        user_balance = get_user_balance(
            self.protocol.global_state, self.user_name, tkn_name
        )
        return user_balance * Decimal(self.random.uniform(float(0.001), float(0.5)))

    def get_random_cooldown_amt(self, user_bntkn_amt: Decimal) -> Decimal:
        max_amt, min_amt = user_bntkn_amt * Decimal(
            "0.01"
        ), user_bntkn_amt * Decimal("0.001")
        return Decimal(self.random.uniform(float(min_amt), float(max_amt)))

    def is_protocol_bnbnt_healthy(
            self, protocol_bnbnt: Decimal, bnbnt_supply: Decimal
    ) -> bool:
        """
        Checks if the protocol owned bnbnt is at a healthy level (greater than 50%)
        """
        return protocol_bnbnt / bnbnt_supply > Decimal("0.5")

    def get_deposit_payload(
            self, state: State
    ) -> Tuple[str, str, Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Gets the input data required for a deposit.
        """
        user_name = self.user_name
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        user_tkn = get_user_balance(state, user_name, tkn_name)
        user_bnt = get_user_balance(state, user_name, "bnt")
        bnbnt_supply = get_pooltoken_balance(state, "bnt")
        protocol_bnbnt = get_protocol_wallet_balance(state, "bnt")
        bnbnt_rate = get_bnbnt_rate(state)
        return (
            user_name,
            tkn_name,
            user_tkn,
            user_bnt,
            bnbnt_supply,
            protocol_bnbnt,
            bnbnt_rate,
        )

    def random_distribute_autocompounding_program(self):
        """
        Performs a random trade on the server.
        """
        state = self.protocol.global_state
        timestamp = self.timestamp * 100000
        for tkn_name in state.whitelisted_tokens:
            if tkn_name in state.active_autocompounding_programs:
                self.protocol.distribute_autocompounding_program(
                    tkn_name=tkn_name, timestamp=timestamp
                )

    def create_random_autocompounding_rewards(self):
        """
        Performs a random trade on the server.
        """
        state = self.protocol.global_state
        timestamp = self.timestamp
        start_time = 1 + timestamp
        tkn_name = self.random.choice([tkn for tkn in state.whitelisted_tokens])
        distribution_type = self.random.choice(["flat", "exp"])
        if distribution_type == "flat":
            self.protocol.create_autocompounding_program(
                state=state,
                tkn_name=tkn_name,
                distribution_type=distribution_type,
                total_rewards="86400",
                total_duration_in_days=365,
                start_time=start_time,
                timestamp=timestamp,
            )
        else:
            self.protocol.create_autocompounding_program(
                state=state,
                tkn_name=tkn_name,
                distribution_type=distribution_type,
                half_life_days=1,
                total_rewards="360000",
                start_time=start_time,
                timestamp=timestamp,
            )

    def perform_random_begin_cooldown(self):
        """
        Begins a random cooldown.
        """
        state = self.protocol.global_state
        timestamp = self.timestamp
        for i in range(self.random.randint(1, 10)):
            user_name = self.user_name
            tkn_name, target_tkn = self.get_random_tkn_names(state)
            user_bntkn_amt = get_user_balance(state, user_name, tkn_name)
            bntkn_rate = compute_bntkn_rate(state, tkn_name)
            if pd.isnull(bntkn_rate):
                bntkn_rate = Decimal("0")
            if pd.isnull(user_bntkn_amt):
                user_bntkn_amt = Decimal("0")
            if user_bntkn_amt > 0 and bntkn_rate > 0:
                bntkn_amt = self.get_random_cooldown_amt(user_bntkn_amt)
                withdraw_value = bntkn_amt / bntkn_rate
                staked_bal = get_staked_balance(state, tkn_name)
                if not staked_bal > 0:
                    state.set_staked_balance(tkn_name, Decimal('0'))
                    self.protocol.set_state(state)
                self.protocol.begin_cooldown_by_rtkn(
                    tkn_name=tkn_name,
                    tkn_amt=str(withdraw_value),
                    user_name=user_name,
                    timestamp=timestamp,
                )
        return self

    def perform_random_deposit(self):
        """
        Performs a random deposit action
        """
        target_tvl = self.target_tvl
        state = self.protocol.global_state
        timestamp = self.timestamp
        (
            user_name,
            tkn_name,
            user_tkn,
            user_bnt,
            bnbnt_supply,
            protocol_bnbnt,
            bnbnt_rate,
        ) = self.get_deposit_payload(state)
        deposit_amt = None
        if tkn_name != "bnt":
            vault_balance = get_vault_balance(state, tkn_name)
            token_price, bnt_price = get_prices(state, tkn_name)
            vault_tvl = compute_vault_tkn_tvl(vault_balance, token_price)
            if vault_tvl < target_tvl:
                max_tkn_deposit = compute_max_tkn_deposit(
                    vault_tvl, target_tvl, user_tkn
                )
                deposit_amt = self.get_random_amt(max_tkn_deposit)
                if pd.isnull(deposit_amt):
                    deposit_amt = Decimal('0')
                if pd.isnull(user_tkn):
                    user_tkn = Decimal('0')
                if 0 < deposit_amt < user_tkn:
                    self.protocol.deposit(
                        tkn_name,
                        str(deposit_amt),
                        user_name,
                        timestamp,
                    )
        elif tkn_name == "bnt":
            if bnbnt_supply > 0 and self.is_protocol_bnbnt_healthy(
                    protocol_bnbnt, bnbnt_supply
            ):
                max_bnt_deposit = get_max_bnt_deposit(
                    state, user_bnt
                )
                deposit_amt = self.get_random_amt(max_bnt_deposit)

                if pd.isnull(deposit_amt):
                    deposit_amt = Decimal('0')
                if pd.isnull(user_tkn):
                    user_tkn = Decimal('0')

                if 0 < deposit_amt < user_tkn:
                    self.protocol.deposit(
                        tkn_name, str(deposit_amt), user_name, timestamp
                    )
        self.latest_tkn_name = tkn_name
        self.latest_amt = deposit_amt
        return self

    def process_withdrawal(
            self,
            user_name: str,
            id_number: int,
            timestamp: int = 0,
    ):
        """
        Main withdrawal logic based on the withdraw algorithm of the BIP15 spec.
        """
        state = self.protocol.global_state

        (
            id_number,
            cooldown_timestamp,
            tkn_name,
            pool_token_amt,
            withdraw_value,
            user_name,
        ) = unpack_withdrawal_cooldown(state, user_name, id_number)

        cooldown_time = state.cooldown_time
        cool_down_complete = timestamp - cooldown_timestamp >= cooldown_time
        if cool_down_complete:
            self.protocol.withdraw(
                user_name=user_name,
                id_number=id_number,
                timestamp=timestamp,
                tkn_name=tkn_name,
                tkn_amt=str(withdraw_value),
            )
        self.latest_tkn_name = tkn_name
        self.latest_amt = withdraw_value
        return self

    def perform_random_withdrawal(self):
        """
        Perform random withdraw action.
        """
        state = self.protocol.global_state
        timestamp = self.timestamp
        user_name = self.random.choice(state.usernames)
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        pending_withdrawals = get_user_pending_withdrawals(state, user_name, tkn_name)
        if len(pending_withdrawals) > 0:
            id_number = self.random.choice(pending_withdrawals)
            self.process_withdrawal(
                user_name=user_name, id_number=id_number, timestamp=timestamp
            )
        return self

    def perform_random_vortex_burner(self):
        """
        Simulation purposes only.
        """
        state = self.protocol.global_state
        vortex_burner(state, self.user_name)
        return self

    def transform_results(self, results: pd.DataFrame, simulation_tokens: list) -> pd.DataFrame:
        nl = []
        results_list = [results[['level_2', 'timestamp', tkn]] for tkn in simulation_tokens]
        state = self.protocol.global_state
        for df in results_list:
            tkn_name = df.columns[-1]
            df['tkn_name'] = [tkn_name for _ in range(len(df))]
            df = df.rename({tkn_name: 'amount', 'level_2': 'name'}, axis=1)
            df = df.sort_values(['tkn_name', 'timestamp', 'name'])
            df = df[['timestamp', 'tkn_name', 'name', 'amount']]
            nl.append(df)
        return pd.concat(nl)

    def reduce_trading_liquidity(self, n_periods, constant_multiplier):
        from statistics import mean
        state = self.protocol.global_state
        for tkn_name in list(state.whitelisted_tokens):
            try:
                new_bnt_funding_limit = mean(self.rolling_trade_fees[tkn_name][-n_periods:]) * constant_multiplier
                """
                Updates the state of the appropriate pool, and the protocol holdings, as required.
                """
                current_bnt_funding_limit = get_bnt_funding_limit(state, tkn_name)
                if round(float(current_bnt_funding_limit), 5) != round(float(new_bnt_funding_limit),5):
                    updated_bnt_trading_liquidity = Decimal(new_bnt_funding_limit)
                    bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)

                    tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
                    ema_rate = get_ema_rate(state, tkn_name)
                    bnt_renounced = bnt_trading_liquidity - updated_bnt_trading_liquidity
                    updated_tkn_trading_liquidity = max(tkn_trading_liquidity - bnt_renounced / ema_rate, 0)

                    if get_is_price_stable(state, tkn_name):
                        print('bnt_funding_limit', tkn_name, current_bnt_funding_limit, ' --> ', new_bnt_funding_limit)
                        state.decrease_bnt_trading_liquidity(tkn_name, bnt_renounced)
                        state.decrease_staked_balance(tkn_name, bnt_renounced)
                        state.decrease_vault_balance(tkn_name, bnt_renounced)
                        state.decrease_pooltoken_balance(tkn_name, bnt_renounced)
                        state.decrease_protocol_wallet_balance(tkn_name, bnt_renounced)
                        state.set_bnt_funding_limit(tkn_name, updated_bnt_trading_liquidity)
                        state.set_bnt_funding_amt(tkn_name, updated_bnt_trading_liquidity)
                        state.set_tkn_trading_liquidity(tkn_name, updated_tkn_trading_liquidity)
                        if check_pool_shutdown(state, tkn_name):
                            state = shutdown_pool(state, tkn_name)
                        self.protocol.set_state(state)
            except:
                pass
            
    def run(self, transact, mean_events_per_day=None, n_periods=None, constant_multiplier=None, is_proposal=False):
        for ct in range(self.num_timesteps):
            self.timestamp = ct
            transact(self, is_proposal)
            if is_proposal:
                try:
                    ts_compare = (num_timestamps_per_day / mean_events_per_day) * n_periods
                    if self.timestamp > ts_compare:
                        self.reduce_trading_liquidity(
                            int(round(mean_events_per_day * n_periods, 0)), constant_multiplier)
                except:
                    pass
        return pd.concat(self.logger)


# COMMAND ----------

# MAGIC %md
# MAGIC Load the `MonteCarloGenerator` class parameters:

# COMMAND ----------

simulator = MonteCarloGenerator(
    target_tvl=target_tvl,
    whitelisted_tokens= whitelisted_tokens,
    price_feed=price_feeds,
    user_initial_balances=user_initial_balances,
    simulation_actions_count=simulation_actions_count,
    num_timesteps=num_timesteps,
    pool_freq_dist=pool_freq_dist,
    action_freq_dist=action_freq_dist,
    bnt_min_liquidity=bnt_min_liquidity
)

# COMMAND ----------

# MAGIC %md
# MAGIC Run the baseline simulation:

# COMMAND ----------

baseline_output = simulator.run(transact)
baseline_output

# COMMAND ----------

# MAGIC %md
# MAGIC Run the simulation using the proposal's modified parameters:

# COMMAND ----------

simulator = MonteCarloGenerator(
    target_tvl=target_tvl,
    whitelisted_tokens= whitelisted_tokens,
    price_feed=price_feeds,
    user_initial_balances=user_initial_balances,
    simulation_actions_count=simulation_actions_count,
    num_timesteps=num_timesteps,
    pool_freq_dist=pool_freq_dist,
    action_freq_dist=action_freq_dist,
    bnt_min_liquidity=bnt_min_liquidity
)

# COMMAND ----------

# MAGIC %md
# MAGIC Note below that the `simulator.run(...)` parameters are significantly different from the baseline simulation above.

# COMMAND ----------

proposal_output = simulator.run(transact, mean_events_per_day, n_periods, constant_multiplier, is_proposal=True)
proposal_output

# COMMAND ----------

# MAGIC %md
# MAGIC Combine the results to compare side-by-side:

# COMMAND ----------

proposal_output['type'] = ['proposal' for _ in range(len(proposal_output))]
baseline_output['type'] = ['baseline' for _ in range(len(baseline_output))]
combined = pd.concat([proposal_output, baseline_output])
combined

# COMMAND ----------

# MAGIC %md
# MAGIC Print the list of data points we collected for each time step.

# COMMAND ----------

print(list(combined.columns))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data visualisation
# MAGIC 
# MAGIC We  will start by visualising the two simulation results.

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = ['eth_bnt_funding_limit'],
              color = "type",
              title='ETH bnt funding limit')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = ['link_bnt_funding_limit'],
              color = "type",
              title='LINK bnt funding limit')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = ['eth_bnt_trading_liquidity'],
              color = "type",
              title='ETH bnt trading liquidity')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = ['link_bnt_trading_liquidity'],
              color = "type",
              title='LINK bnt trading liquidity')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = 'eth_surplus',
              color='type',
               title='ETH surplus')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = 'link_surplus',
              color='type',
               title='LINK surplus')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = 'total_surplus',
              color='type',
               title='total surplus')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = 'total_surplus_bnt',
              color='type',
               title='total surplus (bnt)')
fig.show()

# COMMAND ----------

fig = px.line(combined, x = "timestamp", y = 'total_surplus_usd',
              color='type',
               title='total surplus (usd)')
fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Optimizing the parameters
# MAGIC 
# MAGIC We hypothesized before that ...
# MAGIC 
# MAGIC We can check how the results would be if ...

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC ...

# COMMAND ----------

import mlflow

combined.to_csv(save_results_path)

with mlflow.start_run():
    mlflow.log_artifact(save_results_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Profiling the Results
# MAGIC 
# MAGIC This notebook performs exploratory data analysis (EDA) on the results dataset.
# MAGIC 
# MAGIC To expand on the analysis, edit [the options of pandas-profiling](https://pandas-profiling.github.io/pandas-profiling/docs/master/rtd/pages/advanced_usage.html), and rerun it.

# COMMAND ----------

keep_cols = ['timestamp','type','latest_action','latest_amt','latest_tkn_name','total_surplus','total_surplus_bnt','total_surplus_usd']
for col in combined.columns:
    if 'link' in col:
        keep_cols.append(col)
    if 'eth' in col:
        keep_cols.append(col)
    if 'dai' in col:
        keep_cols.append(col)
    try:
        combined[col] = round(combined[col].astype(float), 4)
    except: 
        pass
    
combined = combined[keep_cols]
combined

# COMMAND ----------

from pandas_profiling import ProfileReport
df_profile = ProfileReport(combined, title="Profiling Report", 
                           progress_bar=False, 
                           infer_dtypes=False,
                           minimal=True
                          )
profile_html = df_profile.to_html()

displayHTML(profile_html)
