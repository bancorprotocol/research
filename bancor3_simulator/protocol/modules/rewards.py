# coding=utf-8
from decimal import Decimal
from typing import List, Tuple

from bancor3_simulator.core.dataclasses import ProgramState, State, UserState


def get_program(state: State, program_id: str) -> ProgramState:
    """Pre-parses the dataclass for convenience and clarity"""
    return state.programs[program_id]


def get_provider(state: State, provider_id: str) -> UserState:
    """Pre-parses the dataclass for convenience and clarity"""
    return state.users[provider_id]


def get_program_and_provider_state(state: State, program_id: str, provider_id: str) -> Tuple[ProgramState, UserState]:
    """Gets pre-parsed dataclasses for convenience and clarity"""
    program = get_program(state, program_id)
    provider = get_provider(state, provider_id)
    return program, provider


def set_program(state: State, program: ProgramState, program_id: str) -> State:
    state.programs[program_id] = program
    return state


def set_provider(state: State,
                 provider_id: str,
                 provider: UserState) -> State:
    state.users[provider_id] = provider
    return state


def set_program_and_provider_state(state: State,
                                   program_id: str,
                                   provider_id: str,
                                   provider: UserState,
                                   program: ProgramState) -> State:
    """Updates the state with the new program state and provider state."""
    state = set_provider(state, provider_id, provider)
    state = set_program(state, program, program_id)
    return state


def total_rewards(state: State, program_id: str) -> Decimal:
    """Sums the bntkn_amt per program across all providers"""
    return sum(
        [state.users[user_name].wallet[program_id].bntkn_amt for user_name in state.programs[program_id].providers])


def create_program(state: State,
                   reserve_token: str,
                   pool_token: str,
                   rewards_tkn: str,
                   total_rewards: Decimal,
                   start_time: int,
                   end_time: int,
                   curr_time: int) -> State:
    """Creates a new rewards program."""
    assert curr_time <= start_time < end_time

    if rewards_tkn not in state.programs:
        state.programs[rewards_tkn] = ProgramState(reserve_token=reserve_token,
                                                   pool_token=pool_token,
                                                   rewards_tkn=rewards_tkn,
                                                   start_time=start_time,
                                                   end_time=end_time,
                                                   total_rewards=total_rewards)
    return state


def join_program(state: State,
                 provider_id: str,
                 program_id: str,
                 curr_time: int) -> State:
    """Adds a user/provider to a rewards program."""

    if provider_id not in state.programs[program_id].providers:
        state.programs[program_id].providers.append(provider_id)

    take_rewards_snapshot(state, program_id, provider_id, curr_time)
    return state


def leave_program(state: State,
                  provider_id: str,
                  program_id: str,
                  curr_time: int) -> State:
    """Removes a user/provider from a rewards program."""

    take_rewards_snapshot(state, program_id, provider_id, curr_time)

    state.programs[program_id].providers.remove(provider_id)
    return state


def claim_rewards(state: State,
                  provider_id: str,
                  program_id: str,
                  curr_time: int) -> State:
    """Sends rewards to the user/provider wallet from a rewards program."""

    take_rewards_snapshot(program_id, provider_id, curr_time)
    program, provider = get_program_and_provider_state(state, program_id, provider_id)

    pending_rewards = provider.wallet[program_id].pending_rewards
    program.remaining_rewards -= pending_rewards

    if program.rewards_tkn == 'bnt':
        provider.wallet['bnt'].tkn_amt += pending_rewards
    else:
        program.rewards_vault_tkn -= pending_rewards
        provider.wallet[program_id].tkn_amt += pending_rewards

    provider.wallet[program_id].pending_rewards = Decimal(0)
    state = set_program_and_provider_state(state, program_id, provider_id, provider, program)
    return state


def get_pending_rewards(state: State,
                    provider_id: str,
                    program_id: str,
                    curr_time: int):
    """Returns the current amount of pending rewards entitled to the user/provider wallet."""

    return calc_pending_rewards(calc_rewards_per_tkn(program_id, curr_time), program_id, provider_id)


def take_rewards_snapshot(state: State,
                          provider_id: str,
                          program_id: str,
                          curr_time: int):

    program, provider = get_program_and_provider_state(state, program_id, provider_id)

    rewards_per_tkn = calc_rewards_per_tkn(program_id, curr_time)
    program.rewards_per_tkn = rewards_per_tkn
    program.last_update_time = max(program.last_update_time, min(program.end_time, curr_time))

    new_pending_rewards = calc_pending_rewards(rewards_per_tkn, program_id, provider_id)
    if new_pending_rewards != 0:
        provider.wallet[program_id].pending_rewards = new_pending_rewards

    provider.wallet[program_id].rewards_per_tkn_paid = rewards_per_tkn
    state = set_program_and_provider_state(state, program_id, provider_id, provider, program)
    return state


def calc_rewards_per_tkn(state: State, provider_id: str, program_id: str, curr_time: int) -> int or Decimal:

    program, provider = get_program_and_provider_state(state, program_id, provider_id)

    start_time = program.start_time
    end_time = program.end_time
    last_update_time = program.last_update_time

    staking_start_time = max(start_time, last_update_time)
    staking_end_time = min(end_time, curr_time)

    n = program.remaining_rewards * (staking_end_time - staking_start_time)
    d = program.staked_tkn * (end_time - start_time)

    return program.rewards_per_tkn + (n / d if d != 0 else 0)


def calc_pending_rewards(rewards_per_tkn: int or Decimal, program_id: str, program: ProgramState, provider: UserState):

    return provider.wallet[program_id].pending_rewards + provider.wallet[program_id].staked_amt * (rewards_per_tkn - provider.wallet[program_id].rewards_per_tkn_paid)
