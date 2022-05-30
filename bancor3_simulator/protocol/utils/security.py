# coding=utf-8
def get_contracttoken_dictionary():
    """
    @_dev
    _returns the token_contract : _t_k_n dictionary.
    """
    contract_token_dictionary = {
        "0x_eeeee_eeee_ee_eee_ee_ee_eee_e_e_eeeee_eeeeeeee_e_ee_e": "eth",
        "0x6_b175474_e89094_c44_da98b954_eede_a_c495271d0_f": "dai",
        "0x514910771_a_f9_ca656af840dff83_e8264_ec_f986_c_a": "link",
        "0x1_f573_d6_fb3_f13d689_f_f844_b4c_e37794d79a7_f_f1_c": "bnt",
    }
    return contract_token_dictionary


def get_empty_monitor():
    """
    @_dev
    _returns an empty monitor dictionary.
    """
    monitor = {
        "token deposits": {
            "block number": [],
            "transaction hash": [],
            "token": [],
            "token amount": [],
            "ethereum master vault balance": [],
            "simulated master vault balance": [],
            "ethereum staking ledger balance": [],
            "simulated staking ledger balance": [],
            "ethereum pool token supply": [],
            "simulated pool token supply": [],
            "ethereum minted pool token amount": [],
            "simulated minted pool token amount": [],
        },
        "withdrawals initiated": {
            "block number": [],
            "transaction hash": [],
            "token": [],
            "withdrawn token amount": [],
            "ethereum pool token amount": [],
            "simulated pool token amount": [],
        },
        "bnt deposits": {
            "block number": [],
            "transaction hash": [],
            "bnt amount": [],
            "ethereum transfered bnbnt amount": [],
            "simulated transfered bnbnt amount": [],
            "ethereum minted vbnt amount": [],
            "simulated minted vbnt amount": [],
        },
        "trades": {
            "block number": [],
            "transaction hash": [],
            "source token amount": [],
            "source token": [],
            "target token": [],
            "ethereum target token amount": [],
            "simulated target token amount": [],
            "ethereum previous bnt liquidity": [],
            "simulated previous bnt liquidity": [],
            "ethereum previous tkn liquidity": [],
            "simulated previous tkn liquidity": [],
            "ethereum new bnt liquidity": [],
            "simulated new bnt liquidity": [],
            "ethereum new tkn liquidity": [],
            "simulated new tkn liquidity": [],
            "ethereum implied trading fee": [],
            "true trading fee": [],
            "ethereum implied network fee": [],
            "true network fee": [],
            "ethereum fee paid by trader": [],
            "simulated fee paid by trader": [],
            "ethereum implied fee to staking ledger": [],
            "simulated fee to staking ledger": [],
            "ethereum implied bnt to vortex ledger": [],
            "simulated bnt to vortex ledger": [],
        },
    }
    return monitor


# *** _main _security _functions ***
def contract_network_fee_ppm_updated(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the new_fee_ppm event from the contracts.
    """
    new_fee_ppm = get_contract_fee_ppm(df, index)
    new_network_fee = contract_convert_ppm(new_fee_ppm)
    change_network_fee(new_network_fee)
    return None


def contract_trading_fee_ppm_updated(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the _trading_fee_ppm_updated event from the contracts.
    """
    new_fee_ppm = get_contract_fee_ppm(df, index)
    new_trading_fee = contract_convert_ppm(new_fee_ppm)
    token_name = get_contract_token_name(df, index)
    change_trading_fee(token_name, new_trading_fee)
    return None


def contract_depositing_enabled(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the _depositing_enabled event from the contracts.
    """
    do_nothing()
    return None


def contract_funding_limits(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the _funding_limits event from the contracts.
    """
    token_name = get_contract_token_name(df, index)
    updated_bnt_funding_limit = get_contract_funding_limit(df, index)
    change_bnt_funding_limit(token_name, updated_bnt_funding_limit)
    return None


def contract_trading_enabled(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the _depositing_enabled event from the contracts.
    """
    new_status = get_contract_new_status(df, index)
    if new_status == _true:
        token_name = get_contract_token_name(df, index)
        token_decimals = get_contract_token_decimals(df, index)
        bnt_virtual_balance = get_contract_bnt_new_liquidity(df, index)
        tkn_token_virtual_balance = get_contract_tkn_new_liquidity(
            df, index, token_decimals
        )
        bnt_funding_limit = get_contract_last_bnt_funding_limit(token_name)
        enable_trading(
            token_name,
            bnt_virtual_balance,
            tkn_token_virtual_balance,
            bnt_funding_limit,
        )
    else:
        do_nothing()
    return None


def contract_deposit_tkn(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the deposit_t_k_n event from the contracts.
    """
    token_name = get_contract_token_name(df, index)
    token_decimals = get_contract_token_decimals(df, index)
    tkn_amount = get_contract_token_amount(df, index, token_decimals)
    (
        contract_master_vault_tkn_balance,
        contract_staking_ledger_tkn_balance,
        contract_erc20_contract_tkn_balance,
        contract_bntkn_amount,
    ) = get_contract_deposit_tkn_outputs(df, index, token_decimals)
    new_timestamp(block_number)
    deposit_t_k_n(tkn_amount, token_name, user)
    (
        simulator_master_vault_tkn_balance,
        simulator_staking_ledger_tkn_balance,
        simulator_erc20_contract_tkn_balance,
        simulator_bntkn_amount,
    ) = get_simulation_deposit_tkn_outputs(token_name)
    deposit_tkn_comparisson(
        block_number,
        tx_hash,
        token_name,
        tkn_amount,
        contract_master_vault_tkn_balance,
        simulator_master_vault_tkn_balance,
        contract_staking_ledger_tkn_balance,
        simulator_staking_ledger_tkn_balance,
        contract_erc20_contract_tkn_balance,
        simulator_erc20_contract_tkn_balance,
        contract_bntkn_amount,
        simulator_bntkn_amount,
    )
    return None


def contract_withdrawal_initiated(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the deposit_t_k_n event from the contracts.
    """
    token_name = get_contract_token_name(df, index)
    token_decimals = get_contract_token_decimals(df, index)
    withdraw_value = get_contract_reserve_token_amount(df, index, token_decimals)
    contract_pool_token_amount = get_contract_withdrawal_initiated_outputs(df, index)
    new_timestamp(block_number)
    begin_cooldown(withdraw_value, token_name, user)
    simulator_pool_token_amount = get_simulated_withdrawal_initiated_outputs()
    withdrawal_initiated_comparisson(
        block_number,
        tx_hash,
        token_name,
        withdraw_value,
        contract_pool_token_amount,
        simulator_pool_token_amount,
    )
    return None


def contract_deposit_bnt(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the deposit_t_k_n event from the contracts.
    """
    bnt_amount = get_contract_bnt_amount(df, index)
    contract_pool_token_amount, contract_vbnt_amount = get_contract_deposit_bnt_outputs(
        df, index
    )
    new_timestamp(block_number)
    deposit_b_n_t(bnt_amount, user)
    (
        simulator_pool_token_amount,
        simulator_vbnt_amount,
    ) = get_simulator_deposit_bnt_outputs()
    deposit_bnt_comparisson(
        block_number,
        tx_hash,
        bnt_amount,
        contract_pool_token_amount,
        contract_vbnt_amount,
        simulator_pool_token_amount,
        simulator_vbnt_amount,
    )
    return None


def contract_trade(df, index, block_number, tx_hash):
    """
    @_dev
    _processes the trade event from the contracts.
    """
    (
        source_token,
        source_token_amount,
        target_token,
        contract_target_token_amount,
        contract_bnt_prev_liquidity,
        contract_bnt_new_liquidity,
        contract_tkn_prev_liquidity,
        contract_tkn_new_liquidity,
        contract_fee_amount,
        implied_trading_fee,
        implied_network_fee,
        implied_fee_to_staking_ledger,
        implied_bnt_to_vortex_ledger,
    ) = get_contract_trade_outputs(df, index, tx_hash)
    trade(source_token_amount, source_token, target_token, user)
    (
        true_trading_fee,
        simulated_bnt_prev_liquidity,
        simulated_bnt_new_liquidity,
        simulated_tkn_prev_liquidity,
        simulated_tkn_new_liquidity,
    ) = get_simulated_trading_pool_vars(source_token, target_token)
    (
        simulated_target_token_amount,
        simulated_fee_to_staking_ledger,
        simulated_bnt_to_vortex_ledger,
    ) = get_simulated_trading_outputs(target_token)
    true_network_fee = non_users["global_protocol_settings"]["network_fee"][-1]
    simulated_fee_amount = get_simulated_fee_amount(
        source_token,
        source_token_amount,
        simulated_bnt_prev_liquidity,
        simulated_tkn_prev_liquidity,
        true_trading_fee,
    )
    trade_comparisson(
        block_number,
        tx_hash,
        source_token_amount,
        source_token,
        target_token,
        contract_target_token_amount,
        simulated_target_token_amount,
        contract_bnt_prev_liquidity,
        simulated_bnt_prev_liquidity,
        contract_tkn_prev_liquidity,
        simulated_tkn_prev_liquidity,
        contract_bnt_new_liquidity,
        simulated_bnt_new_liquidity,
        contract_tkn_new_liquidity,
        simulated_tkn_new_liquidity,
        implied_trading_fee,
        true_trading_fee,
        implied_network_fee,
        true_network_fee,
        contract_fee_amount,
        simulated_fee_amount,
        implied_fee_to_staking_ledger,
        simulated_fee_to_staking_ledger,
        implied_bnt_to_vortex_ledger,
        simulated_bnt_to_vortex_ledger,
    )
    return None


contract_function_dictionary = {
    "_network_fee_ppm_updated": contract_network_fee_ppm_updated,
    "_trading_fee_ppm_updated": contract_trading_fee_ppm_updated,
    "_depositing_enabled": contract_depositing_enabled,
    "_trading_enabled": contract_trading_enabled,
    "_funding_limits": contract_funding_limits,
    "deposit_t_k_n": contract_deposit_tkn,
    "_withdrawal_initiated": contract_withdrawal_initiated,
    "deposit_b_n_t": contract_deposit_bnt,
    "trade": contract_trade,
}


def security_monitor(events):
    df = pd.read_csv(events)
    for index in df.index:
        print(index)
        copy_rows()
        block_number = get_contract_block_number(df, index)
        new_timestamp(block_number)
        tx_hash = get_tx_hash(df, index)
        type = df["type"][index]
        function = contract_function_dictionary[type]
        function(df, index, block_number, tx_hash)


def monitor_charts(monitor):
    monitor_token_deposits = pd._data_frame.from_dict(monitor["token deposits"])
    monitor_withdrawals_initiated = pd._data_frame.from_dict(
        monitor["withdrawals initiated"]
    )
    monitor_bnt_deposits = pd._data_frame.from_dict(monitor["bnt deposits"])
    monitor_trades = pd._data_frame.from_dict(monitor["trades"])
    sns.set(
        rc={
            "axes.facecolor": "black",
            "figure.facecolor": "black",
            "text.color": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "axes.grid": _false,
            "axes.labelcolor": "white",
        }
    )
    monitor_token_deposits.columns
    for monitordict in [
        monitor_token_deposits,
        monitor_withdrawals_initiated,
        monitor_bnt_deposits,
        monitor_trades,
    ]:
        begin = [i for i, c in enumerate(monitordict.keys()) if "simulated" in c][0] - 1
        zippy = list(
            zip(monitordict.keys()[begin::2], monitordict.keys()[begin + 1 :: 2])
        )
        count = 0
        for i in range(len(zippy)):
            monitordict.loc[:, zippy[i]] = monitordict.loc[:, zippy[i]].astype(float)
            fig = plt.figure()
            fig.set_size_inches(6, 6)
            print(zippy[i][0])
            print("_compare max deviation from ethereum vs simulated:")
            print(
                abs(
                    (monitordict.loc[:, zippy[i][1]] - monitordict.loc[:, zippy[i][0]])
                    / monitordict.loc[:, zippy[i][1]]
                ).max()
            )
            sns.lineplot(
                data=monitordict,
                x="block number",
                y=(monitordict.loc[:, zippy[i][1]] - monitordict.loc[:, zippy[i][0]])
                / monitordict.loc[:, zippy[i][1]],
                color="r",
            )
            plt.show()
            count += 1
    return None
