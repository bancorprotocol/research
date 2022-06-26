from solidity import uint, uint8, uint16, uint32, uint128, uint256, mapping, address, payable, revert
from utils import account

from EnumerableSet import EnumerableSet
from Math import Math
from SafeCast import SafeCast
from Constants import PPM_RESOLUTION
from BlockNumber import BlockNumber
from FractionLibrary import Fraction256, Fraction112, zeroFraction112
from MathEx import Sint256, MathEx
from PoolToken import PoolToken as IPoolToken
from PoolCollectionWithdrawal import PoolCollectionWithdrawal

class PoolLiquidity:
    def __init__(self,
        x = {
            'bntTradingLiquidity': 0,
            'baseTokenTradingLiquidity': 0,
            'stakedBalance': 0
        }
    ) -> None:
        self.bntTradingLiquidity = uint128(x['bntTradingLiquidity']); # the BNT trading liquidity
        self.baseTokenTradingLiquidity = uint128(x['baseTokenTradingLiquidity']); # the base token trading liquidity
        self.stakedBalance = uint256(x['stakedBalance']); # the staked balance

class AverageRates:
    def __init__(self,
        x = {
            'blockNumber': 0,
            'rate': {'n': 0, 'd': 0},
            'invRate': {'n': 0, 'd': 0}
        }
    ) -> None:
        self.blockNumber = uint32(x['blockNumber']);
        self.rate = Fraction112(x['rate']);
        self.invRate = Fraction112(x['invRate']);

class Pool:
    def __init__(self,
        x = {
            'poolToken': None,
            'tradingFeePPM': 0,
            'tradingEnabled': False,
            'depositingEnabled': False,
            'averageRates': {
                'blockNumber': 0,
                'rate': {'n': 0, 'd': 0},
                'invRate': {'n': 0, 'd': 0}
            },
            'liquidity': {
                'bntTradingLiquidity': 0,
                'baseTokenTradingLiquidity': 0,
                'stakedBalance': 0
            }
        }
    ) -> None:
        self.poolToken = x['poolToken']; # the pool token of the pool
        self.tradingFeePPM = uint32(x['tradingFeePPM']); # the trading fee (in units of PPM)
        self.tradingEnabled = bool(x['tradingEnabled']); # whether trading is enabled
        self.depositingEnabled = bool(x['depositingEnabled']); # whether depositing is enabled
        self.averageRates = AverageRates(x['averageRates']); # the recent average rates
        self.liquidity = PoolLiquidity(x['liquidity']); # the overall liquidity in the pool

class WithdrawalAmounts:
    def __init__(self,
        x = {
            'totalAmount': 0,
            'baseTokenAmount': 0,
            'bntAmount': 0
        }
    ) -> None:
        self.totalAmount = uint256(x['totalAmount']);
        self.baseTokenAmount = uint256(x['baseTokenAmount']);
        self.bntAmount = uint256(x['bntAmount']);

# trading enabling/disabling reasons
TRADING_STATUS_UPDATE_DEFAULT = uint8(0);
TRADING_STATUS_UPDATE_ADMIN = uint8(1);
TRADING_STATUS_UPDATE_MIN_LIQUIDITY = uint8(2);
TRADING_STATUS_UPDATE_INVALID_STATE = uint8(3);

class TradeAmountAndFee:
    def __init__(self,
        x = {
            'amount': 0,
            'tradingFeeAmount': 0,
            'networkFeeAmount': 0
        }
    ) -> None:
        self.amount = uint256(x['amount']); # the source/target amount (depending on the context) resulting from the trade
        self.tradingFeeAmount = uint256(x['tradingFeeAmount']); # the trading fee amount
        self.networkFeeAmount = uint256(x['networkFeeAmount']); # the network fee amount (always in units of BNT)

# base token withdrawal output amounts
class InternalWithdrawalAmounts:
    def __init__(self,
        x = {
            'baseTokensToTransferFromMasterVault': 0,
            'bntToMintForProvider': 0,
            'baseTokensToTransferFromEPV': 0,
            'baseTokensTradingLiquidityDelta': {'value': 0, 'isNeg': False},
            'bntTradingLiquidityDelta': {'value': 0, 'isNeg': False},
            'bntProtocolHoldingsDelta': {'value': 0, 'isNeg': False},
            'baseTokensWithdrawalFee': 0,
            'baseTokensWithdrawalAmount': 0,
            'poolTokenAmount': 0,
            'poolTokenTotalSupply': 0,
            'newBaseTokenTradingLiquidity': 0,
            'newBNTTradingLiquidity': 0
        }
    ) -> None:
        self.baseTokensToTransferFromMasterVault = uint256(x['baseTokensToTransferFromMasterVault']); # base token amount to transfer from the master vault to the provider
        self.bntToMintForProvider = uint256(x['bntToMintForProvider']); # BNT amount to mint directly for the provider
        self.baseTokensToTransferFromEPV = uint256(x['baseTokensToTransferFromEPV']); # base token amount to transfer from the external protection vault to the provider
        self.baseTokensTradingLiquidityDelta = Sint256(x['baseTokensTradingLiquidityDelta']); # base token amount to add to the trading liquidity
        self.bntTradingLiquidityDelta = Sint256(x['bntTradingLiquidityDelta']); # BNT amount to add to the trading liquidity and to the master vault
        self.bntProtocolHoldingsDelta = Sint256(x['bntProtocolHoldingsDelta']); # BNT amount add to the protocol equity
        self.baseTokensWithdrawalFee = uint256(x['baseTokensWithdrawalFee']); # base token amount to keep in the pool as a withdrawal fee
        self.baseTokensWithdrawalAmount = uint256(x['baseTokensWithdrawalAmount']); # base token amount equivalent to the base pool token's withdrawal amount
        self.poolTokenAmount = uint256(x['poolTokenAmount']); # base pool token
        self.poolTokenTotalSupply = uint256(x['poolTokenTotalSupply']); # base pool token's total supply
        self.newBaseTokenTradingLiquidity = uint256(x['newBaseTokenTradingLiquidity']); # new base token trading liquidity
        self.newBNTTradingLiquidity = uint256(x['newBNTTradingLiquidity']); # new BNT trading liquidity

class TradingLiquidityAction:
    def __init__(self,
        x = {
            'update': False,
            'newAmount': 0
        }
    ) -> None:
        self.update = bool(x['update']);
        self.newAmount = uint256(x['newAmount']);

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
class PoolCollection(account, BlockNumber):
    POOL_TYPE = uint16(1);
    LIQUIDITY_GROWTH_FACTOR = uint256(2);
    BOOTSTRAPPING_LIQUIDITY_BUFFER_FACTOR = uint256(2);
    DEFAULT_TRADING_FEE_PPM = uint32(2_000); # 0.2%
    RATE_MAX_DEVIATION_PPM = uint32(10_000); # %1

    # the average rate is recalculated based on the ratio between the weights of the rates the smaller the weights are,
    # the larger the supported range of each one of the rates is
    EMA_AVERAGE_RATE_WEIGHT = uint256(4);
    EMA_SPOT_RATE_WEIGHT = uint256(1);

    class TradeIntermediateResult:
        def __init__(self,
            x = {
                'sourceAmount': 0,
                'targetAmount': 0,
                'limit': 0,
                'tradingFeeAmount': 0,
                'networkFeeAmount': 0,
                'sourceBalance': 0,
                'targetBalance': 0,
                'stakedBalance': 0,
                'pool': None,
                'isSourceBNT': False,
                'bySourceAmount': False,
                'tradingFeePPM': 0,
                'contextId': 0
            }
        ) -> None:
            self.sourceAmount = uint256(x['sourceAmount']);
            self.targetAmount = uint256(x['targetAmount']);
            self.limit = uint256(x['limit']);
            self.tradingFeeAmount = uint256(x['tradingFeeAmount']);
            self.networkFeeAmount = uint256(x['networkFeeAmount']);
            self.sourceBalance = uint256(x['sourceBalance']);
            self.targetBalance = uint256(x['targetBalance']);
            self.stakedBalance = uint256(x['stakedBalance']);
            self.pool = x['pool'];
            self.isSourceBNT = bool(x['isSourceBNT']);
            self.bySourceAmount = bool(x['bySourceAmount']);
            self.tradingFeePPM = uint32(x['stakedBalance']);
            self.contextId = uint256(x['sourceAmount']);

    class TradeAmountAndTradingFee:
        def __init__(self,
            x = {
                'amount': 0,
                'tradingFeeAmount': 0
            }
        ) -> None:
            self.amount = uint256(x['amount']);
            self.tradingFeeAmount = uint256(x['tradingFeeAmount']);

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
        account.__init__(self)
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

        self._setDefaultTradingFeePPM(PoolCollection.DEFAULT_TRADING_FEE_PPM);

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (uint):
        return uint16(5);

    '''
     * @inheritdoc IPoolCollection
    '''
    def poolType(self) -> (uint):
        return self.POOL_TYPE;

    '''
     * @inheritdoc IPoolCollection
    '''
    def defaultTradingFeePPM(self) -> (uint):
        return self._defaultTradingFeePPM;

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
        return self._poolData[pool].tradingFeePPM;

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
            return 0;

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

        return self._poolRateState(data.liquidity, data.averageRates) == PoolRateState.Stable;

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

        data.tradingFeePPM = newTradingFeePPM;

    '''
     * @dev enables trading in a given pool, by providing the funding rate as two virtual balances, and updates its
     * trading liquidity
     *
     * please note that the virtual balances should be derived from token prices, normalized to the smallest unit of
     * tokens. For example:
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

        # if there are no pool tokens available to support the staked balance - reset the trading liquidity and the
        # staked balance
        prevPoolTokenTotalSupply = data.poolToken.totalSupply();
        if (prevPoolTokenTotalSupply == 0 and currentStakedBalance != 0):
            currentStakedBalance = 0;

            self._resetTradingLiquidity(contextId, pool, data, TRADING_STATUS_UPDATE_INVALID_STATE);

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
            data.averageRates.rate.fromFraction112(),
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
                'bntAmount': amounts.bntToMintForProvider
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
        averageRates = data.averageRates;

        if (self._poolRateState(prevLiquidity, averageRates) == PoolRateState.Unstable):
            revert("RateUnstable");

        data.poolToken.burn(amounts.poolTokenAmount);

        newPoolTokenTotalSupply = amounts.poolTokenTotalSupply - amounts.poolTokenAmount;

        liquidity.stakedBalance = MathEx.mulDivF(
            liquidity.stakedBalance,
            newPoolTokenTotalSupply,
            amounts.poolTokenTotalSupply
        );

        # trading liquidity is assumed to never exceed 128 bits (the cast below will revert("otherwise)
        liquidity.baseTokenTradingLiquidity = SafeCast.toUint128(amounts.newBaseTokenTradingLiquidity);
        liquidity.bntTradingLiquidity = SafeCast.toUint128(amounts.newBNTTradingLiquidity);

        if (amounts.bntProtocolHoldingsDelta.value > 0):
            assert(amounts.bntProtocolHoldingsDelta.isNeg); # currently no support for requesting funding here

            self._bntPool.renounceFunding(contextId, pool, amounts.bntProtocolHoldingsDelta.value);
        elif (amounts.bntTradingLiquidityDelta.value > 0):
            if (amounts.bntTradingLiquidityDelta.isNeg):
                self._bntPool.burnFromVault(amounts.bntTradingLiquidityDelta.value);
            else:
                self._bntPool.mint(address(self._masterVault), amounts.bntTradingLiquidityDelta.value);

        # if the provider should receive some BNT - ask the BNT pool to mint BNT to the provider
        if (amounts.bntToMintForProvider > 0):
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
            self._resetTradingLiquidity(
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

        self._defaultTradingFeePPM = newDefaultTradingFeePPM;

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

        if (self._poolRateState(liquidity, data.averageRates) == PoolRateState.Unstable):
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
            'bntTradingLiquidity': SafeCast.toUint128(action.newBNTTradingLiquidity),
            'baseTokenTradingLiquidity': SafeCast.toUint128(action.newBaseTokenTradingLiquidity),
            'stakedBalance': liquidity.stakedBalance
        });

        # update the liquidity data of the pool
        data.liquidity = newLiquidity;

        self._dispatchTradingLiquidityEvents(contextId, pool, data.poolToken.totalSupply(), liquidity, newLiquidity);

    def _dispatchTradingLiquidityEvents(self,
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
        self._dispatchTradingLiquidityEvents(contextId, pool, prevLiquidity, newLiquidity);

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
        self._resetTradingLiquidity(contextId, pool, data, data.liquidity.bntTradingLiquidity, reason);

    '''
     * @dev resets trading liquidity and renounces any remaining BNT funding
    '''
    def _resetTradingLiquidity(self,
        contextId,
        pool,
        data,
        currentBNTTradingLiquidity,
        reason
    ) -> None:
        # reset the network and base token trading liquidities
        data.liquidity.bntTradingLiquidity = 0;
        data.liquidity.baseTokenTradingLiquidity = 0;

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
            result.sourceBalance = liquidity.bntTradingLiquidity;
            result.targetBalance = liquidity.baseTokenTradingLiquidity;
        else:
            result.sourceBalance = liquidity.baseTokenTradingLiquidity;
            result.targetBalance = liquidity.bntTradingLiquidity;

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
        networkFeePPM = self._networkSettings.networkFeePPM();
        if (networkFeePPM == 0):
            return;

        # calculate the target network fee amount
        targetNetworkFeeAmount = MathEx.mulDivF(result.tradingFeeAmount, networkFeePPM, PPM_RESOLUTION);

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
            'bntTradingLiquidity': SafeCast.toUint128(result.sourceBalance if result.isSourceBNT else result.targetBalance),
            'baseTokenTradingLiquidity': SafeCast.toUint128(
                result.targetBalance if result.isSourceBNT else result.sourceBalance
            ),
            'stakedBalance': result.stakedBalance
        });

        self._dispatchTradingLiquidityEvents(result.contextId, result.pool, prevLiquidity, newLiquidity);

        # update the liquidity data of the pool
        data.liquidity = newLiquidity;

    '''
     * @dev returns the state of a pool's rate
    '''
    def _poolRateState(self, liquidity, averageRates) -> (PoolRateState):
        spotRate = Fraction256({
            'n': liquidity.bntTradingLiquidity,
            'd': liquidity.baseTokenTradingLiquidity
        });

        rate = averageRates.rate;

        if (not spotRate.isPositive() or not rate.isPositive()):
            return PoolRateState.Uninitialized;

        invSpotRate = spotRate.inverse();
        invRate = averageRates.invRate;

        if (not invSpotRate.isPositive() or not invRate.isPositive()):
            return PoolRateState.Uninitialized;

        if (averageRates.blockNumber != self._blockNumber()):
            rate = self._calcAverageRate(rate, spotRate);
            invRate = self._calcAverageRate(invRate, invSpotRate);

        if (
            MathEx.isInRange(rate.fromFraction112(), spotRate, self.RATE_MAX_DEVIATION_PPM) and
            MathEx.isInRange(invRate.fromFraction112(), invSpotRate, self.RATE_MAX_DEVIATION_PPM)
        ):
            return PoolRateState.Stable;

        return PoolRateState.Unstable;

    '''
     * @dev updates the average rates
    '''
    def _updateAverageRates(self, data, spotRate) -> None:
        blockNumber = self._blockNumber();

        if (data.averageRates.blockNumber != blockNumber):
            data.averageRates = AverageRates({
                'blockNumber': blockNumber,
                'rate': self._calcAverageRate(data.averageRates.rate, spotRate),
                'invRate': self._calcAverageRate(data.averageRates.invRate, spotRate.inverse())
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
