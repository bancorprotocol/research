from utils import account

class Vault(account):
    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self, initBNTGovernance, initVBNTGovernance) -> None:
        account.__init__(self)

        self._bntGovernance = initBNTGovernance;
        self._bnt = initBNTGovernance.token();
        self._vbntGovernance = initVBNTGovernance;
        self._vbnt = initVBNTGovernance.token();

    '''
     * @inheritdoc IVault
    '''
    def withdrawFunds(self, sender, token, target, amount) -> None:
        token.transfer(sender, target, amount);

    '''
     * @inheritdoc IVault
    '''
    def burn(self, token, amount) -> None:
        if (token is (self._bnt)):
            self._bntGovernance.burn(amount);
        elif (token is (self._vbnt)):
            self._vbntGovernance.burn(amount);
        else:
            token.burn(amount);
