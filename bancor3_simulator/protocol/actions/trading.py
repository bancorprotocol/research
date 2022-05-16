"""Main supporting logic for protocol staking actions."""
from decimal import Decimal

from typing import Tuple

from bancor3_simulator.core.dataclasses import State

MAX_UINT112 = 2 ** 112 - 1

def trade_bnt_for_tkn(
    state,
    bnt_trading_liquidity,
    tkn_trading_liquidity,
    trading_fee,
    network_fee,
    bnt_amt,
    tkn_name,
    direction="bnt",
):
    """
    Takes bntAmount, tokenName as inputs.
    The trading liquidities are updated according to the swap algorithm.
    Two different fee quantities are collected, one denominated in tkn and the other in bnt.
    The tkn fee is added to the stakingLedger and the bnt fee is added to the vortexLedger.
    This function returns tknSentToUser.
    """

    # solve
    state = handle_ema(tkn_name, state)
    updated_bnt_liquidity = changed_bnt_trading_liquidity(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        bnt_amt,
        direction,
    )
    updated_tkn_liquidity = changed_tkn_trading_liquidity(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        bnt_amt,
        direction,
    )
    tkn_sent_to_user = target_amount(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        bnt_amt,
        direction,
    )
    trade_fee = swap_fee_collection(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        bnt_amt,
        direction,
    )
    bnt_collected_by_vortex = vortex_collection(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        bnt_amt,
        direction,
    )

    # actuate
    state.vault_bnt += bnt_amt
    state.tokens[tkn_name].vault_tkn -= tkn_sent_to_user
    state.tokens[tkn_name].bnt_trading_liquidity = updated_bnt_liquidity
    state.tokens[tkn_name].tkn_trading_liquidity = updated_tkn_liquidity
    state.tokens[tkn_name].staked_tkn += trade_fee
    state.vortex_bnt += bnt_collected_by_vortex
    state.update_spot_rate(tkn_name)
    return state, tkn_sent_to_user


def trade_tkn_for_bnt(
    state: State,
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
    trading_fee: Decimal,
    network_fee: Decimal,
    tkn_amt: Decimal,
    tkn_name: str,
    direction="tkn",
):
    """Main logic to process swaps/trades from TKN->BNT"""

    # solve
    state = handle_ema(tkn_name, state)
    updated_bnt_liquidity = changed_bnt_trading_liquidity(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        tkn_amt,
        direction,
    )
    updated_tkn_liquidity = changed_tkn_trading_liquidity(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        tkn_amt,
        direction,
    )
    bnt_sent_to_user = target_amount(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        tkn_amt,
        direction,
    )
    trade_fee = swap_fee_collection(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        tkn_amt,
        direction,
    )
    bnt_collected_by_vortex = vortex_collection(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        tkn_amt,
        direction,
    )

    # actuate
    state.vault_bnt -= bnt_sent_to_user
    state.tokens[tkn_name].vault_tkn += tkn_amt
    state.tokens[tkn_name].bnt_trading_liquidity = updated_bnt_liquidity
    state.tokens[tkn_name].tkn_trading_liquidity = updated_tkn_liquidity
    state.staked_bnt += trade_fee
    state.tokens[tkn_name].bnt_funding_amount += trade_fee
    state.tokens[tkn_name].bnt_remaining_funding -= trade_fee
    state.vortex_bnt += bnt_collected_by_vortex
    state.update_spot_rate(tkn_name)
    return state, bnt_sent_to_user


def get_trade_inputs(state, tkn_name):
    bnt_trading_liquidity = state.tokens[tkn_name].bnt_trading_liquidity
    tkn_trading_liquidity = state.tokens[tkn_name].tkn_trading_liquidity
    trading_fee = state.tokens[tkn_name].trading_fee
    network_fee = state.network_fee
    return (
        tkn_name,
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
    )


def update_ema(
    last_spot: Decimal, last_ema: Decimal, alpha: Decimal = Decimal("0.2")
) -> Decimal:
    """The ema update is part of the Bancor security system, and is allowed to update only once per bloack per pool.
    This method is called before a trade is performed, therefore the ema is a lagging average.

    Args:
        last_spot (Decimal): Prior spot rate.
        last_ema (Decimal): Prior EMA rate.
        alpha (Decimal): Constant value threshold.

    Returns:
        Updated EMA value.
    """
    print('last_spot ', last_spot)
    print('last_ema ', last_ema)
    return alpha * last_spot + (1 - alpha) * last_ema


def update_compressed_ema(
    last_spot_numerator: int,
    last_spot_denominator: int,
    last_ema_compressed_numerator: int,
    last_ema_compressed_denominator: int,
    alpha=20,
) -> tuple(int, int):
    """
    Takes the current spot rate and the current ema rate as inputs, and returns the new ema rate as output.
    """
    ema_numerator = (
        last_spot_numerator * last_ema_compressed_denominator * alpha +
        last_spot_denominator * last_ema_compressed_numerator * (100 - alpha)
    )
    ema_denominator = last_spot_denominator * last_ema_compressed_denominator * 100
    scaled = (max(ema_numerator, ema_denominator) + MAX_UINT112 - 1) // MAX_UINT112
    return ema_numerator // scaled, ema_denominator // scaled


def measure_ema_deviation(
    new_ema, new_ema_compressed_numerator, new_ema_compressed_denominator
):
    """
    Takes the accerate ema_rate, and the ema_compressed_numerator and ema_compressed_denominator as inputs.
    Returns the deviation between these values as ema_rate/ema_compressed_rate.
    """
    return (
        new_ema
        * Decimal(new_ema_compressed_denominator)
        / Decimal(new_ema_compressed_numerator)
    )


def handle_ema(tkn_name: str, state: State) -> State:
    """Takes update_allowed, a bool, and newEma as inputs.
    Handles the updating of the ema_rate, called before a swap is performed.

    Args:
        tkn_name: Name of the token being transacted.
        state: Current system state.

    Returns:
        Updated system state.
    """
    last_spot = state.tokens[tkn_name].spot_rate
    last_ema = state.tokens[tkn_name].ema_rate
    last_ema_compressed_numerator = state.tokens[tkn_name].ema_compressed_numerator
    last_ema_compressed_denominator = state.tokens[tkn_name].ema_compressed_denominator
    ema_last_updated = state.tokens[tkn_name].ema_last_updated
    update_allowed = state.tokens[tkn_name].is_ema_update_allowed

    if update_allowed:
        new_ema = update_ema(last_spot, last_ema)
        # (
        #     new_ema_compressed_numerator,
        #     new_ema_compressed_denominator,
        # ) = update_compressed_ema(
        #     last_spot,
        #     last_ema_compressed_numerator,
        #     last_ema_compressed_denominator,
        # )
        # ema_deviation = measure_ema_deviation(
        #     new_ema, new_ema_compressed_numerator, new_ema_compressed_denominator
        # )

        # set
        state.tokens[tkn_name].ema_last_updated = state.tokens[tkn_name].timestep
        state.tokens[tkn_name].ema_rate = new_ema

    return state


def process_arbitrage_trade(
    tkn_name: str,
    tkn_token_virtual_balance: Decimal,
    bnt_virtual_balance: Decimal,
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
    trading_fee: Decimal,
    user_tkn: Decimal,
    user_bnt: Decimal,
) -> Tuple[Decimal, str, str, bool]:
    """Computes the appropriate arbitrage trade on the token_name pool.
    Returns user_capability == True if the user has sufficient funds to close the opportunity, else returns
    user_capability == False.

    Args:
        tkn_name: The name of the token being transacted.
        tkn_token_virtual_balance:
        bnt_virtual_balance:
        bnt_trading_liquidity:
        tkn_trading_liquidity:
        trading_fee:
        user_tkn:
        user_bnt:

    Returns:

    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    m = trading_fee
    p = bnt_virtual_balance
    q = tkn_token_virtual_balance
    bnt_trade_amount = (
        -Decimal("2") * a * q
        + b * m * p
        + (
            (Decimal("2") * a * q - b * m * p) ** Decimal("2")
            - Decimal("4") * a * q * (a * q - b * p)
        )
        ** (Decimal("1") / Decimal("2"))
    ) / (Decimal("2") * q)
    tkn_trade_amount = (
        -Decimal("2") * b * p
        + a * m * q
        + (
            (Decimal("2") * b * p - a * m * q) ** Decimal("2")
            - Decimal("4") * b * p * (b * p - a * q)
        )
        ** (Decimal("1") / Decimal("2"))
    ) / (Decimal("2") * p)

    if bnt_trade_amount > 0:
        source_token = "bnt"
        target_token = tkn_name
        trade_amount = bnt_trade_amount
        user_capability = user_bnt > bnt_trade_amount
        return trade_amount, source_token, target_token, user_capability

    elif tkn_trade_amount > 0:
        source_token = tkn_name
        target_token = "bnt"
        trade_amount = tkn_trade_amount
        user_capability = user_tkn > tkn_trade_amount
        return trade_amount, source_token, target_token, user_capability


def changed_bnt_trading_liquidity(
    a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """Computes the changes state values according to the swap algorithm.

    Args:
        a: (Decimal) bnt_trading_liquidity
        b: (Decimal) tkn_trading_liquidity
        d: (Decimal) trading_fee
        e: (Decimal) network_fee
        x: (Decimal) bnt_amount
        direction: (str) Direction of TKN->BNT or BNT->TKN

    Returns:
        bnt_trading_liquidity: (Decimal) Changed state BNT trading liquidity value.
    """
    if direction == "tkn":
        return a * (b + d * x * (1 - e)) / (b + x)
    elif direction == "bnt":
        return (a * (a + x) + d * (1 - e) * (a * x + x**2)) / (a + d * x)


def changed_tkn_trading_liquidity(
    a: Decimal, b: Decimal, d: Decimal, x: Decimal, direction: str
) -> Decimal:
    """Computes the changes state values according to the swap algorithm.

    Args:
        a: (Decimal) bnt_trading_liquidity
        b: (Decimal) tkn_trading_liquidity
        d: (Decimal) trading_fee
        x: (Decimal) bnt_amount
        direction: (str) Direction of TKN->BNT or BNT->TKN

    Returns:
        tkn_trading_liquidity: (Decimal) Changed state TKN trading liquidity value.

    """
    if direction == "tkn":
        return b + x
    elif direction == "bnt":
        return b * (a + d * x) / (a + x)


def target_amount(
    a: Decimal, b: Decimal, d: Decimal, x: Decimal, direction: str
) -> Decimal:
    """Computes the changes state values according to the swap algorithm.

    Args:
        a: (Decimal) bnt_trading_liquidity
        b: (Decimal) tkn_trading_liquidity
        d: (Decimal) trading_fee
        x: (Decimal) bnt_amount
        direction: (str) Direction of TKN->BNT or BNT->TKN

    Returns:
        target_amount: (Decimal) Changed state amount of the target token.

    """
    if direction == "tkn":
        return a * x * (1 - d) / (b + x)
    elif direction == "bnt":
        return b * x * (1 - d) / (a + x)


def vortex_collection(
    a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """Computes the changes state values according to the swap algorithm.

    Args:
        a: (Decimal) bnt_trading_liquidity
        b: (Decimal) tkn_trading_liquidity
        d: (Decimal) trading_fee
        e: (Decimal) network_fee
        x: (Decimal) bnt_amount
        direction: (str) Direction of TKN->BNT or BNT->TKN

    Returns:
        vortex_collection: (Decimal) Changed state amount of the target token.

    """
    if direction == "tkn":
        return a * d * e * x / (b + x)
    elif direction == "bnt":
        return d * e * x * (a + x) / (a + d * x)


def swap_fee_collection(
    a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """

    Args:
        a: (Decimal) bnt_trading_liquidity
        b: (Decimal) tkn_trading_liquidity
        d: (Decimal) trading_fee
        e: (Decimal) network_fee
        x: (Decimal) bnt_amount
        direction: (str) Direction of TKN->BNT or BNT->TKN

    Returns:

    """
    if direction == "tkn":
        return a * d * x * (1 - e) / (b + x)
    elif direction == "bnt":
        return b * d * x * (1 - e) / (a + x)


def trade_tkn_to_ema(
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
    trading_fee: Decimal,
    network_fee: Decimal,
    future_ema: Decimal,
) -> Decimal:
    """Outputs the tkn_amount that should be traded to force the ema and the spot price together on a given pool.


    Args:
        bnt_trading_liquidity:
        tkn_trading_liquidity:
        trading_fee:
        network_fee:
        future_ema:

    Returns:

    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    d = trading_fee
    e = network_fee
    f = future_ema
    tkn_amount = (
        (a * d * (Decimal("1") - e) - Decimal("2") * f * b)
        + (
            a
            * (
                Decimal("4") * f * b * (Decimal("1") - d * (Decimal("1") - e))
                + a * d ** Decimal("2") * (Decimal("1") - e) ** Decimal("2")
            )
        )
        ** (Decimal("1") / Decimal("2"))
    ) / (Decimal("2") * f)
    return tkn_amount


def trade_bnt_to_ema(
    bnt_trading_liquidity,
    tkn_trading_liquidity,
    trading_fee,
    network_fee,
    future_ema,
):
    """Calling this function will analyze the state of any pool, and create a swap that drives the ema and the spot price together.

    Args:
        bnt_trading_liquidity:
        tkn_trading_liquidity:
        trading_fee:
        network_fee:
        future_ema:

    Returns:
        bnt_amount: BNT value needed to drive the EMA closer to the spot.
    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    d = trading_fee
    e = network_fee
    f = future_ema
    x = (
        -Decimal("2") * a
        + b * d * f
        + (
            (Decimal("2") * a - b * d * f) ** Decimal("2")
            - Decimal("4") * a * (a - b * f)
        )
        ** (Decimal("1") / Decimal("2"))
    ) / Decimal("2")
    a_recursion = (
        a * (a + x) + d * (Decimal("1") - e) * (a * x + x ** Decimal("2"))
    ) / (a + d * x)
    b_recursion = b * (a + d * x) / (a + x)
    n = 0
    p = Decimal("0.001")
    while a_recursion / b_recursion < f:
        n += 1
        p += Decimal("0.0001")
        x += x * (f**p - (a_recursion / b_recursion) ** p) / f
        a_recursion = (
            a * (a + x) + d * (Decimal("1") - e) * (a * x + x ** Decimal("2"))
        ) / (a + d * x)
        b_recursion = b * (a + d * x) / (a + x)
        if n > 20000:
            break
    bnt_amount = x
    return bnt_amount
