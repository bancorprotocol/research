# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Mesa Agent-based implementations of the Bancor protocol."""

import mesa

from bancor_research.bancor_simulator.v3.spec.actions import (
    unpack_withdrawal_cooldown,
    vortex_burner,
)
from bancor_research.bancor_simulator.v3.spec.network import BancorDapp
from bancor_research.bancor_simulator.v3.simulation.random_walk import RandomWalker
from bancor_research.bancor_simulator.v3.simulation.utils import (
    trade_tkn_to_ema,
    trade_bnt_to_ema,
    process_arbitrage_trade,
)
from bancor_research.bancor_simulator.v3.spec.utils import (
    compute_user_total_holdings,
    compute_ema,
    compute_bntkn_rate,
    compute_max_tkn_deposit,
    compute_vault_tkn_tvl,
)


class Trader(RandomWalker):
    """
    Represents a Bancor dapp user (trader and/or arbitrageur). Subclass to Mesa Agent
    """

    def __init__(
        self,
        unique_id: int,
        pos: Tuple[int, int],
        model: mesa.Model,
        moore: bool,
        whale_threshold: Decimal,
        whitelisted_tokens: list,
        target_tvl: Decimal,
    ):

        # init parent class with required parameters
        super().__init__(unique_id, pos, model, moore=moore)

        # init system logging parameters for DataCollector
        self.latest_tkn_name = None
        self.latest_tkn_amt = None
        self.latest_action = None
        self.latest_user_name = None
        self.latest_action = None
        self.vault_bnt = None
        self.erc20contracts_bntkn = None
        self.erc20contracts_bnbnt = None
        self.staked_bnt = None
        self.staked_tkn = None
        self.vault_bnt = None
        self.vault_tkn = None
        self.external_protection_vault_tkn = None
        self.protocol_wallet_bnbnt = None
        self.protocol_wallet_bntkn = None
        self.vortex_bnt = None
        self.ema_rate = None
        self.spot_rate = None

        # all agents use a single BancorDapp instance
        self.protocol = model.protocol

        # init agent attributes
        self.target_tvl = target_tvl
        self.whale_threshold = whale_threshold
        self.user_name = f"user_{unique_id}"
        self.protocol.v3.create_user(self.user_name)

        # the whitelisted tokens available in the model
        for tkn_name in whitelisted_tokens:

            # start everyone off with a random amount in their wallet
            random_amt = Decimal(self.random.randint(1, whale_threshold + 1))
            self.protocol.v3.global_state.set_user_balance(
                user_name=self.user_name, tkn_name=tkn_name, value=random_amt
            )

            if tkn_name == "bnt":
                self.initial_bnt = random_amt
            elif tkn_name == "tkn":
                self.initial_tkn = random_amt

        state = self.protocol.v3.global_state
        self.initial_balance = compute_user_total_holdings(state, self.user_name)
        self.daily_trade_volume = 0

    @property
    def profit(self):
        return (
            compute_user_total_holdings(self.protocol.v3.global_state, self.user_name)
            / self.initial_balance
        )

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
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        user_name = self.user_name
        tkn_name, target_tkn = self.get_random_tkn_names(state)
        source_liquidity = get_tkn_trading_liquidity(state, tkn_name)
        user_funds = get_user_balance(state, user_name, tkn_name)
        swap_amt = self.get_random_amt(source_liquidity)
        if user_funds > swap_amt:
            amt = swap_amt
        else:
            amt = user_funds
        self.protocol.v3.trade(
            tkn_amt=amt,
            source_token=tkn_name,
            target_token=target_tkn,
            user_name=user_name,
            timestamp=timestamp,
        )
        self.daily_trade_volume += amt
        self.latest_tkn_name = tkn_name + "_" + target_tkn
        self.latest_amt = amt
        return self

    def arbitrage_trade(self, state: State, tkn_name: str, user_name: str):
        """
        Computes the appropriate arbitrage trade on the token_name pool.
        """
        timestamp = state.timestamp
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
                    self.protocol.v3.trade(
                        trade_amt, source_token, target_token, user_name, timestamp
                    )
                    self.daily_trade_volume += trade_amt
                self.latest_tkn_name = source_token + "_" + target_token
                self.latest_amt = trade_amt

    def perform_random_arbitrage_trade(self):
        """
        Performs a random arbitrage trade.
        """
        state = self.protocol.v3.global_state
        user_name = self.random.choice(state.usernames)
        tokens = [token for token in state.whitelisted_tokens if token != "bnt"]
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
        state = self.protocol.v3.global_state
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
                self.protocol.v3.trade(
                    tkn_amt, source_token, target_token, user_name, timestamp
                )
                self.daily_trade_volume += tkn_amt
                self.latest_tkn_name = source_token + "_" + target_token
                self.latest_amt = tkn_amt
        return self

    def perform_random_ema_force_trade(self):
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        user_name = self.random.choice(state.usernames)
        tokens = [token for token in state.whitelisted_tokens if token != "bnt"]
        tkn_name = self.random.choice(tokens)
        if get_is_trading_enabled(state, tkn_name):
            self.force_moving_average(state, tkn_name, user_name, timestamp)

        return self

    def get_random_tkn_names(self, state: State) -> Tuple[str, str]:
        tokens = state.whitelisted_tokens
        source_tkn = self.random.choice(tokens)
        target_tkn = self.random.choice([tkn for tkn in tokens if tkn != source_tkn])
        return source_tkn, target_tkn

    def get_average_trading_fee(self):
        import numpy as np

        state = self.protocol.v3.global_state
        return np.average(
            [
                float(state.tokens[tkn_name].trading_fee)
                for tkn_name in state.whitelisted_tokens
            ]
        )

    def transact(self):
        """
        These probabilities are completely arbitrary.
        """
        trade_motive = self.get_average_trading_fee()
        latest_action = None
        i = self.random.randint(0, 1500)
        band1 = 500 * trade_motive
        if i < band1:
            latest_action = "trade"
            # # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_trade')
            self.perform_random_trade()
        elif band1 <= i < band1 * 2:
            latest_action = "arbitrage_trade"
            # # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_arbitrage_trade')
            self.perform_random_arbitrage_trade()
        elif band1 * 2 <= i < band1 * 3:
            latest_action = "ema_force_trade"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_ema_force_trade')
            self.perform_random_ema_force_trade()

        state = self.protocol.v3.global_state
        self.latest_user_name = self.user_name
        self.latest_action = latest_action
        self.vault_bnt = get_vault_balance(state, "bnt")
        self.erc20contracts_bntkn = get_pooltoken_balance(state, "tkn")
        self.erc20contracts_bnbnt = get_pooltoken_balance(state, "bnt")
        self.staked_bnt = get_staked_balance(state, "bnt")
        self.staked_tkn = get_staked_balance(state, "tkn")
        self.vault_bnt = get_vault_balance(state, "bnt")
        self.vault_tkn = get_vault_balance(state, "tkn")
        self.external_protection_vault_tkn = get_external_protection_vault(state, "tkn")
        self.protocol_wallet_bnbnt = get_protocol_wallet_balance(state, "bnt")
        self.protocol_wallet_bntkn = get_protocol_wallet_balance(state, "tkn")
        self.vortex_bnt = get_vortex_balance(state, "bnt")
        self.ema_rate = get_ema_rate(state, "tkn")
        self.spot_rate = get_spot_rate(state, "tkn")

    # step is called for each agent in model.BancorSimulator.schedule.step()
    def step(self):
        # move to a cell in my Moore neighborhood
        self.random_move()
        self.transact()


class LP(RandomWalker):
    """
    Represents a Bancor dapp liquidity provider. Subclass to Mesa Agent
    """

    def __init__(
        self,
        unique_id: int,
        pos: Tuple[int, int],
        model: mesa.Model,
        moore: bool,
        whale_threshold: Decimal,
        whitelisted_tokens: list,
        target_tvl: Decimal,
    ):

        # init parent class with required parameters
        super().__init__(unique_id, pos, model, moore=moore)

        # Bancor dapp, set at __init__, all people use the same dapp
        self.latest_tkn_name = None
        self.latest_tkn_amt = None
        self.latest_action = None
        self.latest_user_name = None
        self.latest_action = None
        self.vault_bnt = None
        self.erc20contracts_bntkn = None
        self.erc20contracts_bnbnt = None
        self.staked_bnt = None
        self.staked_tkn = None
        self.vault_bnt = None
        self.vault_tkn = None
        self.external_protection_vault_tkn = None
        self.protocol_wallet_bnbnt = None
        self.protocol_wallet_bntkn = None
        self.vortex_bnt = None
        self.ema_rate = None
        self.spot_rate = None

        user_name = f"user_{unique_id}"
        self.whale_threshold = whale_threshold

        self.protocol = model.protocol
        self.protocol.v3.create_user(user_name)
        self.user_name = user_name
        self.target_tvl = Decimal("100000000")

        # the whitelisted tokens available in the model
        for tkn_name in self.protocol.v3.global_state.whitelisted_tokens:

            # start everyone off with a random amount in their wallet
            random_amt = Decimal(self.random.randint(1, whale_threshold + 1))
            self.protocol.v3.global_state.set_user_balance(
                user_name=self.user_name, tkn_name=tkn_name, value=random_amt
            )

            if tkn_name == "bnt":
                self.initial_bnt = random_amt
            elif tkn_name == "tkn":
                self.initial_tkn = random_amt

        state = self.protocol.v3.global_state
        self.initial_balance = compute_user_total_holdings(state, self.user_name)

    @property
    def profit(self):
        return (
            compute_user_total_holdings(self.protocol.v3.global_state, self.user_name)
            / self.initial_balance
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
        state = self.protocol.v3.global_state
        for i in range(self.random.randint(1, 3)):
            tkn_name = self.random.choice(state.whitelisted_tokens)
            trading_fee = get_trading_fee(state, tkn_name)
            trading_fee = self.get_random_trading_fee(trading_fee)
            state.set_trading_fee(tkn_name, trading_fee)
            self.protocol.v3.set_state(state)
        return self

    def set_random_network_fee(self):
        state = self.protocol.v3.global_state
        tkn_name = self.random.choice(state.whitelisted_tokens)
        network_fee = get_network_fee(state, tkn_name)
        network_fee = self.get_random_network_fee(network_fee)
        state.set_network_fee(tkn_name, network_fee)
        self.protocol.v3.set_state(state)
        return self

    def set_random_withdrawal_fee(self):
        state = self.protocol.v3.global_state
        withdrawal_fee = state.withdrawal_fee
        tkn_name = self.random.choice(state.whitelisted_tokens)
        withdrawal_fee = self.get_random_withdrawal_fee(withdrawal_fee)
        state.set_withdrawal_fee(tkn_name, withdrawal_fee)
        self.protocol.v3.set_state(state)
        return self

    def set_random_bnt_funding_limit(self):
        state = self.protocol.v3.global_state
        tkn_name = self.random.choice(state.whitelisted_tokens)
        bnt_funding_limit = get_bnt_funding_limit(state, tkn_name)
        updated_bnt_funding_limit = self.get_random_bnt_funding_limit(bnt_funding_limit)
        state.set_bnt_funding_limit(tkn_name, updated_bnt_funding_limit)
        self.protocol.v3.set_state(state)
        return self

    def perform_random_enable_trading(self):
        self.protocol.v3.dao_msig_init_pools(
            self.protocol.v3.global_state.whitelisted_tokens, "bnt"
        )
        return self

    def get_random_withdrawal_amt(self, tkn_name: str) -> Decimal:
        user_balance = get_user_balance(
            self.protocol.v3.global_state, self.user_name, tkn_name
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

    def get_random_amt(self, amt: Decimal) -> Decimal:
        if self.random.randint(0, 1000) != 0:
            max_amt, min_amt = amt * Decimal("0.0001"), amt * Decimal("0.000001")
        else:
            max_amt, min_amt = amt * Decimal("0.01"), amt * Decimal("0.001")
        return Decimal(self.random.uniform(float(min_amt), float(max_amt)))

    def get_random_tkn_names(self, state: State) -> Tuple[str, str]:
        tokens = state.whitelisted_tokens
        source_tkn = self.random.choice(tokens)
        target_tkn = self.random.choice([tkn for tkn in tokens if tkn != source_tkn])
        return source_tkn, target_tkn

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
        state = self.protocol.v3.global_state
        timestamp = state.timestamp * 100000

        for tkn_name in state.whitelisted_tokens:
            if tkn_name in state.active_autocompounding_programs:
                self.protocol.v3.distribute_autocompounding_program(
                    tkn_name=tkn_name, timestamp=timestamp
                )

    def create_random_autocompounding_rewards(self):
        """
        Performs a random trade on the server.
        """
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        start_time = 1 + timestamp

        tkn_name = self.random.choice(state.whitelisted_tokens)
        distribution_type = self.random.choice(["flat", "exp"])

        if distribution_type == "flat":
            reward_total = Decimal("86400")

            self.protocol.v3.create_autocompounding_program(
                state=state,
                tkn_name=tkn_name,
                user_name=self.user_name,
                distribution_type=distribution_type,
                total_rewards=reward_total,
                total_duration_in_days=365,
                start_time=start_time,
                timestamp=timestamp,
            )
        else:
            reward_total = Decimal("360000")

            self.protocol.v3.create_autocompounding_program(
                state=state,
                tkn_name=tkn_name,
                user_name=self.user_name,
                distribution_type=distribution_type,
                half_life_days=1,
                total_rewards=reward_total,
                start_time=start_time,
                timestamp=timestamp,
            )

    def perform_random_trade(self):
        """
        Performs a random trade on the server.
        """
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        for i in range(self.random.randint(1, 10)):
            user_name = self.user_name
            tkn_name, target_tkn = self.get_random_tkn_names(state)
            source_liquidity = get_tkn_trading_liquidity(state, tkn_name)
            user_funds = get_user_balance(state, user_name, tkn_name)
            for i in range(self.random.randint(1, 5)):
                swap_amt = self.get_random_amt(source_liquidity)
                if user_funds > swap_amt:
                    amt = swap_amt
                else:
                    amt = user_funds
                self.protocol.v3.trade(
                    tkn_amt=amt,
                    source_token=tkn_name,
                    target_token=target_tkn,
                    user_name=user_name,
                    timestamp=timestamp,
                )

        return self

    def arbitrage_trade(self, state: State, tkn_name: str, user_name: str):
        """
        Computes the appropriate arbitrage trade on the token_name pool.
        """
        timestamp = state.timestamp
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
                    self.protocol.v3.trade(
                        trade_amt, source_token, target_token, user_name, timestamp
                    )

    def perform_random_begin_cooldown(self):
        """
        Begins a random cooldown.
        """
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        for i in range(self.random.randint(1, 10)):
            user_name = self.user_name
            tkn_name, target_tkn = self.get_random_tkn_names(state)
            user_bntkn_amt = get_user_balance(state, user_name, tkn_name)
            bntkn_rate = compute_bntkn_rate(state, tkn_name)
            if user_bntkn_amt > 0 and bntkn_rate > 0:
                bntkn_amt = self.get_random_cooldown_amt(user_bntkn_amt)
                withdraw_value = bntkn_amt / bntkn_rate
                self.protocol.v3.begin_cooldown(
                    tkn_name=tkn_name,
                    tkn_amt=withdraw_value,
                    user_name=user_name,
                    timestamp=timestamp,
                )

        return self

    def perform_random_arbitrage_trade(self):
        """
        Performs a random arbitrage trade.
        """
        state = self.protocol.v3.global_state
        for i in range(self.random.randint(1, 10)):
            user_name = self.random.choice(state.usernames)
            tokens = [token for token in state.whitelisted_tokens if token != "bnt"]
            tkn_name = self.random.choice(tokens)
            if get_is_trading_enabled(state, tkn_name):
                self.arbitrage_trade(state, tkn_name, user_name)

        return self

    def perform_random_deposit(self):
        """
        Performs a random deposit action
        """
        target_tvl = self.target_tvl
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
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
                if deposit_amt < user_tkn:
                    self.protocol.v3.deposit(
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
                    bnbnt_supply, protocol_bnbnt, bnbnt_rate, user_bnt
                )
                deposit_amt = self.get_random_amt(max_bnt_deposit)
                if deposit_amt < user_tkn:
                    self.protocol.v3.deposit(
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
        state = self.protocol.v3.global_state

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
            self.protocol.v3.withdraw(
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
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        user_name = self.random.choice(state.usernames)
        tkn_name = self.random.choice(state.whitelisted_tokens)
        pending_withdrawals = get_user_pending_withdrawals(state, user_name, tkn_name)
        if len(pending_withdrawals) > 0:
            id_number = self.random.choice(pending_withdrawals)
            self.process_withdrawal(
                user_name=user_name, id_number=id_number, timestamp=timestamp
            )
        return self

    def process_force_moving_average(
        self, tkn_name: str, user_tkn: Decimal, user_bnt: Decimal
    ) -> Tuple[Decimal, str, str, bool]:
        """
        Process the trade amount to force the ema and the spot price together.
        """
        state = self.protocol.v3.global_state
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
                self.protocol.v3.trade(
                    tkn_amt, source_token, target_token, user_name, timestamp
                )
                self.latest_tkn_name = source_token + "_" + target_token
                self.latest_amt = tkn_amt
        return self

    def perform_random_ema_force_trade(self):
        state = self.protocol.v3.global_state
        timestamp = state.timestamp
        user_name = self.random.choice(state.usernames)
        tokens = [token for token in state.whitelisted_tokens if token != "bnt"]
        tkn_name = self.random.choice(tokens)
        if get_is_trading_enabled(state, tkn_name):
            self.force_moving_average(state, tkn_name, user_name, timestamp)

        return self

    def perform_random_vortex_burner(self):
        """
        Simulation purposes only.
        """
        state = self.protocol.v3.global_state
        vortex_burner(state, self.user_name)
        return self

    def transact(self):
        """
        These probabilities are completely arbitrary.
        """

        i = self.random.randint(0, 1242)
        if i < 400:
            latest_action = "deposit"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_deposit')
            self.perform_random_deposit()
        elif 400 <= i < 500:
            latest_action = "create_autocompounding"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} create_random_autocompounding_rewards')
            self.create_random_autocompounding_rewards()
        elif 500 <= i < 600:
            latest_action = "distribute_autocompounding"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} random_distribute_autocompounding_program')
            self.random_distribute_autocompounding_program()
        elif 600 <= i < 1000:
            latest_action = "deposit"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_deposit')
            self.perform_random_deposit()
        elif 1000 <= i < 1100:
            latest_action = "cooldown"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_begin_cooldown')
            self.perform_random_begin_cooldown()
        elif 1100 <= i < 1200:
            latest_action = "withdrawal"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_withdrawal')
            self.perform_random_withdrawal()
        elif 1200 <= i < 1210:
            latest_action = "vortex_burner"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_vortex_burner')
            self.perform_random_vortex_burner()
        elif 1210 <= i < 1215:
            latest_action = "change_trading_fee"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} set_random_trading_fee')
            self.set_random_trading_fee()
        elif 1215 <= i < 1220:
            latest_action = "change_network_fee"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} set_random_network_fee')
            self.set_random_network_fee()
        elif 1220 <= i < 1230:
            latest_action = "change_withdrawal_fee"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} set_random_withdrawal_fee')
            self.set_random_withdrawal_fee()
        elif 1230 <= i < 1240:
            latest_action = "change_bnt_funding_limit"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} set_random_bnt_funding_limit')
            self.set_random_bnt_funding_limit()
        elif 1240 <= i <= 1242:
            latest_action = "enable_trading"
            # print(f'{self.protocol.v3.global_state.timestamp} {self.user_name} perform_random_enable_trading')
            self.perform_random_enable_trading()

        state = self.protocol.v3.global_state
        self.latest_user_name = self.user_name
        self.latest_action = latest_action
        self.vault_bnt = get_vault_balance(state, "bnt")
        self.erc20contracts_bntkn = get_pooltoken_balance(state, "tkn")
        self.erc20contracts_bnbnt = get_pooltoken_balance(state, "bnt")
        self.staked_bnt = get_staked_balance(state, "bnt")
        self.staked_tkn = get_staked_balance(state, "tkn")
        self.vault_bnt = get_vault_balance(state, "bnt")
        self.vault_tkn = get_vault_balance(state, "tkn")
        self.external_protection_vault_tkn = get_external_protection_vault(state, "tkn")
        self.protocol_wallet_bnbnt = get_protocol_wallet_balance(state, "bnt")
        self.protocol_wallet_bntkn = get_protocol_wallet_balance(state, "tkn")
        self.vortex_bnt = get_vortex_balance(state, "bnt")
        self.ema_rate = get_ema_rate(state, "tkn")
        self.spot_rate = get_spot_rate(state, "tkn")

    # step is called for each agent in model.BancorSimulator.schedule.step()
    def step(self):
        # move to a cell in my Moore neighborhood
        self.random_move()
        self.transact()


class Protocol(mesa.Agent):
    def __init__(
        self,
        unique_id,
        model,
        trading_fee,
        network_fee,
        withdrawal_fee,
        whitelisted_tokens,
        price_feeds,
        bnt_funding_limit,
        bnt_min_liquidity,
    ):

        # initialize the parent class with required parameters
        super().__init__(unique_id, model)

        # set the dapp interface to Bancor v3
        self.v3 = BancorDapp(
            price_feeds=price_feeds,
            whitelisted_tokens=whitelisted_tokens,
            trading_fee=trading_fee,
            network_fee=network_fee,
            withdrawal_fee=withdrawal_fee,
            bnt_funding_limit=bnt_funding_limit,
            bnt_min_liquidity=bnt_min_liquidity,
        )

    @property
    def bntkn_health(self) -> Decimal:
        state = self.v3.global_state
        pooltoken_balance = get_pooltoken_balance(state, "tkn")
        protocol_bntkn = get_protocol_wallet_balance(state, "tkn")
        if pooltoken_balance > Decimal("0"):
            return protocol_bntkn / pooltoken_balance
        else:
            return Decimal("0")

    @property
    def bnbnt_health(self) -> Decimal:
        state = self.v3.global_state
        pooltoken_balance = get_pooltoken_balance(state, "bnt")
        protocol_bnbnt = get_protocol_wallet_balance(state, "bnt")
        if pooltoken_balance > Decimal("0"):
            return protocol_bnbnt / pooltoken_balance
        else:
            return Decimal("0")
