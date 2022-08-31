import decimal
from decimal import Decimal
import pandas as pd
from bancor_research.bancor_simulator.v3.spec import *
import random
from statistics import mean


class MonteCarloGenerator(object):
    """
    Generates Monte Carlo scenarios.
    """

    def __init__(
        self,
        whitelisted_tokens: dict,
        price_feed: pd.DataFrame,
        user_initial_balances: pd.DataFrame,
        simulation_actions_count: int,
        num_timesteps: int,
        num_simulation_days: int,
        pool_freq_dist: dict,
        action_freq_dist: dict,
        deposit_mean: float,
        trade_mean: float,
        withdraw_mean: float,
        cooldown_time: int = 0,
        bnt_min_liquidity: Any = 10000,
    ):

        # all users/agents use a single BancorDapp instance
        v3 = BancorDapp(
            cooldown_time=cooldown_time,
            whitelisted_tokens=whitelisted_tokens,
            bnt_min_liquidity=bnt_min_liquidity,
            price_feeds=price_feed,
        )

        # set the initial balances for each user.
        for user_id in user_initial_balances["user_id"].unique():
            v3.create_user(user_id)

            user_balances = user_initial_balances[
                user_initial_balances["user_id"] == user_id
            ]
            for tkn_name in user_balances["poolSymbol"].unique():

                user_balance = user_balances[user_balances["poolSymbol"] == tkn_name][
                    "tokenAmount_real_usd"
                ].values[0]
                v3.set_user_balance(
                    user_name=user_id,
                    tkn_name=tkn_name,
                    tkn_amt=user_balance,
                    timestamp=0,
                )

                pooltkn_name = get_pooltoken_name(tkn_name)
                if pooltkn_name not in v3.global_state.users[user_id].wallet:
                    v3.global_state.users[user_id].wallet[pooltkn_name] = Token(
                        balance=Decimal("0")
                    )

        self.protocol = v3
        self.random = random
        self.logger = []
        self.timestamp = 0
        self.simulation_actions_count = simulation_actions_count
        self.whitelisted_tokens = whitelisted_tokens
        self.daily_trade_volume = 0
        self.latest_amt = 0
        self.latest_tkn_name = None
        self.rolling_trade_fees = {}
        self.total_fees_earned = {}
        self.action_freq_dist = action_freq_dist
        self.num_timesteps = num_timesteps
        self.slippage_profile = {}
        self.user_initial_balances = user_initial_balances
        self.iloss_tracker = {}
        self.iloss_realized = {}
        self.total_fees_earned = {}
        self.num_simulation_days = num_simulation_days
        self.slippage_pearson_correlation = 0
        self.deposit_mean = deposit_mean
        self.trade_mean = trade_mean
        self.withdraw_mean = withdraw_mean
        random_tkn_names = []

        # create a list of tokens which occur at the desired frequency
        for tkn in pool_freq_dist:
            self.total_fees_earned[tkn] = [0]
            self.rolling_trade_fees[tkn] = []
            self.iloss_realized[tkn] = [0]
            freq = int(round(float(pool_freq_dist[tkn] * simulation_actions_count), 0))
            for i in range(freq):
                random_tkn_names.append(tkn)

        # randomly shuffle the list of tokens that we will select from
        random.seed(1)
        for i in range(50):
            random.shuffle(random_tkn_names)
        self.pool_freq_dist_list = random_tkn_names

    def process_arbitrage_trade(
        self,
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
        try:
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
        except decimal.InvalidOperation:
            print("Invalid operation of decimal, skipping this action.")

    def get_random_deposit_amt(self, amt: Decimal = None) -> Decimal:
        if amt is None:
            amt = Decimal(self.deposit_mean)
        max_amt, min_amt = amt * Decimal("100.0"), amt / Decimal("100.0")
        return Decimal(self.random.uniform(float(min_amt), float(max_amt)))

    def get_random_trade_amt(self, amt: Decimal = None) -> Decimal:
        if amt is None:
            amt = Decimal(self.trade_mean)
        max_amt, min_amt = amt * Decimal("100.0"), amt / Decimal("100.0")
        return Decimal(self.random.uniform(float(min_amt), float(max_amt)))

    def get_random_withdraw_amt(self, amt: Decimal = None) -> Decimal:
        if amt is None:
            amt = Decimal(self.withdraw_mean)
        max_amt, min_amt = amt * Decimal("100.0"), amt / Decimal("100.0")
        return Decimal(self.random.uniform(float(min_amt), float(max_amt)))

    def handle_trade_fees(self, target_tkn: str, source_tkn: str):
        """
        Collects data on the trade fees earned during the most recent trade action.
        """
        state = self.protocol.global_state

        if source_tkn == "bnt":
            if target_tkn in state.rolling_trade_fees:
                fees_earned = state.rolling_trade_fees[target_tkn][-1]
                self.rolling_trade_fees[target_tkn].append(fees_earned)
                self.total_fees_earned[target_tkn].append(
                    float(self.total_fees_earned[target_tkn][-1]) + float(fees_earned)
                )

        elif target_tkn == "bnt":
            if source_tkn in state.rolling_trade_fees:
                fees_earned = state.rolling_trade_fees[source_tkn][-1]
                self.rolling_trade_fees[source_tkn].append(fees_earned)
                self.total_fees_earned[source_tkn].append(
                    float(self.total_fees_earned[source_tkn][-1]) + float(fees_earned)
                )

        elif target_tkn != "bnt" and source_tkn != "bnt":
            if source_tkn in state.rolling_trade_fees:
                fees_earned_1 = state.rolling_trade_fees[source_tkn][-1]
                self.rolling_trade_fees[source_tkn].append(fees_earned_1)
                self.total_fees_earned[source_tkn].append(
                    float(self.total_fees_earned[source_tkn][-1]) + float(fees_earned_1)
                )

            if target_tkn in state.rolling_trade_fees:
                fees_earned_2 = state.rolling_trade_fees[target_tkn][-1]
                self.rolling_trade_fees[target_tkn].append(fees_earned_2)
                self.total_fees_earned[target_tkn].append(
                    float(self.total_fees_earned[target_tkn][-1]) + float(fees_earned_2)
                )

    def get_slippage(self, amt, tkn_trading_liquidity, tkn_name) -> Decimal:
        """
        Calculates the slippage for a given trade, and enforces historical adjustments.
        """
        slippage_perc = amt / (amt + tkn_trading_liquidity)

        # derived from real-world data
        historical_max_slippage = self.slippage_profile[tkn_name]["max"]
        historical_min_slippage = self.slippage_profile[tkn_name]["min"]

        if slippage_perc > historical_max_slippage:

            # if slippage is equal to or greater than the max., impact equals historical_max_slippage
            slippage_perc = historical_max_slippage

        elif slippage_perc < historical_min_slippage:

            # if slippage is equal to or less than the min., impact equals historical_min_slippage
            slippage_perc = historical_min_slippage

        return slippage_perc

    def perform_random_trade(self):
        """
        Performs a random trade on the server.
        """
        try:
            state = self.protocol.global_state
            timestamp = self.timestamp
            user_name = "global user"
            source_tkn, target_tkn = self.get_random_tkn_names(state)
            tkn_trading_liquidity_source = get_tkn_trading_liquidity(state, source_tkn)
            user_source_before = get_user_balance(state, user_name, source_tkn)
            swap_amt = self.get_random_trade_amt()

            if user_source_before > swap_amt:
                amt = swap_amt
            else:
                amt = user_source_before / Decimal("1000.0")

            if amt > 0:
                self.protocol.trade(
                    tkn_amt=str(amt),
                    source_token=source_tkn,
                    target_token=target_tkn,
                    user_name=user_name,
                    timestamp=timestamp,
                )
                self.latest_tkn_name = source_tkn + "_" + target_tkn
                self.latest_amt = amt
                self.handle_trade_fees(target_tkn, source_tkn)

        except decimal.DivisionByZero:
            print(f"Attempted decimal.DivisionByZero. Skipping transaction.")

    def perform_random_arbitrage_trade(self):
        """
        Performs a random arbitrage trade.
        """
        try:
            state = self.protocol.global_state
            user_name = "global user"
            tkn_name, target_tkn = self.get_random_tkn_names(state)
            timestamp = self.timestamp
            tkn_price, bnt_price = get_prices(state, tkn_name)
            bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
            tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
            trading_fee = get_trading_fee(state, tkn_name)
            user_tkn = get_user_balance(state, user_name, tkn_name)
            user_bnt = get_user_balance(state, user_name, "bnt")
            trade_amt = Decimal("0")
            source_token = tkn_name
            target_token = target_tkn
            x = self.process_arbitrage_trade(
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

                source_tkn = source_token
                target_tkn = target_token
                self.handle_trade_fees(target_tkn, source_tkn)

            self.latest_tkn_name = source_token + "_" + target_token
            self.latest_amt = trade_amt
        except KeyError:
            print("The price feed index is too short, key not found.")

    def get_random_tkn_names(self, state: State) -> Tuple[str, str]:
        source_tkn, target_tkn = "None", "None"
        while source_tkn == target_tkn:
            source_tkn, target_tkn = self.random.sample(self.pool_freq_dist_list, 2)
        if source_tkn == target_tkn:
            target_tkn = self.random.sample(
                self.pool_freq_dist_list.remove(source_tkn), 1
            )
        return source_tkn, target_tkn

    def get_random_withdrawal_amt(self, tkn_name: str) -> Decimal:
        user_balance = get_user_balance(
            self.protocol.global_state, self.user_name, tkn_name
        )
        return user_balance * Decimal(self.random.uniform(float(0.0001), float(0.5)))

    def get_random_cooldown_amt(self, user_bntkn_amt: Decimal = None) -> Decimal:

        if user_bntkn_amt is None:
            user_bntkn_amt = Decimal(self.withdraw_mean)

        max_amt, min_amt = user_bntkn_amt * Decimal("10.0"), user_bntkn_amt * Decimal(
            "0.00001"
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
        self, state: State, user_name: str
    ) -> Tuple[str, str, Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Gets the input data required for a deposit.
        """
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

    def perform_random_enable_trading(self):
        """
        Begins a random withdrawal.
        """
        state = self.protocol.global_state
        timestamp = state.timestamp
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        if not get_is_trading_enabled(state, tkn_name):
            self.protocol.enable_trading(tkn_name=tkn_name, timestamp=timestamp)

    def perform_random_withdrawal(self):
        """
        Begins a random withdrawal.
        """
        state = self.protocol.global_state
        timestamp = self.timestamp
        user_name = self.random.choice(
            [n for n in state.usernames if n not in ["protocol", "global user"]]
        )
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        user_bntkn_amt = get_user_balance(state, user_name, f"bn{tkn_name}")
        bntkn_rate = compute_bntkn_rate(state, tkn_name)
        if user_bntkn_amt > 0 and bntkn_rate > 0:
            try:
                bntkn_amt = user_bntkn_amt
                withdraw_value = bntkn_amt / bntkn_rate
                id_number = self.protocol.begin_cooldown_by_rtkn(
                    tkn_amt=str(withdraw_value),
                    tkn_name=tkn_name,
                    user_name=user_name,
                    timestamp=timestamp,
                )
                self.protocol.withdraw(
                    user_name=user_name, id_number=id_number, timestamp=timestamp
                )
                tkn_price_initial = float(self.iloss_tracker[user_name]["tkn_price"])
                bnt_price_initial = float(self.iloss_tracker[user_name]["bnt_price"])
                tkn_price_final = float(get_tkn_price(state, tkn_name))
                bnt_price_final = float(get_tkn_price(state, "bnt"))

                var_A = (
                    (tkn_price_final - tkn_price_initial) / tkn_price_initial
                ) * 100
                var_B = (
                    (bnt_price_final - bnt_price_initial) / bnt_price_initial
                ) * 100

                iloss_realized = float(self.iloss(var_A, var_B)) * float(withdraw_value)
                self.iloss_tracker[user_name] = {
                    "tkn_name": tkn_name,
                    "tkn_price": tkn_price_final,
                    "bnt_price": bnt_price_final,
                    "timestamp": timestamp,
                    "iloss_realized": iloss_realized,
                }

                self.iloss_realized[tkn_name].append(
                    float(self.iloss_realized[tkn_name][-1]) + iloss_realized
                )
                self.latest_tkn_name = tkn_name
                self.latest_amt = withdraw_value
            except:
                pass
        return self

    def iloss(self, var_A: float, var_B: float) -> float:
        """Returns the impermanent loss value.

        Args:
            var_A: Asset A % variation
            var_B: Asset B % variation
        Returns:
            IL
        """
        price_ratio = (float(var_A) / 100 + 1) / (float(var_B) / 100 + 1)
        il = 2 * (price_ratio**0.5 / (1 + price_ratio)) - 1
        return il

    def perform_random_deposit(self):
        """
        Performs a random deposit action
        """

        try:
            state = self.protocol.global_state
            timestamp = self.timestamp
            user_name = f"user_{timestamp}"
            self.protocol.create_user(user_name)
            user_balances = self.user_initial_balances[
                self.user_initial_balances["user_id"] == "global user"
            ]
            for tkn_name in user_balances["poolSymbol"].unique():
                user_balance = user_balances[user_balances["poolSymbol"] == tkn_name][
                    "tokenAmount_real_usd"
                ].values[0]
                self.protocol.set_user_balance(
                    user_name=user_name,
                    tkn_name=tkn_name,
                    tkn_amt=user_balance,
                    timestamp=timestamp,
                )
                pooltkn_name = get_pooltoken_name(tkn_name)
                if pooltkn_name not in self.protocol.global_state.users[user_name].wallet:
                    self.protocol.global_state.users[user_name].wallet[
                        pooltkn_name
                    ] = Token(balance=Decimal("0"))

            state = self.protocol.global_state

            (
                user_name,
                tkn_name,
                user_tkn,
                user_bnt,
                bnbnt_supply,
                protocol_bnbnt,
                bnbnt_rate,
            ) = self.get_deposit_payload(state, user_name)
            deposit_amt = None
            if tkn_name != "bnt":
                deposit_amt = self.get_random_deposit_amt()
                if 0 < deposit_amt < user_tkn:
                    try:
                        self.protocol.deposit(
                            tkn_name,
                            str(deposit_amt),
                            user_name,
                            timestamp,
                        )
                    except ZeroDivisionError:
                        print(f'ZeroDivisionError during {tkn_name} deposit, skipping this action...')

            elif tkn_name == "bnt":
                if bnbnt_supply > 0 and self.is_protocol_bnbnt_healthy(
                    protocol_bnbnt, bnbnt_supply
                ):
                    deposit_amt = self.get_random_deposit_amt()
                    if 0 < deposit_amt < user_tkn:
                        try:
                            self.protocol.deposit(
                                tkn_name, str(deposit_amt), user_name, timestamp
                            )
                        except ZeroDivisionError:
                            print(f'ZeroDivisionError during {tkn_name} deposit, skipping this action...')

            self.latest_tkn_name = tkn_name
            self.latest_amt = deposit_amt
            self.iloss_tracker[user_name] = {
                "tkn_name": tkn_name,
                "tkn_price": get_tkn_price(state, tkn_name),
                "bnt_price": get_tkn_price(state, "bnt"),
                "timestamp": timestamp,
                "iloss_realized": 0.0,
            }
        except KeyError:
            print('Price feed index key not found during deposit')

    def update_trading_liquidity(self, n_events: int, constant_multiplier: int = 520):
        """
        Updates the state of the appropriate pool, and the protocol holdings, as required.
        """

        state = self.protocol.global_state
        for tkn_name in list(state.whitelisted_tokens):
            if len(self.rolling_trade_fees[tkn_name]) > 0:
                try:
                    # Calculate the new value for bnt_funding_limit based on the rolling avg trade fees.
                    new_bnt_funding_limit = (
                        mean(self.rolling_trade_fees[tkn_name][-n_events:])
                        * constant_multiplier
                    )

                    # Convert the tkn units into BNT
                    tkn_price = get_tkn_price(state, tkn_name)
                    bnt_price = get_tkn_price(state, "bnt")
                    bnt_per_tkn = tkn_price / bnt_price
                    new_bnt_funding_limit = new_bnt_funding_limit * bnt_per_tkn
                    updated_bnt_trading_liquidity = Decimal(new_bnt_funding_limit)

                    # Get the current system state variables
                    current_bnt_funding_limit = get_bnt_funding_limit(state, tkn_name)
                    bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
                    tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)

                    # Calculate the change in trading liquidity
                    bnt_delta = bnt_trading_liquidity - updated_bnt_trading_liquidity

                    # If the price is stable, perform the update
                    if get_is_price_stable(state, tkn_name) and new_bnt_funding_limit > 0:

                        if bnt_delta > 0:
                            # If we are reducing the trading liquidity, make the necessary adjustments
                            state.decrease_staked_balance(tkn_name, bnt_delta)
                            state.decrease_master_vault_balance(tkn_name, bnt_delta)
                            state.decrease_pooltoken_balance(tkn_name, bnt_delta)
                            state.decrease_protocol_wallet_balance(tkn_name, bnt_delta)
                            updated_tkn_trading_liquidity = max(
                                tkn_trading_liquidity - bnt_delta, 0
                            )
                            state.set_tkn_trading_liquidity(
                                tkn_name, updated_tkn_trading_liquidity
                            )
                            state.set_bnt_trading_liquidity(
                                tkn_name, updated_bnt_trading_liquidity
                            )
                            state.set_bnt_funding_amt(
                                tkn_name, updated_bnt_trading_liquidity
                            )

                        # In order to avoid automatic pool shutdown, we change this parameter dynamically also
                        state.tokens[tkn_name].bnt_min_liquidity = Decimal(
                            updated_bnt_trading_liquidity
                        ) * Decimal("0.5")

                        state.set_bnt_funding_limit(tkn_name, updated_bnt_trading_liquidity)

                        if check_pool_shutdown(state, tkn_name):
                            state = shutdown_pool(state, tkn_name)

                        self.protocol.set_state(state)
                except KeyError:
                    print(f"The price feeds dataset is too short. KeyError detected for {tkn_name}. Skipping this actions...")

    def run(
        self,
        transact,
        mean_events_per_day=None,
        num_timestamps_per_day=None,
        n_rolling_days=None,
        constant_multiplier=None,
        is_proposal=False,
    ):
        """
        Executes the simulation run and returns the collected data.
        """
        for _ in range(self.num_simulation_days):
            self.timestamp += 1
            transact(self)
            if is_proposal:
                if self.timestamp > n_rolling_days:
                    n_events = int(round(mean_events_per_day * n_rolling_days, 0))
                    self.update_trading_liquidity(n_events, constant_multiplier)
        return pd.concat(self.logger)
