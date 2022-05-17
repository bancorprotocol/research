"""Main Bancor v3 Protocol Logic"""
import json
import pickle
from datetime import datetime
from decimal import Decimal

import pandas as pd

from bancor3_simulator.core.dataclasses import State
from bancor3_simulator.core.settings import GlobalSettings
from bancor3_simulator.protocol.actions.staking import (
    mint_protocol_bnt,
    pool_depth_adjustment,
)
from bancor3_simulator.protocol.actions.trading import (
    process_arbitrage_trade, get_trade_inputs, trade_bnt_for_tkn, trade_tkn_for_bnt, handle_ema,
)
from bancor3_simulator.protocol.actions.withdraw import (
    unpack_cool_down_state,
    WithdrawalAlgorithm, begin_cooldown,
)


class BancorV3:
    """Main Bancor v3 Protocol Logic."""

    global_settings = GlobalSettings()
    name = global_settings.model
    version = global_settings.version
    max_int = global_settings.max_int

    """
    Args:
        timestep (int): The Ethereum block number to begin with. (default=1)
        alpha (Decimal): Alpha value in the EMA equation. (default=1.1)
        bnt_min_liquidity (Decimal): The minimum liquidity needed to bootstrap a pool.
        withdrawal_fee (Decimal): The global exit (withdrawal) fee. (default=0.002)
        coolown_time (int): The cooldown period in days. (default=7)
        bnt_funding_limit (Decimal): The BancorDAO determines the available liquidity for trading, through adjustment 
                                    of the “BNT funding limit” parameter. (default=100000)
        network_fee (Decimal): The global network fee. (default=1.002)
        trading_fee (Decimal): This value is set on a per pool basis, however, for convenience a single input is offered
                                here which will be used upon system genesis, and can be changed at the pool level later.
        whitelisted_tokens (List[str]): List of token tickernames indicating whitelist status approval. 
                                        (default=['link','usdc','eth','bnt','tkn', wbtc])
        bnt_virtual_balance (Decimal): BNT value provided for testing Barak's solidity output. (default=0)
        base_token_virtual_balance (Decimal): BNT value provided for testing Barak's solidity output. (default=2)
        
    """

    def __init__(
            self,
            timestep=0,
            alpha=global_settings.alpha,
            bnt_min_liquidity=global_settings.bnt_min_liquidity,
            withdrawal_fee=global_settings.withdrawal_fee,
            cooldown_time=global_settings.cooldown_time,
            bnt_funding_limit=global_settings.bnt_funding_limit,
            network_fee=global_settings.network_fee,
            trading_fee=global_settings.trading_fee,
            whitelisted_tokens=global_settings.whitelisted_tokens,
            price_feeds_path=global_settings.price_feeds_path,
            price_feeds: pd.DataFrame = None,
            active_users=global_settings.active_users,
            system_state=None
    ):

        self.json_data = None
        self.transaction_id = 0
        if active_users is None:
            active_users = BancorV3.global_settings.default_users
        self.timestep = timestep
        self.withdrawal_fee = withdrawal_fee
        self.network_fee = network_fee
        self.trading_fee = trading_fee
        self.bnt_min_liquidity = bnt_min_liquidity
        self.cooldown_time = cooldown_time
        self.bnt_funding_limit = bnt_funding_limit
        self.alpha = alpha
        self.whitelisted_tokens = whitelisted_tokens

        if price_feeds is None:
            price_feeds = pd.read_parquet(price_feeds_path)
            price_feeds.columns = [col.upper() for col in price_feeds.columns]

        self.price_feeds = price_feeds
        self.global_state = State(
            timestep=timestep,
            network_fee=network_fee,
            trading_fee=trading_fee,
            bnt_min_liquidity=bnt_min_liquidity,
            cooldown_time=cooldown_time,
            bnt_funding_limit=bnt_funding_limit,
            alpha=alpha,
            whitelisted_tokens=whitelisted_tokens,
        )

        self.global_state.init_protocol(
            whitelisted_tokens=whitelisted_tokens, usernames=active_users
        )
        for tkn_name in whitelisted_tokens:
            self.global_state.tokens[tkn_name].trading_fee = trading_fee
            self.global_state.tokens[tkn_name].bnt_funding_limit = bnt_funding_limit
        self.history = []



    @property
    def list_users(self):
        return self.global_state.list_users()

    @property
    def list_tokens(self):
        return self.global_state.list_tokens()

    @property
    def staked_bnt(self):
        return self.global_state.staked_bnt

    @property
    def vault_bnt(self):
        return self.global_state.vault_bnt

    @property
    def protocol_wallet_bnbnt(self):
        return self.global_state.protocol_wallet_bnbnt

    def step(self):
        """Increments the timestep +1"""
        self.global_state.timestep += 1

    @staticmethod
    def load_json(path, **kwargs):
        """Loads json files for convenient simulation.

        Args:
            path: path to json file.
            **kwargs:

        Returns:
            Loaded json
        """
        with open(path, "r") as f:
            return json.load(f, **kwargs)

    @staticmethod
    def save_json(x, path, indent=True, **kwargs):
        """Saves json for convenience.

        Args:
            x: pd.DataFrame to save as json.
            path: path where the file should be saved.
            indent: styling param for json file.
            **kwargs:
        """
        with open(path, "w") as f:
            if indent:
                json.dump(x, f, indent="\t", **kwargs)
            else:
                json.dump(x, f, **kwargs)
        print("Saved to", path)

    @staticmethod
    def json_serialize_datetime(o):
        if isinstance(o, datetime):
            return o.isoformat()

    @staticmethod
    def load_pickle(path):
        print("Unpickling from", path)
        with open(path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def save_pickle(x, path):
        print("Pickling to", path)
        with open(path, "wb") as f:
            return pickle.dump(x, f)

    def iter_transaction_id(self):
        """Increments a new id for each user action for tracking and logging"""
        self.transaction_id += 1
        self.global_state.transaction_id = self.transaction_id

    def export(self):
        """Exports transaction history record"""
        return pd.concat(self.global_state.history)

    def whitelist_token(self, tkn_name):
        """Appends a new token to the whitelisted tokens"""
        return self.global_state.whitelist_tkn(tkn_name)

    def create_user(self, user_name):
        """Creates a new user with a valid wallet"""
        return self.global_state.create_user(user_name)

    def deposit(self, tkn_name, tkn_amt, user_name, timestep):
        """Alias for stake"""
        return self.stake(tkn_name, tkn_amt, user_name, timestep)

    def stake(
            self, tkn_name: str, tkn_amt: Decimal, user_name: str, timestep: int = None
    ):
        """Router for stake tkn or bnt"""

        try:
            tkn_name = tkn_name.lower()
        except ValueError("tkn_name must be type String") as e:
            print(e)

        try:
            tkn_amt = Decimal(tkn_amt)
        except ValueError("tkn_amt must be convertable to type Decimal") as e:
            print(e)

        try:
            wallet_test = self.global_state.users.users[user_name].wallet
        except ValueError(
                "user_name not found. Create a new user by calling the .create_user(user_name) method"
        ) as e:
            print(e)

        if tkn_name == "bnt":
            return self.stake_bnt(tkn_name, tkn_amt, user_name, timestep)
        else:
            return self.stake_tkn(tkn_name, tkn_amt, user_name, timestep)

    def stake_bnt(self, tkn_name, tkn_amt, user_name, timestep):
        """Specific case of .stake() method, see .stake() method docstring"""

        # sense
        state = self.global_state
        if timestep is not None:
            state.timestep = timestep

        # solve
        bnbnt_amt = state.bnbnt_amt(tkn_amt)

        # actuation
        state.users.users[user_name].wallet[tkn_name].tkn_amt -= tkn_amt
        state.users.users[user_name].wallet[tkn_name].bntkn_amt += bnbnt_amt
        state.users.users[user_name].wallet[tkn_name].vbnt_amt += bnbnt_amt
        state.protocol_wallet_bnbnt -= tkn_amt
        self.global_state.latest_tkn = tkn_name
        self.global_state.latest_amt = tkn_amt
        self.global_state.latest_action = "stake_bnt"
        self.global_state.latest_user_name = user_name
        self.iter_transaction_id()
        self.global_state.log_transaction()
        self.global_state = state

    def stake_tkn(self, tkn_name, tkn_amt, user_name, timestep):
        """Specific case of .stake() method, see .stake() method docstring"""

        # sense
        state = self.global_state
        if timestep is not None:
            state.tokens[tkn_name].timestep = timestep

        # solve
        bntkn_amt = state.bntkn_rate(tkn_name) * tkn_amt

        # actuation
        state.users.users[user_name].wallet[tkn_name].tkn_amt -= tkn_amt
        state.users.users[user_name].wallet[tkn_name].bntkn_amt += bntkn_amt
        state.tokens[tkn_name].erc20contracts_bntkn += bntkn_amt
        state.tokens[tkn_name].vault_tkn += tkn_amt
        state.tokens[tkn_name].staked_tkn += tkn_amt

        # sense & solve
        bnt_increase, tkn_increase = pool_depth_adjustment(tkn_name, state)

        # actuation
        state.tokens[tkn_name].bnt_trading_liquidity += bnt_increase
        state.tokens[tkn_name].tkn_trading_liquidity += tkn_increase
        state.tokens[tkn_name].bnt_funding_amount += bnt_increase
        state.tokens[tkn_name].bnt_remaining_funding -= bnt_increase
        state.protocol_wallet_bnbnt -= bnt_increase
        state = mint_protocol_bnt(state, bnt_increase)
        state.update_spot_rate(tkn_name)
        state = state.check_pool_shutdown(tkn_name)
        state.protocol_bnt_check()
        self.global_state.latest_tkn = tkn_name
        self.global_state.latest_amt = tkn_amt
        self.global_state.latest_action = "stake_tkn"
        self.global_state.latest_user_name = user_name
        self.iter_transaction_id()
        self.global_state.log_transaction()
        self.global_state = state

    def trade(self, swap_amount, source_token, target_token, user_name, timestep=None):
        """Main logic to process Trade/Swap transactions. Performs routing to specilized methods for solving individual
        cases.

        Args:
            swap_amount:
            source_token:
            target_token:
            user_name:
            timestep:
        """
        try:
            source_token = source_token.lower()
        except TypeError("source_token must be type String") as e:
            print(e)

        try:
            target_token = target_token.lower()
        except TypeError("target_token must be type String") as e:
            print(e)

        try:
            swap_amount = Decimal(swap_amount)
        except TypeError("swap_amount must be convertable to type Decimal") as e:
            print(e)

        try:
            wallet_test = self.global_state.users.users[user_name].wallet
        except ValueError(
                "user_name not found. Create a new user by calling the .create_user(user_name) method"
        ) as e:
            print(e)

        # sense
        state = self.global_state
        is_trading_enabled_target = state.tokens[target_token].trading_enabled
        is_trading_enabled_source = state.tokens[source_token].trading_enabled
        if timestep is not None:
            state.tokens[target_token].timestep = timestep
        else:
            state.tokens[target_token].timestep = 0

        # solve
        if source_token == "bnt" and is_trading_enabled_target:

            # sense
            (
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
            ) = get_trade_inputs(state, target_token)

            # solve
            state, target_sent_to_user = trade_bnt_for_tkn(
                state,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
                swap_amount,
                tkn_name,
            )

        elif target_token == "bnt" and is_trading_enabled_source:

            # sense
            (
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
            ) = get_trade_inputs(state, source_token)

            # solve
            state, target_sent_to_user = trade_tkn_for_bnt(
                state,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
                swap_amount,
                tkn_name,
            )

        elif (
                source_token != "bnt"
                and target_token != "bnt"
                and is_trading_enabled_source
                and is_trading_enabled_target
        ):

            # sense
            (
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
            ) = get_trade_inputs(state, source_token)

            # solve
            state, intermediate_bnt = trade_tkn_for_bnt(
                state,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
                swap_amount,
                tkn_name,
            )


            # sense
            (
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
            ) = get_trade_inputs(state, target_token)

            # solve
            state, target_sent_to_user = trade_bnt_for_tkn(
                state,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                network_fee,
                intermediate_bnt,
                tkn_name,
            )

        else:
            # Trading is disabled
            swap_amount = Decimal("0")
            target_sent_to_user = Decimal("0")

        # actuate
        state.users.users[user_name].wallet[source_token].tkn_amt -= swap_amount
        state.users.users[user_name].wallet[source_token].tkn_amt += target_sent_to_user
        state.protocol_bnt_check()
        self.global_state.latest_tkn = source_token + "->" + target_token
        self.global_state.latest_amt = swap_amount
        self.global_state.latest_action = "trade"
        self.global_state.latest_user_name = user_name
        self.iter_transaction_id()
        self.global_state = state
        self.global_state.log_transaction()

    def arbitrage_trade(self, state: State, tkn_name: str, user_name: str):
        """Computes the appropriate arbitrage trade on the token_name pool.

        Args:
            source_token (str): The token name being deposited, withdrawn, or traded. (default=None)
            trade_amount (Decimal): The quantity of the token being deposited, withdrawn, or traded. (default=None)
            user (User or LiquidityProvider): The user performing the deposit, withdrawal, or trade. (default=None)
            target_token (str, optional): The target token name in the case of a trade. (default=None)

        """
        price_feeds = self.price_feeds
        tkn_price, bnt_price = state.get_prices(state, tkn_name, price_feeds)
        bnt_trading_liquidity = state.tokens[tkn_name].bnt_trading_liquidity
        tkn_trading_liquidity = state.tokens[tkn_name].tkn_trading_liquidity
        trading_fee = state.tokens[tkn_name].trading_fee
        user_tkn = state.users.users[user_name].wallet[tkn_name].tkn_amt
        user_bnt = state.users.users[user_name].wallet[tkn_name].bnt_amt
        is_trading_enabled = state.tokens[tkn_name].trading_enabled

        if is_trading_enabled:
            (
                trade_amount,
                source_token,
                target_token,
                user_capability,
            ) = process_arbitrage_trade(
                tkn_name,
                tkn_price,
                bnt_price,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                trading_fee,
                user_tkn,
                user_bnt,
            )
            if user_capability:
                self.trade(trade_amount, source_token, target_token, user_name)
            else:
                print(
                    "The user has insufficient funds to close the arbitrage opportunity."
                )
                pass
        else:
            print("Trading is disabled")
            pass

    def begin_cooldown(self, withdraw_value, tkn_name, user_name, timestep=None):
        """Takes the username and a quantity of tkn tokens as inputs.
        The users bntkn is converted into its tkn equivalent, and these values are stored in the pendingWithdrawals with the current timestamp number.
        After a fixed time duration, these items can be retrieved and passed to the withdrawal algorithm.

        Args:
            withdraw_value: The tkn/bnt value to withdraw.
            tkn_name: The name of the token being transacted.
            user_name: The name of the user performing the transaction.
            timestep: The current timestep.

        Returns:
            id_number (int): A unique withdrawal ID number to track the cooldown time to withdraw.
        """

        state = self.global_state
        if timestep is not None:
            state.tokens[tkn_name].timestep = timestep
            state.timestep = timestep
        else:
            state.tokens[tkn_name].timestep = 0
            state.timestep = 0

        return begin_cooldown(state, withdraw_value, tkn_name, user_name)

    def withdraw(self, user_name: str, id_number: int, timestep: int = None):
        """Takes the username and a quantity of bntkn tokens as inputs.
        The users bntkn is converted into its tkn equivalent, and this amount is passed to a complex algorithm.
        The user may receive only tkn, or a mixture of tkn and bnt, depending on the state of the system.
        The staked balances of both bnt and tkn, and the supplies of both bnbnt and bntkn may change.

        Args:
            user_name: Unique user name of the agent.
            id_number: Pending withdrawal ID number.
            timestep: Current timestep.
        """
        state = self.global_state
        if timestep is not None:
            state.timestep = timestep
        else:
            state.timestep = 0
        (
            id_number,
            cooldown_timestep,
            tkn_name,
            pool_token_amt,
            withdraw_value,
            user_name,
        ) = unpack_cool_down_state(state, user_name, id_number)
        withdrawal_fee = state.withdrawal_fee
        cooldown_time = state.cooldown_time

        cool_down_complete = timestep - cooldown_timestep >= cooldown_time

        if tkn_name != "bnt":
            state = state.check_pool_shutdown(tkn_name)
            trading_enabled = state.tokens[tkn_name].trading_enabled
            staked_bnt = state.staked_bnt
            bnbnt_supply = state.erc20contracts_bnbnt
            bnbnt_rate = state.bnbnt_rate
            ema_rate = state.tokens[tkn_name].ema_rate
            spot_rate = state.tokens[tkn_name].spot_rate
            is_price_stable = state.tokens[tkn_name].is_price_stable

            if cool_down_complete and is_price_stable:
                state.users.users[user_name].wallet[tkn_name].pending_withdrawals[
                    id_number
                ].is_complete = True

                bnt_trading_liquidity = state.tokens[tkn_name].bnt_trading_liquidity
                tkn_trading_liquidity = state.tokens[tkn_name].tkn_trading_liquidity
                avg_tkn_trading_liquidity = state.tokens[
                    tkn_name
                ].avg_tkn_trading_liquidity
                vault_tkn = state.tokens[tkn_name].vault_tkn
                tkn_excess = state.tokens[tkn_name].tkn_excess
                staked_tkn = state.tokens[tkn_name].staked_tkn
                trading_fee = state.tokens[tkn_name].trading_fee
                external_protection_vault = state.tokens[
                    tkn_name
                ].external_protection_vault

                solver = WithdrawalAlgorithm(
                    bnt_trading_liquidity=bnt_trading_liquidity,
                    tkn_trading_liquidity=tkn_trading_liquidity,
                    avg_tkn_trading_liquidity=avg_tkn_trading_liquidity,
                    tkn_excess=tkn_excess,
                    staked_tkn=staked_tkn,
                    trading_fee=trading_fee,
                    withdrawal_fee=withdrawal_fee,
                    withdraw_value=withdraw_value,
                )
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                    external_protection_compensation,
                ) = solver.process_withdrawal()

                state.tokens[tkn_name].bnt_trading_liquidity = updated_bnt_liquidity
                state.staked_bnt -= bnt_renounced
                state.vault_bnt -= bnt_renounced
                state.tokens[tkn_name].bnt_remaining_funding += bnt_renounced
                state.tokens[tkn_name].bnt_funding_amount -= bnt_renounced

                bnbnt_renounced = bnbnt_rate * bnt_renounced
                state.erc20contracts_bnbnt -= bnbnt_renounced
                state.protocol_wallet_bnbnt -= bnbnt_renounced
                state.tokens[tkn_name].tkn_trading_liquidity = tkn_trading_liquidity
                # state.tokens[tkn_name].erc20contracts_bntkn -= pool_token_amt
                state.tokens[tkn_name].staked_tkn -= withdraw_value
                state.tokens[tkn_name].vault_tkn -= tkn_sent_to_user
                state.users.users[user_name].wallet[tkn_name].tkn_amt += (
                        tkn_sent_to_user + external_protection_compensation
                )
                state.tokens[
                    tkn_name
                ].external_protection_vault -= external_protection_compensation
                state.users.users[user_name].wallet["bnt"].tkn_amt += bnt_sent_to_user
                state.update_spot_rate(tkn_name)

        else:

            sufficient_vbnt = (
                    state.users.users[user_name].wallet["bnt"].vbnt_amt >= pool_token_amt
            )

            if cool_down_complete and sufficient_vbnt:
                state.users.users[user_name].wallet[tkn_name].pending_withdrawals[
                    id_number
                ].is_complete = True
                bnt_amount = withdraw_value * (1 - withdrawal_fee)
                # state.users.users[user_name].wallet[
                #     tkn_name
                # ].bnbnt_amt -= pool_token_amt
                state.users.users[user_name].wallet[tkn_name].vbnt_amt -= pool_token_amt
                state.users.users[user_name].wallet[tkn_name].bnt_amt += bnt_amount
                state.protocol_wallet_bnbnt += pool_token_amt

        state.protocol_bnt_check()
        self.global_state.latest_tkn = tkn_name
        self.global_state.latest_amt = withdraw_value
        self.global_state.latest_action = "withdraw"
        self.global_state.latest_user_name = user_name
        self.iter_transaction_id()
        self.global_state = state
        self.global_state.log_transaction()

    def dao_msig_init_pools(self, pools: list) -> None:
        """DAO msig initilizes new pools to allow trading once specified conditions are met."""
        [self.enable_trading(token_name) for token_name in pools if token_name != "bnt"]
        pass

    def enable_trading(self, tkn_name):
        """Checks if the masterVault has the minimum bnt equivalent of tkn to justify bootstrapping.
        If the requirements are met, the trading liquidities are increased to twice the minimum threshold.
        Since bnt is minted to the pool, the bnt_funding_amount and bnt_remaining_funding are adjusted accordingly.
        The protocol_wallet bnbntBalance is also adjusted commensurate with the current rate of bnbnt/bnt.
        After bootstrapping, the spotRate == emaRate == virtualRate.

        Args:
            tkn_name: Name of the token being transacted.

        """
        state = self.global_state
        state, tkn_price, bnt_price = state.get_prices(tkn_name, self.price_feeds)
        bnt_min_liquidity = state.bnt_min_liquidity
        vault_tkn = state.tokens[tkn_name].vault_tkn
        bnt_funding_limit = state.tokens[tkn_name].bnt_funding_limit

        # TODO: Change these to @property methods
        def bnt_virtual_balance():
            return Decimal("1") / bnt_price

        def tkn_virtual_balance():
            return Decimal("1") / tkn_price

        def virtual_rate():
            return bnt_virtual_balance() / tkn_virtual_balance()

        def bnt_bootstrap_liquidity() -> Decimal:
            return Decimal("2") * bnt_min_liquidity

        def tkn_bootstrap_liquidity():
            return bnt_bootstrap_liquidity() / virtual_rate()

        def requirements_met():
            return vault_tkn >= tkn_bootstrap_liquidity()

        def bootstrap_rate():
            return bnt_virtual_balance() / tkn_virtual_balance()

        if requirements_met():
            state.tokens[tkn_name].trading_enabled = True
            state.tokens[tkn_name].spot_rate = state.tokens[
                tkn_name
            ].ema_rate = bootstrap_rate()
            state.tokens[tkn_name].bnt_trading_liquidity = bnt_bootstrap_liquidity()
            state.tokens[tkn_name].bnt_funding_amount = bnt_bootstrap_liquidity()
            state.tokens[tkn_name].bnt_remaining_funding = (
                    bnt_funding_limit - bnt_bootstrap_liquidity()
            )
            state.tokens[tkn_name].tkn_trading_liquidity = tkn_bootstrap_liquidity()

            mint_protocol_bnt(state, bnt_bootstrap_liquidity())

        state.protocol_bnt_check()

    def describe_rates(self, decimals: int = 4, report: dict = {}) -> pd.DataFrame:
        """Builds a dataframe of the current system EMA+spot rates.

        Args:
            decimals: The precision number of decimals to include in the dataframe.

        Returns:
            pd.DataFrame
        """
        for tkn in self.global_state.list_tokens():
            if self.global_state.tokens[tkn].spot_rate == Decimal(0):
                self.global_state.tokens[tkn].spot_rate = self.global_state.tokens[
                    tkn
                ].ema_rate
            report[tkn] = [
                f"Spot Rate={self.global_state.tokens[tkn].spot_rate.quantize(Decimal(10) ** -decimals)}, EMA Rate={self.global_state.tokens[tkn].ema_rate.quantize(Decimal(10) ** -decimals)}"
            ]
        return pd.DataFrame(report).T.reset_index()

    def describe(self, rates: bool = False, decimals=6) -> pd.DataFrame:
        """Builds a dataframe of the current system/ledger state.

        Args:
            rates: If true, returns a dataframe showing the EMA+Spot rates instead of ledgers.
            decimals: The precision number of decimals to include in the dataframe.

        Returns:
            pd.DataFrame
        """
        if rates:
            return self.describe_rates(decimals=decimals)

        QDECIMALS = Decimal(10) ** -decimals
        dic = {
            "Trading Liquidity": [""]
                                 + [
                                     f"bnt={self.global_state.tokens[tkn_name].bnt_trading_liquidity.quantize(QDECIMALS)} {tkn_name}="
                                     + str(
                                         self.global_state.tokens[tkn_name].tkn_trading_liquidity.quantize(
                                             QDECIMALS
                                         )
                                     )
                                     for tkn_name in self.global_state.whitelisted_tokens
                                     if tkn_name != "bnt"
                                 ]
                                 + [""],
            "Vault": [f"bnt={self.global_state.vault_bnt.quantize(QDECIMALS)}"]
                     + [
                         f"{tkn_name}="
                         + str(self.global_state.tokens[tkn_name].vault_tkn.quantize(QDECIMALS))
                         for tkn_name in self.global_state.whitelisted_tokens
                         if tkn_name != "bnt"
                     ],
            "Staking": [f"bnt={self.global_state.staked_bnt.quantize(QDECIMALS)}"]
                       + [
                           f"{tkn_name}="
                           + str(self.global_state.tokens[tkn_name].staked_tkn.quantize(QDECIMALS))
                           for tkn_name in self.global_state.whitelisted_tokens
                           if tkn_name != "bnt"
                       ],
            "ERC20 Contracts": [
                                   f"bnbnt={self.global_state.erc20contracts_bnbnt.quantize(QDECIMALS)}"
                               ]
                               + [
                                   f"bn{tkn_name}="
                                   + str(
                                       self.global_state.tokens[tkn_name].erc20contracts_bntkn.quantize(
                                           QDECIMALS
                                       )
                                   )
                                   for tkn_name in self.global_state.whitelisted_tokens
                                   if tkn_name != "bnt"
                               ],
            "Vortex": ["bnt=" + str(self.global_state.vortex_bnt.quantize(QDECIMALS))]
                      + ["" for x in range(len(self.global_state.whitelisted_tokens[:-1]))],
            "External Protection": [
                f"{tkn_name}="
                + str(
                    self.global_state.tokens[
                        tkn_name
                    ].external_protection_vault.quantize(QDECIMALS)
                )
                for tkn_name in self.global_state.whitelisted_tokens
            ],
            "Protocol Wallet": [
                                   f"bnbnt="
                                   + str(self.global_state.protocol_wallet_bnbnt.quantize(QDECIMALS))
                               ]
                               + ["" for tkn_name in self.global_state.whitelisted_tokens[:-1]],
        }
        max_rows = max([len(dic[key]) for key in dic])
        for col in dic:
            while len(dic[col]) < max_rows:
                dic[col].append("")

        return pd.DataFrame(dic)

    def upload_json_simulation(self, path):
        """This method uploads a pre-formatted JSON file containing simulation actions to run and report on.

        Args:
            path: Path to the JSON file containing the simulation parameters.
        """
        json_data = BancorV3.load_json(path)

        self.global_state.network_fee = Decimal(
            json_data["networkFee"].replace("%", "")
        ) * Decimal(".01")
        self.global_state.withdrawal_fee = Decimal(
            json_data["withdrawalFee"].replace("%", "")
        ) * Decimal(".01")
        self.global_state.external_protection_vault = Decimal(
            json_data["epVaultBalance"]
        )
        self.global_settings.decimals = Decimal(json_data["tknDecimals"])
        self.global_state.bnt_min_liquidity = Decimal(json_data["bntMinLiquidity"])
        self.global_state.bnt_funding_limit = Decimal(json_data["bntFundingLimit"])
        for tkn in ["bnt", "tkn"]:
            self.global_state.tokens[tkn].trading_fee = Decimal(
                json_data["tradingFee"].replace("%", "")
            ) * Decimal(".01")

        for user in json_data["users"]:
            user_name = user["id"]
            self.create_user(user_name)
            tknBalance = Decimal(user["tknBalance"])
            bntBalance = Decimal(user["bntBalance"])
            self.global_state.users.users[user_name].wallet["tkn"].tkn_amt = tknBalance
            self.global_state.users.users[user_name].wallet["bnt"].tkn_amt = bntBalance

        self.json_data = json_data

    def deposit_tkn(self, tkn_name, tkn_amt, user_name, timestep):
        """Alias for stake_tkn"""
        return self.stake_tkn(tkn_name, tkn_amt, user_name, timestep)

    def deposit_bnt(self, tkn_name, tkn_amt, user_name, timestep):
        """Alias for stake_bnt"""
        return self.stake_bnt(tkn_name, tkn_amt, user_name, timestep)
