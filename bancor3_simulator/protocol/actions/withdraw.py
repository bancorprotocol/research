from dataclasses import dataclass
from decimal import Decimal

from bancor3_simulator.core.dataclasses import CooldownState


@dataclass
class Result:
    updated_bnt_liquidity: Decimal("0")
    bnt_renounced: Decimal("0")
    updated_tkn_liquidity: Decimal("0")
    tkn_sent_to_user: Decimal("0")
    bnt_sent_to_user: Decimal("0")


def external_protection(
    bnt_trading_liquidity,
    average_tkn_trading_liquidity,
    withdrawal_fee,
    bnt_sent_to_user,
    external_protection_tkn_balance,
    tkn_withdraw_value,
    tkn_sent_to_user,
    trading_enabled,
):
    """
    This replaces any BNT that would have been received by the user with TKN.
    """
    a = bnt_trading_liquidity
    b = average_tkn_trading_liquidity
    n = withdrawal_fee
    T = bnt_sent_to_user
    w = external_protection_tkn_balance
    x = tkn_withdraw_value
    S = tkn_sent_to_user

    if not trading_enabled:
        bnt_sent_to_user = Decimal("0")
        external_protection_compensation = min(w, x * (1 - n) - S)

    elif T and w:
        if T * b > w * a:
            bnt_sent_to_user = (T * b - w * a) / b
            external_protection_compensation = w
        else:
            bnt_sent_to_user = Decimal("0")
            external_protection_compensation = T * b / a
    else:
        bnt_sent_to_user = T
        external_protection_compensation = Decimal("0")
    return bnt_sent_to_user, external_protection_compensation


def begin_cooldown(state, withdraw_value, tkn_name, user_name):
    """
    Takes the username and a quantity of tkn tokens as inputs.
    The users bntkn is converted into its tkn equivalent, and these values are stored in the pendingWithdrawals with the current timestamp number.
    After a fixed time duration, these items can be retrieved and passed to the withdrawal algorithm.
    """
    timestep = state.timestep
    staked_amt = (
        state.tokens[tkn_name].staked_tkn if tkn_name != "bnt" else state.staked_bnt
    )
    pool_token_supply = (
        state.tokens[tkn_name].erc20contracts_bntkn
        if tkn_name != "bnt"
        else state.erc20contracts_bnbnt
    )
    if staked_amt > 0:
        pool_token_amt = (lambda a, b, c: a * b / c)(
            pool_token_supply, withdraw_value, staked_amt
        )
    else:
        pool_token_amt = 0
    id_number = len(state.withdrawal_ids)
    state.withdrawal_ids.append(id_number)
    state.users.users[user_name].wallet[tkn_name].pending_withdrawals[
        id_number
    ] = CooldownState(
        timestep=timestep,
        withdrawal_id=id_number,
        user_name=user_name,
        tkn_name=tkn_name,
        tkn_amt=withdraw_value,
        pool_token_amt=pool_token_amt,
        is_complete=False,
    )

    state.users.users[user_name].wallet[tkn_name].bntkn_amt -= pool_token_amt
    state.protocol_bnt_check()
    return id_number


def unpack_cool_down_state(state, user_name, id_number):
    """
    Introduced to make the withdrawals eaiser to handle.
    """
    for tkn_name in state.whitelisted_tokens:
        if (
            id_number
            in state.users.users[user_name].wallet[tkn_name].pending_withdrawals
        ):
            cool_down_state = (
                state.users.users[user_name]
                .wallet[tkn_name]
                .pending_withdrawals[id_number]
            )
            if not cool_down_state.is_complete:
                cooldown_timestep = cool_down_state.timestep
                tkn_name = cool_down_state.tkn_name
                pool_token_amt = cool_down_state.pool_token_amt
                withdrawal_value = cool_down_state.tkn_amt
                return (
                    id_number,
                    cooldown_timestep,
                    tkn_name,
                    pool_token_amt,
                    withdrawal_value,
                    user_name,
                )
    raise ValueError(
        f"id_number={id_number} not foound in user_name={user_name} wallet pending_withdrawals"
    )


@dataclass
class WithdrawalAlgorithm:
    bnt_trading_liquidity: Decimal = Decimal("0")
    tkn_trading_liquidity: Decimal = Decimal("0")
    avg_tkn_trading_liquidity: Decimal = Decimal("0")
    tkn_excess: Decimal = Decimal("0")
    staked_tkn: Decimal = Decimal("0")
    trading_fee: Decimal = Decimal("0")
    withdrawal_fee: Decimal = Decimal("0")
    withdraw_value: Decimal = Decimal("0")
    bnt_sent_to_user: Decimal = Decimal("0")
    external_protection_tkn_balance: Decimal = Decimal("0")
    tkn_sent_to_user: Decimal = Decimal("0")
    trading_enabled: bool = True

    @property
    def hmax_surplus(self):
        """
        @Dev
        Returns the maximum number of withdrawn TKN that can currently be supported under the arbitrage method.
        """
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        m = self.trading_fee
        n = self.withdrawal_fee
        hmax = (
            b
            * e
            * (e * n + m * (b + c - e))
            / ((1 - m) * (b + c - e) * (b + c - e * (1 - n)))
        )
        return hmax

    @property
    def hmax_deficit(self):
        """
        @Dev
        Returns the maximum number of withdrawn TKN that can currently be supported under the arbitrage method.
        """
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        m = self.trading_fee
        n = self.withdrawal_fee
        hmax = (
            b
            * e
            * (e * n - m * (b + c - e * (1 - n)))
            / ((1 - m) * (b + c - e) * (b + c - e * (1 - n)))
        )
        return hmax

    @property
    def hlim(self):
        """
        Returns the maximum number of withdrawn TKN that can currently be supported under the arbitrage method.
        """
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        hlim = c * e / (b + c)
        return hlim

    def arbitrage_withdrawal_surplus(self):
        """
        @Dev
        Calculates the withdrawal output variables when the protocol can arbitrage the pool.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        m = self.trading_fee
        n = self.withdrawal_fee
        x = self.withdraw_value
        updated_bnt_liquidity = (
            a
            * (b * e - m * (b * e + x * (b + c - e * (1 - n))))
            / ((1 - m) * (b * e + x * (b + c - e * (1 - n))))
        )
        bnt_renounced = Decimal("0")
        updated_tkn_liquidity = (b * e + x * (b + c + e * (n - 1))) / e
        tkn_sent_to_user = x * (1 - n)
        bnt_sent_to_user = Decimal("0")
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def default_withdrawal_surplus_covered(
        self,
    ):
        """
        @Dev
        Calculates the withdrawal output variables when arbitrage is forbidden, and the excess TKN is sufficient to cover the entire withdrawal amount.
        """
        x = self.withdraw_value
        n = self.withdrawal_fee
        updated_bnt_liquidity = self.bnt_trading_liquidity
        bnt_renounced = Decimal("0")
        updated_tkn_liquidity = self.tkn_trading_liquidity
        tkn_sent_to_user = x * (1 - n)
        bnt_sent_to_user = Decimal("0")
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def default_withdrawal_surplus_exposed(self):
        """
        @Dev
        Calculates the withdrawal output variables when arbitrage is forbidden, and the TKN trading liquidity must be used to cover the withdrawal amount.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        n = self.withdrawal_fee
        x = self.withdraw_value
        updated_bnt_liquidity = a * (b + c - x * (1 - n)) / b
        bnt_renounced = a * (x * (1 - n) - c) / b
        updated_tkn_liquidity = b + c - x * (1 - n)
        tkn_sent_to_user = x * (1 - n)
        bnt_sent_to_user = Decimal("0")
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def arbitrage_withdrawal_deficit(self):
        """
        @Dev
        Calculates the withdrawal output variables when the protocol can arbitrage the pool.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        m = self.trading_fee
        n = self.withdrawal_fee
        x = self.withdraw_value
        updated_bnt_liquidity = (
            a * b * e / (b * e + x * (1 - m) * (b + c - e * (1 - n)))
        )
        bnt_renounced = Decimal("0")
        updated_tkn_liquidity = (b * e + x * (b + c - e * (1 - n))) / e
        tkn_sent_to_user = x * (1 - n)
        bnt_sent_to_user = Decimal("0")
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def default_withdrawal_deficit_covered(self):
        """
        @Dev
        Calculates the withdrawal output variables when arbitrage is forbidden, and the excess TKN is sufficient to cover the entire withdrawal amount.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        n = self.withdrawal_fee
        x = self.withdraw_value
        updated_bnt_liquidity = a
        bnt_renounced = Decimal("0")
        updated_tkn_liquidity = self.tkn_trading_liquidity
        tkn_sent_to_user = x * (1 - n) * (b + c) / e
        bnt_sent_to_user = a * x * (1 - n) * (e - b - c) / (b * e)
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def default_withdrawal_deficit_exposed(self):
        """
        @Dev
        Calculates the withdrawal output variables when arbitrage is forbidden, and the excess TKN is sufficient to cover the entire withdrawal amount.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        n = self.withdrawal_fee
        x = self.withdraw_value
        updated_bnt_liquidity = a * (b + c) * (e - x * (1 - n)) / (b * e)
        bnt_renounced = a * (b * e - (b + c) * (e - x * (1 - n))) / (b * e)
        updated_tkn_liquidity = (b + c) * (e - x * (1 - n)) / e
        tkn_sent_to_user = x * (1 - n) * (b + c) / e
        bnt_sent_to_user = a * x * (1 - n) * (e - b - c) / (b * e)
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def external_protection(self):
        """
        @Dev
        This replaces any BNT that would have been received by the user with TKN.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        n = self.withdrawal_fee
        T = self.bnt_sent_to_user
        w = self.external_protection_tkn_balance
        x = self.withdraw_value
        S = self.tkn_sent_to_user
        if not self.trading_enabled:
            bnt_sent_to_user = Decimal("0")
            external_protection_compensation = min(w, x * (1 - n) - S)
        elif T and w:
            if T * b > w * a:
                bnt_sent_to_user = (T * b - w * a) / b
                external_protection_compensation = w
            else:
                bnt_sent_to_user = Decimal("0")
                external_protection_compensation = T * b / a
        else:
            bnt_sent_to_user = T
            external_protection_compensation = Decimal("0")
        return bnt_sent_to_user, external_protection_compensation

    def illiquid_withdrawal(self):
        """
        Calculates the withdrawal output variables when trading is disabled.
        """
        c = self.tkn_excess
        e = self.staked_tkn
        n = self.withdrawal_fee
        x = self.withdraw_value
        updated_bnt_liquidity = self.bnt_trading_liquidity
        bnt_renounced = Decimal("0")
        updated_tkn_liquidity = self.tkn_trading_liquidity
        if c / (1 - n) > e:
            tkn_sent_to_user = x * (1 - n)
        else:
            tkn_sent_to_user = c * x * (1 - n) / e
        bnt_sent_to_user = Decimal("0")
        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
        )

    def process_withdrawal(
        self,
        updated_bnt_liquidity: Decimal = Decimal("0"),
        bnt_renounced: Decimal = Decimal("0"),
        updated_tkn_liquidity: Decimal = Decimal("0"),
        tkn_sent_to_user: Decimal = Decimal("0"),
    ):
        """
        Evaluates the conditions, and calls the appropriate functions
        """

        b = self.avg_tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        n = self.withdrawal_fee
        x = self.withdraw_value
        if not self.trading_enabled:
            (
                updated_bnt_liquidity,
                bnt_renounced,
                updated_tkn_liquidity,
                tkn_sent_to_user,
                bnt_sent_to_user,
            ) = self.illiquid_withdrawal()
        elif b + c > e * (1 - n):
            if b + c > e and x < self.hlim and x < self.hmax_surplus:
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                ) = self.arbitrage_withdrawal_surplus()
            elif x * (1 - n) <= c:
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                ) = self.default_withdrawal_surplus_covered()
            else:
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                ) = self.default_withdrawal_surplus_exposed()
        elif b + c <= e * (1 - n):
            if x < self.hlim and x < self.hmax_deficit:
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                ) = self.arbitrage_withdrawal_deficit()
            elif x * (1 - n) * (b + c) <= c * e:
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                ) = self.default_withdrawal_deficit_covered()
            else:
                (
                    updated_bnt_liquidity,
                    bnt_renounced,
                    updated_tkn_liquidity,
                    tkn_sent_to_user,
                    bnt_sent_to_user,
                ) = self.default_withdrawal_deficit_exposed()
        bnt_sent_to_user, external_protection_compensation = self.external_protection()

        return (
            updated_bnt_liquidity,
            bnt_renounced,
            updated_tkn_liquidity,
            tkn_sent_to_user,
            bnt_sent_to_user,
            external_protection_compensation,
        )
