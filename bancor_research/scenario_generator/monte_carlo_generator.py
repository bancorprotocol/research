# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Mesa Agent-based implementations of the Bancor protocol."""
from decimal import Decimal
from typing import Tuple, Any

import mesa
from bancor_research.bancor_simulator.v3.spec import get_prices, State, get_bnt_trading_liquidity, \
    get_tkn_trading_liquidity, get_trading_fee, get_user_balance, get_is_trading_enabled, get_network_fee, get_ema_rate, \
    get_spot_rate, get_vault_balance, get_pooltoken_balance, get_staked_balance, get_external_protection_vault, \
    get_protocol_wallet_balance, get_vortex_balance, get_bnt_funding_limit, get_bnbnt_rate, get_max_bnt_deposit, \
    get_user_pending_withdrawals, get_pooltoken_name, Token
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
    compute_vault_tkn_tvl,
)
import pandas as pd
import random

from typing import Tuple


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
    Computes the appropriate arbitrage trade on the token_name pool.
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
        import pandas as pd

        source_token = tkn_name
        target_token = "bnt"
        trade_amt = tkn_trade_amt
        if pd.isnull(user_tkn):
            user_tkn = Decimal('0')
        if pd.isnull(trade_amt):
            trade_amt = Decimal('0')
        user_capability = user_tkn > tkn_trade_amt
        return trade_amt, source_token, target_token, user_capability


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
            simulation_step_count: int,
            pool_freq_dist: dict,
            action_freq_dist: dict,
            bnt_min_liquidity: Any = 10000
    ):

        # all agents use a single BancorDapp instance
        v3 = BancorDapp(whitelisted_tokens=whitelisted_tokens,
                        bnt_min_liquidity=bnt_min_liquidity,
                        price_feeds=price_feed)

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
        self.simulation_step_count = simulation_step_count
        self.whitelisted_tokens = whitelisted_tokens
        self.daily_trade_volume = 0
        self.latest_amt = 0
        self.latest_tkn_name = None
        self.rolling_trade_fees = {}
        self.action_freq_dist = action_freq_dist

        random_tkn_names = []

        for tkn in pool_freq_dist:
            self.rolling_trade_fees[tkn] = []
            freq = int(round(float(pool_freq_dist[tkn] * simulation_step_count), 0))
            for i in range(freq):
                random_tkn_names.append(tkn)
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
        user_funds = get_user_balance(state, user_name, tkn_name)
        swap_amt = self.get_random_amt(source_liquidity)
        if pd.isnull(user_funds):
            user_funds = Decimal('0')
        if pd.isnull(swap_amt):
            swap_amt = Decimal('0')
        if user_funds > swap_amt:
            amt = swap_amt
        else:
            amt = user_funds
        self.protocol.trade(
            tkn_amt=amt,
            source_token=tkn_name,
            target_token=target_tkn,
            user_name=user_name,
            timestamp=timestamp,
        )
        if target_tkn == 'bnt':
            tkn = tkn_name
        else:
            tkn = target_tkn
        trading_fee = get_trading_fee(state, tkn_name)
        fees_earned = trading_fee * amt
        self.rolling_trade_fees[tkn].append(fees_earned)
        self.daily_trade_volume += amt
        self.latest_tkn_name = tkn_name + "_" + target_tkn
        self.latest_amt = amt
        return self

    def arbitrage_trade(self, state: State, tkn_name: str, user_name: str):
        """
        Computes the appropriate arbitrage trade on the token_name pool.
        """
        timestamp = self.timestamp
        tkn_price, bnt_price = get_prices(state, tkn_name)
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
        tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
        trading_fee = get_trading_fee(state, tkn_name)
        user_tkn = get_user_balance(state, user_name, tkn_name)
        user_bnt = get_user_balance(state, user_name, "bnt")
        is_trading_enabled = get_is_trading_enabled(state, tkn_name)

        if is_trading_enabled:
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
                    self.protocol.trade(
                        trade_amt, source_token, target_token, user_name, timestamp
                    )
                    self.daily_trade_volume += trade_amt
                self.latest_tkn_name = source_token + "_" + target_token
                self.latest_amt = trade_amt

                if target_token == 'bnt':
                    tkn = source_token
                else:
                    tkn = target_token
                trading_fee = get_trading_fee(state, tkn_name)
                fees_earned = trading_fee * trade_amt
                self.rolling_trade_fees[tkn].append(fees_earned)

    def perform_random_arbitrage_trade(self):
        """
        Performs a random arbitrage trade.
        """
        state = self.protocol.global_state
        user_name = self.random.choice([usr for usr in state.users if usr != 'protocol'])
        tokens = [token for token in state.users[user_name].wallet if token != "bnt"]
        tkn_name = self.random.choice(tokens)
        if get_is_trading_enabled(state, tkn_name):
            self.arbitrage_trade(state, tkn_name, user_name)

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
        source_tkn, target_tkn = self.random.sample(self.pool_freq_dist_list, 2)
        return source_tkn, target_tkn

    def get_average_trading_fee(self):
        import numpy as np

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
        if self.random.randint(0, 10) != 0:
            max_amt, min_amt = user_bntkn_amt * Decimal(
                "0.1"
            ), user_bntkn_amt * Decimal("0.01")
        else:
            max_amt, min_amt = user_bntkn_amt * Decimal("1"), user_bntkn_amt * Decimal(
                "0.5"
            )
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
                self.protocol.begin_cooldown(
                    tkn_name=tkn_name,
                    tkn_amt=withdraw_value,
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
                if deposit_amt < user_tkn:
                    self.protocol.deposit(
                        tkn_name,
                        deposit_amt,
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
                if deposit_amt < user_tkn:
                    self.protocol.deposit(
                        tkn_name, deposit_amt, user_name, timestamp
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
                tkn_amt=withdraw_value,
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
        tkn_name = self.random.choice([tkn for tkn in state.whitelisted_tokens])
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

    def set_bnt_funding_limit_by_rolling_avg(self, n_periods, constant_multiplier):
        from statistics import mean
        state = self.protocol.global_state
        for tkn_name in list(state.whitelisted_tokens):
            new_bnt_funding_limit = mean(self.rolling_trade_fees[tkn_name][-n_periods:]) * constant_multiplier
            state.set_bnt_funding_limit(tkn_name, new_bnt_funding_limit)
        self.protocol.set_state(state)
        return self

    def run(self, transact, mean_events_per_day=None, n_periods=None, constant_multiplier=None, is_proposal=False):
        for ct in range(self.simulation_step_count):
            self.timestamp = ct
            transact(self)
            if is_proposal:
                try:
                    self.set_bnt_funding_limit_by_rolling_avg(n_periods, constant_multiplier)
                except:
                    pass
        return self.transform_results(pd.concat(self.logger), list(self.whitelisted_tokens))
