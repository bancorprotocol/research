# coding=utf-8
import json
import pickle
from typing import List

import cloudpickle
from decimal import Decimal

import pandas as pd

from bancor_simulator.v3.actions import (
    deposit_bnt,
    deposit_tkn,
    begin_withdrawal_cooldown,
    process_trade,
    process_withdrawal
)
from bancor_simulator.v3.rewards import (
    claim_standard_rewards,
    distribute_autocompounding_program, join_standard_reward_program, leave_standard_reward_program,
)
from bancor_simulator.v3.simulation import setup_json_simulation, run
from bancor_simulator.v3.state import (
    State,
    GlobalSettings,
    init_protocol,
    handle_logging,
    handle_vandalism_attack,
    dao_msig_init_pools,
    describe,
    describe_rates,
    SECONDS_PER_DAY,
    get_pooltoken_name,
    AutocompoundingProgramState,
    get_protocol_wallet_balance,
    get_json_virtual_balances,
    Token,
    get_whitelist_token_logging_inputs,
    get_create_user_logging_inputs,
    get_dao_msig_init_pools_logging_inputs, validate_input, build_json_operation
)


class BancorNetwork:
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
            whitelisted_tokens=None,
            price_feeds_path=global_settings.price_feeds_path,
            price_feeds: pd.DataFrame = None,
            active_users: list = None,
            transaction_id: int = 0,
    ):

        self.json_data = None
        self.transaction_id = transaction_id

        if active_users is None:
            active_users = BancorNetwork.global_settings.active_users

        if price_feeds is None:
            price_feeds = pd.read_parquet(price_feeds_path)
            price_feeds.columns = [col.lower() for col in price_feeds.columns]

        state = State(
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
            price_feeds=price_feeds,
        )

        state = init_protocol(
            state=state,
            whitelisted_tokens=whitelisted_tokens,
            usernames=active_users,
            cooldown_time=cooldown_time,
            network_fee=network_fee,
            trading_fee=trading_fee,
            bnt_min_liquidity=bnt_min_liquidity,
            bnt_funding_limit=bnt_funding_limit,
            withdrawal_fee=withdrawal_fee,
        )

        for tkn_name in whitelisted_tokens:
            state.set_trading_fee(tkn_name, trading_fee)
            state.set_bnt_funding_limit(tkn_name, bnt_funding_limit)

        state.json_export = {"users": [], "operations": []}
        self._backup_state = {}
        self._global_state = state
        self.history = []

    @property
    def global_state(self):
        return self._global_state

    @global_state.setter
    def global_state(self, value):
        self._global_state = value

    @staticmethod
    def load_json(path, **kwargs):
        """
        Loads json files for convenient simulation.
        """
        with open(path, "r") as f:
            return json.load(f, **kwargs)

    @staticmethod
    def save_json(x, path, indent=True, **kwargs):
        """
        Saves json for convenience.
        """
        with open(path, "w") as f:
            if indent:
                json.dump(x, f, indent="\t", **kwargs)
            else:
                json.dump(x, f, **kwargs)
        print("Saved to", path)

    @staticmethod
    def load_pickle(path):
        """
        Loads a pickled BancorNetwork state from a file path.
        """
        print("Unpickling from", path)
        with open(path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def save_pickle(x, path):
        """
        Saves a pickled BancorNetwork state at file path.
        """
        print("Pickling to", path)
        with open(path, "wb") as f:
            return pickle.dump(x, f)

    @staticmethod
    def load(file_path):
        """
        Loads pickled BancorNetwork state at file path via cloudpickle.
        """
        with open(file_path, "rb") as f:
            return cloudpickle.load(f)

    def save_state(self, state: State = None):
        """
        Saves a backup of the current global state BancorNetwork to revert back to if desired.
        """
        if state is None:
            s = self.global_state
        else:
            s = state
        self._backup_state[self.global_state.unix_timestamp] = cloudpickle.dumps(s)
        return self.global_state

    def revert(self, unix_timestamp):
        """
        Reverts the state of the bancor network to a previously saved state.
        """
        self.global_state = cloudpickle.loads(self._backup_state[unix_timestamp])

    def save(self, file_path, pickle_protocol=cloudpickle.DEFAULT_PROTOCOL):
        """
        Saves state at file path.
        """
        with open(file_path, "wb") as f:
            cloudpickle.dump(self, f, protocol=pickle_protocol)

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

    def export_test_scenarios(self, path: str = "test_scenarios.json"):
        """
        Exports the auto-generated json scenarios file to a given path.
        """
        BancorNetwork.save_json(self.global_state.json_export, path)

    def deposit(
            self,
            tkn_name: str,
            tkn_amt: Decimal,
            user_name: str,
            unix_timestamp: int = None,
            bntkn: Decimal = Decimal("0"),
            action_name="deposit"
    ):
        """
        Top level logic for deposit actions.
        """
        state = self.save_state()
        state = validate_input(state, tkn_name, tkn_amt, user_name, unix_timestamp)

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
            tkn_amt: Decimal,
            source_token: str,
            target_token: str,
            user_name: str,
            unix_timestamp: int,
            transaction_type: str = 'trade'
    ):
        """
        Main logic for trade actions.
        """
        state = self.save_state()
        state = validate_input(
            state, source_token, tkn_amt, user_name, unix_timestamp
        )
        state = validate_input(
            state, target_token, tkn_amt, user_name, unix_timestamp
        )
        state = process_trade(state, tkn_amt, source_token, target_token, user_name, unix_timestamp)
        self.next_transaction(state)
        handle_logging(
            source_token + "->" + target_token, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )
        json_operation = build_json_operation(state, target_token, tkn_amt, transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def begin_cooldown(
            self,
            tkn_amt: Decimal,
            tkn_name: str,
            user_name: str,
            unix_timestamp: int = None,
            action_name: str = "begin cooldown",
    ):
        """
        Begin the withdrawal cooldown operation.
        """
        state = self.save_state()
        state = validate_input(state, tkn_name, tkn_amt, user_name, unix_timestamp)
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
            unix_timestamp: int = None,
            tkn_name: str = None,
            tkn_amt: Decimal = None,
            transaction_type: str = 'withdraw'
    ):
        """
        Main withdrawal logic based on the withdraw algorithm of the BIP15 spec.
        """
        state = self.save_state()
        state = process_withdrawal(
            state,
            user_name,
            id_number,
            unix_timestamp,
            tkn_name,
            tkn_amt
        )

        self.next_transaction(state)
        state = handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )
        json_operation = build_json_operation(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def dao_msig_init_pools(
            self,
            pools: list,
            tkn_name: str = None,
            unix_timestamp: int = 0,
            transaction_type: str = "enableTrading",
            user_name: str = "Protocol",
    ) -> None:
        """
        DAO msig initilizes new tokens to allow trading once specified conditions are met.
        """
        state = self.save_state()
        state.unix_timestamp = unix_timestamp
        state = dao_msig_init_pools(state, pools, tkn_name, unix_timestamp)
        amt = get_json_virtual_balances(state, tkn_name)
        self.next_transaction(state)
        handle_logging(
            get_dao_msig_init_pools_logging_inputs(state, tkn_name)
        )
        json_operation = build_json_operation(state, tkn_name, Decimal(0), transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def describe(self):
        """
        Describes the state ledger balances in a format similar to BIP15 documentation.
        """
        return describe(self.global_state)

    def describe_rates(self):
        """
        Describes the state variable rates in a format similar to BIP15 documentation.
        """
        return describe_rates(self.global_state)

    def next_transaction(self, state: State):
        """
        Increments a new id and state for each action
        """
        self.global_state = state
        self.transaction_id += 1

    def export(self):
        """
        Exports transaction history record
        """
        return pd.concat(self.global_state.history)

    def whitelist_token(self, tkn_name: str):
        """
        Creates a new whitelisted token with initialized starting balances
        """
        state = self.save_state()
        state.create_whitelisted_tkn(tkn_name)
        self.next_transaction(state)
        handle_logging(
            get_whitelist_token_logging_inputs(state, tkn_name)
        )

    def create_user(self, user_name: str):
        """
        Creates a new user with a valid wallet
        """
        state = self.save_state()
        state.create_user(user_name)
        self.next_transaction(state)
        handle_logging(
            get_create_user_logging_inputs(state, user_name)
        )

    def distribute_autocompounding_program(
            self, tkn_name: str = "tkn",
            unix_timestamp: int = 0,
            transaction_type: str = 'distribute_autocompounding_program',
            user_name: str = 'protocol'
    ):
        """
        Distribute auto-compounding program.
        """
        state = self.save_state()
        state = distribute_autocompounding_program(
            state=state, tkn_name=tkn_name, unix_timestamp=unix_timestamp
        )
        self.next_transaction(state)
        json_operation = build_json_operation(state, tkn_name, Decimal(0), transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def load_json_simulation(self, path, tkn_name='tkn'):
        """
        Loads a JSON file containing simulation modules to run and report on.
        """
        state = self.save_state()
        json_data = BancorNetwork.load_json(path)
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
            unix_timestamp: int,
            half_life_days: int = 0,
            total_duration_in_days: Decimal = Decimal("0"),
            total_duration_in_seconds: Decimal = Decimal("0"),
            transaction_type: str = "create autocompounding program",
    ):
        """
        Creates a new autocompounding program.
        """
        state = self.save_state(state)
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
                unix_timestamp=unix_timestamp,
            )
            state.decrease_protocol_wallet_balance(tkn_name, program_wallet_bntkn)
        else:
            program_wallet_bntkn = get_protocol_wallet_balance(state, "bnbnt")

        if unix_timestamp >= start_time:
            is_active = True
        else:
            is_active = False

        # Add the program to the rest.
        state.autocompounding_programs[tkn_name] = AutocompoundingProgramState(
            id=program_id,
            tkn_name=tkn_name,
            owner_id=user_name,
            is_active=is_active,
            half_life_days=half_life_days,
            total_duration_in_seconds=total_duration_in_seconds,
            start_time=start_time,
            created_at=unix_timestamp,
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
        json_operation = build_json_operation(state, tkn_name, total_rewards, transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def burn(
            self,
            tkn_name: str,
            tkn_amt: Decimal,
            user_name: str,
            unix_timestamp: int = 0,
            transaction_type: str = "burnPoolTokenTKN"
    ):
        """
        Used for testing vandalism attack.
        """
        state = self.save_state()
        state = validate_input(state, tkn_name, tkn_amt, user_name, unix_timestamp)
        if tkn_name != "bnt":
            state.decrease_pooltoken_balance(tkn_name, tkn_amt)
            state.decrease_user_balance(user_name, get_pooltoken_name(tkn_name), tkn_amt)
            self.next_transaction(state)
            handle_logging(
                tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
            )
            json_operation = build_json_operation(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)
            self.global_state.json_export['operations'].append(json_operation)

    def claim(
            self,
            tkn_name: str,
            tkn_amt: Decimal,
            user_name: str,
            rewards_ids: List[int],
            transaction_type: str = "claim",
            unix_timestamp: int = None,
    ):
        """
        Claim standard rewards for a given reward program and user.
        """
        state = self.save_state()
        state = validate_input(state, tkn_name, tkn_amt, user_name, unix_timestamp)
        state = claim_standard_rewards(state, user_name, rewards_ids, unix_timestamp)
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )
        json_operation = build_json_operation(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def join(
            self,
            tkn_name: str,
            tkn_amt: Decimal,
            user_name: str,
            unix_timestamp: int = None,
            transaction_type="join"
    ):
        """
        Join the standard rewards program for a given user.
        """
        state = self.save_state()
        state = validate_input(state, tkn_name, tkn_amt, user_name, unix_timestamp)
        state = join_standard_reward_program(
            state=state,
            provider_id=user_name,
            program_id=tkn_name,
            tkn_amt=tkn_amt,
            curr_time=unix_timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )
        json_operation = build_json_operation(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)

    def leave(
            self,
            tkn_name: str,
            tkn_amt: Decimal,
            user_name: str,
            id_number: int,
            unix_timestamp: int = None,
            transaction_type="leave"
    ):
        """
        Leave the standard rewards program for a given user.
        """
        state = self.save_state()
        state = validate_input(state, tkn_name, tkn_amt, user_name, unix_timestamp)
        state = leave_standard_reward_program(
            state=state,
            provider_id=user_name,
            program_id=id_number,
            tkn_amt=tkn_amt,
            curr_time=unix_timestamp,
        )
        self.next_transaction(state)
        handle_logging(
            tkn_name, tkn_amt, transaction_type, user_name, self.transaction_id, state
        )
        json_operation = build_json_operation(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)
        self.global_state.json_export['operations'].append(json_operation)
