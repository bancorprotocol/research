from bancor_research.bancor_emulator.solidity import uint, uint8, uint16, uint32, uint256, hours, address, mapping, revert
from bancor_research.bancor_emulator.utils import contract, parse

from bancor_research.bancor_emulator.EnumerableSet import EnumerableSet
from bancor_research.bancor_emulator.Math import Math
from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION
from bancor_research.bancor_emulator.Time import Time
from bancor_research.bancor_emulator.Vault import Vault as IVault
from bancor_research.bancor_emulator.RewardsMath import RewardsMath

# distribution types
FLAT_DISTRIBUTION = uint8(0);
EXP_DECAY_DISTRIBUTION = uint8(1);

class ProgramData:
    def __init__(self, x = None) -> None:
        self.startTime = parse(uint32, x, 'startTime');
        self.endTime = parse(uint32, x, 'endTime');
        self.halfLife = parse(uint32, x, 'halfLife');
        self.prevDistributionTimestamp = parse(uint32, x, 'prevDistributionTimestamp');
        self.poolToken = parse(address, x, 'poolToken');
        self.isPaused = parse(bool, x, 'isPaused');
        self.distributionType = parse(uint8, x, 'distributionType');
        self.totalRewards = parse(uint256, x, 'totalRewards');
        self.remainingRewards = parse(uint256, x, 'remainingRewards');

'''
 * @dev Auto-compounding Rewards contract
'''
class AutoCompoundingRewards(contract, Time):
    # the default number of programs to auto-process the rewards for
    DEFAULT_AUTO_PROCESS_REWARDS_COUNT = uint8(3);

    # the minimum time elapsed before the rewards of a program can be auto-processed
    AUTO_PROCESS_REWARDS_MIN_TIME_DELTA = uint16(1) * hours;

    # the factor used to calculate the maximum number of programs to attempt to auto-process in a single attempt
    AUTO_PROCESS_MAX_PROGRAMS_FACTOR = uint8(2);

    # if a program is attempting to burn a total supply percentage equal or higher to this number,
    # the program will terminate
    SUPPLY_BURN_TERMINATION_THRESHOLD_PPM = uint32(500000);

    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initNetwork,
        initNetworkSettings,
        initBNT,
        initBNTPool,
        initExternalRewardsVault
    ) -> None:
        contract.__init__(self)
        Time.__init__(self)

        self._network = initNetwork;
        self._networkSettings = initNetworkSettings;
        self._bnt = initBNT;
        self._bntPool = initBNTPool;
        self._bntPoolToken = initBNTPool.poolToken();
        self._externalRewardsVault = initExternalRewardsVault;

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__AutoCompoundingRewards_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __AutoCompoundingRewards_init(self) -> None:
        self.__AutoCompoundingRewards_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __AutoCompoundingRewards_init_unchained(self) -> None:
        # a mapping between pools and programs
        self._programs = mapping(lambda: ProgramData());

        # a set of all pools that have a rewards program associated with them
        self._pools = EnumerableSet();

        # the number of programs to auto-process the rewards for
        self._autoProcessRewardsCount = uint256();

        # the index of the next program to auto-process the rewards for
        self._autoProcessRewardsIndex = uint256();

        self._setAutoProcessRewardsCount(self.DEFAULT_AUTO_PROCESS_REWARDS_COUNT);

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 1;

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def program(self, pool) -> (ProgramData):
        return self._programs[pool];

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def programs(self) -> (list):
        return self._pools._programs();

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def pools(self) -> (list):
        return self._pools.values();

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def autoProcessRewardsCount(self) -> (uint):
        return self._autoProcessRewardsCount.clone();

    '''
     * @dev sets the number of programs to auto-process the rewards for
     *
     * requirements:
     *
     * - the caller must be the admin of the contract
    '''
    def setAutoProcessRewardsCount(self, newCount) -> None:
        self._setAutoProcessRewardsCount(newCount);

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def isProgramActive(self, pool) -> (bool):
        p = self._programs[pool];

        if (not self._programExists(p)):
            return False;

        currTime = self._time();

        if (p.distributionType == EXP_DECAY_DISTRIBUTION):
            return p.startTime <= currTime;

        return p.startTime <= currTime and currTime <= p.endTime;

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def isProgramPaused(self, pool) -> (bool):
        return self._programs[pool].isPaused;

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def createFlatProgram(self,
        pool,
        totalRewards,
        startTime,
        endTime
    ) -> None:
        if (startTime >= endTime):
            revert("InvalidParam");

        self._createProgram(pool, totalRewards, FLAT_DISTRIBUTION, startTime, endTime, 0);

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def createExpDecayProgram(self,
        pool,
        totalRewards,
        startTime,
        halfLife
    ) -> None:
        if (halfLife == 0):
            revert("InvalidParam");

        self._createProgram(pool, totalRewards, EXP_DECAY_DISTRIBUTION, startTime, 0, halfLife);

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def terminateProgram(self, pool) -> None:
        self._terminateProgram(pool);

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def pauseProgram(self, pool, pause) -> None:
        p = self._programs[pool];

        if (not self._programExists(p)):
            revert("DoesNotExist");

        prevStatus = p.isPaused;
        if (prevStatus == pause):
            return;

        self._programs[pool].isPaused = pause;

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def autoProcessRewards(self) -> None:
        numOfPools = self._pools.length();
        index = self._autoProcessRewardsIndex.clone();
        count = self._autoProcessRewardsCount.clone();
        maxCount = Math.min(count * self.AUTO_PROCESS_MAX_PROGRAMS_FACTOR, numOfPools);

        for i in range(int(str(maxCount))):
            completed = self._processRewards((self._pools.at(index % numOfPools)), True);
            index += 1;
            if (completed):
                count -= 1;
                if (count == 0):
                    break;

        self._autoProcessRewardsIndex = index % numOfPools;

    '''
     * @inheritdoc IAutoCompoundingRewards
    '''
    def processRewards(self, pool) -> None:
        self._processRewards(pool, False);

    '''
     * @dev sets the number of programs to auto-process the rewards for
    '''
    def _setAutoProcessRewardsCount(self, newCount) -> None:
        prevCount = self._autoProcessRewardsCount;
        if (prevCount == newCount):
            return;

        self._autoProcessRewardsCount = newCount;

    '''
     * @dev processes the rewards of a given pool and returns true if the rewards processing was completed, and false
     * if it was skipped
    '''
    def _processRewards(self, pool, skipRecent) -> (bool):
        p = self._programs[pool];

        currTime = self._time();

        if (p.isPaused or currTime < p.startTime):
            return False;

        if (skipRecent and currTime < p.prevDistributionTimestamp + self.AUTO_PROCESS_REWARDS_MIN_TIME_DELTA):
            return False;

        tokenAmountToDistribute = self._tokenAmountToDistribute(p, currTime);
        if (tokenAmountToDistribute == 0):
            return True;

        poolTokenAmountToBurn = self._poolTokenAmountToBurn(pool, p, tokenAmountToDistribute);
        if (poolTokenAmountToBurn == 0):
            return True;

        # sanity check, if the amount to burn is equal or higher than the termination percentage
        # threshold, terminate the program
        if (
            poolTokenAmountToBurn * PPM_RESOLUTION >= p.poolToken.totalSupply() * self.SUPPLY_BURN_TERMINATION_THRESHOLD_PPM
        ):
            self._terminateProgram(pool);
            return False;

        rewardsVault = self._rewardsVault(pool);
        self._verifyFunds(poolTokenAmountToBurn, p.poolToken, rewardsVault);
        rewardsVault.burn(address(p.poolToken), poolTokenAmountToBurn);

        p.remainingRewards -= tokenAmountToDistribute;
        p.prevDistributionTimestamp = currTime;

        self._programs[pool] = p;

        return True;

    '''
     * @dev creates a rewards program for a given pool
    '''
    def _createProgram(self,
        pool,
        totalRewards,
        distributionType,
        startTime,
        endTime,
        halfLife
    ) -> None:
        if (self._programExists(self._programs[pool])):
            revert("AlreadyExists");

        poolToken = address(0);
        if (pool is (self._bnt)):
            poolToken = self._bntPoolToken;
        else:
            if (not self._networkSettings.isTokenWhitelisted(pool)):
                revert("NotWhitelisted");

            poolToken = self._network.collectionByPool(pool).poolToken(pool);

        if (startTime < self._time()):
            revert("InvalidParam");

        p = ProgramData({
            'startTime': startTime,
            'endTime': endTime,
            'halfLife': halfLife,
            'prevDistributionTimestamp': 0,
            'poolToken': poolToken,
            'isPaused': False,
            'distributionType': distributionType,
            'totalRewards': totalRewards,
            'remainingRewards': totalRewards
        });

        self._verifyFunds(self._poolTokenAmountToBurn(pool, p, totalRewards), poolToken, self._rewardsVault(pool));

        self._programs[pool] = p;

        assert(self._pools.add(address(pool)));

    '''
     * @dev terminates a rewards program
    '''
    def _terminateProgram(self, pool) -> None:
        p = self._programs[pool];

        if (not self._programExists(p)):
            revert("DoesNotExist");

        del self._programs[pool];

        assert(self._pools.remove(address(pool)));

    '''
     * @dev returns the amount of tokens to distribute
    '''
    def _tokenAmountToDistribute(self, p, currTime) -> (uint):
        prevTime = uint32(Math.max(p.prevDistributionTimestamp, p.startTime));

        if (p.distributionType == FLAT_DISTRIBUTION):
            currTimeElapsed = uint32(Math.min(currTime, p.endTime)) - p.startTime;
            prevTimeElapsed = uint32(Math.min(prevTime, p.endTime)) - p.startTime;
            return \
                RewardsMath.calcFlatRewards(p.totalRewards, currTimeElapsed - prevTimeElapsed, p.endTime - p.startTime);
        else:
            currTimeElapsed = currTime - p.startTime;
            prevTimeElapsed = prevTime - p.startTime;
            return \
                RewardsMath.calcExpDecayRewards(p.totalRewards, currTimeElapsed, p.halfLife) - \
                RewardsMath.calcExpDecayRewards(p.totalRewards, prevTimeElapsed, p.halfLife);

    '''
     * @dev returns the amount of pool tokens to burn
    '''
    def _poolTokenAmountToBurn(self,
        pool,
        p,
        tokenAmountToDistribute
    ) -> (uint):
        if (pool is (self._bnt)):
            return self._bntPool.poolTokenAmountToBurn(tokenAmountToDistribute);

        return \
            self._network.collectionByPool(pool).poolTokenAmountToBurn(
                pool,
                tokenAmountToDistribute,
                p.poolToken.balanceOf(address(self._externalRewardsVault))
            );

    '''
     * @dev returns whether or not a given program exists
    '''
    def _programExists(self, p) -> (bool):
        return address(p.poolToken) != address(0);

    '''
     * @dev returns the rewards vault for a given pool
    '''
    def _rewardsVault(self, pool) -> (IVault):
        return (self._bntPool) if pool is (self._bnt) else (self._externalRewardsVault);

    '''
     * @dev verifies that the rewards vault holds a sufficient amount of pool tokens
    '''
    def _verifyFunds(self,
        requiredAmount,
        poolToken,
        rewardsVault
    ) -> None:
        if (requiredAmount > poolToken.balanceOf(address(rewardsVault))):
            revert("InsufficientFunds");
