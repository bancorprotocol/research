# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Simulation utility functions."""


def trade_tkn_to_ema(
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
    trading_fee: Decimal,
    network_fee: Decimal,
    future_ema: Decimal,
) -> Decimal:
    """
    Outputs the tkn_amt that should be traded to force the ema and the spot price together on a given pool.
    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    d = trading_fee
    e = network_fee
    f = future_ema
    tkn_amt = (
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
    return tkn_amt


def trade_bnt_to_ema(
    bnt_trading_liquidity,
    tkn_trading_liquidity,
    trading_fee,
    network_fee,
    future_ema,
):
    """
    Analyze the state of any pool and create a swap that drives the ema and the spot price together.
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
    bnt_amt = x
    return bnt_amt


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
    """
    Computes the appropriate arbitrage trade on the token_name pool.
    """
    a = bnt_trading_liquidity
    b = tkn_trading_liquidity
    m = trading_fee
    p = bnt_virtual_balance
    q = tkn_token_virtual_balance

    bnt_trade_amt = (
        -Decimal("2") * a * q
        + b * m * p
        + (
            (Decimal("2") * a * q - b * m * p) ** Decimal("2")
            - Decimal("4") * a * q * (a * q - b * p)
        )
        ** (Decimal("1") / Decimal("2"))
    ) / (Decimal("2") * q)

    tkn_trade_amt = (
        -Decimal("2") * b * p
        + a * m * q
        + (
            (Decimal("2") * b * p - a * m * q) ** Decimal("2")
            - Decimal("4") * b * p * (b * p - a * q)
        )
        ** (Decimal("1") / Decimal("2"))
    ) / (Decimal("2") * p)

    if bnt_trade_amt > 0:
        source_token = "bnt"
        target_token = tkn_name
        trade_amt = bnt_trade_amt
        user_capability = user_bnt > bnt_trade_amt
        return trade_amt, source_token, target_token, user_capability

    elif tkn_trade_amt > 0:
        source_token = tkn_name
        target_token = "bnt"
        trade_amt = tkn_trade_amt
        user_capability = user_tkn > tkn_trade_amt
        return trade_amt, source_token, target_token, user_capability
