# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Utility functions."""
from bancor_research.bancor_simulator.v3.spec.state import *
import json, pickle, cloudpickle


protocol_user = "protocol"


def check_if_program_enabled(start_time: int, end_time: int, timestamp: int):
    """
    Checks if the given rewards program is enabled.
    """
    return start_time <= timestamp <= end_time


def check_pool_shutdown(state: State, tkn_name: str) -> bool:
    """
    Checks that the bnt_min_trading_liquidity threshold has not been breached.
    """
    trading_enabled = get_is_trading_enabled(state, tkn_name)
    bnt_min_liquidity = get_bnt_min_liquidity(state, tkn_name)
    bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
    if bnt_trading_liquidity < bnt_min_liquidity and trading_enabled:
        return True
    return False


def check_is_bootstrap_reqs_met(
    state: State, tkn_name: str, bootstrap_liquidity: Decimal
) -> bool:
    """
    CHecks if the bootstrap requirements are met for a given tkn_name.
    """
    vault_balance = get_vault_balance(state, tkn_name)
    return vault_balance >= bootstrap_liquidity


def compute_user_total_holdings(state: State, user_name: str):
    """
    Returns the total number of holdings in this state.
    """
    holdings = []
    for tkn_name in state.users[user_name].wallet:
        amt = state.users[user_name].wallet[tkn_name].balance
        if len(tkn_name.replace("bn", "")) > 2:
            bntkn_rate = compute_bntkn_rate(state, tkn_name.replace("bn", ""))
            amt = amt / bntkn_rate
        holdings.append(amt)
    return sum(holdings)


def compute_rtkn_amt(state: State, tkn_name: str, ptkn_amt: Decimal) -> Decimal:
    """
    Returns the reserve token amount for a given pool token amount.
    """
    staked_balance = get_staked_balance(state, tkn_name)
    pool_token_supply = get_pooltoken_balance(state, tkn_name)
    return ptkn_amt * staked_balance / pool_token_supply


def compute_ptkn_amt(state: State, tkn_name: str, rtkn_amt: Decimal) -> Decimal:
    """
    Returns the pool token amount for a given reserve token amount.
    """
    staked_balance = get_staked_balance(state, tkn_name)
    pool_token_supply = get_pooltoken_balance(state, tkn_name)
    return rtkn_amt * pool_token_supply / staked_balance


def compute_bntkn_rate(state: State, tkn_name: str):
    """
    Computes the bntkn issuance rate for tkn deposits, based on the staking ledger and the current bntkn supply
    """
    pool_token_supply = get_pooltoken_balance(state, tkn_name)
    staked_balance = get_staked_balance(state, tkn_name)
    if pool_token_supply != staked_balance:
        return pool_token_supply / staked_balance
    return Decimal("1")


def compute_bntkn_amt(state: State, tkn_name: str, tkn_amt: Decimal) -> Decimal:
    """
    Returns the bntkn_amt for a given tkn_name, tkn_amt.
    """
    return compute_bntkn_rate(state, tkn_name) * tkn_amt


def compute_bnbnt_amt(state: State, bnt_amt: Decimal) -> Decimal:
    """
    Returns the bnbnt for a given bnt amt.
    """
    return state.bnbnt_rate * bnt_amt


def compute_changed_bnt_trading_liquidity(
    a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return a * (b + d * x * (1 - e)) / (b + x)
    elif direction == "bnt":
        return (a * (a + x) + d * (1 - e) * (a * x + x**2)) / (a + d * x)


def compute_changed_tkn_trading_liquidity(
    a: Decimal, b: Decimal, d: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return b + x
    elif direction == "bnt":
        return b * (a + d * x) / (a + x)


def compute_target_amt(
    a: Decimal, b: Decimal, d: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return a * x * (1 - d) / (b + x)
    elif direction == "bnt":
        return b * x * (1 - d) / (a + x)


def compute_bootstrap_rate(state: State, tkn_name: str) -> Decimal:
    """
    Computes the bootstrap rate as bnt / tkn virtual balances.
    """
    return get_bnt_virtual_balance(state) / get_tkn_virtual_balance(state, tkn_name)


def compute_vault_tkn_tvl(vault_balance: Decimal, token_price: Decimal) -> Decimal:
    """
    Computes the vault tvl for a given tkn.
    """
    return vault_balance * token_price


def compute_max_tkn_deposit(
    vault_tvl: Decimal, target_tvl: Decimal, user_funds: Decimal
) -> Decimal:
    """
    Computes the maximum deposit amount which will not exceed the target tvl.
    """
    return max(target_tvl - vault_tvl, user_funds)


def format_json(val: Any, integer: bool = False, percentage: bool = False) -> Any:
    """
    Formats data when generating JSON test scenarios.
    """
    if integer:
        return str(val).replace("0E-18", "0", 10)
    elif percentage:
        return str(round(float(str(val)))).replace("0E-18", "0") + "%"
    else:
        if type(val) == dict:
            return val
        else:
            return str(val).replace("0E-18", "0")


def enable_trading(state: State, tkn_name: str) -> State:
    """
    Enables trading if the minimum bnt equivalent of tkn exists to justify bootstrapping.
    """

    bootstrap_liquidity = get_tkn_bootstrap_liquidity(state, tkn_name)

    if check_is_bootstrap_reqs_met(state, tkn_name, bootstrap_liquidity):
        log = f"Bootstrap requirements met for {tkn_name}"
        print(log)
        state.logger.info(log)

        state.set_is_trading_enabled(tkn_name, True)

        bootstrap_rate = compute_bootstrap_rate(state, tkn_name)
        state.set_initial_rates(tkn_name, bootstrap_rate)

        bnt_bootstrap_liquidity = get_bnt_bootstrap_liquidity(state, tkn_name)
        state.set_bnt_trading_liquidity(tkn_name, bnt_bootstrap_liquidity)
        state.set_bnt_funding_amt(tkn_name, bnt_bootstrap_liquidity)

        tkn_bootstrap_liquidity = get_tkn_bootstrap_liquidity(state, tkn_name)
        state.set_tkn_trading_liquidity(tkn_name, tkn_bootstrap_liquidity)

        state = mint_protocol_bnt(state, bnt_bootstrap_liquidity)
    else:
        log = f"Bootstrap requirements *not* met for {tkn_name}"
        print(log)
        state.logger.info(log)

    return state


def mint_protocol_bnt(state: State, tkn_amt: Decimal) -> State:
    """
    Handles adjustments to the system resulting from the v3 minting BNT.
    """
    bnbnt_amt = compute_bnbnt_amt(state, tkn_amt)
    state.increase_vault_balance("bnt", tkn_amt)
    state.increase_pooltoken_balance("bnt", bnbnt_amt)
    state.increase_staked_balance("bnt", tkn_amt)
    state.increase_protocol_wallet_balance("bnt", bnbnt_amt)
    return state


def shutdown_pool(state: State, tkn_name: str) -> State:
    """
    Shutdown pool when the bnt_min_trading_liquidity threshold is breached.
    """

    bnt_trading_liquidity = state.tokens[tkn_name].bnt_trading_liquidity.balance
    bnbnt_renounced = compute_bnbnt_amt(state, bnt_trading_liquidity)

    # adjust balances
    state.decrease_staked_balance("bnt", bnt_trading_liquidity)
    state.decrease_vault_balance("bnt", bnt_trading_liquidity)
    state.decrease_pooltoken_balance("bnt", bnbnt_renounced)
    state.decrease_protocol_wallet_balance("bnt", bnbnt_renounced)
    state.decrease_bnt_funding_amt(tkn_name, bnt_trading_liquidity)

    # set balances
    state.set_is_trading_enabled(tkn_name, False)
    state.set_bnt_trading_liquidity(tkn_name, Decimal("0"))
    state.set_tkn_trading_liquidity(tkn_name, Decimal("0"))
    state.set_spot_rate(tkn_name, Decimal("0"))
    state.set_ema_rate(tkn_name, Decimal("0"))
    state.set_inv_spot_rate(tkn_name, Decimal("0"))
    state.set_inv_ema_rate(tkn_name, Decimal("0"))
    return state


def compute_pool_depth_adjustment(
    state: State, tkn_name: str, case: str = "none"
) -> Tuple[str, Decimal, Decimal]:
    """
    Computes the quantities of bnt and tkn to add to the pool trading liquidity during a deposit.
    """
    bnt_increase = tkn_increase = Decimal("0")
    is_trading_enabled = get_is_trading_enabled(state, tkn_name)
    is_price_stable = get_is_price_stable(state, tkn_name)
    bnt_remaining_funding = get_bnt_remaining_funding(state, tkn_name)
    if is_trading_enabled and is_price_stable and bnt_remaining_funding > 0:
        tkn_excess = get_tkn_excess(state, tkn_name)
        tkn_excess_bnt_equivalence = get_tkn_excess_bnt_equivalence(state, tkn_name)
        speculated_ema_rate = get_updated_ema_rate(state, tkn_name) # a mistake in the contract implementation
        bnt_trading_liquidity = get_bnt_trading_liquidity(state, tkn_name)
        avg_tkn_trading_liquidity = bnt_trading_liquidity / speculated_ema_rate

        if (
            avg_tkn_trading_liquidity <= tkn_excess
            and bnt_trading_liquidity <= bnt_remaining_funding
        ):
            case = "case1"
            bnt_increase = bnt_trading_liquidity
            tkn_increase = avg_tkn_trading_liquidity

        elif (
            avg_tkn_trading_liquidity <= tkn_excess
            and bnt_trading_liquidity > bnt_remaining_funding
            or avg_tkn_trading_liquidity > tkn_excess
            and tkn_excess_bnt_equivalence >= bnt_remaining_funding
        ):
            case = "case2"
            bnt_increase = bnt_remaining_funding
            tkn_increase = bnt_remaining_funding / speculated_ema_rate

        elif (
            tkn_excess < avg_tkn_trading_liquidity
            and bnt_trading_liquidity <= bnt_remaining_funding
            or avg_tkn_trading_liquidity > tkn_excess
            and bnt_trading_liquidity
            > bnt_remaining_funding
            > tkn_excess_bnt_equivalence
        ):
            case = "case3"
            bnt_increase = tkn_excess_bnt_equivalence
            tkn_increase = tkn_excess

        else:
            raise ValueError("Something went wrong, pool adjustment case not found...")

    return case, bnt_increase, tkn_increase


def vortex_collection(
    a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the changed state values according to the swap algorithm.
    """
    if direction == "tkn":
        return a * d * e * x / (b + x)
    elif direction == "bnt":
        return d * e * x * (a + x) / (a + d * x)


def swap_fee_collection(
    a: Decimal, b: Decimal, d: Decimal, e: Decimal, x: Decimal, direction: str
) -> Decimal:
    """
    Computes the swap fees according to the swap algorithm.
    """
    if direction == "tkn":
        return a * d * x * (1 - e) / (b + x)
    elif direction == "bnt":
        return b * d * x * (1 - e) / (a + x)


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


def init_protocol(
    state: State,
    whitelisted_tokens: dict,
    usernames: List[str],
    cooldown_time: int,
    network_fee: Decimal,
    bnt_min_liquidity: Decimal,
    withdrawal_fee: Decimal,
) -> State:
    """
    Initialize user wallets upon system genesis.
    """

    for tkn_name in whitelisted_tokens:
        if tkn_name not in state.whitelisted_tokens:
            state.create_whitelisted_tkn(tkn_name)

    for tkn_name in whitelisted_tokens:

        # Get tokens not yet initialized.
        if tkn_name not in state.tokens:

            decimals = whitelisted_tokens[tkn_name]["decimals"]
            trading_fee = whitelisted_tokens[tkn_name]["trading_fee"]
            bnt_funding_limit = whitelisted_tokens[tkn_name]["bnt_funding_limit"]
            ep_vault_balance = whitelisted_tokens[tkn_name]["ep_vault_balance"]

            # initialize tokens
            state.tokens[tkn_name] = Tokens(
                tkn_name=tkn_name,
                decimals=decimals,
                trading_fee=trading_fee,
                bnt_min_liquidity=bnt_min_liquidity,
                network_fee=network_fee,
                bnt_funding_limit=bnt_funding_limit,
                withdrawal_fee=withdrawal_fee,
                cooldown_time=cooldown_time,
                external_protection_vault=Token(balance=ep_vault_balance),
            )

            # initialize pooltoken
            pooltkn_name = get_pooltoken_name(tkn_name)
            state.tokens[pooltkn_name] = Tokens(
                tkn_name=pooltkn_name,
                trading_fee=trading_fee,
                bnt_min_liquidity=bnt_min_liquidity,
                network_fee=network_fee,
                bnt_funding_limit=bnt_funding_limit,
                withdrawal_fee=withdrawal_fee,
                cooldown_time=cooldown_time,
            )

    for tkn_name in ["bnt", "bnbnt", "vbnt"]:

        state.tokens[tkn_name] = Tokens(
            tkn_name=tkn_name,
            network_fee=network_fee,
            withdrawal_fee=withdrawal_fee,
            cooldown_time=cooldown_time,
        )

    for usr in usernames:

        # Get users not yet initialized.
        if usr not in state.usernames:
            # initialize users.
            state.create_user(usr)

    state.whitelisted_tokens = whitelisted_tokens
    state.active_users = usernames
    return state


def handle_logging(
    tkn_name: str,
    tkn_amt: Decimal,
    action_name: str,
    user_name: str,
    transaction_id: int,
    state: State,
) -> State:
    """
    Logs the system state history after each action.
    """
    state.iter_transaction_id = transaction_id
    for tkn_name in state.whitelisted_tokens:
        state_variables = {
            "timestamp": [state.timestamp],
            "latest_action": [action_name],
            "latest_amt": [tkn_amt],
            "latest_user_name": [user_name],
            "tkn_name": [tkn_name],
            "vault_tkn": [get_vault_balance(state, tkn_name)],
            "erc20contracts_bntkn": [get_pooltoken_balance(state, tkn_name)],
            "staked_tkn": [get_staked_balance(state, tkn_name)],
            "is_trading_enabled": [get_is_trading_enabled(state, tkn_name)],
            "bnt_trading_liquidity": [get_bnt_trading_liquidity(state, tkn_name)],
            "tkn_trading_liquidity": [get_tkn_trading_liquidity(state, tkn_name)],
            "trading_fee": [get_trading_fee(state, tkn_name)],
            "bnt_funding_limit": [get_bnt_funding_limit(state, tkn_name)],
            "bnt_remaining_funding": [get_bnt_remaining_funding(state, tkn_name)],
            "bnt_funding_amt": [get_bnt_funding_amt(state, tkn_name)],
            "external_protection_vault": [
                get_external_protection_vault(state, tkn_name)
            ],
            "spot_rate": [get_spot_rate(state, tkn_name)],
            "ema_rate": [get_ema_rate(state, tkn_name)],
            "inv_spot_rate": [get_inv_spot_rate(state, tkn_name)],
            "inv_ema_rate": [get_inv_ema_rate(state, tkn_name)],
            "ema_last_updated": [state.tokens[tkn_name].ema_last_updated],
            "network_fee": [state.network_fee],
            "withdrawal_fee": [state.withdrawal_fee],
            "bnt_min_liquidity": [state.bnt_min_liquidity],
            "cooldown_time": [state.cooldown_time],
            "protocol_wallet_bnbnt": [get_protocol_wallet_balance(state, "bnt")],
            "vortex_bnt": [get_vortex_balance(state, "bnt")],
            "erc20contracts_bnbnt": [get_pooltoken_balance(state, "bnt")],
            "vault_bnt": [get_vault_balance(state, "bnt")],
            "staked_bnt": [get_staked_balance(state, "bnt")],
            "bnbnt_rate": [state.bnbnt_rate],
        }
        state.history.append(pd.DataFrame(state_variables))
    return state


def handle_vandalism_attack(state: State, tkn_name):
    """
    Checks if a vandalism attack has occured and adjusts the system state accordingly.
    """
    staked_tkn = get_staked_balance(state, tkn_name)
    bntkn = get_pooltoken_balance(state, tkn_name)
    if staked_tkn > 0 and bntkn == 0:
        state.set_staked_balance(tkn_name, Decimal("0"))
        shutdown_pool(state, tkn_name)
    return state


def handle_ema(state: State, tkn_name: str) -> State:
    """
    Handles the updating of the ema rate and the inverse ema rate, called before a swap is performed.
    """
    if state.tokens[tkn_name].ema_last_updated != state.tokens[tkn_name].timestamp:
        state.tokens[tkn_name].ema_last_updated = state.tokens[tkn_name].timestamp
        state.set_ema_rate(tkn_name, state.tokens[tkn_name].updated_ema_rate)
        state.set_inv_ema_rate(tkn_name, state.tokens[tkn_name].updated_inv_ema_rate)
    return state


def describe_rates(state: State, report={}) -> pd.DataFrame:
    """
    Return a dataframe of the current system EMA & spot rates.
    """
    for tkn in state.whitelisted_tokens:
        report[tkn] = get_rate_report(state, tkn)
    return pd.DataFrame(report).T.reset_index()


def describe(state: State, rates: bool = False, decimals=6) -> pd.DataFrame:
    """
    Builds a dataframe of the current system/ledger state.
    """
    qdecimals = Decimal(10) ** -decimals
    if rates:
        return describe_rates(state, qdecimals=qdecimals)

    description = get_description(state, qdecimals)
    max_rows = max([len(description[key]) for key in description])

    # fill-in the description spacing for display purposes
    for col in description:
        while len(description[col]) < max_rows:
            description[col].append("")

    return pd.DataFrame(description)


def build_json_operation(
    state: State,
    tkn_name: str,
    tkn_amt: Decimal,
    transaction_type: str,
    user_name: str,
    timestamp: int,
) -> dict:
    if "tkn" in state.autocompounding_reward_programs:
        program_wallet_bntkn = get_protocol_wallet_balance(state, tkn_name)
        tkn_remaining_rewards = get_autocompounding_remaining_rewards(state, tkn_name)
    else:
        program_wallet_bntkn = Decimal("0")
        tkn_remaining_rewards = Decimal("0")

    if "bnt" in state.autocompounding_reward_programs:
        bnt_remaining_rewards = get_autocompounding_remaining_rewards(state, "bnt")
    else:
        bnt_remaining_rewards = Decimal("0")

    if "tkn" in state.standard_reward_programs:
        er_vault_tkn = state.tokens[tkn_name].protocol_wallet_pooltokens.balance
    else:
        er_vault_tkn = Decimal("0")

    if "bnt" in state.autocompounding_reward_programs:
        er_vault_bnt = state.tokens["bnt"].protocol_wallet_pooltokens.balance
    else:
        er_vault_bnt = Decimal("0")

    if "User" not in state.users:
        print("User not found, therefore JSON export will not be created.")
        return {}

    json_operation = {
        "type": transaction_type,
        "userId": user_name,
        "elapsed": timestamp,
        "amt": format_json(tkn_amt) if str(tkn_amt) != "NA" else tkn_amt,
        "expected": {
            "tknBalances": {
                "User": format_json(get_user_balance(state, tkn_name, user_name)),
                "masterVault": format_json(get_vault_balance(state, tkn_name)),
                "erVault": format_json(er_vault_tkn),
                "epVault": format_json(get_external_protection_vault(state, tkn_name)),
            },
            "bntBalances": {
                "User": format_json(get_user_balance(state, "bnt", user_name)),
                "masterVault": format_json(get_vault_balance(state, "bnt")),
                "erVault": format_json(er_vault_bnt),
            },
            "bntknBalances": {
                "User": format_json(
                    get_user_balance(state, f"bn{tkn_name}", user_name)
                ),
                "TKNProgramWallet": format_json(program_wallet_bntkn),
            },
            "bnbntBalances": {
                "User": format_json(get_user_balance(state, "bnbnt", user_name)),
                "bntPool": format_json(get_protocol_wallet_balance(state, "bnt")),
            },
            "tknRewardsRemaining": format_json(tkn_remaining_rewards),
            "bntRewardsRemaining": format_json(bnt_remaining_rewards),
            "bntCurrentPoolFunding": format_json(get_bnt_funding_amt(state, tkn_name)),
            "tknStakedBalance": format_json(get_staked_balance(state, tkn_name)),
            "bntStakedBalance": format_json(get_staked_balance(state, "bnt")),
            "tknTradingLiquidity": format_json(
                get_tkn_trading_liquidity(state, tkn_name)
            ),
            "bntTradingLiquidity": format_json(
                get_bnt_trading_liquidity(state, tkn_name)
            ),
            "averageRateN": format_json(
                state.tokens[tkn_name].ema.numerator, integer=True
            ),
            "averageRateD": format_json(
                state.tokens[tkn_name].ema.denominator, integer=True
            ),
            "averageInvRateN": format_json(
                state.tokens[tkn_name].inv_ema.numerator, integer=True
            ),
            "averageInvRateD": format_json(
                state.tokens[tkn_name].inv_ema.denominator, integer=True
            ),
        },
    }
    return json_operation


def log_json_operation(state, transaction_type, user_name, amt, timestamp):
    """Logs the latest operation for json testing."""

    tkn_name = [tkn for tkn in state.whitelisted_tokens if tkn != "bnt"][0]
    json_operation = build_json_operation(
        state, tkn_name, amt, transaction_type, user_name, timestamp
    )

    if transaction_type == "createAutocompoundingRewardProgramTKN":
        json_operation["amt"] = {}
        json_operation["amt"]["tknRewardsTotalamt"] = format_json(
            state.autocompounding_reward_programs["tkn"].total_rewards
        )
        json_operation["amt"]["tknRewardsStartTime"] = format_json(
            state.autocompounding_reward_programs["tkn"].start_time, integer=True
        )
        json_operation["amt"]["tknRewardsType"] = str(
            state.autocompounding_reward_programs["tkn"].distribution_type
        )
        json_operation["amt"]["tknHalfLifeInDays"] = format_json(
            state.autocompounding_reward_programs["tkn"].half_life_days, integer=True
        )

    if transaction_type == "createAutocompoundingRewardProgramBNT":
        state.json_export["bntRewardsTotalamt"] = format_json(
            state.autocompounding_reward_programs["bnt"].total_rewards
        )
        state.json_export["bntRewardsStartTime"] = format_json(
            state.autocompounding_reward_programs["bnt"].start_time, integer=True
        )
        state.json_export["bntRewardsType"] = str(
            state.autocompounding_reward_programs["bnt"].distribution_type
        )
        state.json_export["bntHalfLifeInDays"] = format_json(
            state.autocompounding_reward_programs["bnt"].half_life_days, integer=True
        )

    return json_operation


def validate_input(
    state: State, tkn_name: str, user_name: str, timestamp: int
) -> Tuple[State, str, str]:
    """
    Validates the input for all agent actions.
    """

    assert type(tkn_name) is str, "tkn_name must be of type string"
    assert type(user_name) is str, "tkn_name must be of type string"
    assert user_name != protocol_user, "user_name {} is reserved".format(protocol_user)

    tkn_name = tkn_name.lower()
    user_name = user_name if user_name else protocol_user

    if user_name not in state.users:
        state = state.create_user(user_name)

    if tkn_name not in state.users[user_name].wallet:
        state.users[user_name].wallet[tkn_name] = Token(balance=DEFAULT_ACCOUNT_BALANCE)

    pooltkn_name = get_pooltoken_name(tkn_name)
    if pooltkn_name not in state.users[user_name].wallet:
        state.users[user_name].wallet[pooltkn_name] = Token(
            balance=DEFAULT_ACCOUNT_BALANCE
        )

    if "vbnt" not in state.users[user_name].wallet:
        state.users[user_name].wallet["vbnt"] = Token(balance=DEFAULT_ACCOUNT_BALANCE)

    if "bnbnt" not in state.users[user_name].wallet:
        state.users[user_name].wallet["bnbnt"] = Token(balance=DEFAULT_ACCOUNT_BALANCE)

    state.tokens[tkn_name].timestamp = timestamp

    return state, tkn_name, user_name


def setup_json_simulation(
    state: State, json_data: dict, tkn_name: str, id_number: int
) -> State:
    """This method uploads a pre-formatted JSON file containing simulation modules to run and report on."""

    trading_fee = Decimal(json_data["tradingFee"].replace("%", "")) * Decimal(".01")

    if "tknRewardsamt" in json_data:
        try:
            state.standard_reward_programs[id_number].total_rewards = Decimal(
                json_data["tknRewardsamt"]
            )
            state.standard_reward_programs[id_number].end_time = int(
                json_data["tknRewardsDuration"]
            )
            state.standard_reward_programs["bnt"].total_rewards = Decimal(
                json_data["bntRewardsamt"]
            )
            state.standard_reward_programs["bnt"].end_time = int(
                json_data["bntRewardsDuration"]
            )
        except:
            pass

    # set params
    state.network_fee = Decimal(json_data["networkFee"].replace("%", "")) * Decimal(
        ".01"
    )

    state.withdrawal_fee = Decimal(
        json_data["withdrawalFee"].replace("%", "")
    ) * Decimal(".01")

    state.tokens[tkn_name].external_protection_vault = Decimal(
        json_data["epVaultBalance"]
    )

    state.decimals = Decimal(json_data["tknDecimals"])
    state.bnt_min_liquidity = Decimal(json_data["bntMinLiquidity"])
    state.bnt_funding_limit = Decimal(json_data["bntFundingLimit"])
    state.trading_fee = trading_fee

    for tkn_name in ["bnt", tkn_name]:
        state.tokens[tkn_name].trading_fee = trading_fee
        state.tokens[tkn_name].bnt_min_liquidity = state.bnt_min_liquidity
        state.tokens[tkn_name].bnt_funding_limit = state.bnt_funding_limit

    for user in json_data["users"]:
        user_name = user["id"]
        state.create_user(user_name)
        tknBalance = Decimal(user["tknBalance"])
        bntBalance = Decimal(user["bntBalance"])
        state.set_user_balance(user_name, "bnt", bntBalance)
        state.set_user_balance(user_name, "tkn", tknBalance)

    # set data to iterate
    state.json_data = json_data
    return state


def generate_emulator_expected_results(
    state: State,
    tkn_name: str,
    tkn_amt: Decimal,
    transaction_type: str,
    user_name: str,
    timestamp: int,
) -> dict:
    """
    Get the expected results for a given transaction.
    """
    json_operation = build_json_operation(
        state, tkn_name, tkn_amt, transaction_type, user_name, timestamp
    )
    return json_operation["expected"]


def load_json(path, **kwargs):
    """
    Loads json files for convenient simulation.
    """
    with open(path, "r") as f:
        return json.load(f, **kwargs)


def save_json(x, path, indent=True, **kwargs):
    """
    Saves json for convenience.
    """
    with open(path, "w") as f:
        if indent:
            json.dump(x, f, indent="\t", **kwargs)
        else:
            json.dump(x, f, **kwargs)
    print("Saved to", path)


def load_pickle(path):
    """
    Loads a pickled state from a file path.
    """
    print("Unpickling from", path)
    with open(path, "rb") as f:
        return pickle.load(f)


def save_pickle(x, path):
    """
    Saves a serialized state at file path.
    """
    print("Pickling to", path)
    with open(path, "wb") as f:
        return pickle.dump(x, f)


def load(file_path):
    """
    Loads saved file via cloudpickle.
    """
    with open(file_path, "rb") as f:
        return cloudpickle.load(f)


def export_test_scenarios(state: State, path: str = "test_scenarios.json"):
    """
    Exports the auto-generated json scenarios file to a given path.
    """
    save_json(state.json_export, path)
