from bancor_research.bancor_emulator.ERC20 import ERC20

'''
 * @dev this is an adapted clone of the OZ's ERC20Burnable extension which is unfortunately required so that it can be
 * explicitly specified in interfaces via our new IERC20Burnable interface.
 *
 * We have also removed the explicit use of Context and updated the code to our style.
'''
class ERC20Burnable(ERC20):
    '''
     * @inheritdoc IERC20Burnable
    '''
    def burn(self, amount) -> None:
        self._burn(self.msg_sender, amount);

    '''
     * @inheritdoc IERC20Burnable
    '''
    def burnFrom(self, recipient, amount) -> None:
        self._approve(recipient, self.msg_sender, self.allowance(recipient, self.msg_sender) - amount);
        self._burn(recipient, amount);
