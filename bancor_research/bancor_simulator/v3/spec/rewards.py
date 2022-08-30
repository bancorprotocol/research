# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Autocompounding and standard rewards issuance logic."""
from bancor_research.bancor_simulator.v3.spec.state import *


def calc_pool_token_amt_to_burn(
    staked_amt: Decimal,
    token_amt_to_distribute: Decimal,
    prev_token_amt_distributed: Decimal,
    erc20contracts_bntkn: Decimal,
    program_wallet_bntkn: Decimal,
) -> Decimal:
    """
    Return the token amt to burn for a given exponential distribution reward program.
    """
    a = staked_amt
    b = token_amt_to_distribute - prev_token_amt_distributed
    c = erc20contracts_bntkn
    d = program_wallet_bntkn
    return b * c**2 / (c * (a + b) - a * d)


def calc_flat_token_amt_to_distribute(
    state: State,
    tkn_name: str,
    time_elapsed: Decimal,
    total_rewards: Decimal,
) -> Decimal:
    """
    Return the token amt to distribute for a given flat distribution reward program.
    """
    flat_distribution_rate_per_second = get_flat_distribution_rate_per_second(
        state, tkn_name
    )
    return min(time_elapsed * flat_distribution_rate_per_second, total_rewards)


def calc_exp_token_amt_to_distribute(
    state: State, tkn_name: str, total_rewards: Decimal, time_elapsed: Decimal
) -> Decimal:
    """
    Return the token amt to distribute for a given exponential distribution reward program.
    """
    half_life = get_half_life(state, tkn_name)
    return total_rewards * (1 - (2 ** (-time_elapsed / half_life)))


def process_ac_rewards_program(state: State, tkn_name: str, timestamp: int) -> State:
    """
    Processes autocompounding rewards program for a given pool.
    """
    assert (
        tkn_name in state.autocompounding_reward_programs
    ), f"{tkn_name} not found in autocompounding_programs"

    staked_amt = get_staked_balance(state, tkn_name)
    erc20contracts_bntkn = get_pooltoken_balance(state, tkn_name)
    total_rewards = get_total_rewards(state, tkn_name)
    prev_token_amt_distributed = get_prev_token_amt_distributed(state, tkn_name)
    distribution_type = get_distribution_type(state, tkn_name)
    start_time = get_autocompounding_start_time(state, tkn_name)
    time_elapsed = Decimal(timestamp) - Decimal(start_time)

    if distribution_type == "flat":

        token_amt_to_distribute = calc_flat_token_amt_to_distribute(
            state=state,
            tkn_name=tkn_name,
            time_elapsed=time_elapsed,
            total_rewards=total_rewards,
        )
    else:

        token_amt_to_distribute = calc_exp_token_amt_to_distribute(
            state=state,
            tkn_name=tkn_name,
            total_rewards=total_rewards,
            time_elapsed=time_elapsed,
        )

    if tkn_name == "bnt":
        program_wallet_bntkn = get_protocol_wallet_balance(state, tkn_name)
    else:
        program_wallet_bntkn = get_external_rewards_vault_balance(state, tkn_name)

    pool_token_amt_to_burn = calc_pool_token_amt_to_burn(
        staked_amt=staked_amt,
        token_amt_to_distribute=token_amt_to_distribute,
        prev_token_amt_distributed=prev_token_amt_distributed,
        erc20contracts_bntkn=erc20contracts_bntkn,
        program_wallet_bntkn=program_wallet_bntkn,
    )

    # sanity check
    if pool_token_amt_to_burn >= erc20contracts_bntkn / 2:
        return terminate_ac_rewards_program(state, tkn_name, timestamp)

    if pool_token_amt_to_burn > 0:
        state.decrease_pooltoken_balance(tkn_name, pool_token_amt_to_burn)
        state.set_prev_token_amt_distributed(tkn_name, token_amt_to_distribute)
        remaining_rewards = total_rewards - token_amt_to_distribute
        state.set_autocompounding_remaining_rewards(tkn_name, remaining_rewards)
        if tkn_name == "bnt":
            state.decrease_protocol_wallet_balance(tkn_name, pool_token_amt_to_burn)
        else:
            state.decrease_external_rewards_vault_balance(
                tkn_name, pool_token_amt_to_burn
            )

    return state


def terminate_ac_rewards_program(state: State, tkn_name: str, timestamp: int) -> State:
    """
    Terminates autocompounding rewards program for a given pool.
    """
    del state.autocompounding_reward_programs[tkn_name]
    return state


"""
 * ------------------------------------------------------
 *
 * Everything below here refers to Standard Rewards
 *
 * ------------------------------------------------------
"""


def create_standard_reward_program(
    state: State,
    tkn_name: str,
    total_rewards: Decimal,
    start_time: int,
    end_time: int,
    timestamp: int,
) -> Tuple[State, int]:
    """
    Create a standard rewards program.
    """

    if not timestamp <= start_time and start_time < end_time:
        raise ValueError("standard program time constraints not met")

    if tkn_name in state.active_standard_programs:
        raise ValueError("standard program already exists")

    id = state.next_standard_program_id()

    reward_rate = total_rewards / (end_time - start_time)
    remaining_rewards = reward_rate * (end_time - start_time)

    state.standard_reward_programs[id] = StandardProgram(
        id=id,
        tkn_name=tkn_name,
        is_active=True,
        last_update_time=start_time,
        start_time=start_time,
        end_time=end_time,
        reward_rate=reward_rate,
    )

    state.set_standard_remaining_rewards(id, remaining_rewards)

    return state, id


def terminate_standard_program(state: State, id: int, timestamp: int) -> State:
    """
    Terminates the standard rewards program.
    """
    state.set_standard_program_is_active(id, False)
    state.set_standard_program_end_time(id, timestamp)
    return state


def snapshot_standard_rewards(
    state: State, id: int, timestamp: int, user_name: str
) -> State:
    """
    Snapshot of the existing standard rewards before modifying the staked_reward_amt balance.
    """
    state.map_user_standard_program(user_name, id)

    new_reward_per_token = calc_standard_reward_per_token(state, id, timestamp)
    state.set_standard_rewards_per_token(id, new_reward_per_token)

    end_time = get_standard_reward_end_time(state, id)
    last_update_time = get_standard_reward_last_update_time(state, id)
    state.set_standard_rewards_last_update_time(
        id, max(min(timestamp, end_time), last_update_time)
    )

    provider_staked_amount = get_user_pending_rewards_staked_balance(
        state, id, user_name
    )
    provider_pending_rewards = get_user_pending_standard_rewards(state, id, user_name)
    reward_per_token_paid = get_user_reward_per_token_paid(state, id, user_name)

    new_pending_rewards = calc_user_pending_standard_rewards(
        provider_pending_rewards,
        provider_staked_amount,
        new_reward_per_token,
        reward_per_token_paid,
    )

    state.set_provider_pending_standard_rewards(user_name, id, new_pending_rewards)
    state.set_provider_reward_per_token_paid(user_name, id, new_reward_per_token)
    return state


def calc_standard_reward_per_token(state: State, id: int, timestamp: int) -> Decimal:
    """
    Calculates the reward per token for the given program id.
    """
    total_staked = get_total_standard_rewards_staked(state, id)
    reward_per_token = get_standard_reward_per_token(state, id)

    if total_staked == 0:
        return reward_per_token

    start_time = get_standard_reward_start_time(state, id)
    end_time = get_standard_reward_end_time(state, id)
    last_update_time = get_standard_reward_last_update_time(state, id)
    reward_rate = get_standard_reward_rate(state, id)

    staking_end_time = min(timestamp, end_time)
    staking_start_time = max(start_time, last_update_time)

    return (
        reward_per_token
        + (staking_end_time - staking_start_time) * reward_rate / total_staked
    )


def calc_user_pending_standard_rewards(
    provider_pending_rewards: Decimal,
    provider_staked_amount: Decimal,
    updated_reward_per_token: Decimal,
    reward_per_token_paid: Decimal,
) -> Decimal:
    """
    Calculates the standard rewards pending for a given user
    """
    return provider_pending_rewards + provider_staked_amount * (
        updated_reward_per_token - reward_per_token_paid
    )


def calc_standard_rewards_remaining(state: State, id: int, timestamp: int) -> Decimal:
    """
    Calculates the standard rewards remaining for a given program id.
    """
    reward_rate = get_standard_reward_rate(state, id)
    end_time = get_standard_reward_end_time(state, id)
    return reward_rate * max(end_time - timestamp, 0)


def join_standard_reward_program(
    state: State, user_name: str, id: int, pool_token_amount: Decimal, timestamp: int
) -> State:
    """
    Join a standard reward program with the given user and id.
    """
    pool_token_name = get_standard_reward_pool_token_name(state, id)
    state = snapshot_standard_rewards(state, id, timestamp, user_name)
    state.decrease_user_balance(user_name, pool_token_name, pool_token_amount)
    state.increase_user_standard_rewards_stakes(id, user_name, pool_token_amount)
    return state


def leave_standard_reward_program(
    state: State, user_name: str, id: int, pool_token_amount: Decimal, timestamp: int
) -> State:
    """
    Leave a standard reward program for the given user and program id.
    """
    pool_token_name = get_standard_reward_pool_token_name(state, id)
    state = snapshot_standard_rewards(state, id, timestamp, user_name)
    state.decrease_user_standard_rewards_stakes(id, user_name, pool_token_amount)
    state.increase_user_balance(user_name, pool_token_name, pool_token_amount)
    return state


def claim_standard_rewards(
    state: State,
    user_name: str,
    ids: list,
    timestamp: int,
) -> State:
    """
    Claim standard rewards for the given user.
    """
    for id in ids:

        state = snapshot_standard_rewards(state, id, timestamp, user_name)
        reward_amt = get_user_pending_standard_rewards(state, id, user_name)
        remaining_rewards = get_standard_remaining_rewards(state, id)
        assert remaining_rewards >= reward_amt
        state.set_standard_remaining_rewards(id, remaining_rewards - reward_amt)
        state.set_user_pending_standard_rewards(user_name, id, Decimal(0))
        state.increase_user_balance(user_name, "bnt", reward_amt)

    return state
