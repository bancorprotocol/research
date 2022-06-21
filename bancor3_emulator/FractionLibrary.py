from Types import uint112

from Fraction import Fraction256, Fraction112
from MathEx import MathEx

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
    '''
     * @dev returns whether a standard fraction is valid
    '''
    def isValid(fraction: Fraction256) -> (bool):
        return fraction.d != 0;

    '''
     * @dev returns whether a 112-bit fraction is valid
    '''
    def isValid(fraction: Fraction112) -> (bool):
        return fraction.d != 0;

    '''
     * @dev returns whether a standard fraction is positive
    '''
    def isPositive(fraction: Fraction256) -> (bool):
        return FractionLibrary.isValid(fraction) and fraction.n != 0;

    '''
     * @dev returns whether a 112-bit fraction is positive
    '''
    def isPositive(fraction: Fraction112) -> (bool):
        return FractionLibrary.isValid(fraction) and fraction.n != 0;

    '''
     * @dev returns the inverse of a given fraction
    '''
    def inverse(fraction: Fraction256) -> (Fraction256):
        invFraction = Fraction256({ 'n': fraction.d, 'd': fraction.n });

        if (not FractionLibrary.isValid(invFraction)):
            assert False, "InvalidFraction";

        return invFraction;

    '''
     * @dev returns the inverse of a given fraction
    '''
    def inverse(fraction: Fraction112) -> (Fraction112):
        invFraction = Fraction112({ 'n': fraction.d, 'd': fraction.n });

        if (not FractionLibrary.isValid(invFraction)):
            assert False, "InvalidFraction";

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
