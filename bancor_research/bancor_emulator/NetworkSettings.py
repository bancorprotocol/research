from bancor_research.bancor_emulator.solidity import uint, uint32, uint256, mapping, address, revert
from bancor_research.bancor_emulator.utils import contract, parse

from bancor_research.bancor_emulator.EnumerableSet import EnumerableSet

'''
 * @dev Network Settings contract
'''
class NetworkSettings(contract):
    DEFAULT_FLASH_LOAN_FEE_PPM = uint32(0); # 0%

    class FlashLoanFee:
        def __init__(self, x = None) -> None:
            self.initialized = parse(bool, x, 'initialized');
            self.feePPM = parse(uint32, x, 'feePPM');

    def __init__(self, initBnt) -> None:
        contract.__init__(self)

        self._bnt = initBnt;

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__NetworkSettings_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __NetworkSettings_init(self) -> None:
        self.__NetworkSettings_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __NetworkSettings_init_unchained(self) -> None:
        # a set of tokens which are eligible for protection
        self._protectedTokenWhitelist = EnumerableSet();

        # a mapping of BNT funding limits per pool
        self._poolFundingLimits = mapping(lambda: uint256());

        # below that amount, trading is disabled and co-investments use the initial rate
        self._minLiquidityForTrading = uint256();

        # the withdrawal fee (in units of PPM)
        self._withdrawalFeePPM = uint32();

        # the default flash-loan fee (in units of PPM)
        self._defaultFlashLoanFeePPM = uint32();

        # a mapping between pools and their flash-loan fees
        self._flashLoanFees = mapping(lambda: self.FlashLoanFee());

        self._setDefaultFlashLoanFeePPM(self.DEFAULT_FLASH_LOAN_FEE_PPM);

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 3;

    '''
     * @inheritdoc INetworkSettings
    '''
    def protectedTokenWhitelist(self) -> (list):
        return self._protectedTokenWhitelist.values();

    '''
     * @dev adds a token to the protected tokens whitelist
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def addTokenToWhitelist(self, token) -> None:
        self._addTokenToWhitelist(token);

    '''
     * @dev adds tokens to the protected tokens whitelist
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def addTokensToWhitelist(self, tokens) -> None:
        length = len(tokens.length);

        for i in range(length):
            self._addTokenToWhitelist(tokens[i]);

    '''
     * @dev adds a token to the protected tokens whitelist
    '''
    def _addTokenToWhitelist(self, token) -> None:
        if (not self._protectedTokenWhitelist.add(address(token))):
            revert("AlreadyExists");

    '''
     * @dev removes a token from the protected tokens whitelist
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def removeTokenFromWhitelist(self, token) -> None:
        if (not self._protectedTokenWhitelist.remove(address(token))):
            revert("DoesNotExist");

    '''
     * @inheritdoc INetworkSettings
    '''
    def isTokenWhitelisted(self, token) -> (bool):
        return self._isTokenWhitelisted(token);

    '''
     * @inheritdoc INetworkSettings
    '''
    def poolFundingLimit(self, pool) -> (uint):
        return self._poolFundingLimits[pool].clone();

    '''
     * @dev updates the amount of BNT that the protocol can provide as funding for a specific pool
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
     * - the token must have been whitelisted
    '''
    def setFundingLimit(self, pool, amount) -> None:
        self._setFundingLimit(pool, amount);

    '''
     * @dev updates the amounts of BNT that the protocol can provide as funding for specific pools
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
     * - each one of the tokens must have been whitelisted
    '''
    def setFundingLimits(self, pools, amounts) -> None:
        length = len(pools);
        if (length != len(amounts)):
            revert("InvalidParam");

        for i in range(length):
            self._setFundingLimit(pools[i], amounts[i]);

    '''
     * @dev updates the amount of BNT that the protocol can provide as funding for a specific pool
    '''
    def _setFundingLimit(self, pool, amount) -> None:
        if (not self._isTokenWhitelisted(pool)):
            revert("NotWhitelisted");

        prevPoolFundingLimit = self._poolFundingLimits[pool];
        if (prevPoolFundingLimit == amount):
            return;

        self._poolFundingLimits[pool] = uint256(amount);

    '''
     * @dev adds a token to the protected tokens whitelist,
     * and sets the amount of BNT that the protocol can provide as funding for this pool
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def addTokenToWhitelistWithLimit(self, token, amount) -> None:
        self._addTokenToWhitelist(token);
        self._setFundingLimit(token, amount);

    '''
     * @inheritdoc INetworkSettings
    '''
    def minLiquidityForTrading(self) -> (uint):
        return self._minLiquidityForTrading.clone();

    '''
     * @dev updates the minimum liquidity for trading amount
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setMinLiquidityForTrading(self, amount) -> None:
        prevMinLiquidityForTrading = self._minLiquidityForTrading;
        if (self._minLiquidityForTrading == amount):
            return;

        self._minLiquidityForTrading = uint256(amount);

    '''
     * @inheritdoc INetworkSettings
    '''
    def withdrawalFeePPM(self) -> (uint):
        return self._withdrawalFeePPM.clone();

    '''
     * @dev sets the withdrawal fee (in units of PPM)
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setWithdrawalFeePPM(self, newWithdrawalFeePPM) -> None:
        prevWithdrawalFeePPM = self._withdrawalFeePPM;
        if (prevWithdrawalFeePPM == newWithdrawalFeePPM):
            return;

        self._withdrawalFeePPM = uint32(newWithdrawalFeePPM);

    '''
     * @inheritdoc INetworkSettings
    '''
    def defaultFlashLoanFeePPM(self) -> (uint):
        return self._defaultFlashLoanFeePPM.clone();

    '''
     * @dev sets the default flash-loan fee (in units of PPM)
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setDefaultFlashLoanFeePPM(self, newDefaultFlashLoanFeePPM) -> None:
        self._setDefaultFlashLoanFeePPM(newDefaultFlashLoanFeePPM);

    '''
     * @inheritdoc INetworkSettings
    '''
    def flashLoanFeePPM(self, pool) -> (uint):
        flashLoanFee = self._flashLoanFees[pool];

        return (flashLoanFee.feePPM if flashLoanFee.initialized else self._defaultFlashLoanFeePPM).clone();

    '''
     * @dev sets the flash-loan fee of a given pool
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
     * - the token must have been whitelisted
    '''
    def setFlashLoanFeePPM(self, pool, newFlashLoanFeePPM) -> None:
        if (not pool.isEqual(self._bnt) and not self._isTokenWhitelisted(pool)):
            revert("NotWhitelisted");

        prevFlashLoanFeePPM = self._flashLoanFees[pool].feePPM;
        if (prevFlashLoanFeePPM == newFlashLoanFeePPM):
            return;

        self._flashLoanFees[pool] = self.FlashLoanFee({ 'initialized': True, 'feePPM': newFlashLoanFeePPM });

    '''
     * @dev checks whether a given token is whitelisted
    '''
    def _isTokenWhitelisted(self, token) -> (bool):
        return self._protectedTokenWhitelist.contains(address(token));

    '''
     * @dev sets the default flash-loan fee (in units of PPM)
    '''
    def _setDefaultFlashLoanFeePPM(self, newDefaultFlashLoanFeePPM) -> None:
        prevDefaultFlashLoanFeePPM = self._defaultFlashLoanFeePPM;
        if (prevDefaultFlashLoanFeePPM == newDefaultFlashLoanFeePPM):
            return;

        self._defaultFlashLoanFeePPM = uint32(newDefaultFlashLoanFeePPM);
