from bancor_research.bancor_emulator.solidity import uint, uint8, mapping
from bancor_research.bancor_emulator.utils import contract

from bancor_research.bancor_emulator.PoolToken import PoolToken

'''
 * @dev Pool Token Factory contract
'''
class PoolTokenFactory(contract):
    POOL_TOKEN_SYMBOL_PREFIX = "bn";
    POOL_TOKEN_NAME_PREFIX = "Bancor";
    POOL_TOKEN_NAME_SUFFIX = "Pool Token";

    def __init__(self) -> None:
        contract.__init__(self)

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__PoolTokenFactory_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __PoolTokenFactory_init(self) -> None:
        self.__PoolTokenFactory_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __PoolTokenFactory_init_unchained(self) -> None:
        # a mapping between tokens and custom symbol overrides (only needed for tokens with malformed symbol property)
        self._tokenSymbolOverrides = mapping(lambda: str());

        # a mapping between tokens and custom token overrides (only needed for tokens with malformed decimals property)
        self._tokenDecimalsOverrides = mapping(lambda: uint8());

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 1;

    '''
     * @inheritdoc IPoolTokenFactory
    '''
    def tokenSymbolOverride(self, token) -> (str):
        return self._tokenSymbolOverrides[token];

    '''
     * @dev sets the custom symbol override for a given reserve token
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setTokenSymbolOverride(self, token, symbol) -> None:
        self._tokenSymbolOverrides[token] = symbol;

    '''
     * @inheritdoc IPoolTokenFactory
    '''
    def tokenDecimalsOverride(self, token) -> (uint):
        return self._tokenDecimalsOverrides[token];

    '''
     * @dev sets the decimals override for a given reserve token
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setTokenDecimalsOverride(self, token, decimals) -> None:
        self._tokenDecimalsOverrides[token] = decimals;

    '''
     * @inheritdoc IPoolTokenFactory
    '''
    def createPoolToken(self, token) -> (PoolToken):
        customSymbol = self._tokenSymbolOverrides[token];
        tokenSymbol = customSymbol if len(customSymbol) != 0 else token.symbol();

        customDecimals = self._tokenDecimalsOverrides[token];
        tokenDecimals = customDecimals if customDecimals != 0 else token.decimals();

        symbol = "".join([self.POOL_TOKEN_SYMBOL_PREFIX, tokenSymbol]);
        name = "".join([self.POOL_TOKEN_NAME_PREFIX, " ", tokenSymbol, " ", self.POOL_TOKEN_NAME_SUFFIX]);

        newPoolToken = PoolToken(name, symbol, tokenDecimals, token);

        # make sure to transfer the ownership to the caller
        newPoolToken.transferOwnership(self.msg_sender);

        return newPoolToken;
