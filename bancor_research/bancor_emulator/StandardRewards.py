from bancor_research.bancor_emulator.solidity import uint, uint32, uint256, address, mapping, revert
from bancor_research.bancor_emulator.utils import contract, parse

from bancor_research.bancor_emulator.EnumerableSet import EnumerableSet
from bancor_research.bancor_emulator.Math import Math
from bancor_research.bancor_emulator.Time import Time

class Rewards:
    def __init__(self, x = None) -> None:
        self.lastUpdateTime = parse(uint32, x, 'lastUpdateTime');
        self.rewardPerToken = parse(uint256, x, 'rewardPerToken');

class ProgramData:
    def __init__(self, x = None) -> None:
        self.id = parse(uint256, x, 'id');
        self.pool = parse(address, x, 'pool');
        self.poolToken = parse(address, x, 'poolToken');
        self.rewardsToken = parse(address, x, 'rewardsToken');
        self.isPaused = parse(bool, x, 'isPaused');
        self.startTime = parse(uint32, x, 'startTime');
        self.endTime = parse(uint32, x, 'endTime');
        self.rewardRate = parse(uint256, x, 'rewardRate');
        self.remainingRewards = parse(uint256, x, 'remainingRewards');

class ProviderRewards:
    def __init__(self, x = None) -> None:
        self.rewardPerTokenPaid = parse(uint256, x, 'rewardPerTokenPaid');
        self.pendingRewards = parse(uint256, x, 'pendingRewards');
        self.stakedAmount = parse(uint256, x, 'stakedAmount');

class StakeAmounts:
    def __init__(self, x = None) -> None:
        self.stakedRewardAmount = parse(uint256, x, 'stakedRewardAmount');
        self.poolTokenAmount = parse(uint256, x, 'poolTokenAmount');

'''
 * @dev Standard Rewards contract
'''
class StandardRewards(contract, Time):
    class ClaimData:
        def __init__(self, x = None) -> None:
            self.reward = parse(uint256, x, 'reward');
            self.stakedAmount = parse(uint256, x, 'stakedAmount');

    # since we will be dividing by the total amount of protected tokens in units of wei, we can encounter cases
    # where the total amount in the denominator is higher than the product of the rewards rate and staking duration. In
    # order to avoid this imprecision, we will amplify the reward rate by the units amount.
    REWARD_RATE_FACTOR = uint256(10 ** 18);

    INITIAL_PROGRAM_ID = uint256(1);

    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initNetwork,
        initNetworkSettings,
        initBNTGovernance,
        initVBNT,
        initBNTPool
    ) -> None:
        contract.__init__(self)
        Time.__init__(self)

        self._network = initNetwork;
        self._networkSettings = initNetworkSettings;
        self._bntGovernance = initBNTGovernance;
        self._bnt = initBNTGovernance.token();
        self._vbnt = initVBNT;
        self._bntPoolToken = initBNTPool.poolToken();

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__StandardRewards_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __StandardRewards_init(self) -> None:
       self.__StandardRewards_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __StandardRewards_init_unchained(self) -> None:
        self._nextProgramId = self.INITIAL_PROGRAM_ID.clone();

        # a mapping between providers and the program IDs of the program they are participating in
        self._programIdsByProvider = mapping(lambda: EnumerableSet());

        # a mapping between program IDs and program data
        self._programs = mapping(lambda: ProgramData());

        # a mapping between pools and their latest programs
        self._latestProgramIdByPool = mapping(lambda: uint256());

        # a mapping between programs and their respective rewards data
        self._programRewards = mapping(lambda: Rewards());

        # a mapping between providers, programs and their respective rewards data
        self._providerRewards = mapping(lambda: mapping(lambda: ProviderRewards()));

        # a mapping between programs and their total stakes
        self._programStakes = mapping(lambda: uint256());

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 4;

    '''
     * @inheritdoc IStandardRewards
    '''
    def programIds(self) -> (list):
        length = self._nextProgramId - self.INITIAL_PROGRAM_ID;
        return [self.INITIAL_PROGRAM_ID + i for i in range(length)]

    '''
     * @inheritdoc IStandardRewards
    '''
    def programs(self, ids) -> (list):
        length = len(ids);
        return [self._programs[ids[i]] for i in range(length)]

    '''
     * @inheritdoc IStandardRewards
    '''
    def providerProgramIds(self, provider) -> (list):
        return self._programIdsByProvider[provider].values();

    '''
     * @inheritdoc IStandardRewards
    '''
    def programRewards(self, id) -> (Rewards):
        return self._programRewards[id];

    '''
     * @inheritdoc IStandardRewards
    '''
    def providerRewards(self, provider, id) -> (ProviderRewards):
        return self._providerRewards[provider][id];

    '''
     * @inheritdoc IStandardRewards
    '''
    def programStake(self, id) -> (uint):
        return self._programStakes[id].clone();

    '''
     * @inheritdoc IStandardRewards
    '''
    def providerStake(self, provider, id) -> (uint):
        return self._providerRewards[provider][id].stakedAmount.clone();

    '''
     * @inheritdoc IStandardRewards
    '''
    def isProgramActive(self, id) -> (bool):
        return self._isProgramActive(self._programs[id]);

    '''
     * @inheritdoc IStandardRewards
    '''
    def isProgramPaused(self, id) -> (bool):
        return self._isProgramPaused(self._programs[id]);

    '''
     * @inheritdoc IStandardRewards
    '''
    def latestProgramId(self, pool) -> (uint):
        return self._latestProgramIdByPool[pool].clone();

    '''
     * @inheritdoc IStandardRewards
    '''
    def createProgram(self,
        pool,
        totalRewards,
        startTime,
        endTime
    ) -> (uint):
        if (not (self._time() <= startTime and startTime < endTime)):
            revert("InvalidParam");

        # ensure that no program exists for the specific pool
        if (self._isProgramActive(self._programs[self._latestProgramIdByPool[pool]])):
            revert("AlreadyExists");

        poolToken = address(0);
        if (pool is (self._bnt)):
            poolToken = self._bntPoolToken;
        else:
            if (not self._networkSettings.isTokenWhitelisted(pool)):
                revert("NotWhitelisted");

            poolToken = self._network.collectionByPool(pool).poolToken(pool);

        id = self._nextProgramId.clone(); self._nextProgramId += 1;
        rewardRate = totalRewards / (endTime - startTime);

        self._programs[id] = ProgramData({
            'id': id,
            'pool': pool,
            'poolToken': poolToken,
            'rewardsToken': address(self._bnt),
            'isPaused': False,
            'startTime': startTime,
            'endTime': endTime,
            'rewardRate': rewardRate,
            'remainingRewards': rewardRate * (endTime - startTime)
        });

        # set the program as the latest program of the pool
        self._latestProgramIdByPool[pool] = id;

        return id;

    '''
     * @inheritdoc IStandardRewards
    '''
    def terminateProgram(self, id) -> None:
        p = self._programs[id];

        self._verifyProgramActive(p);

        # unset the program from being the latest program of the pool
        del self._latestProgramIdByPool[p.pool];

        endTime = p.endTime;

        # reduce the remaining rewards for the token by the remaining rewards and stop rewards accumulation
        p.remainingRewards -= self._remainingRewards(p);
        p.endTime = self._time();

    '''
     * @inheritdoc IStandardRewards
    '''
    def pauseProgram(self, id, pause) -> None:
        p = self._programs[id];

        self._verifyProgramExists(p);

        prevStatus = p.isPaused;
        if (prevStatus == pause):
            return;

        p.isPaused = pause;

    '''
     * @inheritdoc IStandardRewards
    '''
    def join(self, id, poolTokenAmount) -> None:
        p = self._programs[id];

        self._verifyProgramActiveAndNotPaused(p);

        self._join(self.msg_sender, p, poolTokenAmount, self.msg_sender);

    '''
     * @inheritdoc IStandardRewards
    '''
    def leave(self, id, poolTokenAmount) -> None:
        p = self._programs[id];

        self._verifyProgramExists(p);

        self._leave(self.msg_sender, p, poolTokenAmount);

    '''
     * @inheritdoc IStandardRewards
    '''
    def depositAndJoin(self, id, tokenAmount) -> None:
        p = self._programs[id];

        self._verifyProgramActiveAndNotPaused(p);

        self._depositAndJoin(self.msg_sender, p, tokenAmount);

    '''
     * @inheritdoc IStandardRewards
    '''
    def pendingRewards(self, provider, ids) -> (uint):
        reward = uint256(0);

        for i in range(len(ids)):
            id = ids[i];

            p = self._programs[id];

            self._verifyProgramExists(p);

            newRewardPerToken = self._rewardPerToken(p, self._programRewards[id]);
            providerRewardsData = self._providerRewards[provider][id];

            reward += self._pendingRewards(newRewardPerToken, providerRewardsData);

        return reward;

    '''
     * @inheritdoc IStandardRewards
    '''
    def claimRewards(self, ids) -> (uint):
        reward = self._claimRewards(self.msg_sender, ids, False);

        if (reward == 0):
            return uint256(0);

        self._bntGovernance.mint(self.msg_sender, reward);

        return reward;

    '''
     * @inheritdoc IStandardRewards
    '''
    def stakeRewards(self, ids) -> (StakeAmounts):
        reward = self._claimRewards(self.msg_sender, ids, True);

        if (reward == 0):
            return StakeAmounts({ 'stakedRewardAmount': 0, 'poolTokenAmount': 0 });

        self._bntGovernance.mint(address(self), reward);

        # deposit provider's tokens to the network. Please note, that since we're staking rewards, then the deposit
        # should come from the contract itself, but the pool tokens should be sent to the provider directly
        poolTokenAmount = self._deposit(self.msg_sender, address(self), False, address(self._bnt), reward);

        return StakeAmounts({ 'stakedRewardAmount': reward, 'poolTokenAmount': poolTokenAmount });

    '''
     * @dev adds provider's stake to the program
    '''
    def _join(self,
        provider,
        p,
        poolTokenAmount,
        payer
    ) -> None:
        # take a snapshot of the existing rewards (before increasing the stake)
        data = self._snapshotRewards(p, provider);

        # update both program and provider stakes
        self._programStakes[p.id] += poolTokenAmount;

        prevStake = data.stakedAmount;
        data.stakedAmount = prevStake + poolTokenAmount;

        # unless the payer is the contract itself (in which case, no additional transfer is required), transfer the
        # tokens from the payer (we aren't using safeTransferFrom, since the PoolToken is a fully compliant ERC20 token
        # contract)
        if (payer != address(self)):
            p.poolToken.transferFrom(payer, address(self), poolTokenAmount);

        # add the program to the provider's program list
        self._programIdsByProvider[provider].add(p.id);

    '''
     * @dev removes (some of) provider's stake from the program
    '''
    def _leave(self,
        provider,
        p,
        poolTokenAmount
    ) -> None:
        # take a snapshot of the existing rewards (before decreasing the stake)
        data = self._snapshotRewards(p, provider);

        # update both program and provider stakes
        self._programStakes[p.id] -= poolTokenAmount;

        remainingStake = data.stakedAmount - poolTokenAmount;
        data.stakedAmount = remainingStake;

        # transfer the tokens to the provider (we aren't using safeTransfer, since the PoolToken is a fully
        # compliant ERC20 token contract)
        p.poolToken.transfer(provider, poolTokenAmount);

        # if the provider has removed all of its stake and there are no pending rewards - remove the program from the
        # provider's program list
        if (remainingStake == 0 and data.pendingRewards == 0):
            self._programIdsByProvider[provider].remove(p.id);

    '''
     * @dev deposits provider's stake to the network and returns the received pool token amount
    '''
    def _deposit(self,
        provider,
        payer,
        keepPoolTokens,
        pool,
        tokenAmount
    ) -> (uint):
        poolTokenAmount = uint256(0);
        recipient = address(self) if keepPoolTokens else provider;
        externalPayer = payer != address(self);

        # unless the payer is the contract itself (e.g., during the staking process), in which case the tokens were
        # already claimed and pending in the contract - get the tokens from the provider
        if (externalPayer):
            pool.safeTransferFrom(payer, address(self), tokenAmount);

        pool.ensureApprove(address(self._network), tokenAmount);
        poolTokenAmount = self._network.depositFor(recipient, pool, tokenAmount);

        if (keepPoolTokens and pool is (self._bnt)):
            self._vbnt.safeTransfer(provider, poolTokenAmount);

        return poolTokenAmount;

    '''
     * @dev deposits and adds provider's stake to the program
    '''
    def _depositAndJoin(self,
        provider,
        p,
        tokenAmount
    ) -> None:
        # deposit provider's tokens to the network and let the contract itself to claim the pool tokens so that it can
        # immediately add them to a program
        poolTokenAmount = self._deposit(provider, provider, True, p.pool, tokenAmount);

        # join the existing program, but ensure not to attempt to transfer the tokens from the provider by setting the
        # payer as the contract itself
        self._join(provider, p, poolTokenAmount, address(self));

    '''
     * @dev claims rewards
    '''
    def _claimRewards(self,
        provider,
        ids,
        stake
    ) -> (uint):
        reward = uint256(0);

        for i in range(len(ids)):
            p = self._programs[ids[i]];

            self._verifyProgramNotPaused(p);

            claimData = self._claimRewards_(provider, p);

            if (claimData.reward > 0):
                remainingRewards = p.remainingRewards;

                # a sanity check that the reward amount doesn't exceed the remaining rewards per program
                if (remainingRewards < claimData.reward):
                    revert("RewardsTooHigh");

                # decrease the remaining rewards per program
                self._programs[ids[i]].remainingRewards = remainingRewards - claimData.reward;

                # collect same-reward token rewards
                reward += claimData.reward;

            # if the program is no longer active, has no stake left, and there are no pending rewards - remove the
            # program from the provider's program list
            if (not self._isProgramActive(p) and claimData.stakedAmount == 0):
                self._programIdsByProvider[provider].remove(p.id);

        return reward;

    '''
     * @dev claims rewards and returns the received and the pending reward amounts
    '''
    def _claimRewards_(self, provider, p) -> (ClaimData):
        providerRewardsData = self._snapshotRewards(p, provider);

        reward = providerRewardsData.pendingRewards;

        providerRewardsData.pendingRewards = uint256(0);

        return self.ClaimData({ 'reward': reward, 'stakedAmount': providerRewardsData.stakedAmount });

    '''
     * @dev returns whether the specified program is active
    '''
    def _isProgramActive(self, p) -> (bool):
        currTime = self._time();

        return \
            self._programExists(p) and \
            p.startTime <= currTime and \
            currTime <= p.endTime and \
            self._latestProgramIdByPool[p.pool] == p.id;

    '''
     * @dev returns whether the specified program is paused
    '''
    def _isProgramPaused(self, p) -> (bool):
        return p.isPaused;

    '''
     * @dev returns whether or not a given program exists
    '''
    def _programExists(self, p) -> (bool):
        return address(p.pool) != address(0);

    '''
     * @dev verifies that a program exists
    '''
    def _verifyProgramExists(self, p) -> None:
        if (not self._programExists(p)):
            revert("DoesNotExist");

    '''
     * @dev verifies that a program exists, and active
    '''
    def _verifyProgramActive(self, p) -> None:
        self._verifyProgramExists(p);

        if (not self._isProgramActive(p)):
            revert("ProgramInactive");

    '''
     * @dev verifies that a program is not paused
    '''
    def _verifyProgramNotPaused(self, p) -> None:
        self._verifyProgramExists(p);

        if (p.isPaused):
            revert("ProgramSuspended");

    '''
     * @dev verifies that a program exists, active, and not paused
    '''
    def _verifyProgramActiveAndNotPaused(self, p) -> None:
        self._verifyProgramActive(p);
        self._verifyProgramNotPaused(p);

    '''
     * @dev returns the remaining rewards of given program
    '''
    def _remainingRewards(self, p) -> (uint):
        currTime = self._time();

        return p.rewardRate * (p.endTime - currTime) if p.endTime > currTime else uint256(0);

    '''
     * @dev updates program and provider's rewards
    '''
    def _snapshotRewards(self, p, provider) -> (ProviderRewards):
        rewards = self._programRewards[p.id];

        newRewardPerToken = self._rewardPerToken(p, rewards);
        if (newRewardPerToken != rewards.rewardPerToken):
            rewards.rewardPerToken = newRewardPerToken;

        newUpdateTime = uint32(Math.min(self._time(), p.endTime));
        if (rewards.lastUpdateTime < newUpdateTime):
            rewards.lastUpdateTime = newUpdateTime;

        providerRewardsData = self._providerRewards[provider][p.id];

        newPendingRewards = self._pendingRewards(newRewardPerToken, providerRewardsData);
        if (newPendingRewards != 0):
            providerRewardsData.pendingRewards = newPendingRewards;

        providerRewardsData.rewardPerTokenPaid = newRewardPerToken;

        return providerRewardsData;

    '''
     * @dev calculates current reward per-token amount
    '''
    def _rewardPerToken(self, p, rewards) -> (uint):
        currTime = self._time();
        if (currTime < p.startTime):
            return uint256(0);

        totalStaked = self._programStakes[p.id];
        if (totalStaked == 0):
            return rewards.rewardPerToken;

        stakingEndTime = Math.min(currTime, p.endTime);
        stakingStartTime = Math.max(p.startTime, rewards.lastUpdateTime);

        return \
            rewards.rewardPerToken + \
            (((stakingEndTime - stakingStartTime) * p.rewardRate * self.REWARD_RATE_FACTOR) / totalStaked);

    '''
     * @dev calculates provider's pending rewards
    '''
    def _pendingRewards(self, updatedRewardPerToken, providerRewardsData) -> (uint):
        return \
            providerRewardsData.pendingRewards + \
            (providerRewardsData.stakedAmount * (updatedRewardPerToken - providerRewardsData.rewardPerTokenPaid)) / \
            self.REWARD_RATE_FACTOR;

    '''
     * @dev returns whether the specified array has duplicates
    '''
    def _isArrayUnique(self, ids) -> (bool):
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if (ids[i] == ids[j]):
                    return False;

        return True;

    '''
     * @dev post upgrade callback
    '''
    def _postUpgrade(self,
        data
    ) -> None:
        # since we have renamed the "isEnabled" field to "isPaused", we need to manually inverse all exiting programs
        # values (which is still manageable, as at the time of this upgrade - there were only 8 programs)
        length = self._nextProgramId - self.INITIAL_PROGRAM_ID;
        for i in range(length):
            id = uint256(i) + self.INITIAL_PROGRAM_ID;

            self._programs[id].isPaused = False;
