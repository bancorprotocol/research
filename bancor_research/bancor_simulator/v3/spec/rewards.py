# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Autocompounding and standard rewards issuance logic."""
from bancor_research.bancor_simulator.v3.spec.state import *


def burn_tokens(state: State, tkn_name: str, tkn_amt: Decimal) -> State:
    """
    Burn tokens for a given exponential distribution reward program.
    """
    state.decrease_pooltoken_balance(tkn_name, tkn_amt)
    state.decrease_protocol_wallet_balance(tkn_name, tkn_amt)
    return state


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
    half_life_seconds = get_half_life_seconds(state, tkn_name)
    return total_rewards * (1 - (2 ** (-time_elapsed / half_life_seconds)))


def distribute_autocompounding_program(
    state: State, tkn_name: str, timestamp: int, verbose: bool = True
) -> State:
    """
    Distribute autocompounding rewards for a given program.
    """
    assert (
        tkn_name in state.autocompounding_reward_programs
    ), f"{tkn_name} not found in autocompounding_programs"

    staked_amt = get_staked_balance(state, tkn_name)
    erc20contracts_bntkn = get_pooltoken_balance(state, tkn_name)
    program_wallet_bntkn = get_protocol_wallet_balance(state, tkn_name)
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

    pool_token_amt_to_burn = calc_pool_token_amt_to_burn(
        staked_amt=staked_amt,
        token_amt_to_distribute=token_amt_to_distribute,
        prev_token_amt_distributed=prev_token_amt_distributed,
        erc20contracts_bntkn=erc20contracts_bntkn,
        program_wallet_bntkn=program_wallet_bntkn,
    )

    if pool_token_amt_to_burn > program_wallet_bntkn:
        print(
            "pool_token_amt_to_burn > program_wallet_bntkn, setting pool_token_amt_to_burn=0"
        )
        pool_token_amt_to_burn = program_wallet_bntkn
        state.set_program_is_active(tkn_name, False)

    state = burn_tokens(state, tkn_name, pool_token_amt_to_burn)
    state.set_prev_token_amt_distributed(tkn_name, token_amt_to_distribute)
    remaining_rewards = total_rewards - token_amt_to_distribute
    state.set_autocompounding_remaining_rewards(tkn_name, remaining_rewards)

    if verbose:
        print(f" staked_amt = {staked_amt}")
        print(f" erc20contracts_bntkn = {erc20contracts_bntkn}")
        print(f" program_wallet_bntkn = {program_wallet_bntkn}")
        print(f" total_rewards = {total_rewards}")
        print(f" prev_token_amt_distributed = {prev_token_amt_distributed}")
        print(f" token_amt_to_distribute = {token_amt_to_distribute}")
        print(f" pool_token_amt_to_burn = {pool_token_amt_to_burn}")
        print(f" remaining_rewards = {remaining_rewards}")

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
    rewards_token: str,
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

    unclaimed_rewards = get_unclaimed_rewards(state, rewards_token)
    reward_rate = total_rewards / (end_time - start_time)
    remaining_rewards = reward_rate * (end_time - start_time)

    state.standard_reward_programs[id] = StandardProgram(
        id=id,
        tkn_name=tkn_name,
        rewards_token=rewards_token,
        is_enabled=True,
        start_time=start_time,
        end_time=end_time,
        reward_rate=reward_rate,
        remaining_rewards=remaining_rewards,
    )

    state.set_standard_rewards_vault_balance(
        rewards_token, unclaimed_rewards + total_rewards
    )
    return state, id


def terminate_standard_program(state: State, id: int, timestamp: int) -> State:
    """
    Terminates the standard program.
    """
    tkn_name, rewards_token = get_standard_reward_tkn_name(state, id)
    remaining_rewards = calc_standard_rewards_remaining(state, id, timestamp)

    state.set_standard_program_is_active(id, False)
    state.decrease_standard_rewards_vault_balance(rewards_token, remaining_rewards)
    state.set_standard_program_end_time(id, timestamp)
    return state


def snapshot_standard_rewards(
    state: State, id: int, timestamp: int, user_name: str
) -> State:
    """
    Snapshot of the existing standard rewards before modifying the staked_reward_amt balance.
    """
    new_reward_per_token = calc_standard_reward_per_token(state, id)
    old_reward_per_token = get_standard_reward_per_token(state, id)

    if new_reward_per_token != old_reward_per_token:
        state.set_standard_rewards_per_token(id, new_reward_per_token)

    end_time = get_standard_reward_end_time(state, id)
    new_update_time = min(timestamp, end_time)
    last_update_time = get_standard_reward_last_update_time(state, id)

    if last_update_time < new_update_time:
        state.set_standard_rewards_last_update_time(id, new_update_time)

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

    if new_pending_rewards != 0:
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
    return reward_rate * (end_time - timestamp) if end_time > timestamp else Decimal(0)


def join_standard_reward_program(
    state: State, user_name: str, id: int, pool_token_amount: Decimal, timestamp: int
) -> State:
    """
    Join a standard reward program with the given user and id.
    """
    tkn_name, rewards_token = get_standard_reward_tkn_name(state, id)
    assert tkn_name in get_user_wallet_tokens(
        state, user_name
    ), f"User {user_name} does not have token {tkn_name} in wallet"

    state = snapshot_standard_rewards(state, id, timestamp, user_name)
    state.decrease_user_balance(
        user_name, get_pooltoken_name(tkn_name), pool_token_amount
    )
    state.increase_standard_reward_program_stakes(id, pool_token_amount)
    state.increase_user_standard_rewards_stakes(id, pool_token_amount)
    state.add_user_to_standard_reward_providers(id, user_name)
    return state


def leave_standard_reward_program(
    state: State, user_name: str, id: int, pool_token_amount: Decimal, timestamp: int
) -> State:
    """
    Leave a standard reward program for the given user and program id.
    """
    tkn_name, rewards_token = get_standard_reward_tkn_name(state, id)
    assert user_name in get_standard_reward_providers(
        state, id
    ), f"User {user_name} not in standard reward providers"

    state = snapshot_standard_rewards(state, id, timestamp, user_name)
    state.decrease_standard_reward_program_stakes(id, pool_token_amount)
    state.decrease_user_standard_rewards_stakes(id, pool_token_amount)
    state.increase_user_balance(
        user_name, get_pooltoken_name(rewards_token), pool_token_amount
    )
    state.remove_user_from_standard_reward_program(id, user_name)
    return state


def claim_standard_rewards(
    state: State,
    user_name: str,
    ids: list,
    timestamp: int,
    is_vault_updated: bool = False,
) -> State:
    """
    Claim standard rewards for the given user.
    """
    total_amt = Decimal("0")

    for id in ids:

        tkn_name, rewards_token = get_standard_reward_tkn_name(state, id)
        state = snapshot_standard_rewards(state, id, timestamp, user_name)
        reward_amt = get_user_pending_standard_rewards(state, id, user_name)
        state.set_user_pending_standard_rewards(user_name, id, Decimal(0))
        remaining_rewards = get_remaining_standard_rewards(state, id)

        if reward_amt > 0:

            if remaining_rewards < reward_amt:
                raise ValueError("Claimed rewards exceed available rewards")

            updated_remaining_rewards = remaining_rewards - reward_amt

            state.set_standard_remaining_rewards(id, updated_remaining_rewards)

            total_amt += reward_amt

            is_vault_updated = True

    if is_vault_updated:
        state.decrease_standard_rewards_vault_balance(rewards_token, total_amt)

    return state


def distribute_standard_rewards(
    state: State, user_name: str, rewards_token: str, reward_amt: Decimal
) -> State:
    state.decrease_standard_rewards_vault_balance(rewards_token, reward_amt)
    state.increase_user_balance(user_name, rewards_token, reward_amt)
    return state
