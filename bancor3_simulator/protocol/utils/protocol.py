# coding=utf-8
from decimal import Decimal

from bancor3_simulator.core.dataclasses import State


def mint_protocol_bnt(state: State, tkn_amt: Decimal) -> State:
    """Handles adjustments to the system resulting from the protocol minting BNT.
    The bnbnt supply and protocol_wallet bnbnt_balance are incremented commensurate with bnbnt/bnt-rate and bnt_amount.

    Args:
        state (dataclass object): Current system state and all its params.
        tkn_amt (Decimal): The amount of tkn transacted.

    Returns:
        state (dataclass object): Updated system state.

    """
    bnbnt_amt = state.get_bnbnt_amt(tkn_amt)

    # actuator tasks
    state.vault_bnt += tkn_amt
    state.erc20contracts_bnbnt += bnbnt_amt
    state.staked_bnt += tkn_amt
    state.protocol_wallet_bnbnt += bnbnt_amt
    return state


def handle_logging(
    tkn_name, tkn_amt, action_name, user_name, iter_transaction_id, state
):
    state.log.tkn_name = tkn_name
    state.log.tkn_amt = tkn_amt
    state.log.action_name = action_name
    state.log.user_name = user_name
    state.iter_transaction_id = iter_transaction_id
    state.log_transaction()
    return state
