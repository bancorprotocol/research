from bancor_research.bancor_emulator.solidity import uint, uint256, mapping, address, payable, revert
from bancor_research.bancor_emulator.utils import contract, parse

from bancor_research.bancor_emulator.EnumerableSet import EnumerableSet
from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION
from bancor_research.bancor_emulator.Time import Time
from bancor_research.bancor_emulator.MathEx import MathEx
from bancor_research.bancor_emulator.PoolCollection import PoolCollection as IPoolCollection

'''
 * @dev Bancor Network contract
'''
class BancorNetwork(contract, Time):
    class TradeParams:
        def __init__(self, x = None) -> None:
            self.amount = parse(uint256, x, 'amount');
            self.limit = parse(uint256, x, 'limit');
            self.bySourceAmount = parse(bool, x, 'bySourceAmount');

    class TradeResult:
        def __init__(self, x = None) -> None:
            self.sourceAmount = parse(uint256, x, 'sourceAmount');
            self.targetAmount = parse(uint256, x, 'targetAmount');
            self.tradingFeeAmount = parse(uint256, x, 'tradingFeeAmount');
            self.networkFeeAmount = parse(uint256, x, 'networkFeeAmount');

    class TradeTokens:
        def __init__(self, x = None) -> None:
            self.sourceToken = parse(address, x, 'sourceToken');
            self.targetToken = parse(address, x, 'targetToken');

    class TraderInfo:
        def __init__(self, x = None) -> None:
            self.trader = parse(address, x, 'trader');
            self.beneficiary = parse(address, x, 'beneficiary');

    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initBNTGovernance,
        initVBNTGovernance,
        initNetworkSettings,
        initMasterVault,
        initExternalProtectionVault,
        initBNTPoolToken
    ) -> None:
        contract.__init__(self)
        Time.__init__(self)

        self._bntGovernance = initBNTGovernance;
        self._bnt = initBNTGovernance.token();
        self._vbntGovernance = initVBNTGovernance;
        self._vbnt = initVBNTGovernance.token();

        self._networkSettings = initNetworkSettings;
        self._masterVault = initMasterVault;
        self._externalProtectionVault = initExternalProtectionVault;
        self._bntPoolToken = initBNTPoolToken;

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self,
         initBNTPool,
         initPendingWithdrawals,
         initPoolMigrator
    ) -> None:
        self.__BancorNetwork_init(initBNTPool, initPendingWithdrawals, initPoolMigrator);

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __BancorNetwork_init(self,
         initBNTPool,
         initPendingWithdrawals,
         initPoolMigrator
    ) -> None:
        self.__BancorNetwork_init_unchained(initBNTPool, initPendingWithdrawals, initPoolMigrator);

    '''
     * @dev performs contract-specific initialization
    '''
    def __BancorNetwork_init_unchained(self,
         initBNTPool,
         initPendingWithdrawals,
         initPoolMigrator
    ) -> None:
        self._bntPool = initBNTPool;
        self._pendingWithdrawals = initPendingWithdrawals;
        self._poolMigrator = initPoolMigrator;

        # the set of all valid pool collections
        self._poolCollections = EnumerableSet();

        # the set of all pools
        self._liquidityPools = EnumerableSet();

        # a mapping between pools and their respective pool collections
        self._collectionByPool = mapping(lambda: address(0));

        # the pending network fee amount to be burned by the vortex
        self._pendingNetworkFeeAmount = uint256();

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 7;

    '''
     * @dev returns the pending network fee amount to be burned by the vortex
    '''
    def pendingNetworkFeeAmount(self) -> (uint):
        return self._pendingNetworkFeeAmount.clone();

    '''
     * @dev registers new pool collection with the network
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def registerPoolCollection(self, newPoolCollection) -> None:
        # verify that there is no pool collection of the same type and version
        newPoolType = newPoolCollection.poolType();
        newPoolVersion = newPoolCollection.version();

        poolCollection = self._findPoolCollection(newPoolType, newPoolVersion);
        if (poolCollection != address(0) or not self._poolCollections.add(address(newPoolCollection))):
            revert("AlreadyExists");

    '''
     * @dev unregisters an existing pool collection from the network
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def unregisterPoolCollection(self, poolCollection) -> None:
        # verify that no pools are associated with the specified pool collection
        if (poolCollection.poolCount() != 0):
            revert("NotEmpty");

        if (not self._poolCollections.remove(address(poolCollection))):
            revert("DoesNotExist");

        self._setAccessRoles(poolCollection, False);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def poolCollections(self) -> (list):
        return self._poolCollections.values();

    '''
     * @inheritdoc IBancorNetwork
    '''
    def liquidityPools(self) -> (list):
        return self._liquidityPools.values();

    '''
     * @inheritdoc IBancorNetwork
    '''
    def collectionByPool(self, pool) -> (IPoolCollection):
        return self._collectionByPool[pool];

    '''
     * @inheritdoc IBancorNetwork
    '''
    def createPools(self, tokens, poolCollection) -> None:
        if (not self._poolCollections.contains(address(poolCollection))):
            revert("DoesNotExist");

        length = len(tokens);
        for i in range(length):
            self._createPool(tokens[i], poolCollection);

    '''
     * @dev creates a new pool
    '''
    def _createPool(self, token, poolCollection) -> None:
        if (token is (self._bnt)):
            revert("InvalidToken");

        if (not self._liquidityPools.add(address(token))):
            revert("AlreadyExists");

        # this is where the magic happens...
        poolCollection.createPool(token);

        # add the pool collection to the reverse pool collection lookup
        self._collectionByPool[token] = poolCollection;

    '''
     * @inheritdoc IBancorNetwork
    '''
    def migratePools(self, pools, newPoolCollection) -> None:
        if (not self._poolCollections.contains(address(newPoolCollection))):
            revert("DoesNotExist");

        length = len(pools);
        for i in range(length):
            pool = pools[i];

            # request the pool migrator to migrate the pool to the new pool collection
            self._poolMigrator.migratePool(pool, newPoolCollection);

            prevPoolCollection = self._collectionByPool[pool];

            # update the mapping between pools and their respective pool collections
            self._collectionByPool[pool] = newPoolCollection;

    '''
     * @inheritdoc IBancorNetwork
    '''
    def depositFor(self,
        provider,
        pool,
        tokenAmount
    ) -> (uint):
        return self._depositFor(provider, pool, tokenAmount, self.msg_sender);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def deposit(self, pool, tokenAmount) -> (uint):
        return self._depositFor(self.msg_sender, pool, tokenAmount, self.msg_sender);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def initWithdrawal(self, poolToken, poolTokenAmount) -> (uint):
        return self._initWithdrawal(self.msg_sender, poolToken, poolTokenAmount);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def cancelWithdrawal(self, id) -> (uint):
        return self._pendingWithdrawals.cancelWithdrawal(self.msg_sender, id);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def withdraw(self, id) -> (uint):
        provider = self.msg_sender;
        contextId = self._withdrawContextId(id, provider);

        # complete the withdrawal and claim the locked pool tokens
        completedRequest = self._pendingWithdrawals.completeWithdrawal(contextId, provider, id);

        if (completedRequest.poolToken == self._bntPoolToken):
            return self._withdrawBNT(contextId, provider, completedRequest);

        return self._withdrawBaseToken(contextId, provider, completedRequest);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def tradeBySourceAmount(self,
        sourceToken,
        targetToken,
        sourceAmount,
        minReturnAmount,
        deadline,
        beneficiary
    ) -> (uint):
        self._verifyTradeParams(sourceToken, targetToken, sourceAmount, minReturnAmount, deadline);

        return \
            self._trade(
                self.TradeTokens({ 'sourceToken': sourceToken, 'targetToken': targetToken }),
                self.TradeParams({ 'bySourceAmount': True, 'amount': sourceAmount, 'limit': minReturnAmount }),
                self.TraderInfo({ 'trader': self.msg_sender, 'beneficiary': beneficiary }),
                deadline
            );

    '''
     * @inheritdoc IBancorNetwork
    '''
    def tradeByTargetAmount(self,
        sourceToken,
        targetToken,
        targetAmount,
        maxSourceAmount,
        deadline,
        beneficiary
    ) -> (uint):
        self._verifyTradeParams(sourceToken, targetToken, targetAmount, maxSourceAmount, deadline);

        return \
            self._trade(
                self.TradeTokens({ 'sourceToken': sourceToken, 'targetToken': targetToken }),
                self.TradeParams({ 'bySourceAmount': False, 'amount': targetAmount, 'limit': maxSourceAmount }),
                self.TraderInfo({ 'trader': self.msg_sender, 'beneficiary': beneficiary }),
                deadline
            );

    '''
     * @inheritdoc IBancorNetwork
    '''
    def flashLoan(self,
        token,
        amount,
        recipient,
        data
    ) -> None:
        if (not token is (self._bnt) and not self._networkSettings.isTokenWhitelisted(token)):
            revert("NotWhitelisted");

        feeAmount = MathEx.mulDivF(amount, self._networkSettings.flashLoanFeePPM(token), PPM_RESOLUTION);

        # save the current balance
        prevBalance = token.balanceOf(address(self));

        # transfer the amount from the master vault to the recipient
        self._masterVault.withdrawFunds(token, payable(address(recipient)), amount);

        # invoke the recipient's callback
        recipient.onFlashLoan(self.msg_sender, token.toIERC20(), amount, feeAmount, data);

        # ensure that the tokens + fee have been deposited back to the network
        returnedAmount = token.balanceOf(address(self)) - prevBalance;
        if (returnedAmount < amount + feeAmount):
            revert("InsufficientFlashLoanReturn");

        # transfer the amount and the fee back to the vault
        token.transfer(payable(address(self._masterVault)), returnedAmount);

        # notify the pool of accrued fees
        if (token is (self._bnt)):
            cachedBNTPool = self._bntPool;

            cachedBNTPool.onFeesCollected(token, feeAmount, False);
        else:
            # get the pool and verify that it exists
            poolCollection = self._poolCollection(token);
            poolCollection.onFeesCollected(token, feeAmount);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def migrateLiquidity(self,
        token,
        provider,
        amount,
        availableAmount,
        originalAmount
    ) -> None:
        contextId = uint256(0);

        if (token is (self._bnt)):
            self._depositBNTFor(contextId, provider, amount, True, originalAmount);
        else:
            self._depositBaseTokenFor(contextId, provider, token, amount, availableAmount);

    '''
     * @inheritdoc IBancorNetwork
    '''
    def withdrawNetworkFees(self, recipient) -> (uint):
        currentPendingNetworkFeeAmount = self._pendingNetworkFeeAmount;
        if (currentPendingNetworkFeeAmount == 0):
            return uint256(0);

        self._pendingNetworkFeeAmount = uint256(0);

        self._masterVault.withdrawFunds(address(self._bnt), payable(recipient), currentPendingNetworkFeeAmount);

        return currentPendingNetworkFeeAmount;

    '''
     * @dev generates context ID for a deposit request
    '''
    def _depositContextId(self,
        provider,
        pool,
        tokenAmount,
        caller
    ) -> (uint):
        return uint256(0);

    '''
     * @dev generates context ID for a withdraw request
    '''
    def _withdrawContextId(self, id, caller) -> (uint):
        return uint256(0);

    '''
     * @dev deposits liquidity for the specified provider from caller
     *
     * requirements:
     *
     * - the caller must have approved the network to transfer the liquidity tokens on its behalf
    '''
    def _depositFor(self,
        provider,
        pool,
        tokenAmount,
        caller
    ) -> (uint):
        contextId = self._depositContextId(provider, pool, tokenAmount, caller);

        if (pool is (self._bnt)):
            return self._depositBNTFor(contextId, provider, tokenAmount, caller, False, 0);

        return self._depositBaseTokenFor(contextId, provider, pool, tokenAmount, caller, tokenAmount);

    '''
     * @dev deposits BNT liquidity for the specified provider from caller
     *
     * requirements:
     *
     * - the caller must have approved the network to transfer BNT on its behalf
    '''
    def _depositBNTFor(self,
        contextId,
        provider,
        bntAmount,
        caller,
        isMigrating,
        originalAmount
    ) -> (uint):
        cachedBNTPool = self._bntPool;

        # transfer the tokens from the caller to the BNT pool
        self._bnt.transferFrom(caller, address(cachedBNTPool), bntAmount);

        # process BNT pool deposit
        return cachedBNTPool.depositFor(contextId, provider, bntAmount, isMigrating, originalAmount);

    '''
     * @dev deposits base token liquidity for the specified provider from sender
     *
     * requirements:
     *
     * - the caller must have approved the network to transfer base tokens to on its behalf
    '''
    def _depositBaseTokenFor(self,
         contextId,
         provider,
         pool,
         tokenAmount,
         caller,
         availableAmount
    ) -> (uint):
        # transfer the tokens from the sender to the vault
        self._depositToMasterVault(pool, caller, availableAmount);

        # get the pool collection that managed this pool
        poolCollection = self._poolCollection(pool);

        # process deposit to the base token pool (includes the native token pool)
        return poolCollection.depositFor(contextId, provider, pool, tokenAmount);

    '''
     * @dev handles BNT withdrawal
    '''
    def _withdrawBNT(self,
        contextId,
        provider,
        completedRequest
    ) -> (uint):
        cachedBNTPool = self._bntPool;

        # transfer the pool tokens to from the pending withdrawals contract to the BNT pool
        completedRequest.poolToken.transferFrom(
            address(self._pendingWithdrawals),
            address(cachedBNTPool),
            completedRequest.poolTokenAmount
        );

        # transfer vBNT from the caller to the BNT pool
        self._vbnt.transferFrom(provider, address(cachedBNTPool), completedRequest.poolTokenAmount);

        # call withdraw on the BNT pool
        return \
            cachedBNTPool.withdraw(
                contextId,
                provider,
                completedRequest.poolTokenAmount,
                completedRequest.reserveTokenAmount
            );

    '''
     * @dev handles base token withdrawal
    '''
    def _withdrawBaseToken(self,
        contextId,
        provider,
        completedRequest
    ) -> (uint):
        pool = completedRequest.poolToken.reserveToken();

        # get the pool collection that manages this pool
        poolCollection = self._poolCollection(pool);

        # transfer the pool tokens to from the pending withdrawals contract to the pool collection
        completedRequest.poolToken.transferFrom(
            address(self._pendingWithdrawals),
            address(poolCollection),
            completedRequest.poolTokenAmount
        );

        # call withdraw on the base token pool - returns the amounts/breakdown
        return \
            poolCollection.withdraw(
                contextId,
                provider,
                pool,
                completedRequest.poolTokenAmount,
                completedRequest.reserveTokenAmount
            );

    '''
     * @dev verifies that the provided trade params are valid
    '''
    def _verifyTradeParams(self,
        sourceToken,
        targetToken,
        amount,
        limit,
        deadline
    ) -> None:
        if (sourceToken == targetToken):
            revert("InvalidToken");

        if (deadline < self._time()):
            revert("DeadlineExpired");

    '''
     * @dev performs a trade by providing either the source or target 'amount':
     *
     * - when trading by the source amount, the amount represents the source amount and the limit is the minimum return
     *   amount
     * - when trading by the target amount, the amount represents the target amount and the limit is the maximum source
     *   amount
     *
     * requirements:
     *
     * - the caller must have approved the network to transfer the source tokens on its behalf (except for in the
     *   native token case)
    '''
    def _trade(self,
        tokens,
        params,
        traderInfo,
        deadline
    ) -> (uint):
        # ensure the beneficiary is set
        if (traderInfo.beneficiary == address(0)):
            traderInfo.beneficiary = traderInfo.trader;

        contextId = uint256(0);

        # perform either a single or double hop trade, based on the source and the target pool
        firstHopTradeResult = self.TradeResult();
        lastHopTradeResult = self.TradeResult();
        networkFeeAmount = uint256();

        if (tokens.sourceToken is (self._bnt)):
            lastHopTradeResult = self._tradeBNT(contextId, tokens.targetToken, True, params);

            firstHopTradeResult = lastHopTradeResult;

            networkFeeAmount = lastHopTradeResult.networkFeeAmount;
        elif (tokens.targetToken is (self._bnt)):
            lastHopTradeResult = self._tradeBNT(contextId, tokens.sourceToken, False, params);

            firstHopTradeResult = lastHopTradeResult;

            networkFeeAmount = lastHopTradeResult.networkFeeAmount;
        else:
            (firstHopTradeResult, lastHopTradeResult) = self._tradeBaseTokens(contextId, tokens, params);

            networkFeeAmount = firstHopTradeResult.networkFeeAmount + lastHopTradeResult.networkFeeAmount;

        # transfer the tokens from the trader to the vault
        self._depositToMasterVault(tokens.sourceToken, traderInfo.trader, firstHopTradeResult.sourceAmount);

        # transfer the target tokens/native token to the beneficiary
        self._masterVault.withdrawFunds(
            tokens.targetToken,
            payable(traderInfo.beneficiary),
            lastHopTradeResult.targetAmount
        );

        # update the pending network fee amount to be burned by the vortex
        self._pendingNetworkFeeAmount += networkFeeAmount;

        return lastHopTradeResult.targetAmount if params.bySourceAmount else lastHopTradeResult.sourceAmount;

    '''
     * @dev performs a single hop between BNT and a base token trade by providing either the source or the target amount
     *
     * - when trading by the source amount, the amount represents the source amount and the limit is the minimum return
     *   amount
     * - when trading by the target amount, the amount represents the target amount and the limit is the maximum source
     *   amount
    '''
    def _tradeBNT(self,
        contextId,
        pool,
        fromBNT,
        params
    ) -> (TradeResult):
        tokens = \
            self.TradeTokens({ 'sourceToken': address(self._bnt), 'targetToken': pool }) if fromBNT else \
            self.TradeTokens({ 'sourceToken': pool, 'targetToken': address(self._bnt) });

        tradeAmountsAndFee = \
            self._poolCollection(pool).tradeBySourceAmount(
                contextId,
                tokens.sourceToken,
                tokens.targetToken,
                params.amount,
                params.limit
            ) if params.bySourceAmount else \
            self._poolCollection(pool).tradeByTargetAmount(
                contextId,
                tokens.sourceToken,
                tokens.targetToken,
                params.amount,
                params.limit
            );

        # if the target token is BNT, notify the BNT pool on collected fees (which shouldn't include the network fee
        # amount, so we have to deduct it explicitly from the full trading fee amount)
        if (not fromBNT):
            self._bntPool.onFeesCollected(
                pool,
                tradeAmountsAndFee.tradingFeeAmount - tradeAmountsAndFee.networkFeeAmount,
                True
            );

        return \
            self.TradeResult({
                'sourceAmount': params.amount if params.bySourceAmount else tradeAmountsAndFee.amount,
                'targetAmount': tradeAmountsAndFee.amount if params.bySourceAmount else params.amount,
                'tradingFeeAmount': tradeAmountsAndFee.tradingFeeAmount,
                'networkFeeAmount': tradeAmountsAndFee.networkFeeAmount
            });

    '''
     * @dev performs a double hop trade between two base tokens by providing either the source or the target amount
     *
     * - when trading by the source amount, the amount represents the source amount and the limit is the minimum return
     *   amount
     * - when trading by the target amount, the amount represents the target amount and the limit is the maximum source
     *   amount
    '''
    def _tradeBaseTokens(self,
        contextId,
        tokens,
        params
    ):# -> (TradeResult, TradeResult):
        if (params.bySourceAmount):
            sourceAmount = params.amount;
            minReturnAmount = params.limit;

            # trade source tokens to BNT (while accepting any return amount)
            targetHop1 = self._tradeBNT(
                contextId,
                tokens.sourceToken,
                False,
                self.TradeParams({ 'bySourceAmount': True, 'amount': sourceAmount, 'limit': 1 })
            );

            # trade the received BNT target amount to target tokens (while respecting the minimum return amount)
            targetHop2 = self._tradeBNT(
                contextId,
                tokens.targetToken,
                True,
                self.TradeParams({ 'bySourceAmount': True, 'amount': targetHop1.targetAmount, 'limit': minReturnAmount })
            );

            return (targetHop1, targetHop2);

        targetAmount = params.amount;
        maxSourceAmount = params.limit;

        # trade any amount of BNT to get the requested target amount (we will use the actual traded amount to restrict
        # the trade from the source)
        sourceHop2 = self._tradeBNT(
            contextId,
            tokens.targetToken,
            True,
            self.TradeParams({ 'bySourceAmount': False, 'amount': targetAmount, 'limit': uint256.max })
        );

        # trade source tokens to the required amount of BNT (while respecting the maximum source amount)
        sourceHop1 = self._tradeBNT(
            contextId,
            tokens.sourceToken,
            False,
            self.TradeParams({ 'bySourceAmount': False, 'amount': sourceHop2.sourceAmount, 'limit': maxSourceAmount })
        );

        return (sourceHop1, sourceHop2);

    '''
     * @dev deposits tokens to the master vault and verifies that msg.value corresponds to its type
    '''
    def _depositToMasterVault(self,
        token,
        caller,
        amount
    ) -> None:
        token.transferFrom(caller, address(self._masterVault), amount);

    '''
     * @dev verifies that the specified pool is managed by a valid pool collection and returns it
    '''
    def _poolCollection(self, token) -> (IPoolCollection):
        # verify that the pool is managed by a valid pool collection
        poolCollection = self._collectionByPool[token];
        if (address(poolCollection) == address(0)):
            revert("InvalidToken");

        return poolCollection;

    '''
     * @dev initiates liquidity withdrawal
    '''
    def _initWithdrawal(self,
        provider,
        poolToken,
        poolTokenAmount
    ) -> (uint):
        if (poolToken != self._bntPoolToken):
            reserveToken = poolToken.reserveToken();
            if (self._poolCollection(reserveToken).poolToken(reserveToken) != poolToken):
                revert("InvalidPool");

        # transfer the pool tokens from the provider (we aren't using safeTransferFrom, since the PoolToken is a fully
        # compliant ERC20 token contract)
        poolToken.transferFrom(provider, address(self._pendingWithdrawals), poolTokenAmount);

        return self._pendingWithdrawals.initWithdrawal(provider, poolToken, poolTokenAmount);

    '''
     * @dev finds a pool collection with the given type and version
    '''
    def _findPoolCollection(self, poolType, poolVersion) -> (IPoolCollection):
        # note that there's no risk of using an unbounded loop here since the list of all the active pool collections
        # is always going to remain sufficiently small
        length = self._poolCollections.length();
        for i in range(length):
            poolCollection = self._poolCollections.at(i);
            if ((poolCollection.poolType() == poolType and poolCollection.version() == poolVersion)):
                return poolCollection;

        return address(0);
