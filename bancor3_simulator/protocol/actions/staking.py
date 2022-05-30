"""Main supporting logic for protocol staking actions."""
from decimal import Decimal
from typing import Tuple

from bancor3_simulator.core.dataclasses import State
from bancor3_simulator.protocol.utils.protocol import mint_protocol_bnt


def stake_bnt(state, tkn_name, tkn_amt, user_name, unix_timestamp):
    """Specific case of .stake() method, see .stake() method docstring"""

    # sense
    if unix_timestamp is not None:
        state.unix_timestamp = unix_timestamp

    # solve
    bnbnt_amt = state.bnbnt_amt(tkn_amt)

    # actuation
    state.users[user_name].wallet[tkn_name].tkn_amt -= tkn_amt
    state.users[user_name].wallet[tkn_name].bntkn_amt += bnbnt_amt
    state.users[user_name].wallet[tkn_name].vbnt_amt += bnbnt_amt
    state.protocol_wallet_bnbnt -= tkn_amt
    return state

# def update_protocol_owned_liquidity(state, bnt_amount):

    # ledger actuation
    # bnbnt_amt = state.bnbnt_rate * bnt_amount
    # state.erc20contracts_bnbnt += bnbnt_amt
    # state.vault_bnt += bnt_amount
    # state.staked_bnt += bnt_amount
    # state.protocol_wallet_bnbnt -= bnbnt_amt
    # return state

def stake_tkn(state, tkn_name, tkn_amt, user_name, unix_timestamp):
    """Specific case of .stake() method, see .stake() method docstring"""

    # sense
    if unix_timestamp is not None:
        state.pools[tkn_name].unix_timestamp = unix_timestamp

    # solve

    bntkn_amt = state.bntkn_rate(tkn_name) * tkn_amt
    print('bntkn_rate', state.bntkn_rate(tkn_name))
    print('bntkn_amt', bntkn_amt)

    # actuation
    # user actuation
    state.users[user_name].wallet[tkn_name].tkn_amt -= tkn_amt
    state.users[user_name].wallet[tkn_name].bntkn_amt += bntkn_amt

    # ledger actuation
    state.pools[tkn_name].erc20contracts_bntkn += bntkn_amt
    state.pools[tkn_name].vault_tkn += tkn_amt
    state.pools[tkn_name].staked_tkn += tkn_amt

    # sense & solve
    bnt_increase, tkn_increase = pool_depth_adjustment(tkn_name, state)


    # actuation
    state.pools[tkn_name].bnt_trading_liquidity += bnt_increase
    state.pools[tkn_name].tkn_trading_liquidity += tkn_increase
    state.pools[tkn_name].bnt_funding_amount += bnt_increase

    # TODO: Crosscheck Barak with Mark on the following line, results disagree
    # state.protocol_wallet_bnbnt -= bnbnt_amt
    bnbnt_amt = state.bnbnt_rate * bnt_increase
    state.erc20contracts_bnbnt += bnbnt_amt
    state.vault_bnt += bnt_increase
    state.staked_bnt += bnt_increase
    state.protocol_wallet_bnbnt += bnbnt_amt



    # state = mint_protocol_bnt(state, bnt_increase)
    state.update_spot_rate(tkn_name)
    state = state.check_pool_shutdown(tkn_name)
    state.protocol_bnt_check()
    return state


def deposit_tkn(state, tkn_name, tkn_amt, user_name, unix_timestamp):
    """Alias for stake_tkn"""
    return stake_tkn(state, tkn_name, tkn_amt, user_name, unix_timestamp)


def deposit_bnt(state, tkn_name, tkn_amt, user_name, unix_timestamp):
    """Alias for stake_bnt"""
    return stake_bnt(state, tkn_name, tkn_amt, user_name, unix_timestamp)


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
    ema_rate = state.pools[tkn_name].ema_rate
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
    ema_rate = state.pools[tkn_name].ema_rate
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
    unix_timestamp = state.unix_timestamp
    bnt_increase = tkn_increase = Decimal("0")

    # Setting the bnt_funding_limit as follows is not a general solution.
    # Currently, the bnt_funding_limit is used as a global setting, however, throughout the codebase it is setup
    # to be a per-pool tuneable parameter. Setting as follows overrides the per-pool value to the global value.
    state.pools[tkn_name].bnt_funding_limit = state.bnt_funding_limit

    trading_enabled = state.pools[tkn_name].trading_enabled
    is_price_stable = state.pools[tkn_name].is_price_stable
    bnt_remaining_funding = state.pools[tkn_name].bnt_remaining_funding

    if trading_enabled and is_price_stable and bnt_remaining_funding > 0:

        avg_tkn_trading_liquidity = state.pools[tkn_name].avg_tkn_trading_liquidity
        tkn_excess = state.pools[tkn_name].tkn_excess
        tkn_excess_bnt_equivalence = state.pools[tkn_name].tkn_excess_bnt_equivalence
        bnt_trading_liquidity = state.pools[tkn_name].bnt_trading_liquidity
        tkn_trading_liquidity = state.pools[tkn_name].tkn_trading_liquidity

        if (
                avg_tkn_trading_liquidity <= tkn_excess
                and bnt_trading_liquidity <= bnt_remaining_funding
        ):
            print('case1')
            bnt_increase = bnt_trading_liquidity
            tkn_increase = modified_tkn_increase(
                state,
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                bnt_increase,
            )

        elif (
                avg_tkn_trading_liquidity <= tkn_excess and bnt_trading_liquidity > bnt_remaining_funding
                or avg_tkn_trading_liquidity > tkn_excess and tkn_excess_bnt_equivalence >= bnt_remaining_funding
        ):
            print('case2')
            bnt_increase = bnt_remaining_funding
            tkn_increase = modified_tkn_increase(
                state,
                tkn_name,
                bnt_trading_liquidity,
                tkn_trading_liquidity,
                bnt_increase,
            )

        elif (
                tkn_excess < avg_tkn_trading_liquidity and bnt_trading_liquidity <= bnt_remaining_funding
                or avg_tkn_trading_liquidity > tkn_excess and bnt_trading_liquidity > bnt_remaining_funding > tkn_excess_bnt_equivalence
        ):
            print('case3')
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
