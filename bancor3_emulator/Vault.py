class Vault:
    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self, initBNTGovernance, initVBNTGovernance) -> None:
        self._bntGovernance = initBNTGovernance;
        self._bnt = initBNTGovernance.token();
        self._vbntGovernance = initVBNTGovernance;
        self._vbnt = initVBNTGovernance.token();

    '''
     * @dev initializes the contract and its parents
    '''
    def __Vault_init(self) -> None:
        self.__Vault_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __Vault_init_unchained(self) -> None:
        pass

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
