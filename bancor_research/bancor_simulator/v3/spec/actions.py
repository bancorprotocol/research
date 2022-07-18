# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Agent-based actions. (e.g. trade, deposit, withdraw, etc...)"""
from pydantic.dataclasses import dataclass

from bancor_research.bancor_simulator.v3.spec.state import (
    get_trade_inputs,
    get_withdrawal_id,
    Cooldown,
    Token,
)
from bancor_research.bancor_simulator.v3.spec.utils import *


def deposit_bnt(state: State, tkn_name: str, tkn_amt: Decimal, user_name: str) -> State:
    """
    Specific case of .stake() method, see .stake() method docstring
    """
    bnbnt_amt = compute_bnbnt_amt(state, tkn_amt)
    state.decrease_user_balance(user_name, tkn_name, tkn_amt)
    state.decrease_protocol_wallet_balance("bnt", tkn_amt)
    state.increase_user_balance(user_name, f"bn{tkn_name}", bnbnt_amt)
    state.increase_user_balance(user_name, "vbnt", bnbnt_amt)
    return state


def deposit_tkn(state: State, tkn_name: str, tkn_amt: Decimal, user_name: str) -> State:
    """
    Specific case of .stake() method, see .stake() method docstring
    """
    bntkn_amt = compute_bntkn_amt(state, tkn_name, tkn_amt)
    state.decrease_user_balance(user_name, tkn_name, tkn_amt)
    state.increase_user_balance(user_name, f"bn{tkn_name}", bntkn_amt)
    state.increase_pooltoken_balance(tkn_name, bntkn_amt)
    state.increase_vault_balance(tkn_name, bntkn_amt)
    state.increase_staked_balance(tkn_name, bntkn_amt)

    case, bnt_increase, tkn_increase = compute_pool_depth_adjustment(state, tkn_name)

    state.increase_bnt_trading_liquidity(tkn_name, bnt_increase)
    state.increase_tkn_trading_liquidity(tkn_name, tkn_increase)
    state.decrease_bnt_funding_amt(tkn_name, bnt_increase)
    state.set_protocol_wallet_balance("bnt", bnt_increase)

    state.update_spot_rate(tkn_name)

    if check_pool_shutdown(state, tkn_name):
        state = shutdown_pool(state, tkn_name)

    return state


def process_trade(
    state: State,
    tkn_amt: Decimal,
    source_token: str,
    target_token: str,
    user_name: str,
    timestamp: int = 0,
) -> State:
    """
    Main logic for trade actions.
    """

    is_trading_enabled_target = get_is_trading_enabled(state, target_token)
    is_trading_enabled_source = get_is_trading_enabled(state, source_token)

    if source_token == "bnt" and is_trading_enabled_target:

        (
            tkn_name,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
        ) = get_trade_inputs(state, target_token)

        state, target_sent_to_user = trade_bnt_for_tkn(
            state,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            tkn_amt,
            tkn_name,
        )

    elif target_token == "bnt" and is_trading_enabled_source:

        (
            tkn_name,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
        ) = get_trade_inputs(state, source_token)

        state, target_sent_to_user = trade_tkn_for_bnt(
            state,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            tkn_amt,
            tkn_name,
        )

    elif (
        source_token != "bnt"
        and target_token != "bnt"
        and is_trading_enabled_source
        and is_trading_enabled_target
    ):

        (
            tkn_name,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
        ) = get_trade_inputs(state, source_token)

        state, intermediate_bnt = trade_tkn_for_bnt(
            state,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            tkn_amt,
            tkn_name,
        )

        (
            tkn_name,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
        ) = get_trade_inputs(state, target_token)

        state, target_sent_to_user = trade_bnt_for_tkn(
            state,
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            intermediate_bnt,
            tkn_name,
        )

    else:
        # Trading is disabled
        tkn_amt = Decimal("0")
        target_sent_to_user = Decimal("0")

    state.decrease_user_balance(user_name, source_token, tkn_amt)
    state.increase_user_balance(user_name, target_token, target_sent_to_user)
    return state


def trade_bnt_for_tkn(
    state: State,
    bnt_trading_liquidity: Decimal,
    tkn_trading_liquidity: Decimal,
    trading_fee: Decimal,
    network_fee: Decimal,
    bnt_amt: Decimal,
    tkn_name: str,
    direction: str = "bnt",
) -> Tuple[State, Decimal]:
    state = handle_ema(state, tkn_name)
    updated_bnt_liquidity = compute_changed_bnt_trading_liquidity(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        bnt_amt,
        direction,
    )

    updated_tkn_liquidity = compute_changed_tkn_trading_liquidity(
        bnt_trading_liquidity, tkn_trading_liquidity, trading_fee, bnt_amt, direction
    )
    tkn_sent_to_user = compute_target_amt(
        bnt_trading_liquidity, tkn_trading_liquidity, trading_fee, bnt_amt, direction
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

    state.increase_vault_balance("bnt", bnt_amt)
    state.decrease_vault_balance(tkn_name, tkn_sent_to_user)
    state.set_bnt_trading_liquidity(tkn_name, updated_bnt_liquidity)
    state.set_tkn_trading_liquidity(tkn_name, updated_tkn_liquidity)
    state.increase_staked_balance(tkn_name, trade_fee)
    state.increase_vortex_balance("bnt", bnt_collected_by_vortex)
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
    """
    Main logic to process swaps/trades from TKN->BNT
    """

    state = handle_ema(state, tkn_name)
    updated_bnt_liquidity = compute_changed_bnt_trading_liquidity(
        bnt_trading_liquidity,
        tkn_trading_liquidity,
        trading_fee,
        network_fee,
        tkn_amt,
        direction,
    )
    updated_tkn_liquidity = compute_changed_tkn_trading_liquidity(
        bnt_trading_liquidity, tkn_trading_liquidity, trading_fee, tkn_amt, direction
    )
    bnt_sent_to_user = compute_target_amt(
        bnt_trading_liquidity, tkn_trading_liquidity, trading_fee, tkn_amt, direction
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

    state.decrease_vault_balance("bnt", bnt_sent_to_user)
    state.increase_vault_balance(tkn_name, tkn_amt)
    state.set_bnt_trading_liquidity(tkn_name, updated_bnt_liquidity)
    state.set_tkn_trading_liquidity(tkn_name, updated_tkn_liquidity)
    state.increase_staked_balance("bnt", trade_fee)
    state.increase_bnt_funding_amt(tkn_name, trade_fee)
    state.increase_vortex_balance("bnt", bnt_collected_by_vortex)
    state.update_spot_rate(tkn_name)
    return state, bnt_sent_to_user


def process_withdrawal(
    state: State,
    user_name: str,
    id_number: int,
    timestamp: int = 0,
    tkn_name: str = None,
    tkn_amt: Decimal = None,
):
    """
    Main withdrawal logic based on the withdraw algorithm of the BIP15 spec.
    """

    (
        id_number,
        cooldown_timestamp,
        tkn_name,
        pool_token_amt,
        withdraw_value,
        user_name,
    ) = unpack_withdrawal_cooldown(state, user_name, id_number)

    withdrawal_fee = state.withdrawal_fee
    bnt_amt = withdraw_value * (1 - withdrawal_fee)
    cooldown_time = state.cooldown_time
    cool_down_complete = timestamp - cooldown_timestamp >= cooldown_time

    if tkn_name != "bnt":
        bnbnt_rate = state.bnbnt_rate
        is_price_stable = get_is_price_stable(state, tkn_name)

        if cool_down_complete and is_price_stable:

            state.set_pending_withdrawals_status(
                state, user_name, tkn_name, id_number, True
            )

            bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
            tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
            avg_tkn_trading_liquidity = get_avg_tkn_trading_liquidity(state, tkn_name)
            tkn_excess = get_tkn_excess(state, tkn_name)
            staked_tkn = get_staked_balance(state, tkn_name)
            trading_fee = get_trading_fee(state, tkn_name)

            solver = WithdrawalAlgorithm(
                bnt_trading_liquidity=bnt_trading_liquidity,
                tkn_trading_liquidity=tkn_trading_liquidity,
                avg_tkn_trading_liquidity=avg_tkn_trading_liquidity,
                tkn_excess=tkn_excess,
                staked_tkn=staked_tkn,
                trading_fee=trading_fee,
                withdrawal_fee=withdrawal_fee,
                withdraw_value=withdraw_value,
            )
            (
                updated_bnt_liquidity,
                bnt_renounced,
                updated_tkn_liquidity,
                tkn_sent_to_user,
                bnt_sent_to_user,
                external_protection_compensation,
            ) = solver.process_withdrawal()

            if bnt_renounced == 0:
                bnt_delta = updated_bnt_liquidity - bnt_trading_liquidity
                state.increase_vault_balance(tkn_name, bnt_delta)

            state.set_bnt_trading_liquidity(tkn_name, updated_bnt_liquidity)
            state.decrease_staked_balance("bnt", bnt_renounced)
            state.decrease_vault_balance("bnt", bnt_renounced)
            state.increase_bnt_funding_amt(tkn_name, bnt_renounced)

            bnbnt_renounced = bnbnt_rate * bnt_renounced

            state.decrease_pooltoken_balance("bnbnt", bnbnt_renounced)
            state.decrease_protocol_wallet_balance("bnbnt", bnbnt_renounced)
            state.set_tkn_trading_liquidity(tkn_name, updated_tkn_liquidity)
            state.decrease_protocol_wallet_balance(f"bn{tkn_name}", pool_token_amt)
            state.decrease_staked_balance(tkn_name, withdraw_value)
            state.decrease_vault_balance(tkn_name, tkn_sent_to_user)
            state.increase_user_balance(
                user_name,
                tkn_name,
                tkn_sent_to_user + external_protection_compensation,
            )
            state.decrease_external_protection_balance(
                tkn_name, external_protection_compensation
            )
            state.increase_user_balance(user_name, "bnt", bnt_sent_to_user)

            state.update_spot_rate(tkn_name)

            if check_pool_shutdown(state, tkn_name):
                state = shutdown_pool(state, tkn_name)

    else:

        sufficient_vbnt = get_user_balance(state, "vbnt") >= pool_token_amt

        if cool_down_complete and sufficient_vbnt:
            state.set_pending_withdrawals_status(user_name, tkn_name, id_number, True)
            state.decrease_user_balance(user_name, "vbnt", pool_token_amt)
            state.increase_user_balance(user_name, "bnt", bnt_amt)
            state.increase_protocol_wallet_balance("bnbnt", pool_token_amt)

    return state


def begin_withdrawal_cooldown(state, withdraw_value, tkn_name, user_name):
    """
    After a fixed time duration, these items can be retrieved and passed to the withdrawal algorithm.
    """
    pool_token_amt = compute_pooltoken_amt(state, tkn_name, withdraw_value)
    id_number = get_withdrawal_id(state)
    state.users[user_name].pending_withdrawals[id_number] = Cooldown(
        id=id_number,
        created_at=state.timestamp,
        user_name=user_name,
        tkn_name=tkn_name,
        tkn=Token(balance=withdraw_value),
        pooltoken=Token(balance=pool_token_amt),
        is_complete=False,
    )

    state.decrease_user_balance(user_name, f"bn{tkn_name}", pool_token_amt)
    return state, id_number


def unpack_withdrawal_cooldown(
    state: State, user_name: str, id_number: int
) -> Tuple[int, int, str, Decimal, Decimal, str]:
    """
    Introduced to make the withdrawals easier to handle.
    """
    if id_number in state.users[user_name].pending_withdrawals:
        cool_down_state = state.users[user_name].pending_withdrawals[id_number]
        if not cool_down_state.is_complete:
            cooldown_timestamp = cool_down_state.created_at
            tkn_name = cool_down_state.tkn_name
            pool_token_amt = cool_down_state.pooltoken.balance
            withdrawal_value = cool_down_state.tkn.balance
            return (
                id_number,
                cooldown_timestamp,
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
    is_trading_enabled: bool = True

    @property
    def hmax_surplus(self):
        """
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
        Calculates the withdrawal output variables when the v3 can arbitrage the pool.
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
        Calculates the withdrawal output variables when arbitrage is forbidden, and the excess TKN is sufficient to cover the entire withdrawal amt.
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
        Calculates the withdrawal output variables when arbitrage is forbidden, and the TKN trading liquidity must be used to cover the withdrawal amt.
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
        Calculates the withdrawal output variables when the v3 can arbitrage the pool.
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
        Calculates the withdrawal output variables when arbitrage is forbidden, and the excess TKN is sufficient to cover the entire withdrawal amt.
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
        Calculates the withdrawal output variables when arbitrage is forbidden, and the excess TKN is sufficient to cover the entire withdrawal amt.
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
        This replaces any BNT that would have been received by the user with TKN.
        """
        a = self.bnt_trading_liquidity
        b = self.avg_tkn_trading_liquidity
        n = self.withdrawal_fee
        T = self.bnt_sent_to_user
        w = self.external_protection_tkn_balance
        x = self.withdraw_value
        S = self.tkn_sent_to_user
        if not self.is_trading_enabled:
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

        b = self.tkn_trading_liquidity
        c = self.tkn_excess
        e = self.staked_tkn
        n = self.withdrawal_fee
        x = self.withdraw_value
        if not self.is_trading_enabled:
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


def get_burn_reward(vortex_ledger_balance: Decimal) -> Tuple[Decimal, Decimal]:
    """
    Returns the burn_reward and the updated_bnt_amount.
    """
    burn_reward = min(Decimal("100"), vortex_ledger_balance / Decimal("10"))
    bnt_amount = vortex_ledger_balance - burn_reward
    return burn_reward, bnt_amount


def get_target_amount(a, b, d, x, direction):
    """
    Returns the quantity of the target asset purchased to the user.
    """
    if direction == "tkn":
        return a * x * (1 - d) / (b + x)
    elif direction == "bnt":
        return b * x * (1 - d) / (a + x)


def vortex_burner(state: State, user_name: str):
    """
    The bnt balance of the vortex is swapped for vbnt, vbnt is destroyed, and the user is rewarded.
    """
    vortex_ledger_balance = get_vortex_balance(state, "bnt")
    tkn_name = "vbnt"
    if get_is_trading_enabled(state, tkn_name) and vortex_ledger_balance > 0:
        burn_reward, bnt_amount = get_burn_reward(vortex_ledger_balance)
        handle_ema(tkn_name)
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
        tkn_trading_liquidity = get_tkn_trading_liquidity(state, tkn_name)
        trading_fee = get_trading_fee(state, tkn_name)
        network_fee = Decimal("0")
        direction = "bnt"
        updated_bnt_liquidity = compute_changed_bnt_trading_liquidity(
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            bnt_amount,
            direction,
        )
        updated_tkn_liquidity = compute_changed_tkn_trading_liquidity(
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            bnt_amount,
            direction,
        )
        vbnt_to_burner = vortex_collection(
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            bnt_amount,
            direction,
        )
        trade_fee = swap_fee_collection(
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            bnt_amount,
            direction,
        )
        state.increase_user_balance(user_name, "bnt", burn_reward)
        state.set_vortex_balance("bnt", Decimal("0"))
        state.increase_vbnt_burned("bnt", Decimal("0"))
        state.decrease_vault_balance("bnt", burn_reward)
        state.decrease_vault_balance(tkn_name, burn_reward)
        state.set_bnt_trading_liquidity(tkn_name, updated_bnt_liquidity)
        state.set_tkn_trading_liquidity(tkn_name, updated_tkn_liquidity)
        state.increase_staked_balance(tkn_name, trade_fee)
        state.update_spot_rate(tkn_name)
