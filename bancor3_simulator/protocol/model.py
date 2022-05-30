"""Main Bancor v3 Protocol Logic"""
import json
import pickle
from datetime import datetime
from decimal import Decimal

import pandas as pd

from bancor3_simulator.core.dataclasses import State
from bancor3_simulator.core.settings import GlobalSettings
from bancor3_simulator.protocol.actions.staking import (
    stake_bnt, stake_tkn,
)
from bancor3_simulator.protocol.actions.trading import (
    get_trade_inputs, trade_bnt_for_tkn, trade_tkn_for_bnt, enable_trading,
)
from bancor3_simulator.protocol.actions.withdraw import (
    unpack_cool_down_state,
    WithdrawalAlgorithm, begin_cooldown
)
from bancor3_simulator.protocol.utils.protocol import handle_logging


class BancorV3:
    """Main Bancor v3 Protocol Logic."""

    global_settings = GlobalSettings()
    name = global_settings.model
    version = global_settings.version

    """
    Args:
        unix_timestamp (int): The Ethereum block number to begin with. (default=1)
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
            unix_timestamp=0,
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
            active_users: list = None,
            transaction_id: int = 0
    ):

        self.json_data = None
        self.transaction_id = transaction_id

        if active_users is None:
            active_users = BancorV3.global_settings.active_users

        if price_feeds is None:
            price_feeds = pd.read_parquet(price_feeds_path)
            price_feeds.columns = [col.lower() for col in price_feeds.columns]

        self.global_state = State(
            transaction_id=transaction_id,
            withdrawal_fee=withdrawal_fee,
            unix_timestamp=unix_timestamp,
            network_fee=network_fee,
            trading_fee=trading_fee,
            bnt_min_liquidity=bnt_min_liquidity,
            cooldown_time=cooldown_time,
            bnt_funding_limit=bnt_funding_limit,
            alpha=alpha,
            whitelisted_tokens=whitelisted_tokens,
            price_feeds=price_feeds
        )

        self.global_state.init_protocol(
            whitelisted_tokens=whitelisted_tokens, usernames=active_users
        )
        for tkn_name in whitelisted_tokens:
            self.global_state.pools[tkn_name].trading_fee = trading_fee
            self.global_state.pools[tkn_name].bnt_funding_limit = bnt_funding_limit
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

    def deposit(self, tkn_name, tkn_amt, user_name, unix_timestamp):
        """Alias for stake"""
        return self.stake(tkn_name, tkn_amt, user_name, unix_timestamp)

    def stake(
            self, tkn_name: str, tkn_amt: Decimal, user_name: str, unix_timestamp: int = None
    ):
        """Router for staking tkn or bnt"""

        try:
            tkn_name = tkn_name.lower()
        except ValueError("tkn_name must be type String") as e:
            print(e)

        try:
            tkn_amt = Decimal(tkn_amt)
        except ValueError("tkn_amt must be convertable to type Decimal") as e:
            print(e)

        try:
            wallet_test = self.global_state.users[user_name].wallet
        except ValueError(
                "user_name not found. Create a new user by calling the .create_user(user_name) method"
        ) as e:
            print(e)

        state = self.global_state
        if tkn_name == "bnt":
            state = stake_bnt(state, tkn_name, tkn_amt, user_name, unix_timestamp)
            action_name = 'stake_bnt'
        else:
            state = stake_tkn(state, tkn_name, tkn_amt, user_name, unix_timestamp)
            action_name = 'stake_tkn'

        self.iter_transaction_id()
        state = handle_logging(tkn_name, tkn_amt, action_name, user_name, self.transaction_id, state)
        self.global_state = state

    def trade(self, swap_amount, source_token, target_token, user_name, unix_timestamp=None):
        """Main logic to process Trade/Swap transactions. Performs routing to specilized methods for solving individual
        cases.

        Args:
            swap_amount:
            source_token:
            target_token:
            user_name:
            unix_timestamp:
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
            wallet_test = self.global_state.users[user_name].wallet
        except ValueError(
                "user_name not found. Create a new user by calling the .create_user(user_name) method"
        ) as e:
            print(e)

        # sense
        state = self.global_state
        is_trading_enabled_target = state.pools[target_token].trading_enabled
        is_trading_enabled_source = state.pools[source_token].trading_enabled
        if unix_timestamp is not None:
            state.pools[target_token].unix_timestamp = unix_timestamp
        else:
            state.pools[target_token].unix_timestamp = 0

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
        state.users[user_name].wallet[source_token].tkn_amt -= swap_amount
        state.users[user_name].wallet[target_token].tkn_amt += target_sent_to_user
        state.protocol_bnt_check()
        self.iter_transaction_id()
        state = handle_logging(source_token + "->" + target_token, swap_amount, "trade", user_name, self.transaction_id,
                               state)
        self.global_state = state

    def begin_cooldown(self, withdraw_value, tkn_name, user_name, unix_timestamp=None):
        state = self.global_state
        if unix_timestamp is not None:
            state.pools[tkn_name].unix_timestamp = unix_timestamp
        else:
            state.pools[tkn_name].unix_timestamp = 0
        id_number = begin_cooldown(state, withdraw_value, tkn_name, user_name)
        return id_number

    def withdraw(self, user_name: str, id_number: int, unix_timestamp: int = None):
        """Takes the username and a quantity of bntkn transactions as inputs.
        The users bntkn is converted into its tkn equivalent, and this amount is passed to a complex algorithm.
        The user may receive only tkn, or a mixture of tkn and bnt, depending on the state of the system.
        The staked balances of both bnt and tkn, and the supplies of both bnbnt and bntkn may change.

        Args:
            user_name: Unique user name of the agent.
            id_number: Pending withdrawal ID number.
            unix_timestamp: Current unix_timestamp.
        """
        state = self.global_state
        if unix_timestamp is not None:
            state.unix_timestamp = unix_timestamp
        else:
            state.unix_timestamp = 0
        (
            id_number,
            cooldown_unix_timestamp,
            tkn_name,
            pool_token_amt,
            withdraw_value,
            user_name,
        ) = unpack_cool_down_state(state, user_name, id_number)
        withdrawal_fee = state.withdrawal_fee
        cooldown_time = state.cooldown_time

        cool_down_complete = unix_timestamp - cooldown_unix_timestamp >= cooldown_time

        if tkn_name != "bnt":
            state = state.check_pool_shutdown(tkn_name)
            trading_enabled = state.pools[tkn_name].trading_enabled
            staked_bnt = state.staked_bnt
            bnbnt_supply = state.erc20contracts_bnbnt
            bnbnt_rate = state.bnbnt_rate
            ema_rate = state.pools[tkn_name].ema_rate
            spot_rate = state.pools[tkn_name].spot_rate
            is_price_stable = state.pools[tkn_name].is_price_stable

            if cool_down_complete and is_price_stable:
                state.users[user_name].wallet[tkn_name].pending_withdrawals[
                    id_number
                ].is_complete = True

                bnt_trading_liquidity = state.pools[tkn_name].bnt_trading_liquidity
                tkn_trading_liquidity = state.pools[tkn_name].tkn_trading_liquidity
                avg_tkn_trading_liquidity = state.pools[
                    tkn_name
                ].avg_tkn_trading_liquidity
                vault_tkn = state.pools[tkn_name].vault_tkn
                tkn_excess = state.pools[tkn_name].tkn_excess
                staked_tkn = state.pools[tkn_name].staked_tkn
                trading_fee = state.pools[tkn_name].trading_fee
                external_protection_vault = state.pools[
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

                state.pools[tkn_name].bnt_trading_liquidity = updated_bnt_liquidity
                state.staked_bnt -= bnt_renounced
                state.vault_bnt -= bnt_renounced
                # state.pools[tkn_name].bnt_remaining_funding += bnt_renounced
                state.pools[tkn_name].bnt_funding_amount -= bnt_renounced

                bnbnt_renounced = bnbnt_rate * bnt_renounced
                state.erc20contracts_bnbnt -= bnbnt_renounced
                state.protocol_wallet_bnbnt -= bnbnt_renounced
                state.pools[tkn_name].tkn_trading_liquidity = tkn_trading_liquidity
                # state.pools[tkn_name].erc20contracts_bntkn -= pool_token_amt
                state.pools[tkn_name].staked_tkn -= withdraw_value
                state.pools[tkn_name].vault_tkn -= tkn_sent_to_user
                state.users[user_name].wallet[tkn_name].tkn_amt += (
                        tkn_sent_to_user + external_protection_compensation
                )
                state.pools[
                    tkn_name
                ].external_protection_vault -= external_protection_compensation
                state.users[user_name].wallet["bnt"].tkn_amt += bnt_sent_to_user
                state.update_spot_rate(tkn_name)

        else:

            sufficient_vbnt = (
                    state.users[user_name].wallet["bnt"].vbnt_amt >= pool_token_amt
            )

            if cool_down_complete and sufficient_vbnt:
                state.users[user_name].wallet[tkn_name].pending_withdrawals[
                    id_number
                ].is_complete = True
                bnt_amount = withdraw_value * (1 - withdrawal_fee)
                state.users[user_name].wallet[tkn_name].vbnt_amt -= pool_token_amt
                state.users[user_name].wallet['bnt'].tkn_amt += bnt_amount
                state.protocol_wallet_bnbnt += pool_token_amt

        state.protocol_bnt_check()
        self.iter_transaction_id()
        state = handle_logging(tkn_name, withdraw_value, "withdraw", user_name, self.transaction_id, state)
        self.global_state = state

    def dao_msig_init_pools(self, pools: list) -> None:
        """DAO msig initilizes new pools to allow trading once specified conditions are met."""
        state = self.global_state
        for token_name in pools:
            if token_name != "bnt":
                state = enable_trading(state, token_name)
        pass

    def describe_rates(self, decimals: int = 4, report: dict = {}) -> pd.DataFrame:
        """Builds a dataframe of the current system EMA+spot rates.

        Args:
            decimals: The precision number of decimals to include in the dataframe.

        Returns:
            pd.DataFrame
        """
        for tkn in self.global_state.list_tokens():
            if self.global_state.pools[tkn].spot_rate == Decimal(0):
                self.global_state.pools[tkn].spot_rate = self.global_state.pools[
                    tkn
                ].ema_rate
            report[tkn] = [
                f"Spot Rate={self.global_state.pools[tkn].spot_rate.quantize(Decimal(10) ** -decimals)}, EMA Rate={self.global_state.pools[tkn].ema_rate.quantize(Decimal(10) ** -decimals)}"
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
                                     f"bnt={self.global_state.pools[tkn_name].bnt_trading_liquidity.quantize(QDECIMALS)} {tkn_name}="
                                     + str(
                                         self.global_state.pools[tkn_name].tkn_trading_liquidity.quantize(
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
                         + str(self.global_state.pools[tkn_name].vault_tkn.quantize(QDECIMALS))
                         for tkn_name in self.global_state.whitelisted_tokens
                         if tkn_name != "bnt"
                     ],
            "Staking": [f"bnt={self.global_state.staked_bnt.quantize(QDECIMALS)}"]
                       + [
                           f"{tkn_name}="
                           + str(self.global_state.pools[tkn_name].staked_tkn.quantize(QDECIMALS))
                           for tkn_name in self.global_state.whitelisted_tokens
                           if tkn_name != "bnt"
                       ],
            "ERC20 Contracts": [
                                   f"bnbnt={self.global_state.erc20contracts_bnbnt.quantize(QDECIMALS)}"
                               ]
                               + [
                                   f"bn{tkn_name}="
                                   + str(
                                       self.global_state.pools[tkn_name].erc20contracts_bntkn.quantize(
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
                    self.global_state.pools[
                        tkn_name
                    ].external_protection_vault.quantize(QDECIMALS)
                )
                for tkn_name in self.global_state.whitelisted_tokens
            ],
            "Protocol WalletState": [
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
        trading_fee = Decimal(
            json_data["tradingFee"].replace("%", "")
        ) * Decimal(".01")

        # set params
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
        self.global_state.trading_fee = trading_fee

        for tkn in ["bnt", "tkn"]:
            self.global_state.pools[tkn].trading_fee = trading_fee
            self.global_state.pools[tkn].bnt_min_liquidity = self.global_state.bnt_min_liquidity
            self.global_state.pools[tkn].bnt_funding_limit = self.global_state.bnt_funding_limit

        for user in json_data["users"]:
            user_name = user["id"]
            self.create_user(user_name)
            tknBalance = Decimal(user["tknBalance"])
            bntBalance = Decimal(user["bntBalance"])
            self.global_state.users[user_name].wallet["tkn"].tkn_amt = tknBalance
            self.global_state.users[user_name].wallet["bnt"].tkn_amt = bntBalance

        # set data to iterate
        self.json_data = json_data

    def step(self):
        """Increments the unix_timestamp +1"""
        self.global_state.unix_timestamp += 1

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

    def export(self):
        """Exports transaction history record"""
        return pd.concat(self.global_state.history)

    def whitelist_token(self, tkn_name):
        """Appends a new token to the whitelisted transactions"""
        return self.global_state.whitelist_tkn(tkn_name)

    def create_user(self, user_name):
        """Creates a new user with a valid wallet"""
        return self.global_state.create_user(user_name)
