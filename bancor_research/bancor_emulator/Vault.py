from bancor_research.bancor_emulator.utils import account


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

    def withdrawFunds(self,
                      token,
                      target,
                      amount
                      ) -> None:
        if (amount == 0):
            return;

        token.transfer(target, amount);

    '''
     * @inheritdoc IVault
    '''

    def burn(self, token, amount) -> None:
        if (amount == 0):
            return;

        if (token is (self._bnt)):
            self._bntGovernance.burn(amount);
        elif (token is (self._vbnt)):
            self._vbntGovernance.burn(amount);
        else:
            token.burn(amount);
