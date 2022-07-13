from bancor_research.bancor_emulator.solidity import uint, uint32, uint256, address, mapping, days, revert
from bancor_research.bancor_emulator.utils import contract, parse

from bancor_research.bancor_emulator.EnumerableSet import EnumerableSet
from bancor_research.bancor_emulator.Time import Time

'''
 * @dev the data struct representing a pending withdrawal request
'''
class WithdrawalRequest:
    def __init__(self, x = None) -> None:
        self.provider = parse(address, x, 'provider'); # the liquidity provider
        self.poolToken = parse(address, x, 'poolToken'); # the locked pool token
        self.reserveToken = parse(address, x, 'reserveToken'); # the reserve token to withdraw
        self.createdAt = parse(uint32, x, 'createdAt'); # the time when the request was created (Unix timestamp)
        self.poolTokenAmount = parse(uint256, x, 'poolTokenAmount'); # the locked pool token amount
        self.reserveTokenAmount = parse(uint256, x, 'reserveTokenAmount'); # the expected reserve token amount to withdraw

'''
 * @dev the data struct representing a completed withdrawal request
'''
class CompletedWithdrawal:
    def __init__(self, x = None) -> None:
        self.poolToken = parse(address, x, 'poolToken'); # the withdraw pool token
        self.poolTokenAmount = parse(uint256, x, 'poolTokenAmount'); # the original pool token amount in the withdrawal request
        self.reserveTokenAmount = parse(uint256, x, 'reserveTokenAmount'); # the original reserve token amount at the time of the withdrawal init request

'''
 * @dev Pending Withdrawals contract
'''
class PendingWithdrawals(contract, Time):
    DEFAULT_LOCK_DURATION = uint32(7 * days);

    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initNetwork,
        initBNT,
        initBNTPool
    ) -> None:
        contract.__init__(self)
        Time.__init__(self)

        self._network = initNetwork;
        self._bnt = initBNT;
        self._bntPool = initBNTPool;

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__PendingWithdrawals_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __PendingWithdrawals_init(self) -> None:
        self.__PendingWithdrawals_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __PendingWithdrawals_init_unchained(self) -> None:
        # the lock duration
        self._lockDuration = uint32()

        # a mapping between accounts and their pending withdrawal requests
        self._nextWithdrawalRequestId = uint256()
        self._withdrawalRequestIdsByProvider = mapping(lambda: EnumerableSet());
        self._withdrawalRequests = mapping(lambda: WithdrawalRequest());

        self._setLockDuration(self.DEFAULT_LOCK_DURATION);

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 4;

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def lockDuration(self) -> (uint):
        return self._lockDuration.clone();

    '''
     * @dev sets the lock duration
     *
     * notes:
     *
     * - updating it will affect existing locked positions retroactively
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setLockDuration(self, newLockDuration) -> None:
        self._setLockDuration(newLockDuration);

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def withdrawalRequestCount(self, provider) -> (int):
        return self._withdrawalRequestIdsByProvider[provider].length();

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def withdrawalRequestIds(self, provider) -> (list):
        return self._withdrawalRequestIdsByProvider[provider].values();

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def withdrawalRequest(self, id) -> (WithdrawalRequest):
        return self._withdrawalRequests[id];

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def initWithdrawal(self,
        provider,
        poolToken,
        poolTokenAmount
    ) -> (uint):
        return self._initWithdrawal(provider, poolToken, poolTokenAmount);

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def cancelWithdrawal(self, provider, id) -> (uint):
        request = self._withdrawalRequests[id];

        if (request.provider != provider):
            revert("AccessDenied");

        return self._cancelWithdrawal(request, id);

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def completeWithdrawal(self,
        contextId,
        provider,
        id
    ) -> (CompletedWithdrawal):
        request = self._withdrawalRequests[id];

        if (provider != request.provider):
            revert("AccessDenied");

        currentTime = self._time();
        if (not self._canWithdrawAt(currentTime, request.createdAt)):
            revert("WithdrawalNotAllowed");

        # remove the withdrawal request and its id from the storage
        self._removeWithdrawalRequest(provider, id);

        # approve the caller to transfer the locked pool tokens
        request.poolToken.approve(self.msg_sender, request.poolTokenAmount);

        return CompletedWithdrawal({
            'poolToken': request.poolToken,
            'poolTokenAmount': request.poolTokenAmount,
            'reserveTokenAmount': request.reserveTokenAmount
        });

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def isReadyForWithdrawal(self, id) -> (bool):
        request = self._withdrawalRequests[id];

        return request.provider != address(0) and self._canWithdrawAt(self._time(), request.createdAt);

    '''
     * @dev sets the lock duration
     *
     * notes:
     *
     * - updating it will affect existing locked positions retroactively
     *
    '''
    def _setLockDuration(self, newLockDuration) -> None:
        prevLockDuration = self._lockDuration;
        if (prevLockDuration == newLockDuration):
            return;

        self._lockDuration = uint32(newLockDuration);

    '''
     * @dev initiates liquidity withdrawal
    '''
    def _initWithdrawal(self,
        provider,
        poolToken,
        poolTokenAmount
    ) -> (uint):
        # record the current withdrawal request alongside previous pending withdrawal requests
        id = self._nextWithdrawalRequestId.clone(); self._nextWithdrawalRequestId += 1;

        # get the pool token value in reserve/pool tokens
        pool = poolToken.reserveToken();
        reserveTokenAmount = self._poolTokenToUnderlying(pool, poolTokenAmount);
        self._withdrawalRequests[id] = WithdrawalRequest({
            'provider': provider,
            'poolToken': poolToken,
            'reserveToken': pool,
            'poolTokenAmount': poolTokenAmount,
            'reserveTokenAmount': reserveTokenAmount,
            'createdAt': self._time()
        });

        if (not self._withdrawalRequestIdsByProvider[provider].add(id)):
            revert("AlreadyExists");

        return id;

    '''
     * @dev returns the pool token value in tokens
    '''
    def _poolTokenToUnderlying(self, pool, poolTokenAmount) -> (uint):
        if (pool is (self._bnt)):
            return self._bntPool.poolTokenToUnderlying(poolTokenAmount);

        return self._network.collectionByPool(pool).poolTokenToUnderlying(pool, poolTokenAmount);

    '''
     * @dev cancels a withdrawal request
    '''
    def _cancelWithdrawal(self, request, id) -> (uint):
        # remove the withdrawal request and its id from the storage
        self._removeWithdrawalRequest(request.provider, id);

        # transfer the locked pool tokens back to the provider
        request.poolToken.transfer(request.provider, request.poolTokenAmount);

        return request.poolTokenAmount;

    '''
     * @dev removes withdrawal request
    '''
    def _removeWithdrawalRequest(self, provider, id) -> None:
        if (not self._withdrawalRequestIdsByProvider[provider].remove(id)):
            revert("DoesNotExist");

        del self._withdrawalRequests[id];

    '''
     * @dev returns whether it's possible to withdraw a request at the provided time
    '''
    def _canWithdrawAt(self, time, createdAt) -> (bool):
        return createdAt + self._lockDuration <= time;
