from bancor_research.bancor_emulator.solidity import uint112, revert
from bancor_research.bancor_emulator.utils import library

from bancor_research.bancor_emulator.Fraction import Fraction256, Fraction112
from bancor_research.bancor_emulator.MathEx import MathEx

# solhint-disable-next-line func-visibility
def zeroFraction256() -> (Fraction256):
    return Fraction256({ 'n': 0, 'd': 1 });

# solhint-disable-next-line func-visibility
def zeroFraction112() -> (Fraction112):
    return Fraction112({ 'n': 0, 'd': 1 });

'''
 * @dev this library provides a set of fraction operations
'''
class FractionLibrary:
    isValid = None
    isPositive = None
    inverse = None
    toFraction112 = None
    fromFraction112 = None

'''
    * @dev returns whether a given fraction is valid
'''
def isValid(fraction) -> (bool):
    return fraction.d != 0;

'''
    * @dev returns whether a given fraction is positive
'''
def isPositive(fraction) -> (bool):
    return isValid(fraction) and fraction.n != 0;

'''
    * @dev returns the inverse of a given fraction
'''
def inverse(fraction):
    invFraction = type(fraction)({ 'n': fraction.d, 'd': fraction.n });

    if (not isValid(invFraction)):
        revert("InvalidFraction");

    return invFraction;

'''
    * @dev reduces a standard fraction to a 112-bit fraction
'''
def toFraction112(fraction: Fraction256) -> (Fraction112):
    reducedFraction = MathEx.reducedFraction(fraction, uint112.max);

    return Fraction112({ 'n': uint112(reducedFraction.n), 'd': uint112(reducedFraction.d) });

'''
    * @dev expands a 112-bit fraction to a standard fraction
'''
def fromFraction112(fraction: Fraction112) -> (Fraction256):
    return Fraction256({ 'n': fraction.n, 'd': fraction.d });

library(vars(), FractionLibrary)