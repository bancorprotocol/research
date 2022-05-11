"""Main supporting logic for protocol staking actions."""
from decimal import Decimal
from typing import Tuple

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
    bnbnt_amt = state.bnbnt_amt(tkn_amt)

    # actuator tasks
    state.vault_bnt += tkn_amt
    state.erc20contracts_bnbnt += bnbnt_amt
    state.staked_bnt += tkn_amt
    state.protocol_wallet_bnbnt += bnbnt_amt
    return state


def modified_tkn_increase(
    state: State,
    tkn_name: str,
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
    bnt_increase: Decimal,
) -> Decimal:
    """Introduced during the Bancor 3 Beta.
    In the final version of the protocol, this function is no longer required.
    """
    ema_rate = state.tokens[tkn_name].ema_rate
    return (bnt_trading_liquidity + bnt_increase) / ema_rate - tkn_trading_liquidity


def modified_bnt_increase(
    state: State,
    tkn_excess: Decimal,
    tkn_name: str,
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
) -> Decimal:
    """Introduced during the Bancor 3 Beta.
    In the final version of the protocol, this function is no longer required.
    """
    ema_rate = state.tokens[tkn_name].ema_rate
    return (tkn_excess + tkn_trading_liquidity) * ema_rate - bnt_trading_liquidity


def pool_depth_adjustment(tkn_name: str, state: State) -> Tuple[Decimal, Decimal]:
    """If the pool has trading disabled, or if the ema and spot rates deviate by more than 1%, returns nil.

    Args:
        tkn_name (str): The token name in question.
        state (State): Instance of the current active state.

    Returns:
        bnt_increase, tkn_increase (Decimal, Decimal): The quantities of BNT and TKN to add to the pool trading
                                                        liquidity during a deposit.
    """
    bnt_increase = tkn_increase = Decimal("0")
    trading_enabled = state.tokens[tkn_name].trading_enabled
    is_price_stable = state.tokens[tkn_name].is_price_stable
    bnt_remaining_funding = state.tokens[tkn_name].bnt_remaining_funding

    if trading_enabled and is_price_stable and bnt_remaining_funding > 0:

        avg_tkn_trading_liquidity = state.tokens[tkn_name].avg_tkn_trading_liquidity
        tkn_excess = state.tokens[tkn_name].tkn_excess
        tkn_excess_bnt_equivalence = state.tokens[tkn_name].tkn_excess_bnt_equivalence
        bnt_trading_liquidity = state.tokens[tkn_name].bnt_trading_liquidity
        tkn_trading_liquidity = state.tokens[tkn_name].tkn_trading_liquidity

        if (
            avg_tkn_trading_liquidity <= tkn_excess
            and bnt_trading_liquidity <= bnt_remaining_funding
        ):
            bnt_increase = bnt_trading_liquidity
            tkn_increase = modified_tkn_increase(
                state,
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                bnt_increase,
            )

        elif (
            avg_tkn_trading_liquidity <= tkn_excess
            and bnt_trading_liquidity > bnt_remaining_funding
            or avg_tkn_trading_liquidity > tkn_excess
            and tkn_excess_bnt_equivalence >= bnt_remaining_funding
        ):
            bnt_increase = bnt_remaining_funding
            tkn_increase = modified_tkn_increase(
                state,
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                bnt_increase,
            )

        elif (
            tkn_excess < avg_tkn_trading_liquidity
            and bnt_trading_liquidity <= bnt_remaining_funding
            or avg_tkn_trading_liquidity > tkn_excess
            and bnt_trading_liquidity
            > bnt_remaining_funding
            > tkn_excess_bnt_equivalence
        ):
            bnt_increase = modified_bnt_increase(
                state,
                tkn_excess,
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
            )
            tkn_increase = tkn_excess

        else:
            raise ValueError("Something went wrong, pool adjustment case not found...")

    return bnt_increase, tkn_increase
