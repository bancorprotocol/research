# coding=utf-8
import random
from decimal import Decimal
from typing import Tuple

from bancor_simulator.v3.actions import trade_tkn_to_ema, trade_bnt_to_ema
from bancor_simulator.v3.state import GlobalSettings as Settings, State, get_prices, get_max_bnt_deposit, \
    compute_vault_tvl, compute_max_tkn_deposit, compute_ema, compute_bntkn_rate

settings = Settings()


def randomise_amts(amt: Decimal) -> Decimal:
    if random.randint(0, 1000) != 0:
        max_amt, min_amt = amt * Decimal("0.0001"), amt * Decimal("0.000001")
    else:
        max_amt, min_amt = amt * Decimal("0.01"), amt * Decimal("0.001")
    return Decimal(random.uniform(float(min_amt), float(max_amt)))


def is_protocol_bnbnt_healthy(protocol_bnbnt: Decimal, bnbnt_supply: Decimal) -> bool:
    return protocol_bnbnt / bnbnt_supply > Decimal("0.5")


def random_cooldown_amt(user_bntkn_amt: Decimal) -> Decimal:
    if random.randint(0, 10) != 0:
        max_amt, min_amt = user_bntkn_amt * Decimal("0.1"), user_bntkn_amt * Decimal(
            "0.01"
        )
    else:
        max_amt, min_amt = user_bntkn_amt * Decimal("1"), user_bntkn_amt * Decimal(
            "0.5"
        )
    return Decimal(random.uniform(float(min_amt), float(max_amt)))


def random_trading_fee(trading_fee: Decimal) -> Decimal:
    min_trading_fee, max_trading_fee = max(
        trading_fee / Decimal("3"), Decimal("0.001")
    ), min(trading_fee * Decimal("3"), Decimal("0.05"))
    return Decimal(random.uniform(float(min_trading_fee), float(max_trading_fee)))


def random_network_fee(network_fee: Decimal) -> Decimal:
    min_fee, max_fee = max(network_fee / Decimal("2"), Decimal("0.05")), min(
        network_fee * Decimal("2"), Decimal("0.25")
    )
    return Decimal(random.uniform(float(min_fee), float(max_fee)))


def random_withdrawal_fee(withdrawal_fee: Decimal) -> Decimal:
    min_fee, max_fee = max(withdrawal_fee / Decimal("2"), Decimal("0.001")), min(
        withdrawal_fee * Decimal("2"), Decimal("0.01")
    )
    return Decimal(random.uniform(float(min_fee), float(max_fee)))


def random_bnt_funding_limit(bnt_funding_amt: Decimal) -> Decimal:
    min_bnt_funding_limit = bnt_funding_amt * Decimal("1.5")
    max_bnt_funding_limit = bnt_funding_amt * Decimal("3.0")
    bnt_funding_limit = Decimal(
        random.uniform(float(min_bnt_funding_limit), float(max_bnt_funding_limit))
    )
    return bnt_funding_limit


def random_bnt_trading_liquidity(bnt_trading_liquidity: Decimal) -> Decimal:
    min_amt, max_amt = bnt_trading_liquidity * Decimal(
        "0.4"
    ), bnt_trading_liquidity * Decimal("0.9")
    return Decimal(
        random.uniform(
            float(min_amt),
            float(max_amt),
        )
    )


def random_trades(protocol):
    for i in range(random.randint(1, 10)):
        user_name = random.choice([user for user in protocol.global_state.usernames])
        tokens = [token for token in protocol.global_state.whitelisted_tokens]
        source_tkn = tokens.pop(tokens.index(random.choice(tokens)))
        target_tkn = random.choice(tokens)
        source_liquidity = protocol.global_state.tokens[source_tkn].tkn_trading_liquidity
        user_funds = protocol.global_state.users[user_name].wallet[source_tkn].tkn_amt
        for i in range(random.randint(1, 5)):
            swap_amt = randomise_amts(source_liquidity)
            if user_funds > swap_amt:
                protocol.trade(swap_amt, source_tkn, target_tkn, user_name)
            else:
                protocol.trade(user_funds, source_tkn, target_tkn, user_name)

            if random.randint(0, 2) != 0:
                protocol.step()
    return protocol


def random_deposits(protocol, target_tvl=Decimal("100000000")):
    for i in range(random.randint(1, 10)):
        user_name = random.choice([user for user in protocol.global_state.usernames])
        tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
        user_tkn = protocol.global_state.users[user_name].wallet[tkn_name].tkn_amt
        user_bnt = protocol.global_state.users[user_name].wallet["bnt"].tkn_amt
        bnbnt_supply = protocol.global_state.erc20contracts_bnbnt
        protocol_bnbnt = protocol.global_state.protocol_wallet_bnbnt
        bnbnt_rate = protocol.global_state.bnbnt_rate
        user_funds = protocol.global_state.users[user_name].wallet[tkn_name].tkn_amt
        if tkn_name != "bnt":
            vault_balance = protocol.global_state.tokens[tkn_name].vault_tkn
            state, token_price, bnt_price = get_prices(
                tkn_name, protocol.global_state.price_feeds
            )
            vault_tvl = compute_vault_tvl(vault_balance, token_price)
            if vault_tvl < target_tvl:
                max_tkn_deposit = compute_max_tkn_deposit(vault_tvl, target_tvl, user_tkn)
                deposit_amt = randomise_amts(max_tkn_deposit)
                if deposit_amt < user_funds:
                    protocol.deposit(
                        tkn_name,
                        deposit_amt,
                        user_name,
                        protocol.global_state.unix_timestamp,
                    )

        elif tkn_name == "bnt":
            if bnbnt_supply > 0 and is_protocol_bnbnt_healthy(
                    protocol_bnbnt, bnbnt_supply
            ):
                max_bnt_deposit = get_max_bnt_deposit(
                    bnbnt_supply, protocol_bnbnt, bnbnt_rate, user_bnt
                )
                deposit_amt = randomise_amts(max_bnt_deposit)
                if deposit_amt < user_funds:
                    protocol.deposit(
                        tkn_name,
                        deposit_amt,
                        user_name,
                        protocol.global_state.unix_timestamp,
                    )

        if random.randint(0, 2) != 0:
            protocol.step()
    return protocol


def random_arbitrage_trades(protocol):
    for i in range(random.randint(1, 10)):
        user = random.choice([user for user in protocol.global_state.usernames])
        tokens = [
            token
            for token in protocol.global_state.whitelisted_tokens
            if token != "bnt"
        ]
        tkn_name = random.choice(tokens)
        if protocol.global_state.tokens[tkn_name].is_trading_enabled:
            protocol.arbitrage_trade(tkn_name, user)
            if random.randint(0, 2) != 0:
                protocol.step()
    return protocol


def process_force_moving_average(
        protocol, tkn_name: str, user_tkn: Decimal, user_bnt: Decimal
) -> Tuple[Decimal, str, str, bool]:
    tkn_trading_liquidity = protocol.global_state.tokens[tkn_name].tkn_trading_liquidity
    bnt_trading_liquidity = protocol.global_state.tokens[tkn_name].bnt_trading_liquidity
    trading_fee = protocol.global_state.tokens[tkn_name].trading_fee
    network_fee = protocol.global_state.network_fee
    ema_rate = protocol.global_state.tokens[tkn_name].ema_rate
    spot_rate = protocol.global_state.tokens[tkn_name].spot_rate
    future_ema = compute_ema(spot_rate, ema_rate)
    if ema_rate < spot_rate:
        source_tkn = tkn_name
        target_tkn = "bnt"
        trade_amt = trade_tkn_to_ema(
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            future_ema,
        )
        user_capability = user_tkn > trade_amt
    elif ema_rate > spot_rate:
        source_tkn = "bnt"
        target_tkn = tkn_name
        trade_amt = trade_bnt_to_ema(
            bnt_trading_liquidity,
            tkn_trading_liquidity,
            trading_fee,
            network_fee,
            future_ema,
        )
        user_capability = user_bnt > trade_amt
    else:
        source_tkn = tkn_name
        target_tkn = tkn_name
        trade_amt = Decimal("0")
        user_capability = False
    print("Processed the ema force.")
    return trade_amt, source_tkn, target_tkn, user_capability


def force_moving_average(protocol, tkn_name: str, user_name: str):
    user_tkn = protocol.global_state.users[user_name].wallet[tkn_name].tkn_amt
    user_bnt = protocol.global_state.users[user_name].wallet["bnt"].tkn_amt
    if protocol.global_state.tokens[tkn_name].is_trading_enabled:
        (
            trade_amt,
            source_tkn,
            target_tkn,
            user_capability,
        ) = process_force_moving_average(tkn_name, user_tkn, user_bnt)
        if user_capability:
            protocol.trade(trade_amt, source_tkn, target_tkn, user_name)
        else:
            print("The user has insufficient funds to force the ema.")
            pass
    else:
        print("Trading is disabled")
        pass
    return protocol


def random_ema_force_trades(protocol):
    for i in range(random.randint(1, 10)):
        user_name = random.choice([user for user in protocol.global_state.usernames])
        tokens = [
            token
            for token in protocol.global_state.whitelisted_tokens
            if token != "bnt"
        ]
        tkn_name = random.choice(tokens)
        if protocol.global_state.tokens[tkn_name].is_trading_enabled:
            force_moving_average(tkn_name, user_name)
            if random.randint(0, 2) != 0:
                protocol.global_state.step()
    return protocol


def random_begin_cooldowns(protocol):
    for i in range(random.randint(1, 10)):
        user_name = random.choice([user for user in protocol.global_state.usernames])
        tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
        user_bntkn_amt = (
            protocol.global_state.users[user_name].wallet[tkn_name].bntkn_amt
        )

        if user_bntkn_amt > 0:
            bntkn_amt = random_cooldown_amt(user_bntkn_amt)
            staked_tkn = protocol.global_state.tokens[tkn_name].staked_tkn
            bntkn_supply = protocol.global_state.tokens[tkn_name].erc20contracts_bntkn
            bntkn_rate = compute_bntkn_rate(protocol.global_state, tkn_name)
            withdraw_value = bntkn_amt / bntkn_rate
            protocol.begin_withdrawal_cooldown(
                tkn_name=tkn_name,
                withdraw_value=withdraw_value,
                user_name=user_name,
                unix_timestamp=protocol.global_state.unix_timestamp,
            )
            if random.randint(0, 2) != 0:
                protocol.step()
    return protocol


def random_withdrawals(protocol):
    # for i in range(random.randint(1, 10)):
    user_name = random.choice([user for user in protocol.global_state.usernames])
    tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
    pending_withdrawals = (
        protocol.global_state.users[user_name].wallet[tkn_name].pending_withdrawals
    )
    if len(pending_withdrawals) > 0:
        try:
            id_number = random.choice(
                [id_number for id_number in pending_withdrawals if pending_withdrawals]
            )
            protocol.withdraw(
                user_name=user_name,
                id_number=id_number,
                unix_timestamp=protocol.global_state.unix_timestamp,
            )
            if random.randint(0, 2) != 0:
                protocol.step()
        except:
            pass
    return protocol


def random_change_trading_fee(protocol):
    for i in range(random.randint(1, 3)):
        tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
        trading_fee = protocol.global_state.tokens[tkn_name].trading_fee
        trading_fee = random_trading_fee(trading_fee)
        protocol.global_state.tokens[tkn_name].trading_fee = trading_fee
        if random.randint(0, 2) != 0:
            protocol.step()
    return protocol


def random_change_network_fee(protocol):
    network_fee = protocol.global_state.network_fee
    network_fee = random_network_fee(network_fee)
    protocol.global_state.network_fee = network_fee
    if random.randint(0, 2) != 0:
        protocol.step()
    return protocol


def random_change_withdrawal_fee(protocol):
    withdrawal_fee = protocol.global_state.withdrawal_fee
    withdrawal_fee = random_withdrawal_fee(withdrawal_fee)
    protocol.global_state.withdrawal_fee = withdrawal_fee
    if random.randint(0, 2) != 0:
        protocol.step()
    return protocol


def random_change_bnt_funding_limit(protocol):
    tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
    bnt_funding_limit = protocol.global_state.tokens[tkn_name].bnt_funding_limit
    updated_bnt_funding_limit = random_bnt_funding_limit(bnt_funding_limit)
    protocol.global_state.tokens[tkn_name].bnt_funding_limit = updated_bnt_funding_limit
    if random.randint(0, 2) != 0:
        protocol.step()
    return protocol


def reduce_trading_liquidity(protocol, tkn_name, updated_bnt_trading_liquidity):
    """
    _takes token_name, updated_bnt_trading_liquidity as inputs.
    _updates the state of the appropriate pool, and the v3 holdings, as required.
    _this function returns nothing.
    """
    bnt_trading_liquidity = protocol.global_state.tokens[tkn_name].bnt_trading_liquidity
    tkn_trading_liquidity = protocol.global_state.tokens[tkn_name].tkn_trading_liquidity
    ema_rate = protocol.global_state.tokens[tkn_name].ema_rate
    spot_rate = protocol.global_state.tokens[tkn_name].spot_rate
    bnt_renounced = bnt_trading_liquidity - updated_bnt_trading_liquidity

    staked_bnt = protocol.global_state.staked_bnt
    bnbnt_supply = protocol.global_state.erc20contracts_bnbnt
    bnbnt_rate = protocol.global_state.get_bnbnt_rate(tkn_name)
    bnbnt_renounced = bnbnt_rate * bnt_renounced
    updated_tkn_trading_liquidity = max(
        tkn_trading_liquidity - bnt_renounced / ema_rate, 0
    )
    if protocol.global_state.is_price_stable(tkn_name):
        protocol.global_state.tokens[tkn_name].bnt_trading_liquidity -= bnt_renounced
        protocol.global_state.staked_bnt -= bnt_renounced
        protocol.global_state.vault_bnt -= bnt_renounced
        protocol.global_state.erc20contracts_bnbnt -= bnbnt_renounced
        protocol.global_state.protocol_wallet_bnbnt -= bnbnt_renounced
        protocol.global_state.tokens[
            tkn_name
        ].bnt_funding_limit = updated_bnt_trading_liquidity
        protocol.global_state.tokens[
            tkn_name
        ].bnt_funding_amt = updated_bnt_trading_liquidity
        protocol.global_state.tokens[
            tkn_name
        ].tkn_trading_liquidity = updated_tkn_trading_liquidity
        protocol.global_state.check_pool_shutdown(tkn_name)
    return protocol


def random_reduce_trading_liquidity(protocol):
    tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
    bnt_trading_liquidity = protocol.global_state.tokens[tkn_name].bnt_trading_liquidity
    if bnt_trading_liquidity > 0:
        updated_bnt_trading_liquidity = random_bnt_trading_liquidity(
            bnt_trading_liquidity
        )
        protocol = reduce_trading_liquidity(
            protocol, tkn_name, updated_bnt_trading_liquidity
        )
        if random.randint(0, 2) != 0:
            protocol.step()
    return protocol


def random_burn(protocol):
    user_name = random.choice([user for user in protocol.global_state.usernames])
    protocol.burn(tkn_name="tkn", user_name=user_name)
    if random.randint(0, 2) != 0:
        protocol.step()
    return protocol


def random_leave(protocol):
    user_name = random.choice([user for user in protocol.global_state.usernames])
    tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
    user_tkn = int(protocol.global_state.users[user_name].wallet[tkn_name].tkn_amt)
    tkn_amt = random.randint(0, user_tkn)
    protocol.leave(
        tkn_name=tkn_name,
        tkn_amt=tkn_amt,
        user_name=user_name,
        unix_timestamp=protocol.global_state.unix_timestamp,
    )

    if random.randint(0, 2) != 0:
        protocol.step()
    return protocol


def random_join(protocol):
    user_name = random.choice([user for user in protocol.global_state.usernames])
    tkn_name = random.choice(protocol.global_state.whitelisted_tokens)
    user_tkn = int(protocol.global_state.users[user_name].wallet[tkn_name].tkn_amt)
    tkn_amt = random.randint(0, user_tkn)
    protocol.join(
        tkn_name=tkn_name,
        tkn_amt=tkn_amt,
        user_name=user_name,
        unix_timestamp=protocol.global_state.unix_timestamp,
    )

    if random.randint(0, 2) != 0:
        protocol.step()
    return protocol


def generate_user_actions(protocol):
    i = random.randint(0, 1721)
    if i < 400:
        protocol = random_trades(protocol)
    elif 400 < i < 1400:
        protocol = random_deposits(protocol)
    elif 1400 < i < 1500:
        protocol = random_begin_cooldowns(protocol)
    elif 1500 < i < 1700:
        protocol = random_withdrawals(protocol)
    # elif 1700 < i < 1710:
    #     v3 = random_join(v3)
    # elif 1710 < i < 1720:
    #     v3 = random_leave(v3)
    # elif 1720 < i < 1721:
    #     v3 = random_burn(v3)

    return protocol


def tkn_airdrop(protocol, user_name):
    protocol.global_state.users[user_name].wallet["tkn"].tkn_amt = Decimal(1000000)
    return protocol


def bnt_airdrop(protocol, user_name):
    protocol.global_state.users[user_name].wallet["bnt"].tkn_amt = Decimal(1000000)
    return protocol


def run(protocol, iter_limit=None):
    for user_name in protocol.global_state.usernames:
        protocol = tkn_airdrop(protocol, user_name)
        protocol = bnt_airdrop(protocol, user_name)

    i = random.randint(0, 15)
    ct = 0
    if iter_limit is not None:
        while protocol.global_state.unix_timestamp <= iter_limit:
            protocol = generate_user_actions(protocol)
            ct += 1
            if ct == i:
                protocol.dao_msig_init_pools(protocol.global_state.whitelisted_tokens)
    else:
        while (
                protocol.global_state.unix_timestamp
                <= protocol.global_state.price_feeds.shape[0]
        ):
            protocol = generate_user_actions(protocol)
            ct += 1
            if ct == i:
                protocol.dao_msig_init_pools(protocol.global_state.whitelisted_tokens)
    return protocol.json_export


def setup_json_simulation(state: State, json_data: dict, tkn_name: str) -> State:
    """This method uploads a pre-formatted JSON file containing simulation modules to run and report on."""

    trading_fee = Decimal(json_data["tradingFee"].replace("%", "")) * Decimal(".01")

    if "tknRewardsamt" in json_data:
        try:
            state.standard_reward_programs[
                tkn_name
            ].total_rewards = Decimal(json_data["tknRewardsamt"])
            state.standard_reward_programs[tkn_name].end_time = int(
                json_data["tknRewardsDuration"]
            )
            state.standard_reward_programs[
                "bnt"
            ].total_rewards = Decimal(json_data["bntRewardsamt"])
            state.standard_reward_programs["bnt"].end_time = int(
                json_data["bntRewardsDuration"]
            )
        except:
            pass

    # set params
    state.network_fee = Decimal(
        json_data["networkFee"].replace("%", "")
    ) * Decimal(".01")

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
        state.tokens[
            tkn_name
        ].bnt_min_liquidity = state.bnt_min_liquidity
        state.tokens[
            tkn_name
        ].bnt_funding_limit = state.bnt_funding_limit

    for user in json_data["users"]:
        user_name = user["id"]
        state.create_user(user_name)
        tknBalance = Decimal(user["tknBalance"])
        bntBalance = Decimal(user["bntBalance"])
        state.users[user_name].wallet[tkn_name].tkn_amt = tknBalance
        state.users[user_name].wallet["bnt"].tkn_amt = bntBalance

    # set data to iterate
    state.json_data = json_data
    return state

