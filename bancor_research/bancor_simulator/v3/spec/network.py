# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Main BancorDapp class and simulator module interface."""

import cloudpickle, pandas

from bancor_research.bancor_simulator.v3.spec.actions import *
from bancor_research.bancor_simulator.v3.spec.rewards import *
from bancor_research.bancor_simulator.v3.spec.state import *

from bancor_research import DataFrame, read_price_feeds


def to_decimal(percent: str):
    try:
        return Decimal(percent[:-1]) / 100
    except TypeError:
        return percent


def to_user_amount(state: State, tkn_name: str, user_name: str, amount: str):
    if amount.endswith("%"):
        return get_user_balance(state, user_name, tkn_name) * to_decimal(amount)
    return Decimal(amount)


class BancorDapp:
    """Main BancorDapp class and simulator module interface."""

    """
    Args:
        timestamp (integer, default = 0): The Ethereum block number to begin the simulation with
        bnt_min_liquidity (numeric string, default = 10000): The minimum BNT liquidity needed to bootstrap a pool
        withdrawal_fee (percentage string, default = 0.25%): The global exit (withdrawal) fee
        coolown_time (integer, default = 7 days): The cooldown period in seconds
        network_fee (percentage string, default = 20%): The global network fee
        whitelisted_tokens (dictionary): The configuration of each pool (default = ["eth", "link", "tkn", "wbtc"]):
        - trading_fee (percentage string, default = 1%): The trading fee of the pool
        - bnt_funding_limit (numeric string, default = 1000000): The BNT funding limit of the pool
        price_feeds_path (string): The path to a file containing price feeds
        price_feeds (dictionary): The price feeds to use instead of the file
    """

    def __init__(
        self,
        timestamp: int = DEFAULT.TIMESTAMP,
        bnt_min_liquidity: str = DEFAULT.BNT_MIN_LIQUIDITY,
        withdrawal_fee: str = DEFAULT.WITHDRAWAL_FEE,
        cooldown_time: int = DEFAULT.COOLDOWN_TIME,
        network_fee: str = DEFAULT.NETWORK_FEE,
        whitelisted_tokens=DEFAULT.WHITELIST,
        price_feeds_path: str = DEFAULT.PRICE_FEEDS_PATH,
        price_feeds: PandasDataFrame = DEFAULT.PRICE_FEEDS,
        log_state: bool = True,
    ):

        transaction_id = 0

        self.json_data = None
        self.transaction_id = transaction_id

        self.price_feeds = (
            price_feeds
            if price_feeds is not None
            else read_price_feeds(price_feeds_path)
        )

        for tkn_name in whitelisted_tokens:
            assert tkn_name in price_feeds.columns, (
                f"Whitelisted token `{tkn_name}` not found in price feed. "
                f"Add `{tkn_name}` to the price feed, "
                f"or remove `{tkn_name}` from the whitelisted tokens."
            )

        whitelisted_tokens = {
            k: {
                "decimals": v["decimals"],
                "trading_fee": to_decimal(v["trading_fee"]),
                "bnt_funding_limit": Decimal(v["bnt_funding_limit"]),
                "ep_vault_balance": Decimal(v["ep_vault_balance"]),
            }
            for k, v in whitelisted_tokens.items()
        }

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
            network_fee=to_decimal(network_fee),
            bnt_min_liquidity=Decimal(bnt_min_liquidity),
            withdrawal_fee=to_decimal(withdrawal_fee),
        )

        state.json_export = {"users": [], "operations": []}
        self._backup_states = {}
        self._global_state = state
        self.history = []
        self.log_state = log_state

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
            s.timestamp = timestamp
        self._backup_states[f"{copy_type}_{ts}"] = s.copy()
        return s

    def update_state(self, state: State, timestamp: int = 0):
        """
        Updates the global state at the end of each action.
        """
        self.global_state = self.copy_state("end", state, timestamp)

    def next_transaction(self, state: State, timestamp: int = 0):
        """
        Increments a new id and state for each action
        """
        if self.log_state:
            self.update_state(state, timestamp)
        self.transaction_id += 1

    def get_state(
        self, copy_type: str = "initial", state: State = None, timestamp: int = 0
    ):
        """
        Creates a copy of the global state which will modified during a new action.
        """
        if self.log_state:
            return self.copy_state(
                copy_type=copy_type, state=state, timestamp=timestamp
            )
        else:
            self.global_state.timestamp = timestamp
            return self.global_state

    def revert_state(self, timestamp):
        """
        Reverts the state of the bancor network to a previously saved state.
        """
        self.global_state = self._backup_states[timestamp]

    def show_history(self):
        """
        Displays the history of the bancor network in a dataframe.
        """
        return pandas.concat(
            [
                self.global_state.history[i]
                for i in range(len(self.global_state.history))
            ]
        )

    def deposit(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        timestamp: int = 0,
        action_name="deposit",
    ):
        """
        Top level logic for deposit actions.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, tkn_name, user_name, tkn_amt)
        if tkn_name == "bnt":
            state = deposit_bnt(
                state=state, tkn_name=tkn_name, tkn_amt=tkn_amt, user_name=user_name
            )
        else:
            state = handle_vandalism_attack(state, tkn_name)
            state = deposit_tkn(
                state=state, tkn_name=tkn_name, tkn_amt=tkn_amt, user_name=user_name
            )
        state = handle_logging(
            tkn_name=tkn_name,
            tkn_amt=tkn_amt,
            action_name=action_name,
            user_name=user_name,
            transaction_id=self.transaction_id,
            state=state,
        )
        self.next_transaction(state)

    def trade(
        self,
        tkn_amt: str,
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
        state, source_token, user_name = validate_input(
            state, source_token, user_name, timestamp
        )
        state, target_token, user_name = validate_input(
            state, target_token, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, source_token, user_name, tkn_amt)
        state = process_trade(
            state, tkn_amt, source_token, target_token, user_name, timestamp
        )
        state = handle_logging(
            source_token + "->" + target_token,
            tkn_amt,
            transaction_type,
            user_name,
            self.transaction_id,
            state,
        )
        self.next_transaction(state)

    def begin_cooldown_by_rtkn(
        self,
        tkn_amt: str,
        tkn_name: str,
        user_name: str,
        timestamp: int = 0,
        action_name: str = "begin cooldown by reserve token amount",
    ):
        """
        Begin the withdrawal cooldown operation by specifying the output amount of reserve tokens.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, tkn_name, user_name, tkn_amt)
        id_number = begin_withdrawal_cooldown_by_rtkn(
            state, tkn_amt, tkn_name, user_name
        )
        state = handle_logging(
            tkn_name, tkn_amt, action_name, user_name, self.transaction_id, state
        )
        self.next_transaction(state)

        return id_number

    def begin_cooldown_by_ptkn(
        self,
        tkn_amt: str,
        tkn_name: str,
        user_name: str,
        timestamp: int = 0,
        action_name: str = "begin cooldown by pool token amount",
    ):
        """
        Begin the withdrawal cooldown operation by specifying the intput amount of pool tokens.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, "bn" + tkn_name, user_name, tkn_amt)
        id_number = begin_withdrawal_cooldown_by_ptkn(
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
        transaction_type: str = "withdraw",
    ):
        """
        Main withdrawal logic based on the withdraw algorithm of the BIP15 spec.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = state.users[user_name].pending_withdrawals[id_number].tkn_name
        state = process_withdrawal(state, user_name, id_number, timestamp)
        state = handle_logging(
            tkn_name,
            Decimal(0),
            transaction_type,
            user_name,
            self.transaction_id,
            state,
        )
        self.next_transaction(state)

    def enable_trading(
        self,
        tkn_name: str,
        tkn_price: str = "",
        bnt_price: str = "",
        timestamp: int = 0,
        transaction_type: str = "enableTrading",
    ) -> None:
        """
        DAO msig initilizes new tokens to allow trading once specified conditions are met.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        if tkn_price:
            state.price_feeds.at[state.timestamp, tkn_name] = tkn_price
        if bnt_price:
            state.price_feeds.at[state.timestamp, "bnt"] = bnt_price
        state = enable_trading(state, tkn_name)
        state = handle_logging(
            tkn_name,
            Decimal("0"),
            transaction_type,
            user_name,
            state.transaction_id,
            state,
        )
        self.next_transaction(state)

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
            for account in [user for user in state.users if user != protocol_user]:
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
            ] = state.tokens[tkn_name].external_rewards_vault.balance
            table["bn" + tkn_name][
                tuple([3, "Network", "Protocol Equity"])
            ] = state.tokens[tkn_name].protocol_wallet_pooltokens.balance


        # Iterate only bnt
        table["bnt"][tuple([3, "Network", "BNT Staked Balance"])] = state.tokens[
            "bnt"
        ].staking_ledger.balance
        table["bnt"][
                tuple([3, "Network", "Vortex"])
            ] = state.tokens["bnt"].vortex_ledger.balance

        df = DataFrame(table).fillna(0).sort_index()
        return df.applymap(lambda x: round(x, decimals)) if decimals >= 0 else df

    def export(self):
        """
        Exports transaction history record
        """
        return pandas.concat(self.global_state.history)

    def whitelist_token(self, tkn_name: str, timestamp: int = 0):
        """
        Creates a new whitelisted token with initialized starting balances
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        tkn_name = tkn_name.lower()
        state.price_feeds[tkn_name] = state.price_feeds["bnt"].values

        state.create_whitelisted_tkn(tkn_name)
        handle_whitelisting_tokens(state)

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

    def process_ac_rewards_program(
        self,
        tkn_name: str,
        timestamp: int = 0,
        transaction_type: str = "process autocompounding rewards program",
    ):
        """
        Processes autocompounding rewards program.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        state = process_ac_rewards_program(
            state=state, tkn_name=tkn_name, timestamp=timestamp
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name=tkn_name,
            user_name=user_name,
            tkn_amt=Decimal(0),
            action_name=transaction_type,
            transaction_id=self.transaction_id,
            state=state,
        )

    def load_json_simulation(self, path, tkn_name="tkn", timestamp: int = 0):
        """
        Loads a JSON file containing simulation modules to run and report on.
        """
        tkn_name = tkn_name.lower()
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        json_data = BancorDapp.load_json(path)
        state = setup_json_simulation(state, json_data, tkn_name)
        self.next_transaction(state)

    def create_flat_ac_rewards_program(
        self,
        tkn_name: str,
        user_name: str,
        total_rewards: str,
        start_time: int,
        total_duration: int,
        timestamp: int = 0,
        transaction_type: str = "create flat autocompounding rewards program",
    ):
        self._create_ac_rewards_program(
            tkn_name=tkn_name,
            user_name=user_name,
            total_rewards=total_rewards,
            distribution_type="flat",
            start_time=start_time,
            total_duration=total_duration,
            timestamp=timestamp,
            transaction_type=transaction_type,
        )

    def create_exp_ac_rewards_program(
        self,
        tkn_name: str,
        user_name: str,
        total_rewards: str,
        start_time: int,
        half_life: int,
        timestamp: int = 0,
        transaction_type: str = "create exp autocompounding rewards program",
    ):
        self._create_ac_rewards_program(
            tkn_name=tkn_name,
            user_name=user_name,
            total_rewards=total_rewards,
            distribution_type="exp",
            start_time=start_time,
            half_life=half_life,
            timestamp=timestamp,
            transaction_type=transaction_type,
        )

    def _create_ac_rewards_program(
        self,
        tkn_name: str,
        user_name: str,
        total_rewards: str,
        distribution_type: str,
        start_time: int,
        total_duration: int = 0,
        half_life: int = 0,
        timestamp: int = 0,
        transaction_type: str = "",
    ):
        """
        Creates autocompounding rewards program.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )

        program_id = state.autocompounding_programs_count + 1

        is_active = timestamp >= start_time

        total_rewards = to_user_amount(state, tkn_name, user_name, total_rewards)

        ptkn_amt = compute_ptkn_amt(state, tkn_name, total_rewards)
        state.decrease_user_balance(user_name, "bn" + tkn_name, ptkn_amt)
        state.increase_external_rewards_vault_balance(tkn_name, ptkn_amt)

        # Add the program to the rest.
        state.autocompounding_reward_programs[tkn_name] = AutocompoundingProgram(
            id=program_id,
            created_at=timestamp,
            tkn_name=tkn_name,
            distribution_type=distribution_type,
            start_time=start_time,
            total_duration=total_duration,
            half_life=half_life,
            total_rewards=Token(balance=total_rewards),
            remaining_rewards=Token(balance=total_rewards),
            is_active=is_active,
        )

        self.next_transaction(state)
        handle_logging(
            tkn_name=tkn_name,
            user_name=user_name,
            tkn_amt=total_rewards,
            action_name=transaction_type,
            transaction_id=self.transaction_id,
            state=state,
        )

    def terminate_ac_rewards_program(
        self,
        tkn_name: str,
        timestamp: int = 0,
        transaction_type: str = "terminate autocompounding rewards program",
    ):
        """
        Terminates autocompounding rewards program.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        state = terminate_ac_rewards_program(
            state=state, tkn_name=tkn_name, timestamp=timestamp
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name=tkn_name,
            user_name=user_name,
            tkn_amt=Decimal(0),
            action_name=transaction_type,
            transaction_id=self.transaction_id,
            state=state,
        )

    def burn_pool_tokens(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        timestamp: int = 0,
        transaction_type: str = "burnPoolTokenTKN",
    ):
        """
        Used for testing vandalism attack.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, "bn" + tkn_name, user_name, tkn_amt)
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
        timestamp: int,
        transaction_type="create_standard_rewards_program",
    ):
        """
        Create a standard rewards program for a given token.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        tkn_amt = Decimal(rewards_amt)
        state, id = create_standard_reward_program(
            state=state,
            tkn_name=tkn_name,
            total_rewards=tkn_amt,
            start_time=start_time,
            end_time=end_time,
            timestamp=timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )
        return id

    def join_standard_rewards_program(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        program_id: int,
        timestamp: int = 0,
        transaction_type="join_standard_rewards_program",
    ):
        """
        Join the standard rewards program for a given user.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, "bn" + tkn_name, user_name, tkn_amt)
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
        tkn_amt: str,
        user_name: str,
        program_id: int,
        timestamp: int = 0,
        transaction_type="leave_standard_rewards_program",
    ):
        """
        Leave the standard rewards program for a given user.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = to_user_amount(state, "bn" + tkn_name, user_name, tkn_amt)
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
        user_name: str,
        program_ids: list,
        timestamp: int = 0,
        transaction_type: str = "claim_standard_rewards",
    ):
        """
        Claim standard rewards for a given reward program and user.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state = claim_standard_rewards(
            state=state,
            user_name=user_name,
            ids=program_ids,
            timestamp=timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            "",
            Decimal(0),
            transaction_type,
            user_name,
            self.transaction_id,
            state,
        )

    def set_user_balance(
        self,
        user_name: str,
        tkn_name: str,
        tkn_amt: str,
        timestamp: int = 0,
        transaction_type: str = "set user balance",
    ):
        """
        Sets user balance at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(
            state, tkn_name, user_name, timestamp
        )
        tkn_amt = Decimal(tkn_amt)
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
        percent: str,
        timestamp: int = 0,
        transaction_type: str = "set trading fee",
    ):
        """
        Sets the system trading fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        value = to_decimal(percent)
        state.set_trading_fee(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def set_network_fee(
        self,
        tkn_name: str,
        percent: str,
        timestamp: int = 0,
        transaction_type: str = "set network fee",
    ):
        """
        Sets the system network fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        value = to_decimal(percent)
        state.set_network_fee(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def set_withdrawal_fee(
        self,
        tkn_name: str,
        percent: str,
        timestamp: int = 0,
        transaction_type: str = "set withdrawal fee",
    ):
        """
        Sets the system withdrawal fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        value = to_decimal(percent)
        state.set_withdrawal_fee(tkn_name, value)
        self.next_transaction(state)
        handle_logging(
            tkn_name, value, transaction_type, user_name, self.transaction_id, state
        )
        return self

    def set_bnt_funding_limit(
        self,
        tkn_name: str,
        amount: str,
        timestamp: int = 0,
        transaction_type: str = "set bnt funding limit",
    ):
        """
        Sets the system withdrawal fee at the network interface level for convenience.
        """
        state = self.get_state(copy_type="initial", timestamp=timestamp)
        state, tkn_name, user_name = validate_input(state, tkn_name, "", timestamp)
        value = to_decimal(amount)
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
