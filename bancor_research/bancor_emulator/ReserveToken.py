from bancor_research.bancor_emulator.ERC20 import ERC20

'''
 * @dev ReserveToken represents a token with dynamic supply.
 * The owner of the token can mint/burn tokens to/from any account.
 *
'''
class ReserveToken(ERC20):
    '''
     * @dev initializes a new ReserveToken instance
     *
     * @param _name       token name
     * @param _symbol     token short symbol, minimum 1 character
     * @param _decimals   for display purposes only
    '''
    def __init__(self,
        _name,
        _symbol,
        _decimals
    ) -> None:
        ERC20.__init__(self, _name, _symbol)

        self._decimals = _decimals;

    '''
     * @dev increases the token supply and sends the new tokens to the given account
     * can only be called by the contract owner
     *
     * @param _to      account to receive the new amount
     * @param _amount  amount to increase the supply by
    '''
    def issue(self, _to, _amount):
        self._mint(_to, _amount);

    '''
     * @dev removes tokens from the given account and decreases the token supply
     * can only be called by the contract owner
     *
     * @param _from    account to remove the amount from
     * @param _amount  amount to decrease the supply by
    '''
    def destroy(self, _from, _amount):
        self._burn(_from, _amount);

    def decimals(self):
        return self._decimals;
