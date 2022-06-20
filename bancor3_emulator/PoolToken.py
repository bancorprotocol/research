from ERC20 import ERC20

'''
 * @dev Pool Token contract
'''
class PoolToken(ERC20):
    '''
     * @dev initializes a new PoolToken contract
    '''
    def __init__(self,
        name,
        symbol,
        initDecimals,
        initReserveToken
    ) -> None:
        ERC20().__init__(name, symbol)
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
