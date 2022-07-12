from bancor_research.bancor_emulator.solidity import uint, uint256, mapping, address, revert
from bancor_research.bancor_emulator.utils import parse

from bancor_research.bancor_emulator.Math import Math
from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION
from bancor_research.bancor_emulator.MathEx import MathEx
from bancor_research.bancor_emulator.Vault import Vault
from bancor_research.bancor_emulator.PoolToken import PoolToken as IPoolToken

'''
 * @dev BNT Pool contract
'''
class BNTPool(Vault):
    class InternalWithdrawalAmounts:
        def __init__(self, x = None) -> None:
            self.bntAmount = parse(uint256, x, 'bntAmount');
            self.withdrawalFeeAmount = parse(uint256, x, 'withdrawalFeeAmount');

    '''
     * @dev a "virtual" constructor that is only used to set immutable state variables
    '''
    def __init__(self,
        initNetwork,
        initBNTGovernance,
        initVBNTGovernance,
        initNetworkSettings,
        initMasterVault,
        initBNTPoolToken
    ) -> None:
        Vault.__init__(self, initBNTGovernance, initVBNTGovernance)

        self._network = initNetwork;
        self._networkSettings = initNetworkSettings;
        self._masterVault = initMasterVault;
        self._poolToken = initBNTPoolToken;

    '''
     * @dev fully initializes the contract and its parents
    '''
    def initialize(self) -> None:
        self.__BNTPool_init();

    # solhint-disable func-name-mixedcase

    '''
     * @dev initializes the contract and its parents
    '''
    def __BNTPool_init(self) -> None:
        self.__BNTPool_init_unchained();

    '''
     * @dev performs contract-specific initialization
    '''
    def __BNTPool_init_unchained(self) -> None:
        self._stakedBalance = uint256()
        self._currentPoolFunding = mapping(lambda: uint256())

    # solhint-enable func-name-mixedcase

    '''
     * @inheritdoc Upgradeable
    '''
    def version(self) -> (int):
        return 3;

    '''
     * @inheritdoc IBNTPool
    '''
    def poolToken(self) -> (IPoolToken):
        return self._poolToken;

    '''
     * @inheritdoc IBNTPool
    '''
    def stakedBalance(self) -> (uint):
        return self._stakedBalance.clone();

    '''
     * @inheritdoc IBNTPool
    '''
    def currentPoolFunding(self, pool) -> (uint):
        return self._currentPoolFunding[pool].clone();

    '''
     * @inheritdoc IBNTPool
    '''
    def availableFunding(self, pool) -> (uint):
        return MathEx.subMax0(self._networkSettings.poolFundingLimit(pool), self._currentPoolFunding[pool]);

    '''
     * @inheritdoc IBNTPool
    '''
    def poolTokenToUnderlying(self, poolTokenAmount) -> (uint):
        return self._poolTokenToUnderlying(poolTokenAmount);

    '''
     * @inheritdoc IBNTPool
    '''
    def underlyingToPoolToken(self, bntAmount) -> (uint):
        return self._underlyingToPoolToken(bntAmount);

    '''
     * @inheritdoc IBNTPool
    '''
    def poolTokenAmountToBurn(self, bntAmountToDistribute) -> (uint):
        if (bntAmountToDistribute == 0):
            return uint256(0);

        poolTokenSupply = self._poolToken.totalSupply();
        val = bntAmountToDistribute * poolTokenSupply;

        return MathEx.mulDivF(
            val,
            poolTokenSupply,
            val + self._stakedBalance * (poolTokenSupply - self._poolToken.balanceOf(address(self)))
        );

    '''
     * @inheritdoc IBNTPool
    '''
    def mint(self, recipient, bntAmount):
        self._bntGovernance.mint(recipient, bntAmount);

    '''
     * @inheritdoc IBNTPool
    '''
    def burnFromVault(self, bntAmount):
        self._masterVault.burn(address(self._bnt), bntAmount);

    '''
     * @inheritdoc IBNTPool
    '''
    def depositFor(self,
        contextId,
        provider,
        bntAmount,
        isMigrating,
        originalVBNTAmount
    ):
        # calculate the required pool token amount
        currentStakedBalance = self._stakedBalance;
        poolTokenTotalSupply = self._poolToken.totalSupply();
        if (poolTokenTotalSupply == 0 and currentStakedBalance > 0):
            revert("InvalidStakedBalance");

        poolTokenAmount = self._underlyingToPoolToken_(bntAmount, poolTokenTotalSupply, currentStakedBalance);

        # if the protocol doesn't have enough pool tokens, mint new ones
        poolTokenBalance = self._poolToken.balanceOf(address(self));
        if (poolTokenAmount > poolTokenBalance):
            newPoolTokenAmount = poolTokenAmount - poolTokenBalance;
            increaseStakedBalanceAmount = self._poolTokenToUnderlying_(
                newPoolTokenAmount,
                currentStakedBalance,
                poolTokenTotalSupply
            );

            # update the staked balance
            self._stakedBalance = currentStakedBalance + increaseStakedBalanceAmount;

            # mint pool tokens to the protocol
            self._poolToken.mint(address(self), newPoolTokenAmount);

        # transfer pool tokens from the protocol to the provider
        self._poolToken.transfer(provider, poolTokenAmount);

        # burn the previously received BNT
        self._bntGovernance.burn(bntAmount);

        vbntAmount = poolTokenAmount;

        # the provider should receive pool tokens and vBNT in equal amounts. since the provider might already have
        # some vBNT during migration, the contract only mints the delta between the full amount and the amount the
        # provider already has
        if (isMigrating):
            vbntAmount = MathEx.subMax0(vbntAmount, originalVBNTAmount);

        # mint vBNT to the provider
        if (vbntAmount > 0):
            self._vbntGovernance.mint(provider, vbntAmount);

        return poolTokenAmount;

    '''
     * @inheritdoc IBNTPool
    '''
    def withdraw(self,
        contextId,
        provider,
        poolTokenAmount,
        bntAmount
    ):
        # ensure that the provided amounts correspond to the state of the pool. Note the pool tokens should
        # have been already deposited back from the network
        underlyingAmount = self._poolTokenToUnderlying(poolTokenAmount);
        if (bntAmount > underlyingAmount):
            revert("InvalidParam");

        amounts = self._withdrawalAmounts(bntAmount);

        # burn the respective vBNT amount
        self._vbntGovernance.burn(poolTokenAmount);

        # mint BNT to the provider
        self._bntGovernance.mint(provider, amounts.bntAmount);

        return amounts.bntAmount;

    '''
     * @inheritdoc IBNTPool
    '''
    def withdrawalAmount(self, poolTokenAmount):
        return self._withdrawalAmounts(self._poolTokenToUnderlying(poolTokenAmount)).bntAmount;

    '''
     * @inheritdoc IBNTPool
    '''
    def requestFunding(self,
        contextId,
        pool,
        bntAmount
    ):
        currentFunding = self._currentPoolFunding[pool];
        fundingLimit = self._networkSettings.poolFundingLimit(pool);
        newFunding = currentFunding + bntAmount;

        # verify that the new funding amount doesn't exceed the limit
        if (newFunding > fundingLimit):
            revert("FundingLimitExceeded");

        # calculate the pool token amount to mint
        currentStakedBalance = self._stakedBalance;
        poolTokenAmount = uint256();
        poolTokenTotalSupply = self._poolToken.totalSupply();
        if (poolTokenTotalSupply == 0 and currentStakedBalance > 0):
            revert("InvalidStakedBalance");

        poolTokenAmount = self._underlyingToPoolToken_(bntAmount, poolTokenTotalSupply, currentStakedBalance);

        # update the staked balance
        newStakedBalance = currentStakedBalance + bntAmount;
        self._stakedBalance = newStakedBalance;

        # update the current funding amount
        self._currentPoolFunding[pool] = newFunding;

        # mint pool tokens to the protocol
        self._poolToken.mint(address(self), poolTokenAmount);

        # mint BNT to the vault
        self._bntGovernance.mint(address(self._masterVault), bntAmount);

    '''
     * @inheritdoc IBNTPool
    '''
    def renounceFunding(self,
        contextId,
        pool,
        bntAmount
    ):
        currentStakedBalance = self._stakedBalance;

        # calculate the final amount to deduct from the current pool funding
        currentFunding = self._currentPoolFunding[pool];
        reduceFundingAmount = Math.min(currentFunding, bntAmount);

        # calculate the amount of pool tokens to burn
        # note that the given amount can exceed the total available but the request shouldn't fail
        poolTokenTotalSupply = self._poolToken.totalSupply();
        poolTokenAmount = self._underlyingToPoolToken_(
            reduceFundingAmount,
            poolTokenTotalSupply,
            currentStakedBalance
        );

        # ensure the amount of pool tokens doesn't exceed the total available
        poolTokenAmount = Math.min(poolTokenAmount, self._poolToken.balanceOf(address(self)));

        # calculate the final amount to deduct from the staked balance
        reduceStakedBalanceAmount = self._poolTokenToUnderlying_(
            poolTokenAmount,
            currentStakedBalance,
            poolTokenTotalSupply
        );

        # update the current pool funding. Note that the given amount can exceed the funding amount but the
        # request shouldn't fail (and the funding amount cannot get negative)
        self._currentPoolFunding[pool] = currentFunding - reduceFundingAmount;

        # update the staked balance
        newStakedBalance = currentStakedBalance - reduceStakedBalanceAmount;
        self._stakedBalance = newStakedBalance;

        # burn pool tokens from the protocol
        self._poolToken.burn(poolTokenAmount);

        # burn all BNT from the master vault
        self._masterVault.burn(address(self._bnt), bntAmount);

    '''
     * @inheritdoc IBNTPool
    '''
    def onFeesCollected(self,
        pool,
        feeAmount,
        isTradeFee
    ):
        if (feeAmount == 0):
            return;

        # increase the staked balance by the given amount
        self._stakedBalance += feeAmount;

        if (isTradeFee):
            # increase the current funding for the specified pool by the given amount
            self._currentPoolFunding[pool] += feeAmount;

    '''
     * @dev converts the specified pool token amount to the underlying BNT amount
    '''
    def _poolTokenToUnderlying(self, poolTokenAmount) -> (uint):
        return self._poolTokenToUnderlying_(poolTokenAmount, self._stakedBalance, self._poolToken.totalSupply());

    '''
     * @dev converts the specified pool token amount to the underlying BNT amount
    '''
    def _poolTokenToUnderlying_(self,
        poolTokenAmount,
        currentStakedBalance,
        poolTokenTotalSupply
    ) -> (uint):
        # if no pool token supply exists yet, use a one-to-one pool token to BNT rate
        if (poolTokenTotalSupply == 0):
            return poolTokenAmount;

        return MathEx.mulDivF(poolTokenAmount, currentStakedBalance, poolTokenTotalSupply);

    '''
     * @dev converts the specified underlying BNT amount to pool token amount
    '''
    def _underlyingToPoolToken(self, bntAmount) -> (uint):
        return self._underlyingToPoolToken_(bntAmount, self._poolToken.totalSupply(), self._stakedBalance);

    '''
     * @dev converts the specified underlying BNT amount to pool token amount
    '''
    def _underlyingToPoolToken_(self,
        bntAmount,
        poolTokenTotalSupply,
        currentStakedBalance
    ) -> (uint):
        # if no pool token supply exists yet, use a one-to-one pool token to BNT rate
        if (poolTokenTotalSupply == 0):
            return bntAmount;

        return MathEx.mulDivC(bntAmount, poolTokenTotalSupply, currentStakedBalance);

    '''
     * @dev returns withdrawal amounts
    '''
    def _withdrawalAmounts(self, bntAmount) -> (InternalWithdrawalAmounts):
        # deduct the exit fee from BNT amount
        withdrawalFeeAmount = MathEx.mulDivF(bntAmount, self._networkSettings.withdrawalFeePPM(), PPM_RESOLUTION);

        bntAmount -= withdrawalFeeAmount;

        return self.InternalWithdrawalAmounts({ 'bntAmount': bntAmount, 'withdrawalFeeAmount': withdrawalFeeAmount });
