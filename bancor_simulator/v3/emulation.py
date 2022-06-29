# coding=utf-8
from decimal import Decimal

from bancor_simulator.v3.state import State, get_emulator_expected_results


def emulate_deposit(
        state: State,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        unix_timestamp: int,
        transaction_type: str
):
    """
    Validate deposit results (simulator) against the fixedpoint precision (emulator).
    """
    expected_results = get_emulator_expected_results(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)

    # run emulation code here
    pass


def emulate_trade(
        state: State,
        tkn_amt: Decimal,
        source_token: str,
        target_token: str,
        user_name: str,
        unix_timestamp: int,
        transaction_type: str,
):
    """
    Validate trade results (simulator) against the fixedpoint precision (emulator).
    """
    expected_results = get_emulator_expected_results(state, target_token, tkn_amt, transaction_type, user_name, unix_timestamp)

    # run emulation code here
    pass


def emulate_withdraw(
        state: State,
        user_name: str,
        id_number: int,
        unix_timestamp: int,
        tkn_name: str,
        tkn_amt: Decimal,
        transaction_type: str,
):
    """
    Validate trade results (simulator) against the fixedpoint precision (emulator).
    """
    expected_results = get_emulator_expected_results(state, tkn_name, tkn_amt, transaction_type, user_name, unix_timestamp)

    # run emulation code here
    pass
