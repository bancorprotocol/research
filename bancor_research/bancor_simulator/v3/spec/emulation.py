# coding=utf-8
# --------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
from decimal import Decimal

from bancor_research.bancor_simulator.v3.spec.state import State
from bancor_research.bancor_simulator.v3.spec.utils import (
    generate_emulator_expected_results,
)


def emulate_deposit(
    state: State,
    tkn_name: str,
    tkn_amt: Decimal,
    user_name: str,
    timestamp: int,
    transaction_type: str,
):
    """
    Validate deposit results (bancor_simulator) against the fixedpoint precision (bancor_emulator).
    """
    expected_results = generate_emulator_expected_results(
        state, tkn_name, tkn_amt, transaction_type, user_name, timestamp
    )

    # run emulation code here
    pass


def emulate_trade(
    state: State,
    tkn_amt: Decimal,
    source_token: str,
    target_token: str,
    user_name: str,
    timestamp: int,
    transaction_type: str,
):
    """
    Validate trade results (bancor_simulator) against the fixedpoint precision (bancor_emulator).
    """
    expected_results = generate_emulator_expected_results(
        state, target_token, tkn_amt, transaction_type, user_name, timestamp
    )

    # run emulation code here
    pass


def emulate_withdraw(
    state: State,
    user_name: str,
    id_number: int,
    timestamp: int,
    tkn_name: str,
    tkn_amt: Decimal,
    transaction_type: str,
):
    """
    Validate trade results (bancor_simulator) against the fixedpoint precision (bancor_emulator).
    """
    expected_results = generate_emulator_expected_results(
        state, tkn_name, tkn_amt, transaction_type, user_name, timestamp
    )

    # run emulation code here
    pass
