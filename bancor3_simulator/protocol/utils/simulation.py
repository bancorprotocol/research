# coding=utf-8
import random
from decimal import Decimal
from bancor3_simulator.core.settings import GlobalSettings as Settings
from bancor3_simulator.protocol.actions import update_ema, trade_tkn_to_ema, trade_bnt_to_ema

settings = Settings()


class MonteCarlo:
    """Monte Carlo methods are a broad class of computational algorithms that rely on repeated random sampling to
    obtain numerical results, i.e. by running simulations many times in succession in order to calculate those same
    probabilities with machine learning just like actually playing and recording your results in a real casino
    situation: hence the name. Monte Carlo simulations are often the precursor to building machine learning algorithms
    for specific classes of problems."""

    @staticmethod
    def twice_minimum_liquidity(bnt_min_liquidity):
        return 2 * bnt_min_liquidity

    @staticmethod
    def randomise_amounts(amount):
        if random.randint(0, 1000) != 0:
            max_amount = amount * Decimal("0.0001")
            min_amount = amount * Decimal("0.000001")
        else:
            max_amount = amount * Decimal("0.01")
            min_amount = amount * Decimal("0.001")
        random_amount = Decimal(random.uniform(float(min_amount), float(max_amount)))
        return random_amount

    @staticmethod
    def get_master_vault_tvl(master_vault_balance, token_price):
        master_vault_tvl = master_vault_balance * token_price
        return master_vault_tvl

    @staticmethod
    def get_maximum_tkn_deposit(master_vault_tvl, target_tvl, user_funds):
        maximum_tkn_deposit = max(target_tvl - master_vault_tvl, user_funds)
        return maximum_tkn_deposit

    @staticmethod
    def is_protocol_bnbnt_healthy(protocol_bnbnt, bnbnt_supply):
        protocol_bnbnt_healthy = protocol_bnbnt / bnbnt_supply > Decimal("0.5")
        return protocol_bnbnt_healthy

    @staticmethod
    def get_maximum_bnt_deposit(bnbnt_supply, protocol_bnbnt, bnbnt_rate, user_bnt):
        maximum_bnbnt_issued = bnbnt_supply / Decimal("0.5") - protocol_bnbnt
        maximum_bnt_deposit = max(maximum_bnbnt_issued / bnbnt_rate, user_bnt)
        return maximum_bnt_deposit

    @staticmethod
    def random_cooldown_amount(user_bntkn_amount):
        if random.randint(0, 10) != 0:
            max_amount = user_bntkn_amount * Decimal("0.1")
            min_amount = user_bntkn_amount * Decimal("0.01")
        else:
            max_amount = user_bntkn_amount * Decimal("1")
            min_amount = user_bntkn_amount * Decimal("0.5")
        bntkn_amount = Decimal(random.uniform(float(min_amount), float(max_amount)))
        return bntkn_amount

    @staticmethod
    def random_new_trading_fee(trading_fee):
        min_trading_fee = max(trading_fee / Decimal("3"), Decimal("0.001"))
        max_trading_fee = min(trading_fee * Decimal("3"), Decimal("0.05"))
        new_trading_fee = Decimal(
            random.uniform(float(min_trading_fee), float(max_trading_fee))
        )
        return new_trading_fee

    @staticmethod
    def random_new_network_fee(network_fee):
        min_network_fee = max(network_fee / Decimal("2"), Decimal("0.05"))
        max_network_fee = min(network_fee * Decimal("2"), Decimal("0.25"))
        new_network_fee = Decimal(
            random.uniform(float(min_network_fee), float(max_network_fee))
        )
        return new_network_fee

    @staticmethod
    def random_new_withdrawal_fee(withdrawal_fee):
        min_withdrawal_fee = max(withdrawal_fee / Decimal("2"), Decimal("0.001"))
        max_withdrawal_fee = min(withdrawal_fee * Decimal("2"), Decimal("0.01"))
        new_network_fee = Decimal(
            random.uniform(float(min_withdrawal_fee), float(max_withdrawal_fee))
        )
        return new_network_fee

    @staticmethod
    def random_new_bnt_funding_limit(bnt_funding_amount):
        min_bnt_funding_limit = bnt_funding_amount * Decimal("1.5")
        max_bnt_funding_limit = bnt_funding_amount * Decimal("3.0")
        new_bnt_funding_limit = Decimal(
            random.uniform(float(min_bnt_funding_limit), float(max_bnt_funding_limit))
        )
        return new_bnt_funding_limit

    @staticmethod
    def random_new_bnt_trading_liquidity(bnt_trading_liquidity):
        min_new_bnt_trading_liquidity = bnt_trading_liquidity * Decimal("0.4")
        max_new_bnt_trading_liquidity = bnt_trading_liquidity * Decimal("0.9")
        new_new_bnt_trading_liquidity = Decimal(
            random.uniform(
                float(min_new_bnt_trading_liquidity),
                float(max_new_bnt_trading_liquidity),
            )
        )
        return new_new_bnt_trading_liquidity

    @staticmethod
    def random_trades(protocol):

        for i in range(random.randint(1, 10)):
            user_name = random.choice([user for user in protocol.state.usernames])
            tokens = [token for token in protocol.state.whitelisted_tokens]
            source_token = tokens.pop(tokens.index(random.choice(tokens)))
            target_token = random.choice(tokens)
            source_liquidity = protocol.state.transactions[source_token].tkn_trading_liquidity
            user_funds = protocol.state.users[user_name].wallet[source_token].tkn_amt
            for i in range(random.randint(1, 5)):
                swap_amount = MonteCarlo.randomise_amounts(source_liquidity)
                if user_funds > swap_amount:
                    protocol.trade(swap_amount, source_token, target_token, user_name)
                else:
                    protocol.trade(user_funds, source_token, target_token, user_name)

                if random.randint(0, 2) != 0:
                    protocol.step()

    @staticmethod
    def random_deposits(protocol, target_tvl=Decimal("100000000")):

        for i in range(random.randint(1, 10)):
            user_name = random.choice([user for user in protocol.state.usernames])
            token_name = random.choice(settings.whitelisted_tokens)
            user_tkn = protocol.state.users[user_name].wallet[token_name].tkn_amt
            user_bnt = protocol.state.users[user_name].wallet['bnt'].tkn_amt
            bnbnt_supply = protocol.state.erc20contracts_bnbnt
            protocol_bnbnt = protocol.state.protocol_wallet_bnbnt
            staked_bnt = protocol.state.staked_bnt
            bnbnt_rate = protocol.state.bnbnt_rate
            user_funds = protocol.state.users[user_name].wallet[token_name].tkn_amt
            if token_name != "bnt":
                master_vault_balance = protocol.state.transactions[token_name].vault_tkn
                state, token_price, bnt_price = protocol.state.get_prices(token_name, protocol.price_feeds)
                master_vault_tvl = MonteCarlo.get_master_vault_tvl(
                    master_vault_balance, token_price
                )
                if master_vault_tvl < target_tvl:
                    maximum_tkn_deposit = MonteCarlo.get_maximum_tkn_deposit(
                        master_vault_tvl, target_tvl, user_tkn
                    )
                    deposit_amount = MonteCarlo.randomise_amounts(maximum_tkn_deposit)
                    if deposit_amount < user_funds:
                        protocol.deposit_tkn(deposit_amount, token_name, user_name)

            elif token_name == "bnt":
                if bnbnt_supply > 0 and MonteCarlo.is_protocol_bnbnt_healthy(
                        protocol_bnbnt, bnbnt_supply
                ):
                    maximum_bnt_deposit = MonteCarlo.get_maximum_bnt_deposit(
                        bnbnt_supply, protocol_bnbnt, bnbnt_rate, user_bnt
                    )
                    deposit_amount = MonteCarlo.randomise_amounts(maximum_bnt_deposit)
                    if deposit_amount < user_funds:
                        protocol.deposit_bnt(deposit_amount, user_name)

            if random.randint(0, 2) != 0:
                protocol.step()

    @staticmethod
    def random_arbitrage_trades(protocol):

        for i in range(random.randint(1, 10)):
            user = random.choice([user for user in protocol.state.usernames])
            tokens = [token for token in protocol.state.whitelisted_tokens if token != "bnt"]
            token_name = random.choice(tokens)
            if protocol.state.transactions[token_name].trading_enabled:
                protocol.arbitrage_trade(token_name, user)
                if random.randint(0, 2) != 0:
                    protocol.step()

    @staticmethod
    def process_force_moving_average(protocol, token_name, user_tkn, user_bnt):

        tkn_trading_liquidity = protocol.state.transactions[token_name].tkn_trading_liquidity
        bnt_trading_liquidity = protocol.state.transactions[token_name].bnt_trading_liquidity
        trading_fee = protocol.state.transactions[token_name].trading_fee
        network_fee = protocol.state.network_fee
        ema_rate = protocol.state.transactions[token_name].ema_rate
        spot_rate = protocol.state.transactions[token_name].spot_rate
        future_ema = update_ema(spot_rate, ema_rate)
        if ema_rate < spot_rate:
            source_token = token_name
            target_token = "bnt"
            trade_amount = trade_tkn_to_ema(bnt_trading_liquidity, tkn_trading_liquidity, trading_fee, network_fee,
                                            future_ema)
            user_capability = user_tkn > trade_amount
        elif ema_rate > spot_rate:
            source_token = "bnt"
            target_token = token_name
            trade_amount = trade_bnt_to_ema(bnt_trading_liquidity, tkn_trading_liquidity, trading_fee, network_fee,
                                            future_ema)
            user_capability = user_bnt > trade_amount
        else:
            source_token = token_name
            target_token = token_name
            trade_amount = Decimal("0")
            user_capability = False
        print("Processed the ema force.")
        return trade_amount, source_token, target_token, user_capability

    @staticmethod
    def force_moving_average(protocol, token_name, user_name):
        user_tkn = protocol.state.users[user_name].wallet[token_name].tkn_amt
        user_bnt = protocol.state.users[user_name].wallet['bnt'].tkn_amt
        if protocol.state.transactions[token_name].trading_enabled:
            trade_amount, source_token, target_token, user_capability = MonteCarlo.process_force_moving_average(
                token_name, user_tkn, user_bnt)
            if user_capability:
                protocol.trade(trade_amount, source_token, target_token, user_name)
            else:
                print("The user has insufficient funds to force the ema.")
                pass
        else:
            print("Trading is disabled")
            pass

    @staticmethod
    def random_ema_force_trades(protocol):

        for i in range(random.randint(1, 10)):
            user_name = random.choice([user for user in protocol.global_state.usernames])
            tokens = [token for token in protocol.global_state.whitelisted_tokens if token != "bnt"]
            token_name = random.choice(tokens)
            if protocol.global_state.transactions[token_name].trading_enabled:
                MonteCarlo.force_moving_average(token_name, user_name)
                if random.randint(0, 2) != 0:
                    protocol.step()

    @staticmethod
    def get_minimum_bnt_funding(bnt_min_liquidity):
        return (Decimal("2.0") * bnt_min_liquidity) / Decimal("0.000001")

    @staticmethod
    def random_enable_trading(protocol):

        tokens = [token for token in protocol.global_state.whitelisted_tokens if token != "bnt"]
        for token_name in tokens:
            bnt_min_liquidity = protocol.global_state.bnt_min_liquidity

            if not protocol.global_state.transactions[token_name].trading_enabled:
                state = protocol.global_state
                state.tkn_name = token_name

                state, state.tkn_price, state.bnt_price = state.get_prices(token_name, protocol.price_feeds)

                bnt_virtual_balance = protocol.bnt_virtual_balance
                tkn_virtual_balance = protocol.tkn_virtual_balance
                smallest_bnt_funding_limit = MonteCarlo.get_minimum_bnt_funding(bnt_min_liquidity)
                bnt_funding_limit = MonteCarlo.randomise_amounts(smallest_bnt_funding_limit)
                protocol.enable_trading(
                    token_name,
                    bnt_virtual_balance,
                    tkn_virtual_balance,
                    bnt_funding_limit,
                )
                if random.randint(0, 2) != 0:
                    protocol.step()

    @staticmethod
    def random_begin_cooldowns():

        for i in range(random.randint(1, 10)):
            user = random.choice([user for user in users])
            token_name = random.choice(whitelisted_tokens)
            user_bntkn_amount = users[user][f"bn{token_name}_balance"][-1]
            if user_bntkn_amount > 0:
                bntkn_amount = random_cooldown_amount(user_bntkn_amount)
                staked_tkn = non_users["staking_ledger"][f"{token_name}_balance"][-1]
                bntkn_supply = non_users["erc20_contracts"][f"bn{token_name}_balance"][
                    -1
                ]
                bntkn_rate = get_bntkn_rate(staked_tkn, bntkn_supply)
                withdraw_value = get_tkn_amount(bntkn_rate, bntkn_amount)
                begin_cooldown(withdraw_value, token_name, user)
                copy_rows()
                if random.randint(0, 2) != 0:
                    new_timestamp()
            else:
                pass

    @staticmethod
    def random_withdrawals():

        for i in range(random.randint(1, 10)):
            user = random.choice([user for user in users])
            if len(pending_withdrawals[user]) > 0:
                id_number = random.choice(
                    [id_number for id_number in pending_withdrawals[user]]
                )
                withdraw(user, id_number)
                copy_rows()
                if random.randint(0, 2) != 0:
                    new_timestamp()
            else:
                pass

    @staticmethod
    def random_change_trading_fee():

        for i in range(random.randint(1, 3)):
            token_name = random.choice(whitelisted_tokens)
            trading_fee = non_users[f"{token_name}_pool"]["trading_fee"][-1]
            new_trading_fee = random_new_trading_fee(trading_fee)
            change_trading_fee(token_name, new_trading_fee)
            copy_rows()
            if random.randint(0, 2) != 0:
                new_timestamp()

    @staticmethod
    def random_change_network_fee():

        network_fee = non_users["global_protocol_settings"]["network_fee"][-1]
        new_network_fee = random_new_network_fee(network_fee)
        change_network_fee(new_network_fee)
        copy_rows()
        if random.randint(0, 2) != 0:
            new_timestamp()

    @staticmethod
    def random_change_withdrawal_fee():

        withdrawal_fee = non_users["global_protocol_settings"]["withdrawal_fee"][-1]
        new_withdrawal_fee = random_new_withdrawal_fee(withdrawal_fee)
        change_network_fee(new_withdrawal_fee)
        copy_rows()
        if random.randint(0, 2) != 0:
            new_timestamp()

    @staticmethod
    def random_change_bnt_funding_limit():

        token_name = random.choice(whitelisted_tokens)
        bnt_funding_amount = non_users[f"{token_name}_pool"]["bnt_funding_amount"][-1]
        updated_bnt_funding_limit = random_new_bnt_funding_limit(bnt_funding_amount)
        change_bnt_funding_limit(token_name, updated_bnt_funding_limit)
        copy_rows()
        if random.randint(0, 2) != 0:
            new_timestamp()

    @staticmethod
    def random_reduce_trading_liquidity():

        token_name = random.choice(whitelisted_tokens)
        bnt_trading_liquidity = non_users[f"{token_name}_pool"][
            "bnt_trading_liquidity"
        ][-1]
        if bnt_trading_liquidity > 0:
            updated_bnt_trading_liquidity = random_new_bnt_trading_liquidity(
                bnt_trading_liquidity
            )
            reduce_trading_liquidity(token_name, updated_bnt_trading_liquidity)
            copy_rows()
            if random.randint(0, 2) != 0:
                new_timestamp()
        else:
            pass

    @staticmethod
    def random_vortex_burner():

        user = random.choice([user for user in users])
        vortex_burner(user)
        copy_rows()
        if random.randint(0, 2) != 0:
            new_timestamp()

    @staticmethod
    def actions():

        i = random.randint(0, 2000)
        if i < 400:
            random_trades()
        elif 400 < i < 1000:
            random_arbitrage_trades()
        elif 1000 < i < 1200:
            random_ema_force_trades()
        elif 1200 < i < 1400:
            random_deposits()
        elif 1400 < i < 1500:
            random_begin_cooldowns()
        elif 1500 < i < 1700:
            random_withdrawals()
        elif 1700 < i < 1710:
            random_change_trading_fee()
        elif 1710 < i < 1720:
            random_change_network_fee()
        elif 1720 < i < 1730:
            random_change_withdrawal_fee()
        elif 1730 < i < 1740:
            random_reduce_trading_liquidity()
        elif 1740 < i < 1800:
            random_change_bnt_funding_limit()
        else:
            random_vortex_burner()
        random_enable_trading()

    @staticmethod
    def run():
        global timestamp
        while timestamp <= price_feeds.shape[0]:
            actions()
