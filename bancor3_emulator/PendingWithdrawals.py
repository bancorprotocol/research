from solidity import uint, uint32, uint256, mapping, days, revert

from EnumerableSet import EnumerableSet
from Time import Time

'''
 * @dev the data struct representing a pending withdrawal request
'''
class WithdrawalRequest:
    def __init__(self,
        x = {
            'provider': None,
            'poolToken': None,
            'reserveToken': None,
            'createdAt': 0,
            'poolTokenAmount': 0,
            'reserveTokenAmount': 0
        }
    ) -> None:
        self.provider = x['provider']; # the liquidity provider
        self.poolToken = x['poolToken']; # the locked pool token
        self.reserveToken = x['reserveToken']; # the reserve token to withdraw
        self.createdAt = uint32(x['createdAt']); # the time when the request was created (Unix timestamp)
        self.poolTokenAmount = uint256(x['poolTokenAmount']); # the locked pool token amount
        self.reserveTokenAmount = uint256(x['reserveTokenAmount']); # the expected reserve token amount to withdraw

'''
 * @dev the data struct representing a completed withdrawal request
'''
class CompletedWithdrawal:
    def __init__(self,
        x = {
            'poolToken': None,
            'poolTokenAmount': 0,
            'reserveTokenAmount': 0
        }
    ) -> None:
        self.poolToken = x['poolToken']; # the withdraw pool token
        self.poolTokenAmount = uint256(x['poolTokenAmount']); # the original pool token amount in the withdrawal request
        self.reserveTokenAmount = uint256(x['reserveTokenAmount']); # the original reserve token amount at the time of the withdrawal init request

'''
 * @dev Pending Withdrawals contract
'''
class PendingWithdrawals(Time):
    DEFAULT_LOCK_DURATION = uint32(7 * days);

    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initNetwork,
        initBNT,
        initBNTPool
    ) -> None:
        super().__init__()
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
        self._setLockDuration(self.DEFAULT_LOCK_DURATION);

        # the lock duration
        self._lockDuration = uint32()

        # a mapping between accounts and their pending withdrawal requests
        self._nextWithdrawalRequestId = uint256()
        self._withdrawalRequestIdsByProvider = mapping(lambda: EnumerableSet());
        self._withdrawalRequests = mapping(lambda: WithdrawalRequest());

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc IPendingWithdrawals
    '''
    def lockDuration(self) -> (uint):
        return self._lockDuration;

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
    def completeWithdrawal(self, _msgSender,
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
        request.poolToken.approve(_msgSender, request.poolTokenAmount);

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

        return self._canWithdrawAt(self._time(), request.createdAt);

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

        self._lockDuration = newLockDuration;

    '''
     * @dev initiates liquidity withdrawal
    '''
    def _initWithdrawal(self,
        provider,
        poolToken,
        poolTokenAmount
    ) -> (uint):
        # record the current withdrawal request alongside previous pending withdrawal requests
        id = self._nextWithdrawalRequestId;
        self._nextWithdrawalRequestId += 1;

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
        request.poolToken.safeTransfer(request.provider, request.poolTokenAmount);

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
