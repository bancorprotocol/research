# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Main BancorDapp class and simulator module interface."""

import json
import pickle
import cloudpickle
import pandas as pd

from bancor_research.bancor_simulator.v3.spec.actions import *
from bancor_research.bancor_simulator.v3.spec.rewards import *
from bancor_research.bancor_simulator.v3.spec.state import *


def userAmount(state: State, tkn_name: str, user_name: str, amount: str):
    if amount.endswith("%"):
        return get_user_balance(state, user_name, tkn_name) * Decimal(amount[:-1]) / 100
    return Decimal(amount)


class BancorDapp:
    """Main BancorDapp class and simulator module interface."""

    name = MODEL

    """
    Args:
        timestamp (int): The Ethereum block number to begin with. (default=1)
        bnt_min_liquidity (Decimal): The minimum liquidity needed to bootstrap a pool.
        withdrawal_fee (Decimal): The global exit (withdrawal) fee. (default=0.002)
        coolown_time (int): The cooldown period in days. (default=7)
        network_fee (Decimal): The global network fee. (default=1.002)
        whitelisted_tokens (Dict[str]): List of token tickernames indicating whitelist status approval.
                                        (default=["dai", "eth", "link", "bnt", "tkn", "wbtc"])
        price_feeds_path (str): Path to a file containing price feeds.
        price_feeds (pandas.DataFrame): A pandas.DataFrame containing the price feed information.
    """

    def __init__(
        self,
        timestamp: int = DEFAULT_TIMESTAMP,
        bnt_min_liquidity: Decimal = DEFAULT_BNT_MIN_LIQUIDITY,
        withdrawal_fee: Decimal = DEFAULT_WITHDRAWAL_FEE,
        cooldown_time: int = DEFAULT_COOLDOWN_TIME,
        network_fee: Decimal = DEFAULT_NETWORK_FEE,
        whitelisted_tokens=DEFAULT_WHITELIST,
        price_feeds_path: str = DEFAULT_PRICE_FEEDS_PATH,
        price_feeds: PandasDataFrame = DEFAULT_PRICE_FEEDS,
    ):

        transaction_id = 0

        self.json_data = None
        self.transaction_id = transaction_id

        if price_feeds is None:
            price_feeds = pd.read_parquet(price_feeds_path)
            price_feeds.columns = [col.lower() for col in price_feeds.columns]

        for tkn_name in whitelisted_tokens:
            assert tkn_name in price_feeds.columns, (
                f"Whitelisted token `{tkn_name}` not found in price feed. "
                f"Add `{tkn_name}` to the price feed, "
                f"or remove `{tkn_name}` from the whitelisted tokens."
            )

        state = State(
            transaction_id=transaction_id,
            timestamp=timestamp,
            whitelisted_tokens=whitelisted_tokens,
            price_feeds=price_feeds,
        )

        state = init_protocol(
            state=state,
            whitelisted_tokens=whitelisted_tokens,
            usernames=[],
            cooldown_time=cooldown_time,
            network_fee=network_fee,
            bnt_min_liquidity=bnt_min_liquidity,
            withdrawal_fee=withdrawal_fee,
        )

        # initialize bnt
        state.tokens["bnt"] = Tokens(tkn_name="bnt")
        state.tokens["bnbnt"] = Tokens(tkn_name="bnbnt")
        state.tokens["vbnt"] = Tokens(tkn_name="vbnt")

        state.json_export = {"users": [], "operations": []}
        self._backup_states = {}
        self._global_state = state
        self.history = []

    @property
    def backup_states(self):
        return [i for i in self._backup_states]

    @property
    def global_state(self):
        return self._global_state

    @global_state.setter
    def global_state(self, value):
        self._global_state = value

    def copy_state(self, copy_type: str, state: State = None, timestamp: int = 0):
        """
        Saves a backup of the current global state to revert_state back to if desired.
        """
        assert copy_type in ["initial", "end"], "copy_type must be 'initial' or 'end'"

        if state is None:
            s = self.global_state.copy()
        else:
            s = state.copy()

        if timestamp is None:
            ts = s.timestamp
        else:
            ts = timestamp
        self._backup_states[f"{copy_type}_{ts}"] = s.copy()
        return s

    def update_state(self, state: State):
        """
        Updates the global state at the end of each action.
        """
        self.global_state = self.copy_state("end", state)

    def next_transaction(self, state: State):
        """
        Increments a new id and state for each action
        """
        self.update_state(state)
        self.transaction_id += 1

    def get_state(
        self, copy_type: str = "initial", state: State = None, timestamp: int = 0
    ):
        """
        Creates a copy of the global state which will modified during a new action.
        """
        return self.copy_state(copy_type=copy_type, state=state, timestamp=timestamp)

    def revert_state(self, timestamp):
        """
        Reverts the state of the bancor network to a previously saved state.
        """
        self.global_state = self._backup_states[timestamp]

    def show_history(self):
        """
        Displays the history of the bancor network in a dataframe.
        """
        return pd.concat(
            [
                self.global_state.history[i]
                for i in range(len(self.global_state.history))
            ]
        )

    def deposit(
        self,
        tkn_name: str,
        tkn_amt_abs_or_rel: str,
        user_name: str,
        timestamp: int = 0,
        bntkn: Decimal = Decimal("0"),
        action_name="deposit",
    ):
        """
        Top level logic for deposit actions.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = userAmount(state, tkn_name, user_name, tkn_amt_abs_or_rel)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        if tkn_name == "bnt":
            state = deposit_bnt(
                state=state, tkn_name=tkn_name, tkn_amt=tkn_amt, user_name=user_name
            )
        else:
            state = handle_vandalism_attack(state, tkn_name)
            state = deposit_tkn(
                state=state, tkn_name=tkn_name, tkn_amt=tkn_amt, user_name=user_name
            )
        self.next_transaction(state)
        handle_logging(
            tkn_name=tkn_name,
            tkn_amt=tkn_amt,
            action_name=action_name,
            user_name=user_name,
            transaction_id=self.transaction_id,
            state=state,
        )
        return bntkn

    def trade(
        self,
        tkn_amt_abs_or_rel: str,
        source_token: str,
        target_token: str,
        user_name: str,
        timestamp: int,
        transaction_type: str = "trade",
    ):
        """
        Main logic for trade actions.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = userAmount(state, tkn_name, user_name, tkn_amt_abs_or_rel)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, source_token, tkn_amt, user_name, timestamp
        )
        state = process_trade(
            state, tkn_amt, source_token, target_token, user_name, timestamp
        )
        self.next_transaction(state)
        handle_logging(
            source_token + "->" + target_token,
            tkn_amt,
            transaction_type,
            user_name,
            self.transaction_id,
            state,
        )

    def begin_cooldown(
        self,
        tkn_amt_abs_or_rel: str,
        tkn_name: str,
        user_name: str,
        timestamp: int = 0,
        action_name: str = "begin cooldown",
    ):
        """
        Begin the withdrawal cooldown operation.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = userAmount(state, tkn_name, user_name, tkn_amt_abs_or_rel)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        state, id_number = begin_withdrawal_cooldown(
            state, tkn_amt, tkn_name, user_name
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, action_name, user_name, self.transaction_id, state
        )
        return id_number

    def withdraw(
        self,
        user_name: str,
        id_number: int,
        timestamp: int = 0,
        tkn_name: str = None,
        transaction_type: str = "withdraw",
    ):
        """
        Main withdrawal logic based on the withdraw algorithm of the BIP15 spec.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state = process_withdrawal(state, user_name, id_number, timestamp, tkn_name)

        self.next_transaction(state)
        state = handle_logging(
            tkn_name,
            Decimal(0),
            transaction_type,
            user_name,
            self.transaction_id,
            state,
        )

    def enable_trading(
        self,
        tkn_name: str,
        timestamp: int = 0,
        transaction_type: str = "enableTrading",
        user_name: str = "protocol",
    ) -> None:
        """
        DAO msig initilizes new tokens to allow trading once specified conditions are met.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state.timestamp = timestamp
        tkn_name = tkn_name.lower()
        state = enable_trading(state, tkn_name)
        self.next_transaction(state)
        handle_logging(
            tkn_name,
            Decimal("0"),
            transaction_type,
            user_name,
            state.transaction_id,
            state,
        )

    def describe(self, decimals: int = -1):
        """
        Describes the state ledger in a format similar to BIP15 documentation.
        """
        table = {}

        state = self.global_state

        reserve_tokens = ["bnt"] + [tkn for tkn in state.whitelisted_tokens]
        pool_tokens = ["bnbnt"] + ["bn" + tkn for tkn in state.whitelisted_tokens]

        # Iterate all tokens
        for tkn_name in reserve_tokens + pool_tokens + ["vbnt"]:
            table[tkn_name] = {}
            for account in state.users:
                table[tkn_name][tuple([1, "Account", account])] = (
                    state.users[account].wallet[tkn_name].balance
                )

        # Iterate all reserve tokens except bnt
        for tkn_name in [tkn_name for tkn_name in reserve_tokens if tkn_name != "bnt"]:
            table[tkn_name][tuple([2, "Pool", "a: TKN Staked Balance"])] = state.tokens[
                tkn_name
            ].staking_ledger.balance
            table[tkn_name][
                tuple([2, "Pool", "b: TKN Trading Liquidity"])
            ] = state.tokens[tkn_name].tkn_trading_liquidity.balance
            table[tkn_name][
                tuple([2, "Pool", "c: BNT Trading Liquidity"])
            ] = state.tokens[tkn_name].bnt_trading_liquidity.balance
            table[tkn_name][
                tuple([2, "Pool", "d: BNT Current Funding"])
            ] = state.tokens[tkn_name].bnt_funding_amt.balance
            table[tkn_name][tuple([2, "Pool", "e: Spot Rate"])] = state.tokens[
                tkn_name
            ].spot_rate
            table[tkn_name][tuple([2, "Pool", "f: Average Rate"])] = state.tokens[
                tkn_name
            ].ema_rate
            table[tkn_name][
                tuple([2, "Pool", "g: Average Inverse Rate"])
            ] = state.tokens[tkn_name].inv_ema_rate

        # Iterate all reserve tokens
        for tkn_name in reserve_tokens:
            table[tkn_name][tuple([3, "Network", "Master Vault"])] = state.tokens[
                tkn_name
            ].master_vault.balance
            table[tkn_name][tuple([3, "Network", "Protection Vault"])] = state.tokens[
                tkn_name
            ].external_protection_vault.balance
            table["bn" + tkn_name][
                tuple([3, "Network", "Rewards Vault"])
            ] = state.tokens[tkn_name].standard_rewards_vault.balance
            table["bn" + tkn_name][
                tuple([3, "Network", "Protocol Equity"])
            ] = state.tokens[tkn_name].protocol_wallet_pooltokens.balance

        df = pd.DataFrame(table).sort_index()
        return df.applymap(lambda x: round(x, decimals)) if decimals >= 0 else df

    def export(self):
        """
        Exports transaction history record
        """
        return pd.concat(self.global_state.history)

    def whitelist_token(self, tkn_name: str, timestamp: int = 0):
        """
        Creates a new whitelisted token with initialized starting balances
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state.create_whitelisted_tkn(tkn_name)
        self.next_transaction(state)
        handle_logging(
            tkn_name,
            Decimal("0"),
            f"whitelist_{tkn_name}",
            "NA",
            state.transaction_id,
            state,
        )

    def create_user(self, user_name: str, timestamp: int = 0):
        """
        Creates a new user with a valid wallet
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state.create_user(user_name)
        self.next_transaction(state)
        handle_logging(
            "NA", Decimal("0"), f"create_{user_name}", "NA", state.transaction_id, state
        )

    def distribute_autocompounding_program(
        self,
        tkn_name: str = "tkn",
        timestamp: int = 0,
        transaction_type: str = "distribute_autocompounding_program",
        user_name: str = "protocol",
    ):
        """
        Distribute auto-compounding program.
        """
        tkn_name = tkn_name.lower()
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state = distribute_autocompounding_program(
            state=state, tkn_name=tkn_name, timestamp=timestamp
        )
        self.next_transaction(state)

    def load_json_simulation(self, path, tkn_name="tkn", timestamp: int = 0):
        """
        Loads a JSON file containing simulation modules to run and report on.
        """
        tkn_name = tkn_name.lower()
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        json_data = BancorDapp.load_json(path)
        state = setup_json_simulation(state, json_data, tkn_name)
        self.next_transaction(state)

    def create_autocompounding_program(
        self,
        state: State,
        tkn_name: str,
        user_name: str,
        total_rewards: Decimal,
        start_time: int,
        distribution_type: str,
        timestamp: int,
        half_life_days: int = 0,
        total_duration_in_days: Decimal = Decimal("0"),
        total_duration_in_seconds: Decimal = Decimal("0"),
        transaction_type: str = "create autocompounding program",
    ):
        """
        Creates a new autocompounding program.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        if total_duration_in_seconds == 0 and total_duration_in_days != 0:
            total_duration_in_seconds = Decimal(f"{SECONDS_PER_DAY}") * Decimal(
                total_duration_in_days
            )

        program_id = state.autocompounding_programs_count + 1

        if tkn_name != "bnt":
            program_wallet_bntkn = self.deposit(
                tkn_name=tkn_name,
                tkn_amt=total_rewards,
                user_name=user_name,
                timestamp=timestamp,
            )
            state.decrease_protocol_wallet_balance(tkn_name, program_wallet_bntkn)
        else:
            program_wallet_bntkn = get_protocol_wallet_balance(state, "bnt")

        if timestamp >= start_time:
            is_active = True
        else:
            is_active = False

        # Add the program to the rest.
        state.autocompounding_reward_programs[tkn_name] = AutocompoundingProgram(
            id=program_id,
            tkn_name=tkn_name,
            owner_id=user_name,
            is_active=is_active,
            half_life_days=half_life_days,
            total_duration_in_seconds=total_duration_in_seconds,
            start_time=start_time,
            created_at=timestamp,
            total_rewards=Token(balance=total_rewards),
            remaining_rewards=Token(balance=total_rewards),
            distribution_type=distribution_type,
        )

        self.next_transaction(state)
        handle_logging(
            tkn_name=tkn_name,
            tkn_amt=total_rewards,
            action_name=transaction_type,
            user_name=user_name,
            transaction_id=self.transaction_id,
            state=state,
        )

    def burn_pool_tokens(
        self,
        tkn_name: str,
        tkn_amt_abs_or_rel: str,
        user_name: str,
        timestamp: int = 0,
        transaction_type: str = "burnPoolTokenTKN",
    ):
        """
        Used for testing vandalism attack.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = userAmount(state, tkn_name, user_name, tkn_amt_abs_or_rel)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        if tkn_name != "bnt":
            state.decrease_pooltoken_balance(tkn_name, tkn_amt)
            state.decrease_user_balance(
                user_name, get_pooltoken_name(tkn_name), tkn_amt
            )
            self.next_transaction(state)
            handle_logging(
                tkn_name,
                tkn_amt,
                transaction_type,
                user_name,
                self.transaction_id,
                state,
            )

    def create_standard_rewards_program(
        self,
        tkn_name: str,
        rewards_amt: str,
        start_time: int,
        end_time: int,
        user_name: str,
        timestamp: int,
        transaction_type="create_standard_rewards_program",
    ):
        """
        Create a standard rewards program for a given token.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = Decimal(rewards_amt)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        state = create_standard_reward_program(
            state=state,
            tkn_name=tkn_name,
            rewards_token="bnt",
            total_rewards=tkn_amt,
            start_time=start_time,
            end_time=end_time,
            curr_time=timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )

    def join_standard_rewards_program(
        self,
        tkn_name: str,
        tkn_amt_abs_or_rel: str,
        user_name: str,
        program_id: int,
        timestamp: int = 0,
        transaction_type="join_standard_rewards_program",
    ):
        """
        Join the standard rewards program for a given user.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = userAmount(state, tkn_name, user_name, tkn_amt_abs_or_rel)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        state = join_standard_reward_program(
            state=state,
            user_name=user_name,
            id=program_id,
            pool_token_amount=tkn_amt,
            timestamp=timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )

    def leave_standard_rewards_program(
        self,
        tkn_name: str,
        tkn_amt_abs_or_rel: str,
        user_name: str,
        program_id: int,
        timestamp: int = 0,
        transaction_type="leave_standard_rewards_program",
    ):
        """
        Leave the standard rewards program for a given user.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = userAmount(state, tkn_name, user_name, tkn_amt_abs_or_rel)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        state = leave_standard_reward_program(
            state=state,
            user_name=user_name,
            id=program_id,
            pool_token_amount=tkn_amt,
            timestamp=timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )

    def claim_standard_rewards(
        self,
        tkn_name: str,
        user_name: str,
        program_ids: List[int],
        timestamp: int = 0,
        transaction_type: str = "claim_standard_rewards",
    ):
        """
        Claim standard rewards for a given reward program and user.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, Decimal(0), user_name, timestamp
        )
        state = claim_standard_rewards(
            state=state,
            user_name=user_name,
            ids=program_ids,
            timestamp=timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )

    def set_user_balance(
        self,
        user_name: str,
        tkn_name: str,
        tkn_amt_abs: str,
        timestamp: int = 0,
        transaction_type: str = "set user balance",
    ):
        """
        Sets user balance at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_amt = Decimal(tkn_amt_abs)
        state, tkn_name, tkn_amt, user_name = validate_input(
            state, tkn_name, tkn_amt, user_name, timestamp
        )
        state.set_user_balance(user_name, tkn_name, tkn_amt)
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )

    def step(self):
        self.global_state.step()

    def set_state(self, state: State):
        self.global_state = state

    def set_trading_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set trading fee",
        user_name: str = "protocol",
    ):
        """
        Sets the system trading fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state.set_trading_fee(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def set_network_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set network fee",
        user_name: str = "protocol",
    ):
        """
        Sets the system network fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state.set_network_fee(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def set_withdrawal_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set withdrawal fee",
        user_name: str = "protocol",
    ):
        """
        Sets the system withdrawal fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state.set_withdrawal_fee(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def set_bnt_funding_limit(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set bnt funding limit",
        user_name: str = "protocol",
    ):
        """
        Sets the system withdrawal fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state.set_bnt_funding_limit(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def save(self, file_path, pickle_protocol=cloudpickle.DEFAULT_PROTOCOL):
        """
        Saves state at file path.
        """
        with open(file_path, "wb") as f:
            cloudpickle.dump(self, f, protocol=pickle_protocol)
