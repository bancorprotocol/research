from bancor_research.bancor_emulator.solidity import uint, uint128, address, revert
from bancor_research.bancor_emulator.utils import contract, parse

from bancor_research.bancor_emulator import ERC20 as IERC20
from bancor_research.bancor_emulator import TokenGovernance as ITokenGovernance
from bancor_research.bancor_emulator.Vault import Vault as IVault
from bancor_research.bancor_emulator import PoolToken as IPoolToken
from bancor_research.bancor_emulator import PoolCollection as IPoolCollection
from bancor_research.bancor_emulator.PoolCollection import WithdrawalAmounts
from bancor_research.bancor_emulator import BNTPool as IBNTPool
from bancor_research.bancor_emulator import BancorNetwork as IBancorNetwork
from bancor_research.bancor_emulator import NetworkSettings as INetworkSettings
from bancor_research.bancor_emulator import PendingWithdrawals as IPendingWithdrawals

class TradingLiquidity:
    def __init__(self, x = None) -> None:
        self.bntTradingLiquidity = parse(uint128, x, 'bntTradingLiquidity');
        self.baseTokenTradingLiquidity = parse(uint128, x, 'baseTokenTradingLiquidity');

'''
 * @dev Bancor Network Information contract
'''
class BancorNetworkInfo(contract):
    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initNetwork,
        initBNTGovernance,
        initVBNTGovernance,
        initNetworkSettings,
        initMasterVault,
        initExternalProtectionVault,
        initExternalRewardsVault,
        initBNTPool,
        initPendingWithdrawals,
        initPoolMigrator
    ) -> None:
        contract.__init__(self)

        self._network = initNetwork;
        self._bntGovernance = initBNTGovernance;
        self._bnt = initBNTGovernance.token();
        self._vbntGovernance = initVBNTGovernance;
        self._vbnt = initVBNTGovernance.token();
        self._networkSettings = initNetworkSettings;
        self._masterVault = initMasterVault;
        self._externalProtectionVault = initExternalProtectionVault;
        self._externalRewardsVault = initExternalRewardsVault;
        self._bntPool = initBNTPool;
        self._bntPoolToken = initBNTPool.poolToken();
        self._pendingWithdrawals = initPendingWithdrawals;
        self._poolMigrator = initPoolMigrator;

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__BancorNetworkInfo_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __BancorNetworkInfo_init(self) -> None:
        self.__BancorNetworkInfo_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __BancorNetworkInfo_init_unchained(self) -> None:
        pass

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 2;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def network(self) -> (IBancorNetwork):
        return self._network;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def bnt(self) -> (IERC20):
        return self._bnt;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def bntGovernance(self) -> (ITokenGovernance):
        return self._bntGovernance;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def vbnt(self) -> (IERC20):
        return self._vbnt;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def vbntGovernance(self) -> (ITokenGovernance):
        return self._vbntGovernance;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def networkSettings(self) -> (INetworkSettings):
        return self._networkSettings;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def masterVault(self) -> (IVault):
        return self._masterVault;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def externalProtectionVault(self) -> (IVault):
        return self._externalProtectionVault;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def externalRewardsVault(self) -> (IVault):
        return self._externalRewardsVault;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def bntPool(self) -> (IBNTPool):
        return self._bntPool;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def poolToken(self, pool) -> (IPoolToken):
        return self._bntPoolToken if pool == self._bnt else self._poolCollection(pool).poolToken(pool);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def stakedBalance(self, pool) -> (uint):
        return self._bntPool.stakedBalance() if pool == self._bnt else self._poolCollection(pool).poolLiquidity(pool).stakedBalance;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def tradingLiquidity(self, pool) -> (TradingLiquidity):
        if (pool == self._bnt):
            revert("InvalidParam");

        liquidity = self._poolCollection(pool).poolLiquidity(pool);

        return \
            TradingLiquidity({
                'bntTradingLiquidity': liquidity.bntTradingLiquidity,
                'baseTokenTradingLiquidity': liquidity.baseTokenTradingLiquidity
            });

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def tradingFeePPM(self, pool) -> (uint):
        if (pool == self._bnt):
            revert("InvalidParam");

        return self._poolCollection(pool).tradingFeePPM(pool);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def tradingEnabled(self, pool) -> (bool):
        return True if pool == self._bnt else self._poolCollection(pool).tradingEnabled(pool);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def depositingEnabled(self, pool) -> (bool):
        return True if pool == self._bnt else self._poolCollection(pool).depositingEnabled(pool);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def isPoolStable(self, pool) -> (bool):
        return True if pool == self._bnt else self._poolCollection(pool).isPoolStable(pool);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def pendingWithdrawals(self) -> (IPendingWithdrawals):
        return self._pendingWithdrawals;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def poolMigrator(self) -> (any):
        return self._poolMigrator;

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def tradeOutputBySourceAmount(self,
        sourceToken,
        targetToken,
        sourceAmount
    ) -> (uint):
        return self._tradeOutputAmount(sourceToken, targetToken, sourceAmount, True);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def tradeInputByTargetAmount(self,
        sourceToken,
        targetToken,
        targetAmount
    ) -> (uint):
        return self._tradeOutputAmount(sourceToken, targetToken, targetAmount, False);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def isReadyForWithdrawal(self, id) -> (bool):
        return self._pendingWithdrawals.isReadyForWithdrawal(id);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def poolTokenToUnderlying(self, pool, poolTokenAmount) -> (uint):
        return \
            self._bntPool.poolTokenToUnderlying(poolTokenAmount) if pool == self._bnt else \
            self._poolCollection(pool).poolTokenToUnderlying(pool, poolTokenAmount);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def underlyingToPoolToken(self, pool, tokenAmount) -> (uint):
        return \
            self._bntPool.underlyingToPoolToken(tokenAmount) if pool == self._bnt else \
            self._poolCollection(pool).underlyingToPoolToken(pool, tokenAmount);

    '''
     * @inheritdoc IBancorNetworkInfo
    '''
    def withdrawalAmounts(self, pool, poolTokenAmount) -> (WithdrawalAmounts):
        if (pool == self._bnt):
            amount = self._bntPool.withdrawalAmount(poolTokenAmount);
            return WithdrawalAmounts({ 'totalAmount': amount, 'baseTokenAmount': 0, 'bntAmount': amount });

        poolCollection = self._poolCollection(pool);
        return poolCollection.withdrawalAmounts(pool, poolTokenAmount);

    '''
     * @dev returns either the source amount or the target amount by providing the source and the target tokens
     * and whether we're interested in the target or the source amount
    '''
    def _tradeOutputAmount(self,
        sourceToken,
        targetToken,
        amount,
        bySourceAmount
    ) -> (uint):
        isSourceBNT = sourceToken == self._bnt;
        isTargetBNT = targetToken == self._bnt;

        # return the trade amount when trading BNT
        if (isSourceBNT or isTargetBNT):
            token = targetToken if isSourceBNT else sourceToken;
            poolCollection = self._poolCollection(token);

            return \
                (
                    poolCollection.tradeOutputAndFeeBySourceAmount(sourceToken, targetToken, amount) if bySourceAmount else
                    poolCollection.tradeInputAndFeeByTargetAmount(sourceToken, targetToken, amount)
                ).amount;

        # return the target amount by simulating double-hop trade from the source token to the target token via BNT
        if (bySourceAmount):
            targetAmount = self._poolCollection(sourceToken) \
                .tradeOutputAndFeeBySourceAmount(sourceToken, address(self._bnt), amount) \
                .amount;

            return \
                self._poolCollection(targetToken) \
                    .tradeOutputAndFeeBySourceAmount(address(self._bnt), targetToken, targetAmount) \
                    .amount;

        # return the source amount by simulating a "reverse" double-hop trade from the source token to the target token
        # via BNT
        requireNetworkAmount = self._poolCollection(targetToken) \
            .tradeInputAndFeeByTargetAmount(address(self._bnt), targetToken, amount) \
            .amount;

        return \
            self._poolCollection(sourceToken) \
                .tradeInputAndFeeByTargetAmount(sourceToken, address(self._bnt), requireNetworkAmount) \
                .amount;

    '''
     * @dev verifies that the specified pool is managed by a valid pool collection and returns it
    '''
    def _poolCollection(self, token) -> (IPoolCollection):
        # verify that the pool is managed by a valid pool collection
        poolCollection = self._network.collectionByPool(token);
        if (address(poolCollection) == address(0)):
            revert("InvalidToken");

        return poolCollection;
