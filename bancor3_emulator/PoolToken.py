from ERC20 import ERC20
from Owned import Owned

'''
 * @dev Pool Token contract
'''
class PoolToken(ERC20, Owned):
    '''
     * @dev initializes a new PoolToken contract
    '''
    def __init__(self,
        name,
        symbol,
        initDecimals,
        initReserveToken
    ) -> None:
        ERC20.__init__(self, name, symbol)
        Owned.__init__(self)

        self._decimals = initDecimals;
        self._reserveToken = initReserveToken;

    '''
     * @dev returns the number of decimals used to get its user representation
    '''
    def decimals(self):
        return self._decimals;

    '''
     * @inheritdoc IPoolToken
    '''
    def reserveToken(self):
        return self._reserveToken;

    '''
     * @inheritdoc IPoolToken
    '''
    def mint(self, recipient, amount):
        self._mint(recipient, amount);
