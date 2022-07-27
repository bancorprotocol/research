from bancor_research.bancor_emulator.solidity import uint

from bancor_research.bancor_emulator.FractionLibrary import Fraction256
from bancor_research.bancor_emulator.MathEx import MathEx

'''
 * @dev This library supports the calculation of staking rewards
'''
class RewardsMath:
    '''
        * @dev returns the amount of rewards distributed on a flat amount ratio
    '''
    def calcFlatRewards(
        totalRewards,
        timeElapsed,
        programDuration
    ) -> (uint):
        # ensures that the function never returns more than the total rewards
        assert(timeElapsed <= programDuration);
        return MathEx.mulDivF(totalRewards, timeElapsed, programDuration);

    '''
        * @dev returns the amount of rewards distributed after a given time period since deployment has elapsed
        *
        * the returned value is calculated as `totalRewards * (1 - 1 / 2 ^ (timeElapsed / halfLife))`
        * note that because the exponentiation function is limited to an input of up to (and excluding)
        * 16 / ln 2, the input value to this function is limited by `timeElapsed / halfLife < 16 / ln 2`
    '''
    def calcExpDecayRewards(
        totalRewards,
        timeElapsed,
        halfLife
    ) -> (uint):
        input = Fraction256({ 'n': timeElapsed, 'd': halfLife });
        output = MathEx.exp2(input);
        return MathEx.mulDivF(totalRewards, output.n - output.d, output.n);
