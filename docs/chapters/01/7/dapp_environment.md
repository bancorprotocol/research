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

# Network dApp Environment

The `BancorNetwork` class provides the top level interface through which the entire codebase is made to simulate real-world scenarios in a practical sense. An instance of this class is analogous to the **Environment** in common agent-oriented-programming jargon, and more practically, can be thought of like an instance of the **Bancor dApp** where Traders can perform trades, and where LPs can make deposits, withdraws, and participate in DAO votes which change the system's tuneable fee (and other) parameters. 

 * `v3.begin_cooldown`
 * `v3.burn`
 * `v3.claim_standard_rewards`
 * `v3.create_autocompounding_program`
 * `v3.create_user`
 * `v3.dao_msig_init_pools`
 * `v3.deposit`
 * `v3.describe`
 * `v3.describe_rates`
 * `v3.distribute_autocompounding_program`
 * `v3.export`
 * `v3.export_test_scenarios`
 * `v3.get_state`
 * `v3.join_standard_rewards`
 * `v3.leave_standard_rewards`
 * `v3.next_transaction`
 * `v3.revert_state`
 * `v3.set_state`
 * `v3.set_user_balance`
 * `v3.show_history`
 * `v3.trade`
 * `v3.update_state`
 * `v3.whitelist_token`
 * `v3.withdraw`
 * `v3.set_trading_fee`
 * `v3.set_network_fee`
 * `v3.set_withdrawal_fee`
 * `v3.set_bnt_funding_limit`

## Example 

```
v3 = BancorNetwork()

tkn_name = 'wbtc'
value = .005

v3.set_trading_fee(tkn_name=tkn_name, value=value)
```
