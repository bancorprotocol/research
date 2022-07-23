from bancor_research.bancor_emulator.solidity import uint, uint8, uint16, uint32, uint128, uint256, mapping, address, payable, revert
from bancor_research.bancor_emulator.utils import contract, using, parse

from bancor_research.bancor_emulator.EnumerableSet import EnumerableSet
from bancor_research.bancor_emulator.Math import Math
from bancor_research.bancor_emulator.SafeCast import SafeCast
from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION
from bancor_research.bancor_emulator.BlockNumber import BlockNumber
from bancor_research.bancor_emulator.FractionLibrary import Fraction256, Fraction112, FractionLibrary, zeroFraction112
from bancor_research.bancor_emulator.MathEx import Sint256, MathEx
from bancor_research.bancor_emulator.PoolToken import PoolToken as IPoolToken
from bancor_research.bancor_emulator.PoolCollectionWithdrawal import PoolCollectionWithdrawal

class PoolLiquidity:
    def __init__(self, x = None) -> None:
        self.bntTradingLiquidity = parse(uint128, x, 'bntTradingLiquidity'); # the BNT trading liquidity
        self.baseTokenTradingLiquidity = parse(uint128, x, 'baseTokenTradingLiquidity'); # the base token trading liquidity
        self.stakedBalance = parse(uint256, x, 'stakedBalance'); # the staked balance

class AverageRates:
    def __init__(self, x = None) -> None:
        self.blockNumber = parse(uint32, x, 'blockNumber');
        self.rate = parse(Fraction112, x, 'rate');
        self.invRate = parse(Fraction112, x, 'invRate');

class Pool:
    def __init__(self, x = None) -> None:
        self.poolToken = parse(address, x, 'poolToken'); # the pool token of the pool
        self.tradingFeePPM = parse(uint32, x, 'tradingFeePPM'); # the trading fee (in units of PPM)
        self.tradingEnabled = parse(bool, x, 'tradingEnabled'); # whether trading is enabled
        self.depositingEnabled = parse(bool, x, 'depositingEnabled'); # whether depositing is enabled
        self.averageRates = parse(AverageRates, x, 'averageRates'); # the recent average rates
        self.liquidity = parse(PoolLiquidity, x, 'liquidity'); # the overall liquidity in the pool

class WithdrawalAmounts:
    def __init__(self, x = None) -> None:
        self.totalAmount = parse(uint256, x, 'totalAmount');
        self.baseTokenAmount = parse(uint256, x, 'baseTokenAmount');
        self.bntAmount = parse(uint256, x, 'bntAmount');

# trading enabling/disabling reasons
TRADING_STATUS_UPDATE_DEFAULT = uint8(0);
TRADING_STATUS_UPDATE_ADMIN = uint8(1);
TRADING_STATUS_UPDATE_MIN_LIQUIDITY = uint8(2);
TRADING_STATUS_UPDATE_INVALID_STATE = uint8(3);

class TradeAmountAndFee:
    def __init__(self, x = None) -> None:
        self.amount = parse(uint256, x, 'amount'); # the source/target amount (depending on the context) resulting from the trade
        self.tradingFeeAmount = parse(uint256, x, 'tradingFeeAmount'); # the trading fee amount
        self.networkFeeAmount = parse(uint256, x, 'networkFeeAmount'); # the network fee amount (always in units of BNT)

# base token withdrawal output amounts
class InternalWithdrawalAmounts:
    def __init__(self, x = None) -> None:
        self.baseTokensToTransferFromMasterVault = parse(uint256, x, 'baseTokensToTransferFromMasterVault'); # base token amount to transfer from the master vault to the provider
        self.bntToMintForProvider = parse(uint256, x, 'bntToMintForProvider'); # BNT amount to mint directly for the provider
        self.baseTokensToTransferFromEPV = parse(uint256, x, 'baseTokensToTransferFromEPV'); # base token amount to transfer from the external protection vault to the provider
        self.baseTokensTradingLiquidityDelta = parse(Sint256, x, 'baseTokensTradingLiquidityDelta'); # base token amount to add to the trading liquidity
        self.bntTradingLiquidityDelta = parse(Sint256, x, 'bntTradingLiquidityDelta'); # BNT amount to add to the trading liquidity and to the master vault
        self.bntProtocolHoldingsDelta = parse(Sint256, x, 'bntProtocolHoldingsDelta'); # BNT amount add to the protocol equity
        self.baseTokensWithdrawalFee = parse(uint256, x, 'baseTokensWithdrawalFee'); # base token amount to keep in the pool as a withdrawal fee
        self.baseTokensWithdrawalAmount = parse(uint256, x, 'baseTokensWithdrawalAmount'); # base token amount equivalent to the base pool token's withdrawal amount
        self.poolTokenAmount = parse(uint256, x, 'poolTokenAmount'); # base pool token
        self.poolTokenTotalSupply = parse(uint256, x, 'poolTokenTotalSupply'); # base pool token's total supply
        self.newBaseTokenTradingLiquidity = parse(uint256, x, 'newBaseTokenTradingLiquidity'); # new base token trading liquidity
        self.newBNTTradingLiquidity = parse(uint256, x, 'newBNTTradingLiquidity'); # new BNT trading liquidity

class TradingLiquidityAction:
    def __init__(self, x = None) -> None:
        self.update = parse(bool, x, 'update');
        self.newBNTTradingLiquidity = parse(uint256, x, 'newBNTTradingLiquidity');
        self.newBaseTokenTradingLiquidity = parse(uint256, x, 'newBaseTokenTradingLiquidity');

class PoolRateState:
    Uninitialized = 0
    Unstable = 1
    Stable = 2

'''
 * @dev Pool Collection contract
 *
 * notes:
 *
 * - the address of reserve token serves as the pool unique ID in both contract functions and events
'''
class PoolCollection(contract, BlockNumber):
    using(FractionLibrary, Fraction256);
    using(FractionLibrary, Fraction112);
    using(SafeCast, uint);

    POOL_TYPE = uint16(1);
    LIQUIDITY_GROWTH_FACTOR = uint256(2);
    BOOTSTRAPPING_LIQUIDITY_BUFFER_FACTOR = uint256(2);
    DEFAULT_TRADING_FEE_PPM = uint32(2_000); # 0.2%
    DEFAULT_NETWORK_FEE_PPM = uint32(200_000); # 20%
    RATE_MAX_DEVIATION_PPM = uint32(10_000); # %1
    RATE_RESET_BLOCK_THRESHOLD = uint32(100);

    # the average rate is recalculated based on the ratio between the weights of the rates the smaller the weights are,
    # the larger the supported range of each one of the rates is
    EMA_AVERAGE_RATE_WEIGHT = uint256(4);
    EMA_SPOT_RATE_WEIGHT = uint256(1);

    class TradeIntermediateResult:
        def __init__(self, x = None) -> None:
            self.sourceAmount = parse(uint256, x, 'sourceAmount');
            self.targetAmount = parse(uint256, x, 'targetAmount');
            self.limit = parse(uint256, x, 'limit');
            self.tradingFeeAmount = parse(uint256, x, 'tradingFeeAmount');
            self.networkFeeAmount = parse(uint256, x, 'networkFeeAmount');
            self.sourceBalance = parse(uint256, x, 'sourceBalance');
            self.targetBalance = parse(uint256, x, 'targetBalance');
            self.stakedBalance = parse(uint256, x, 'stakedBalance');
            self.pool = parse(address, x, 'pool');
            self.isSourceBNT = parse(bool, x, 'isSourceBNT');
            self.bySourceAmount = parse(bool, x, 'bySourceAmount');
            self.tradingFeePPM = parse(uint32, x, 'stakedBalance');
            self.contextId = parse(uint256, x, 'sourceAmount');

    class TradeAmountAndTradingFee:
        def __init__(self, x = None) -> None:
            self.amount = parse(uint256, x, 'amount');
            self.tradingFeeAmount = parse(uint256, x, 'tradingFeeAmount');

    '''
     * @dev initializes a new PoolCollection contract
    '''
    def __init__(self,
        initNetwork,
        initBNT,
        initNetworkSettings,
        initMasterVault,
        initBNTPool,
        initExternalProtectionVault,
        initPoolTokenFactory,
        initPoolMigrator
    ) -> None:
        contract.__init__(self)
        BlockNumber.__init__(self)

        self._network = initNetwork;
        self._bnt = initBNT;
        self._networkSettings = initNetworkSettings;
        self._masterVault = initMasterVault;
        self._bntPool = initBNTPool;
        self._externalProtectionVault = initExternalProtectionVault;
        self._poolTokenFactory = initPoolTokenFactory;
        self._poolMigrator = initPoolMigrator;

        # a mapping between tokens and their pools
        self._poolData = mapping(lambda: Pool());

        # the set of all pools which are managed by this pool collection
        self._pools = EnumerableSet();

        # the default trading fee (in units of PPM)
        self._defaultTradingFeePPM = uint32();

        # true if protection is enabled, false otherwise
        self._protectionEnabled = True;

        # the global network fee (in units of PPM)
        self._networkFeePPM = uint32();

        self._setDefaultTradingFeePPM(self.DEFAULT_TRADING_FEE_PPM);
        self._setNetworkFeePPM(self.DEFAULT_NETWORK_FEE_PPM);

    '''
     * @inheritdoc IVersioned
    '''
    def version(self) -> (int):
        return 9;

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolType(self) -> (uint):
        return self.POOL_TYPE.clone();

    '''
     * @inheritdoc IPoolCollection
    '''
    def defaultTradingFeePPM(self) -> (uint):
        return self._defaultTradingFeePPM.clone();

    '''
     * @inheritdoc IPoolCollection
    '''
    def networkFeePPM(self) -> (uint):
        return self._networkFeePPM.clone();

    '''
     * @inheritdoc IPoolCollection
    '''
    def pools(self) -> (list):
        return self._pools.values();

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolCount(self) -> (int):
        return self._pools.length();

    '''
     * @dev sets the default trading fee (in units of PPM)
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def setDefaultTradingFeePPM(self, newDefaultTradingFeePPM) -> None:
        self._setDefaultTradingFeePPM(newDefaultTradingFeePPM);

    '''
     * @dev sets the network fee (in units of PPM)
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def setNetworkFeePPM(self, newNetworkFeePPM) -> None:
        self._setNetworkFeePPM(newNetworkFeePPM);

    '''
     * @dev enables/disables protection
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def enableProtection(self, status) -> None:
        if (self._protectionEnabled == status):
            return;

        self._protectionEnabled = status;

    '''
     * @dev returns the status of the protection
    '''
    def protectionEnabled(self) -> (bool):
        return self._protectionEnabled;

    '''
     * @inheritdoc IPoolCollection
    '''
    def createPool(self, token):
        if (not self._networkSettings.isTokenWhitelisted(token)):
            revert("NotWhitelisted");

        newPoolToken = self._poolTokenFactory.createPoolToken(token);

        newPoolToken.acceptOwnership();

        newPool = Pool({
            'poolToken': newPoolToken,
            'tradingFeePPM': self._defaultTradingFeePPM,
            'tradingEnabled': False,
            'depositingEnabled': True,
            'averageRates': AverageRates({ 'blockNumber': 0, 'rate': zeroFraction112(), 'invRate': zeroFraction112() }),
            'liquidity': PoolLiquidity({ 'bntTradingLiquidity': 0, 'baseTokenTradingLiquidity': 0, 'stakedBalance': 0 })
        });

        self._addPool(token, newPool);

    '''
     * @inheritdoc IPoolCollection
    '''
    def isPoolValid(self, pool) -> (bool):
        return address(self._poolData[pool].poolToken) != address(0);

    '''
     * @dev returns specific pool's data
     *
     * notes:
     *
     * - there is no guarantee that this function will remains forward compatible, so please avoid relying on it and
     *   rely on specific getters from the IPoolCollection interface instead
    '''
    def poolData(self, pool) -> (Pool):
        return self._poolData[pool];

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolLiquidity(self, pool) -> (PoolLiquidity):
        return self._poolData[pool].liquidity;

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolToken(self, pool) -> (IPoolToken):
        return self._poolData[pool].poolToken;

    '''
     * @inheritdoc IPoolCollection
    '''
    def tradingFeePPM(self, pool) -> (uint):
        return self._poolData[pool].tradingFeePPM.clone();

    '''
     * @inheritdoc IPoolCollection
    '''
    def tradingEnabled(self, pool) -> (bool):
        return self._poolData[pool].tradingEnabled;

    '''
     * @inheritdoc IPoolCollection
    '''
    def depositingEnabled(self, pool) -> (bool):
        return self._poolData[pool].depositingEnabled;

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolTokenToUnderlying(self, pool, poolTokenAmount) -> (uint):
        data = self._poolData[pool];

        return self._poolTokenToUnderlying(poolTokenAmount, data.poolToken.totalSupply(), data.liquidity.stakedBalance);

    '''
     * @inheritdoc IPoolCollection
    '''
    def underlyingToPoolToken(self, pool, baseTokenAmount) -> (uint):
        data = self._poolData[pool];

        return self._underlyingToPoolToken(baseTokenAmount, data.poolToken.totalSupply(), data.liquidity.stakedBalance);

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolTokenAmountToBurn(self,
        pool,
        baseTokenAmountToDistribute,
        protocolPoolTokenAmount
    ) -> (uint):
        if (baseTokenAmountToDistribute == 0):
            return uint256(0);

        data = self._poolData[pool];

        poolTokenSupply = data.poolToken.totalSupply();
        val = baseTokenAmountToDistribute * poolTokenSupply;

        return \
            MathEx.mulDivF(
                val,
                poolTokenSupply,
                val + data.liquidity.stakedBalance * (poolTokenSupply - protocolPoolTokenAmount)
            );

    '''
     * @inheritdoc IPoolCollection
    '''
    def isPoolStable(self, pool) -> (bool):
        data = self._poolData[pool];

        return self._poolRateState(data) == PoolRateState.Stable;

    '''
     * @dev sets the trading fee of a given pool
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def setTradingFeePPM(self, pool, newTradingFeePPM) -> None:
        data = self._poolStorage(pool);

        prevTradingFeePPM = data.tradingFeePPM;
        if (prevTradingFeePPM == newTradingFeePPM):
            return;

        data.tradingFeePPM = uint32(newTradingFeePPM);

    '''
     * @dev enables trading in a given pool, by providing the funding rate as two virtual balances, and updates its
     * trading liquidity
     *
     * please note that the virtual balances should be derived from token prices, normalized to the smallest unit of
     * tokens. In other words, the ratio between BNT and TKN virtual balances should be the ratio between the $ value
     * of 1 wei of TKN and 1 wei of BNT, taking both of their decimals into account. For example:
     *
     * - if the price of one (10**18 wei) BNT is $X and the price of one (10**18 wei) TKN is $Y, then the virtual balances
     *   should represent a ratio of X to Y
     * - if the price of one (10**18 wei) BNT is $X and the price of one (10**6 wei) USDC is $Y, then the virtual balances
     *   should represent a ratio of X to Y*10**12
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def enableTrading(self,
        pool,
        bntVirtualBalance,
        baseTokenVirtualBalance
    ) -> None:
        fundingRate = Fraction256({ 'n': bntVirtualBalance, 'd': baseTokenVirtualBalance });
        self._validRate(fundingRate);

        data = self._poolStorage(pool);

        if (data.tradingEnabled):
            revert("AlreadyEnabled");

        # adjust the trading liquidity based on the base token vault balance and funding limits
        contextId = uint256(0);
        minLiquidityForTrading = self._networkSettings.minLiquidityForTrading();
        self._updateTradingLiquidity(contextId, pool, data, fundingRate, minLiquidityForTrading);

        # verify that the BNT trading liquidity is equal or greater than the minimum liquidity for trading
        if (data.liquidity.bntTradingLiquidity < minLiquidityForTrading):
            revert("InsufficientLiquidity");

        fundingRate112 = fundingRate.toFraction112();
        data.averageRates = AverageRates({
            'blockNumber': self._blockNumber(),
            'rate': fundingRate112,
            'invRate': fundingRate112.inverse()
        });

        data.tradingEnabled = True;

    '''
     * @dev disables trading in a given pool
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def disableTrading(self, pool) -> None:
        data = self._poolStorage(pool);

        self._resetTradingLiquidity(uint256(0), pool, data, TRADING_STATUS_UPDATE_ADMIN);

    '''
     * @dev adjusts the trading liquidity in the given pool based on the base token
     * vault balance/funding limit
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def updateTradingLiquidity(self, pool) -> None:
        data = self._poolStorage(pool);
        liquidity = data.liquidity;

        contextId = uint256(0);

        effectiveAverageRates = self._effectiveAverageRates(
            data.averageRates,
            Fraction256({ 'n': liquidity.bntTradingLiquidity, 'd': liquidity.baseTokenTradingLiquidity })
        );
        minLiquidityForTrading = self._networkSettings.minLiquidityForTrading();
        self._updateTradingLiquidity(
            contextId,
            pool,
            data,
            effectiveAverageRates.rate.fromFraction112(),
            minLiquidityForTrading
        );

        self._dispatchTradingLiquidityEvents(contextId, pool, data.poolToken.totalSupply(), liquidity, data.liquidity);

    '''
     * @dev enables/disables depositing into a given pool
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
    '''
    def enableDepositing(self, pool, status) -> None:
        data = self._poolStorage(pool);

        if (data.depositingEnabled == status):
            return;

        data.depositingEnabled = status;

    '''
     * @inheritdoc IPoolCollection
    '''
    def depositFor(self,
        contextId,
        provider,
        pool,
        baseTokenAmount
    ) -> (uint):
        data = self._poolStorage(pool);

        if (not data.depositingEnabled):
            revert("DepositingDisabled");

        prevLiquidity = data.liquidity;
        currentStakedBalance = prevLiquidity.stakedBalance;

        # if there are no pool tokens available to support the staked balance - reset the
        # trading liquidity and the staked balance
        # in addition, get the effective average rates
        prevPoolTokenTotalSupply = data.poolToken.totalSupply();
        if (prevPoolTokenTotalSupply == 0 and currentStakedBalance != 0):
            currentStakedBalance = uint256(0);

            self._resetTradingLiquidity(contextId, pool, data, TRADING_STATUS_UPDATE_INVALID_STATE);
            effectiveAverageRates = AverageRates({
                'blockNumber': 0,
                'rate': zeroFraction112(),
                'invRate': zeroFraction112()
            });
        else:
            effectiveAverageRates = self._effectiveAverageRates(
                data.averageRates,
                Fraction256({ 'n': prevLiquidity.bntTradingLiquidity, 'd': prevLiquidity.baseTokenTradingLiquidity })
            );

        # calculate the pool token amount to mint
        poolTokenAmount = self._underlyingToPoolToken(
            baseTokenAmount,
            prevPoolTokenTotalSupply,
            currentStakedBalance
        );

        # update the staked balance with the full base token amount
        data.liquidity.stakedBalance = currentStakedBalance + baseTokenAmount;

        # mint pool tokens to the provider
        data.poolToken.mint(provider, poolTokenAmount);

        # adjust the trading liquidity based on the base token vault balance and funding limits
        self._updateTradingLiquidity(
            contextId,
            pool,
            data,
            effectiveAverageRates.rate.fromFraction112(),
            self._networkSettings.minLiquidityForTrading()
        );

        # if trading is enabled, then update the recent average rates
        if (data.tradingEnabled):
            self._updateAverageRates(
                data,
                Fraction256({ 'n': data.liquidity.bntTradingLiquidity, 'd': data.liquidity.baseTokenTradingLiquidity })
            );

        self._dispatchTradingLiquidityEvents(
            contextId,
            pool,
            prevPoolTokenTotalSupply + poolTokenAmount,
            prevLiquidity,
            data.liquidity
        );

        return poolTokenAmount;

    '''
     * @inheritdoc IPoolCollection
    '''
    def withdraw(self,
        contextId,
        provider,
        pool,
        poolTokenAmount,
        baseTokenAmount
    ) -> (uint):
        data = self._poolStorage(pool);
        liquidity = data.liquidity;

        poolTokenTotalSupply = data.poolToken.totalSupply();
        underlyingAmount = self._poolTokenToUnderlying(
            poolTokenAmount,
            poolTokenTotalSupply,
            liquidity.stakedBalance
        );

        if (baseTokenAmount > underlyingAmount):
            revert("InvalidParam");

        if (self._poolRateState(data) == PoolRateState.Unstable):
            revert("RateUnstable");

        # obtain the withdrawal amounts
        amounts = self._poolWithdrawalAmounts(
            pool,
            poolTokenAmount,
            baseTokenAmount,
            liquidity,
            data.tradingFeePPM,
            poolTokenTotalSupply
        );

        # execute the actual withdrawal
        self._executeWithdrawal(contextId, provider, pool, data, amounts);

        # if trading is enabled, then update the recent average rates
        if (data.tradingEnabled):
            self._updateAverageRates(
                data,
                Fraction256({ 'n': data.liquidity.bntTradingLiquidity, 'd': data.liquidity.baseTokenTradingLiquidity })
            );

        return amounts.baseTokensToTransferFromMasterVault;

    '''
     * @inheritdoc IPoolCollection
    '''
    def withdrawalAmounts(self, pool, poolTokenAmount) -> (WithdrawalAmounts):
        data = self._poolData[pool];
        liquidity = data.liquidity;

        poolTokenTotalSupply = data.poolToken.totalSupply();
        underlyingAmount = self._poolTokenToUnderlying(
            poolTokenAmount,
            poolTokenTotalSupply,
            liquidity.stakedBalance
        );

        amounts = self._poolWithdrawalAmounts(
            pool,
            poolTokenAmount,
            underlyingAmount,
            liquidity,
            data.tradingFeePPM,
            poolTokenTotalSupply
        );

        return \
            WithdrawalAmounts({
                'totalAmount': amounts.baseTokensWithdrawalAmount - amounts.baseTokensWithdrawalFee,
                'baseTokenAmount': amounts.baseTokensToTransferFromMasterVault + amounts.baseTokensToTransferFromEPV,
                'bntAmount': amounts.bntToMintForProvider if self._protectionEnabled else 0
            });

    '''
     * @inheritdoc IPoolCollection
    '''
    def tradeBySourceAmount(self,
        contextId,
        sourceToken,
        targetToken,
        sourceAmount,
        minReturnAmount
    ) -> (TradeAmountAndFee):
        result = self._initTrade(
            contextId,
            sourceToken,
            targetToken,
            sourceAmount,
            minReturnAmount,
            True
        );

        self._performTrade(result);

        return \
            TradeAmountAndFee({
                'amount': result.targetAmount,
                'tradingFeeAmount': result.tradingFeeAmount,
                'networkFeeAmount': result.networkFeeAmount
            });

    '''
     * @inheritdoc IPoolCollection
    '''
    def tradeByTargetAmount(self,
        contextId,
        sourceToken,
        targetToken,
        targetAmount,
        maxSourceAmount
    ) -> (TradeAmountAndFee):
        result = self._initTrade(
            contextId,
            sourceToken,
            targetToken,
            targetAmount,
            maxSourceAmount,
            False
        );

        self._performTrade(result);

        return \
            TradeAmountAndFee({
                'amount': result.sourceAmount,
                'tradingFeeAmount': result.tradingFeeAmount,
                'networkFeeAmount': result.networkFeeAmount
            });

    '''
     * @inheritdoc IPoolCollection
    '''
    def tradeOutputAndFeeBySourceAmount(self,
        sourceToken,
        targetToken,
        sourceAmount
    ) -> (TradeAmountAndFee):
        result = self._initTrade(uint256(0), sourceToken, targetToken, sourceAmount, 1, True);

        self._processTrade(result);

        return \
            TradeAmountAndFee({
                'amount': result.targetAmount,
                'tradingFeeAmount': result.tradingFeeAmount,
                'networkFeeAmount': result.networkFeeAmount
            });

    '''
     * @inheritdoc IPoolCollection
    '''
    def tradeInputAndFeeByTargetAmount(self,
        sourceToken,
        targetToken,
        targetAmount
    ) -> (TradeAmountAndFee):
        result = self._initTrade(
            uint256(0),
            sourceToken,
            targetToken,
            targetAmount,
            type(uint256).max,
            False
        );

        self._processTrade(result);

        return \
            TradeAmountAndFee({
                'amount': result.sourceAmount,
                'tradingFeeAmount': result.tradingFeeAmount,
                'networkFeeAmount': result.networkFeeAmount
            });

    '''
     * @inheritdoc IPoolCollection
    '''
    def onFeesCollected(self, pool, feeAmount) -> None:
        if (feeAmount == 0):
            return;

        data = self._poolStorage(pool);

        # increase the staked balance by the given amount
        data.liquidity.stakedBalance += feeAmount;

    '''
     * @inheritdoc IPoolCollection
    '''
    def migratePoolIn(self, pool, data) -> None:
        self._addPool(pool, data);

        data.poolToken.acceptOwnership();

    '''
     * @inheritdoc IPoolCollection
    '''
    def migratePoolOut(self, pool, targetPoolCollection) -> None:
        cachedPoolToken = self._poolData[pool].poolToken;

        self._removePool(pool);

        cachedPoolToken.transferOwnership(address(targetPoolCollection));

    '''
     * @dev adds a pool
    '''
    def _addPool(self, pool, data) -> None:
        if (not self._pools.add(address(pool))):
            revert("AlreadyExists");

        self._poolData[pool] = data;

    '''
     * @dev removes a pool
    '''
    def _removePool(self, pool) -> None:
        if (not self._pools.remove(address(pool))):
            revert("DoesNotExist");

        del self._poolData[pool];

    '''
     * @dev returns withdrawal amounts
    '''
    def _poolWithdrawalAmounts(self,
        pool,
        poolTokenAmount,
        baseTokensWithdrawalAmount,
        liquidity,
        poolTradingFeePPM,
        poolTokenTotalSupply
    ) -> (InternalWithdrawalAmounts):
        # the base token trading liquidity of a given pool can never be higher than the base token balance of the vault
        # whenever the base token trading liquidity is updated, it is set to at most the base token balance of the vault
        baseTokenExcessAmount = pool.balanceOf(address(self._masterVault)) - liquidity.baseTokenTradingLiquidity;

        output = PoolCollectionWithdrawal.calculateWithdrawalAmounts(
            liquidity.bntTradingLiquidity,
            liquidity.baseTokenTradingLiquidity,
            baseTokenExcessAmount,
            liquidity.stakedBalance,
            pool.balanceOf(address(self._externalProtectionVault)),
            poolTradingFeePPM,
            self._networkSettings.withdrawalFeePPM(),
            baseTokensWithdrawalAmount
        );

        return \
            InternalWithdrawalAmounts({
                'baseTokensToTransferFromMasterVault': output.s,
                'bntToMintForProvider': output.t,
                'baseTokensToTransferFromEPV': output.u,
                'baseTokensTradingLiquidityDelta': output.r,
                'bntTradingLiquidityDelta': output.p,
                'bntProtocolHoldingsDelta': output.q,
                'baseTokensWithdrawalFee': output.v,
                'baseTokensWithdrawalAmount': baseTokensWithdrawalAmount,
                'poolTokenAmount': poolTokenAmount,
                'poolTokenTotalSupply': poolTokenTotalSupply,
                'newBaseTokenTradingLiquidity':
                    liquidity.baseTokenTradingLiquidity - output.r.value if output.r.isNeg else
                    liquidity.baseTokenTradingLiquidity + output.r.value,
                'newBNTTradingLiquidity':
                    liquidity.bntTradingLiquidity - output.p.value if output.p.isNeg else
                    liquidity.bntTradingLiquidity + output.p.value
            });

    '''
     * @dev executes the following actions:
     *
     * - burn the network's base pool tokens
     * - update the pool's base token staked balance
     * - update the pool's base token trading liquidity
     * - update the pool's BNT trading liquidity
     * - update the pool's trading liquidity product
     * - emit an event if the pool's BNT trading liquidity has crossed the minimum threshold
     *   (either above the threshold or below the threshold)
    '''
    def _executeWithdrawal(self,
        contextId,
        provider,
        pool,
        data,
        amounts
    ) -> None:
        liquidity = data.liquidity;
        prevLiquidity = liquidity;

        data.poolToken.burn(amounts.poolTokenAmount);

        newPoolTokenTotalSupply = amounts.poolTokenTotalSupply - amounts.poolTokenAmount;

        liquidity.stakedBalance = MathEx.mulDivF(
            liquidity.stakedBalance,
            newPoolTokenTotalSupply,
            amounts.poolTokenTotalSupply
        );

        # trading liquidity is assumed to never exceed 128 bits (the cast below will revert("otherwise)
        liquidity.baseTokenTradingLiquidity = amounts.newBaseTokenTradingLiquidity.toUint128();
        liquidity.bntTradingLiquidity = amounts.newBNTTradingLiquidity.toUint128();

        if (amounts.bntProtocolHoldingsDelta.value > 0):
            assert(amounts.bntProtocolHoldingsDelta.isNeg); # currently no support for requesting funding here

            self._bntPool.renounceFunding(contextId, pool, amounts.bntProtocolHoldingsDelta.value);
        elif (amounts.bntTradingLiquidityDelta.value > 0):
            if (amounts.bntTradingLiquidityDelta.isNeg):
                self._bntPool.burnFromVault(amounts.bntTradingLiquidityDelta.value);
            else:
                self._bntPool.mint(address(self._masterVault), amounts.bntTradingLiquidityDelta.value);

        # if the provider should receive some BNT - ask the BNT pool to mint BNT to the provider
        isProtectionEnabled = self._protectionEnabled;
        if (amounts.bntToMintForProvider > 0 and isProtectionEnabled):
            self._bntPool.mint(address(provider), amounts.bntToMintForProvider);

        # if the provider should receive some base tokens from the external protection vault - remove the tokens from
        # the external protection vault and send them to the master vault
        if (amounts.baseTokensToTransferFromEPV > 0):
            self._externalProtectionVault.withdrawFunds(
                pool,
                payable(address(self._masterVault)),
                amounts.baseTokensToTransferFromEPV
            );
            amounts.baseTokensToTransferFromMasterVault += amounts.baseTokensToTransferFromEPV;

        # if the provider should receive some base tokens from the master vault - remove the tokens from the master
        # vault and send them to the provider
        if (amounts.baseTokensToTransferFromMasterVault > 0):
            self._masterVault.withdrawFunds(pool, payable(provider), amounts.baseTokensToTransferFromMasterVault);

        # ensure that the average rate is reset when the pool is being emptied
        if (amounts.newBaseTokenTradingLiquidity == 0):
            data.averageRates.rate = zeroFraction112();
            data.averageRates.invRate = zeroFraction112();

        # if the new BNT trading liquidity is below the minimum liquidity for trading - reset the liquidity
        if (amounts.newBNTTradingLiquidity < self._networkSettings.minLiquidityForTrading()):
            self._resetTradingLiquidity_(
                contextId,
                pool,
                data,
                amounts.newBNTTradingLiquidity,
                TRADING_STATUS_UPDATE_MIN_LIQUIDITY
            );

        self._dispatchTradingLiquidityEvents(contextId, pool, newPoolTokenTotalSupply, prevLiquidity, data.liquidity);

    '''
     * @dev sets the default trading fee (in units of PPM)
    '''
    def _setDefaultTradingFeePPM(self, newDefaultTradingFeePPM) -> None:
        prevDefaultTradingFeePPM = self._defaultTradingFeePPM;
        if (prevDefaultTradingFeePPM == newDefaultTradingFeePPM):
            return;

        self._defaultTradingFeePPM = uint32(newDefaultTradingFeePPM);

    '''
     * @dev sets the network fee (in units of PPM)
    '''
    def _setNetworkFeePPM(self, newNetworkFeePPM) -> None:
        prevNetworkFeePPM = self._networkFeePPM;
        if (prevNetworkFeePPM == newNetworkFeePPM):
            return;

        self._networkFeePPM = uint32(newNetworkFeePPM);

    '''
     * @dev returns a storage reference to pool data
    '''
    def _poolStorage(self, pool) -> (Pool):
        data = self._poolData[pool];
        if (address(data.poolToken) == address(0)):
            revert("DoesNotExist");

        return data;

    '''
     * @dev calculates base tokens amount
    '''
    def _poolTokenToUnderlying(self,
        poolTokenAmount,
        poolTokenSupply,
        stakedBalance
    ) -> (uint):
        if (poolTokenSupply == 0):
            # if this is the initial liquidity provision - use a one-to-one pool token to base token rate
            if (stakedBalance > 0):
                revert("InvalidStakedBalance");

            return poolTokenAmount;

        return MathEx.mulDivF(poolTokenAmount, stakedBalance, poolTokenSupply);

    '''
     * @dev calculates pool tokens amount
    '''
    def _underlyingToPoolToken(self,
        baseTokenAmount,
        poolTokenSupply,
        stakedBalance
    ) -> (uint):
        if (poolTokenSupply == 0):
            # if this is the initial liquidity provision - use a one-to-one pool token to base token rate
            if (stakedBalance > 0):
                revert("InvalidStakedBalance");

            return baseTokenAmount;

        return MathEx.mulDivC(baseTokenAmount, poolTokenSupply, stakedBalance);

    '''
     * @dev calculates the target trading liquidities, taking into account the total out-of-curve base token liquidity,
     * and the deltas between the new and the previous states
    '''
    def _calcTargetTradingLiquidity(self,
        totalBaseTokenReserveAmount,
        availableFunding,
        liquidity,
        fundingRate,
        minLiquidityForTrading
    ) -> (TradingLiquidityAction):
        # calculate the target BNT trading liquidity delta based on the smaller between the following:
        # - BNT liquidity required to match the total out-of-curve based token liquidity
        # - available BNT funding
        totalTokenDeltaAmount = totalBaseTokenReserveAmount - liquidity.baseTokenTradingLiquidity;
        targetBNTTradingLiquidityDelta = Math.min(
            MathEx.mulDivF(totalTokenDeltaAmount, fundingRate.n, fundingRate.d),
            availableFunding
        );
        targetBNTTradingLiquidity = liquidity.bntTradingLiquidity + targetBNTTradingLiquidityDelta;

        # ensure that the target is above the minimum liquidity for trading
        if (targetBNTTradingLiquidity < minLiquidityForTrading):
            return TradingLiquidityAction({ 'update': True, 'newBNTTradingLiquidity': 0, 'newBaseTokenTradingLiquidity': 0 });

        # calculate the new BNT trading liquidity and cap it by the growth factor
        if (liquidity.bntTradingLiquidity == 0):
            # if the current BNT trading liquidity is 0, set it to the minimum liquidity for trading (with an
            # additional buffer so that initial trades will be less likely to trigger disabling of trading)
            newTargetBNTTradingLiquidity = minLiquidityForTrading * self.BOOTSTRAPPING_LIQUIDITY_BUFFER_FACTOR;

            # ensure that we're not allocating more than the previously established limits
            if (newTargetBNTTradingLiquidity > targetBNTTradingLiquidity):
                return \
                    TradingLiquidityAction({
                        'update': False,
                        'newBNTTradingLiquidity': 0,
                        'newBaseTokenTradingLiquidity': 0
                    });

            targetBNTTradingLiquidity = newTargetBNTTradingLiquidity;
        elif (targetBNTTradingLiquidity >= liquidity.bntTradingLiquidity):
            # if the target is above the current trading liquidity, limit it by factoring the current value up. Please
            # note that if the target is below the current trading liquidity - it will be reduced to it immediately
            targetBNTTradingLiquidity = Math.min(
                targetBNTTradingLiquidity,
                liquidity.bntTradingLiquidity * self.LIQUIDITY_GROWTH_FACTOR
            );

        # calculate the base token trading liquidity based on the delta between the new and the previous BNT trading
        # liquidity and the effective funding rate (please note that the effective funding rate is always the rate
        # between BNT and the base token)
        bntTradingLiquidityDelta = targetBNTTradingLiquidity - liquidity.bntTradingLiquidity;
        baseTokenTradingLiquidityDelta = \
            uint256(0) if bntTradingLiquidityDelta == 0 else \
            MathEx.mulDivF(bntTradingLiquidityDelta, fundingRate.d, fundingRate.n);

        return \
            TradingLiquidityAction({
                'update': True,
                'newBNTTradingLiquidity': targetBNTTradingLiquidity,
                'newBaseTokenTradingLiquidity': liquidity.baseTokenTradingLiquidity + baseTokenTradingLiquidityDelta
            });

    '''
     * @dev adjusts the trading liquidity based on the newly added tokens delta amount, and funding limits
    '''
    def _updateTradingLiquidity(self,
        contextId,
        pool,
        data,
        fundingRate,
        minLiquidityForTrading
    ) -> None:
        # ensure that the base token reserve isn't empty
        totalBaseTokenReserveAmount = pool.balanceOf(address(self._masterVault));
        if (totalBaseTokenReserveAmount == 0):
            revert("InsufficientLiquidity");

        liquidity = data.liquidity;

        if (self._poolRateState(data) == PoolRateState.Unstable):
            return;

        if (not fundingRate.isPositive()):
            self._resetTradingLiquidity(contextId, pool, data, TRADING_STATUS_UPDATE_MIN_LIQUIDITY);

            return;

        action = self._calcTargetTradingLiquidity(
            totalBaseTokenReserveAmount,
            self._bntPool.availableFunding(pool),
            liquidity,
            fundingRate,
            minLiquidityForTrading
        );

        if (not action.update):
            return;

        if (action.newBNTTradingLiquidity == 0 or action.newBaseTokenTradingLiquidity == 0):
            self._resetTradingLiquidity(contextId, pool, data, TRADING_STATUS_UPDATE_MIN_LIQUIDITY);

            return;

        # update funding from the BNT pool
        if (action.newBNTTradingLiquidity > liquidity.bntTradingLiquidity):
            self._bntPool.requestFunding(contextId, pool, action.newBNTTradingLiquidity - liquidity.bntTradingLiquidity);
        elif (action.newBNTTradingLiquidity < liquidity.bntTradingLiquidity):
            self._bntPool.renounceFunding(contextId, pool, liquidity.bntTradingLiquidity - action.newBNTTradingLiquidity);

        # trading liquidity is assumed to never exceed 128 bits (the cast below will revert("otherwise)
        newLiquidity = PoolLiquidity({
            'bntTradingLiquidity': action.newBNTTradingLiquidity.toUint128(),
            'baseTokenTradingLiquidity': action.newBaseTokenTradingLiquidity.toUint128(),
            'stakedBalance': liquidity.stakedBalance
        });

        # update the liquidity data of the pool
        data.liquidity = newLiquidity;

        self._dispatchTradingLiquidityEvents(contextId, pool, data.poolToken.totalSupply(), liquidity, newLiquidity);

    def _dispatchTradingLiquidityEvents_(self,
        contextId,
        pool,
        prevLiquidity,
        newLiquidity
    ) -> None:
        if (newLiquidity.bntTradingLiquidity != prevLiquidity.bntTradingLiquidity):
            pass

        if (newLiquidity.baseTokenTradingLiquidity != prevLiquidity.baseTokenTradingLiquidity):
            pass

    def _dispatchTradingLiquidityEvents(self,
        contextId,
        pool,
        poolTokenTotalSupply,
        prevLiquidity,
        newLiquidity
    ) -> None:
        self._dispatchTradingLiquidityEvents_(contextId, pool, prevLiquidity, newLiquidity);

        if (newLiquidity.stakedBalance != prevLiquidity.stakedBalance):
            pass

    '''
     * @dev resets trading liquidity and renounces any remaining BNT funding
    '''
    def _resetTradingLiquidity(self,
        contextId,
        pool,
        data,
        reason
    ) -> None:
        self._resetTradingLiquidity_(contextId, pool, data, data.liquidity.bntTradingLiquidity, reason);

    '''
     * @dev resets trading liquidity and renounces any remaining BNT funding
    '''
    def _resetTradingLiquidity_(self,
        contextId,
        pool,
        data,
        currentBNTTradingLiquidity,
        reason
    ) -> None:
        # reset the network and base token trading liquidities
        data.liquidity.bntTradingLiquidity = uint128(0);
        data.liquidity.baseTokenTradingLiquidity = uint128(0);

        # reset the recent average rage
        data.averageRates = AverageRates({ 'blockNumber': 0, 'rate': zeroFraction112(), 'invRate': zeroFraction112() });

        # ensure that trading is disabled
        if (data.tradingEnabled):
            data.tradingEnabled = False;

        # renounce all network liquidity
        if (currentBNTTradingLiquidity > 0):
            self._bntPool.renounceFunding(contextId, pool, currentBNTTradingLiquidity);

    '''
     * @dev returns initial trading params
    '''
    def _initTrade(self,
        contextId,
        sourceToken,
        targetToken,
        amount,
        limit,
        bySourceAmount
    ) -> (TradeIntermediateResult):
        result = self.TradeIntermediateResult()

        # ensure that BNT is either the source or the target token
        isSourceBNT = sourceToken is (self._bnt);
        isTargetBNT = targetToken is (self._bnt);

        if (isSourceBNT and not isTargetBNT):
            result.isSourceBNT = True;
            result.pool = targetToken;
        elif (not isSourceBNT and isTargetBNT):
            result.isSourceBNT = False;
            result.pool = sourceToken;
        else:
            # BNT isn't one of the tokens or is both of them
            revert("DoesNotExist");

        data = self._poolStorage(result.pool);

        # verify that trading is enabled
        if (not data.tradingEnabled):
            revert("TradingDisabled");

        result.contextId = contextId;
        result.bySourceAmount = bySourceAmount;

        if (result.bySourceAmount):
            result.sourceAmount = amount;
        else:
            result.targetAmount = amount;

        result.limit = limit;
        result.tradingFeePPM = data.tradingFeePPM;

        liquidity = data.liquidity;
        if (result.isSourceBNT):
            result.sourceBalance = uint256(liquidity.bntTradingLiquidity);
            result.targetBalance = uint256(liquidity.baseTokenTradingLiquidity);
        else:
            result.sourceBalance = uint256(liquidity.baseTokenTradingLiquidity);
            result.targetBalance = uint256(liquidity.bntTradingLiquidity);

        result.stakedBalance = liquidity.stakedBalance;

        return result

    '''
     * @dev returns trade amount and fee by providing the source amount
    '''
    def _tradeAmountAndFeeBySourceAmount(self,
        sourceBalance,
        targetBalance,
        feePPM,
        sourceAmount
    ) -> (TradeAmountAndTradingFee):
        if (sourceBalance == 0 or targetBalance == 0):
            revert("InsufficientLiquidity");

        targetAmount = MathEx.mulDivF(targetBalance, sourceAmount, sourceBalance + sourceAmount);
        tradingFeeAmount = MathEx.mulDivF(targetAmount, feePPM, PPM_RESOLUTION);

        return \
            self.TradeAmountAndTradingFee({ 'amount': targetAmount - tradingFeeAmount, 'tradingFeeAmount': tradingFeeAmount });

    '''
     * @dev returns trade amount and fee by providing either the target amount
    '''
    def _tradeAmountAndFeeByTargetAmount(self,
        sourceBalance,
        targetBalance,
        feePPM,
        targetAmount
    ) -> (TradeAmountAndTradingFee):
        if (sourceBalance == 0):
            revert("InsufficientLiquidity");

        tradingFeeAmount = MathEx.mulDivF(targetAmount, feePPM, PPM_RESOLUTION - feePPM);
        fullTargetAmount = targetAmount + tradingFeeAmount;
        sourceAmount = MathEx.mulDivF(sourceBalance, fullTargetAmount, targetBalance - fullTargetAmount);

        return self.TradeAmountAndTradingFee({ 'amount': sourceAmount, 'tradingFeeAmount': tradingFeeAmount });

    '''
     * @dev processes a trade by providing either the source or the target amount and updates the in-memory intermediate
     * result
    '''
    def _processTrade(self, result) -> None:
        tradeAmountAndFee = self.TradeAmountAndTradingFee();

        if (result.bySourceAmount):
            tradeAmountAndFee = self._tradeAmountAndFeeBySourceAmount(
                result.sourceBalance,
                result.targetBalance,
                result.tradingFeePPM,
                result.sourceAmount
            );

            result.targetAmount = tradeAmountAndFee.amount;

            # ensure that the target amount is above the requested minimum return amount
            if (result.targetAmount < result.limit):
                revert("InsufficientTargetAmount");
        else:
            tradeAmountAndFee = self._tradeAmountAndFeeByTargetAmount(
                result.sourceBalance,
                result.targetBalance,
                result.tradingFeePPM,
                result.targetAmount
            );

            result.sourceAmount = tradeAmountAndFee.amount;

            # ensure that the user has provided enough tokens to make the trade
            if (result.sourceAmount == 0 or result.sourceAmount > result.limit):
                revert("InsufficientSourceAmount");

        result.tradingFeeAmount = tradeAmountAndFee.tradingFeeAmount;

        # sync the trading and staked balance
        result.sourceBalance += result.sourceAmount;
        result.targetBalance -= result.targetAmount;

        if (result.isSourceBNT):
            result.stakedBalance += result.tradingFeeAmount;

        self._processNetworkFee(result);

    '''
     * @dev processes the network fee and updates the in-memory intermediate result
    '''
    def _processNetworkFee(self, result) -> None:
        if (self._networkFeePPM == 0):
            return;

        # calculate the target network fee amount
        targetNetworkFeeAmount = MathEx.mulDivF(result.tradingFeeAmount, self._networkFeePPM, PPM_RESOLUTION);

        # update the target balance (but don't deduct it from the full trading fee amount)
        result.targetBalance -= targetNetworkFeeAmount;

        if (not result.isSourceBNT):
            result.networkFeeAmount = targetNetworkFeeAmount;

            return;

        # trade the network fee (taken from the base token) to BNT
        result.networkFeeAmount = self._tradeAmountAndFeeBySourceAmount(
            result.targetBalance,
            result.sourceBalance,
            0,
            targetNetworkFeeAmount
        ).amount;

        # since we have received the network fee in base tokens and have traded them for BNT (so that the network fee
        # is always kept in BNT), we'd need to adapt the trading liquidity and the staked balance accordingly
        result.targetBalance += targetNetworkFeeAmount;
        result.sourceBalance -= result.networkFeeAmount;
        result.stakedBalance -= targetNetworkFeeAmount;

    '''
     * @dev performs a trade
    '''
    def _performTrade(self, result) -> None:
        data = self._poolData[result.pool];
        prevLiquidity = data.liquidity;

        # update the recent average rate
        self._updateAverageRates(
            data,
            Fraction256({ 'n': prevLiquidity.bntTradingLiquidity, 'd': prevLiquidity.baseTokenTradingLiquidity })
        );

        self._processTrade(result);

        # trading liquidity is assumed to never exceed 128 bits (the cast below will revert("otherwise)
        newLiquidity = PoolLiquidity({
            'bntTradingLiquidity': (result.sourceBalance if result.isSourceBNT else result.targetBalance).toUint128(),
            'baseTokenTradingLiquidity': (result.targetBalance if result.isSourceBNT else result.sourceBalance).toUint128(),
            'stakedBalance': result.stakedBalance
        });

        self._dispatchTradingLiquidityEvents_(result.contextId, result.pool, prevLiquidity, newLiquidity);

        # update the liquidity data of the pool
        data.liquidity = newLiquidity;

    '''
     * @dev returns the state of a pool's rate
    '''
    def _poolRateState(self, data) -> (PoolRateState):
        spotRate = Fraction256({
            'n': data.liquidity.bntTradingLiquidity,
            'd': data.liquidity.baseTokenTradingLiquidity
        });

        averageRates = data.averageRates;
        rate = averageRates.rate;
        if (not spotRate.isPositive() or not rate.isPositive()):
            return PoolRateState.Uninitialized;

        invSpotRate = spotRate.inverse();
        invRate = averageRates.invRate;
        if (not invSpotRate.isPositive() or not invRate.isPositive()):
            return PoolRateState.Uninitialized;

        effectiveAverageRates = self._effectiveAverageRates(averageRates, spotRate);

        if (
            MathEx.isInRange(effectiveAverageRates.rate.fromFraction112(), spotRate, self.RATE_MAX_DEVIATION_PPM) and
            MathEx.isInRange(effectiveAverageRates.invRate.fromFraction112(), invSpotRate, self.RATE_MAX_DEVIATION_PPM)
        ):
            return PoolRateState.Stable;

        return PoolRateState.Unstable;

    '''
     * @dev updates the average rates
    '''
    def _updateAverageRates(self, data, spotRate) -> None:
        data.averageRates = self._effectiveAverageRates(data.averageRates, spotRate);

    '''
     * @dev returns the effective average rates
    '''
    def _effectiveAverageRates(self, averageRates, spotRate) -> (AverageRates):
        blockNumber = self._blockNumber();

        # can only be updated once in a single block
        prevUpdateBlock = averageRates.blockNumber;
        if (prevUpdateBlock == blockNumber):
            return averageRates;

        # if sufficient blocks have passed, or if one of the rates isn't positive,
        # reset the average rates
        if (
            blockNumber - prevUpdateBlock >= self.RATE_RESET_BLOCK_THRESHOLD or
            not averageRates.rate.isPositive() or
            not averageRates.invRate.isPositive()
        ):
            if (spotRate.isPositive()):
                return \
                    AverageRates({
                        'blockNumber': blockNumber,
                        'rate': spotRate.toFraction112(),
                        'invRate': spotRate.inverse().toFraction112()
                    });

            return AverageRates({ 'blockNumber': 0, 'rate': zeroFraction112(), 'invRate': zeroFraction112() });

        return \
            AverageRates({
                'blockNumber': blockNumber,
                'rate': self._calcAverageRate(averageRates.rate, spotRate),
                'invRate': self._calcAverageRate(averageRates.invRate, spotRate.inverse())
            });

    '''
     * @dev calculates the average rate
    '''
    def _calcAverageRate(self, averageRate, rate) -> (Fraction112):
        if (rate.n * averageRate.d == rate.d * averageRate.n):
            return averageRate;

        return \
            MathEx \
                .weightedAverage(averageRate.fromFraction112(), rate, self.EMA_AVERAGE_RATE_WEIGHT, self.EMA_SPOT_RATE_WEIGHT) \
                .toFraction112();

    '''
     * @dev verifies if the provided rate is valid
    '''
    def _validRate(self, rate) -> None:
        if (not rate.isPositive()):
            revert("InvalidRate");
