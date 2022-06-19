import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from PoolToken import PoolToken
from ERC20 import ERC20

POOL_TOKEN_NAME = 'Pool Token';
POOL_TOKEN_SYMBOL = 'POOL';
POOL_TOKEN_DECIMALS = 10;

RESERVE_TOKEN_NAME = 'Reserve Token';
RESERVE_TOKEN_SYMBOL = 'Reserve';

reserveToken = ERC20(RESERVE_TOKEN_NAME, RESERVE_TOKEN_SYMBOL);

poolToken = PoolToken(POOL_TOKEN_NAME, POOL_TOKEN_SYMBOL, POOL_TOKEN_DECIMALS, reserveToken);

assert poolToken.name() == POOL_TOKEN_NAME;
assert poolToken.symbol() == POOL_TOKEN_SYMBOL;
assert poolToken.decimals() == POOL_TOKEN_DECIMALS;
assert poolToken.totalSupply() == 0;
assert poolToken.reserveToken() == reserveToken;

NUM_OF_ACCOUNTS = 10
_msgSender = '_msgSender'

for n in range(NUM_OF_ACCOUNTS):
    account = 'account_{}'.format(n)
    assert poolToken.balanceOf(account) == 0;
    amount = n + 1
    poolToken.mint(account, amount)
    assert poolToken.balanceOf(account) == amount;

for n in range(NUM_OF_ACCOUNTS - 1):
    source_account = 'account_{}'.format(n)
    target_account = 'account_{}'.format(n + 1)
    source_amount = poolToken.balanceOf(source_account);
    target_amount = poolToken.balanceOf(source_account);
    poolToken.approve(source_account, _msgSender, source_amount)
    poolToken.transferFrom(_msgSender, source_account, target_account, source_amount)
    assert poolToken.balanceOf(source_account) == 0;
    assert poolToken.balanceOf(target_account) == source_amount + target_amount;
