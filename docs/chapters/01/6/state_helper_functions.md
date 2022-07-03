---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.7
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# State Helper Functions


## Get Values

These functions get the current state variable value.

* `get_autocompounding_remaining_rewards(state, tkn_name)`
* `get_autocompounding_start_time(state, tkn_name)`
* `get_avg_tkn_trading_liquidity(state, tkn_name)`
* `get_bnbnt_rate(state, tkn_name)`
* `get_bnt_bootstrap_liquidity(state, tkn_name)`
* `get_bnt_funding_amt(state, tkn_name)`
* `get_bnt_funding_limit(state, tkn_name)`
* `get_bnt_min_liquidity(state, tkn_name)`
* `get_bnt_remaining_funding(state, tkn_name)`
* `get_bnt_trading_liquidity(state, tkn_name)`
* `get_bnt_virtual_balance(state, tkn_name)`
* `get_description(state, tkn_name)`
* `get_distribution_type(state, tkn_name)`
* `get_ema_last_updated(state, tkn_name)`
* `get_ema_rate(state, tkn_name)`
* `get_external_protection_description(state, tkn_name)`
* `get_external_protection_vault(state, tkn_name)`
* `get_flat_distribution_rate_per_second(state, tkn_name)`
* `get_half_life_seconds(state, tkn_name)`
* `get_inv_spot_rate(state, tkn_name)`
* `get_is_ema_update_allowed(state, tkn_name)`
* `get_is_price_stable(state, tkn_name)`
* `get_is_trading_enabled(state, tkn_name)`
* `get_json_virtual_balances(state, tkn_name)`
* `get_max_bnt_deposit(state, tkn_name)`
* `get_network_fee(state, tkn_name)`
* `get_pooltoken_balance(state, tkn_name)`
* `get_pooltoken_description(state, tkn_name)`
* `get_pooltoken_name(state, tkn_name)`
* `get_prev_token_amt_distributed(state, tkn_name)`
* `get_prices(state, tkn_name)`
* `get_protocol_wallet_balance(state, tkn_name)`
* `get_protocol_wallet_description(state, tkn_name)`
* `get_rate_report(state, tkn_name)`
* `get_remaining_standard_rewards(state, tkn_name)`
* `get_spot_rate(state, tkn_name)`
* `get_staked_balance(state, tkn_name)`
* `get_staking_description(state, tkn_name)`
* `get_standard_program(state, tkn_name)`
* `get_standard_reward_end_time(state, tkn_name)`
* `get_standard_reward_last_update_time(state, tkn_name)`
* `get_standard_reward_per_token(state, tkn_name)`
* `get_standard_reward_providers(state, tkn_name)`
* `get_standard_reward_rate(state, tkn_name)`
* `get_standard_reward_start_time(state, tkn_name)`
* `get_standard_reward_tkn_name(state, tkn_name)`
* `get_timestamp(state, tkn_name)`
* `get_tkn_bootstrap_liquidity(state, tkn_name)`
* `get_tkn_excess(state, tkn_name)`
* `get_tkn_excess_bnt_equivalence(state, tkn_name)`
* `get_tkn_price(state, tkn_name)`
* `get_tkn_trading_liquidity(state, tkn_name)`
* `get_tkn_virtual_balance(state, tkn_name)`
* `get_total_bnt_trading_liquidity(state, tkn_name)`
* `get_total_holdings(state, user_name, tkn_name)`
* `get_total_rewards(state, tkn_name)`
* `get_total_standard_rewards_staked(state, tkn_name)`
* `get_trade_inputs(state, tkn_name)`
* `get_trading_fee(state, tkn_name)`
* `get_trading_liquidity_description(state, tkn_name)`
* `get_unclaimed_rewards(state, tkn_name)`
* `get_user_balance(state, user_name, tkn_name)`
* `get_user_pending_rewards_staked_balance(state, user_name, tkn_name)`
* `get_user_pending_standard_rewards(state, user_name, tkn_name)`
* `get_user_pending_withdrawals(state, user_name, tkn_name)`
* `get_user_reward_per_token_paid(state, user_name, tkn_name)`
* `get_user_wallet_tokens(state, user_name, tkn_name)`
* `get_usernames(state, tkn_name)`
* `get_vault_balance(state, tkn_name)`
* `get_vault_description(state, tkn_name)`
* `get_vault_tvl(state, tkn_name)`
* `get_virtual_rate(state, tkn_name)`
* `get_vortex_balance(state)`
* `get_vortex_description(state, tkn_name)`
* `get_whitelisted_tokens(state, tkn_name)`
* `get_withdrawal_id(state, tkn_name)`

### Example 

```
v3 = BancorNetwork()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"

balance = get_user_balance(state, user_name, tkn_name)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

balance = get_user_balance(state, user_name, pooltoken_name)
```


## Modify State
The following methods provide an interface to modify `State`.

*Note:* For reason of readability and clarity, the following operations are handled by methods of the `State` class, whereas the above *get* operations above are handled by functions. Thus, we include the `state.` prefix for each method below, where typing is assumed `state: State`

## Set Values

 * `state.set_autocompounding_remaining_rewards(tkn_name, value)`
 * `state.set_bnt_funding_amt(tkn_name, value)`
 * `state.set_bnt_funding_limit(tkn_name, value)`
 * `state.set_bnt_trading_liquidity(tkn_name, value)`
 * `state.set_ema_rate(tkn_name, value)`
 * `state.set_initial_rates(tkn_name, value)`
 * `state.set_inv_spot_rate(tkn_name, value)`
 * `state.set_is_trading_enabled(tkn_name, value)`
 * `state.set_network_fee(tkn_name, value)`
 * `state.set_pending_withdrawals_status(tkn_name, value)`
 * `state.set_pooltoken_balance(tkn_name, value)`
 * `state.set_prev_token_amt_distributed(tkn_name, value)`
 * `state.set_program_is_active(tkn_name, value)`
 * `state.set_protocol_wallet_balance(tkn_name, value)`
 * `state.set_provider_pending_standard_rewards(tkn_name, value)`
 * `state.set_provider_reward_per_token_paid(tkn_name, value)`
 * `state.set_spot_rate(tkn_name, value)`
 * `state.set_staked_balance(tkn_name, value)`
 * `state.set_standard_program_end_time(tkn_name, value)`
 * `state.set_standard_program_is_active(tkn_name, value)`
 * `state.set_standard_remaining_rewards(tkn_name, value)`
 * `state.set_standard_rewards_last_update_time(tkn_name, value)`
 * `state.set_standard_rewards_per_token(tkn_name, value)`
 * `state.set_standard_rewards_vault_balance(tkn_name, value)`
 * `state.set_tkn_trading_liquidity(tkn_name, value)`
 * `state.set_token_amt_to_distribute(tkn_name, value)`
 * `state.set_trading_fee(tkn_name, value)`
 * `state.set_user_balance(user_name, tkn_name, value)`
 * `state.set_user_pending_standard_rewards(user_name, tkn_name, value)`
 * `state.set_user_standard_rewards_stakes(user_name, tkn_name, value)`
 * `state.set_vault_balance(tkn_name, value)`
 * `state.set_vbnt_burned(tkn_name, value)`
 * `state.set_vortex_balance(tkn_name, value)`
 * `state.set_withdrawal_fee(tkn_name, value)`
 
 ### Example 

```
v3 = BancorNetwork()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"
value = 100

state.set_user_balance(user_name, tkn_name, value)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

state.set_user_balance(user_name, pooltoken_name, value)
```

## Decrease Values

 * `state.decrease_bnt_funding_amt(tkn_name, value)`
 * `state.decrease_bnt_trading_liquidity(tkn_name, value)`
 * `state.decrease_external_protection_balance(tkn_name, value)`
 * `state.decrease_pooltoken_balance(tkn_name, value)`
 * `state.decrease_protocol_wallet_balance(tkn_name, value)`
 * `state.decrease_staked_balance(tkn_name, value)`
 * `state.decrease_standard_reward_program_stakes(tkn_name, value)`
 * `state.decrease_standard_rewards_vault_balance(tkn_name, value)`
 * `state.decrease_tkn_trading_liquidity(tkn_name, value)`
 * `state.decrease_user_balance(user_name, tkn_name, value)`
 * `state.decrease_user_standard_rewards_stakes(user_name, tkn_name, value)`
 * `state.decrease_vault_balance(tkn_name, value)`
 * `state.decrease_vbnt_burned(tkn_name, value)`
 * `state.decrease_vortex_balance(tkn_name, value)`

### Example 

```
v3 = BancorNetwork()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"

# Amount to be subtracted from the current state
value = 100         

state.decrease_user_balance(user_name, tkn_name, value)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

state.decrease_user_balance(user_name, pooltoken_name, value)
```

## Increase Values

 * `state.increase_bnt_funding_amt(tkn_name, value)`
 * `state.increase_bnt_trading_liquidity(tkn_name, value)`
 * `state.increase_external_protection_balance(tkn_name, value)`
 * `state.increase_pooltoken_balance(tkn_name, value)`
 * `state.increase_protocol_wallet_balance(tkn_name, value)`
 * `state.increase_staked_balance(tkn_name, value)`
 * `state.increase_standard_reward_program_stakes(tkn_name, value)`
 * `state.increase_standard_rewards_vault_balance(tkn_name, value)`
 * `state.increase_tkn_trading_liquidity(tkn_name, value)`
 * `state.increase_user_balance(user_name, tkn_name, value)`
 * `state.increase_user_standard_rewards_stakes(user_name, tkn_name, value)`
 * `state.increase_vault_balance(tkn_name, value)`
 * `state.increase_vbnt_burned(tkn_name, value)`
 * `state.increase_vortex_balance(tkn_name, value)`

### Example 

```
v3 = BancorNetwork()
state = v3.get_state()

user_name = "Alice"
tkn_name = "bnt"

# Amount to be added to the current balance
value = 100         

state.increase_user_balance(user_name, tkn_name, value)
```

*Note:* The operation is similar for pooltokens and vbnt tokens.

```
pooltoken_name = f"bn{tkn_name}"

state.increase_user_balance(user_name, pooltoken_name, value)
```
