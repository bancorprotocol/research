from bancor_research.bancor_emulator.solidity import uint, uint256, unchecked, mulmod, revert
from bancor_research.bancor_emulator.utils import library, parse

from bancor_research.bancor_emulator.Math import Math
from bancor_research.bancor_emulator.Fraction import Fraction256
from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION

ONE = 0x80000000000000000000000000000000;
LN2 = 0x58b90bfbe8e7bcd5e4f1d9cc01f97b57;

class Uint512:
    def __init__(self, x = None) -> None:
        self.hi = parse(uint256, x, 'hi'); # 256 most significant bits
        self.lo = parse(uint256, x, 'lo'); # 256 least significant bits

class Sint256:
    def __init__(self, x = None) -> None:
        self.value = parse(uint256, x, 'value');
        self.isNeg = parse(bool, x, 'isNeg');

'''
 * @dev this library provides a set of complex math operations
'''
class MathEx:
    exp2 = None
    reducedFraction = None
    weightedAverage = None
    isInRange = None
    toPos256 = None
    toNeg256 = None
    mulDivF = None
    mulDivC = None
    subMax0 = None
    gt512 = None
    lt512 = None
    gte512 = None
    lte512 = None
    mul512 = None

'''
    * @dev returns `2 ^ f` by calculating `e ^ (f * ln(2))`, where `e` is Euler's number:
    * - Rewrite the input as a sum of binary exponents and a single residual r, as small as possible
    * - The exponentiation of each binary exponent is given (pre-calculated)
    * - The exponentiation of r is calculated via Taylor series for e^x, where x = r
    * - The exponentiation of the input is calculated by multiplying the intermediate results above
    * - For example: e^5.521692859 = e^(4 + 1 + 0.5 + 0.021692859) = e^4 * e^1 * e^0.5 * e^0.021692859
'''
def exp2(f: Fraction256) -> (Fraction256):
    unchecked.begin()

    x = mulDivF(LN2, f.n, f.d);
    y = uint256();
    z = uint256();
    n = uint256();

    if (x >= (ONE << 4)):
        revert("Overflow");

    z = y = x % (ONE >> 3); # get the input modulo 2^(-3)
    z = (z * y) / ONE;
    n += z * 0x10e1b3be415a0000; # add y^02 * (20! / 02!)
    z = (z * y) / ONE;
    n += z * 0x05a0913f6b1e0000; # add y^03 * (20! / 03!)
    z = (z * y) / ONE;
    n += z * 0x0168244fdac78000; # add y^04 * (20! / 04!)
    z = (z * y) / ONE;
    n += z * 0x004807432bc18000; # add y^05 * (20! / 05!)
    z = (z * y) / ONE;
    n += z * 0x000c0135dca04000; # add y^06 * (20! / 06!)
    z = (z * y) / ONE;
    n += z * 0x0001b707b1cdc000; # add y^07 * (20! / 07!)
    z = (z * y) / ONE;
    n += z * 0x000036e0f639b800; # add y^08 * (20! / 08!)
    z = (z * y) / ONE;
    n += z * 0x00000618fee9f800; # add y^09 * (20! / 09!)
    z = (z * y) / ONE;
    n += z * 0x0000009c197dcc00; # add y^10 * (20! / 10!)
    z = (z * y) / ONE;
    n += z * 0x0000000e30dce400; # add y^11 * (20! / 11!)
    z = (z * y) / ONE;
    n += z * 0x000000012ebd1300; # add y^12 * (20! / 12!)
    z = (z * y) / ONE;
    n += z * 0x0000000017499f00; # add y^13 * (20! / 13!)
    z = (z * y) / ONE;
    n += z * 0x0000000001a9d480; # add y^14 * (20! / 14!)
    z = (z * y) / ONE;
    n += z * 0x00000000001c6380; # add y^15 * (20! / 15!)
    z = (z * y) / ONE;
    n += z * 0x000000000001c638; # add y^16 * (20! / 16!)
    z = (z * y) / ONE;
    n += z * 0x0000000000001ab8; # add y^17 * (20! / 17!)
    z = (z * y) / ONE;
    n += z * 0x000000000000017c; # add y^18 * (20! / 18!)
    z = (z * y) / ONE;
    n += z * 0x0000000000000014; # add y^19 * (20! / 19!)
    z = (z * y) / ONE;
    n += z * 0x0000000000000001; # add y^20 * (20! / 20!)
    n = n / 0x21c3677c82b40000 + y + ONE; # divide by 20! and then add y^1 / 1! + y^0 / 0!

    if ((x & (ONE >> 3)) != 0):
        n = (n * 0x1c3d6a24ed82218787d624d3e5eba95f9) / 0x18ebef9eac820ae8682b9793ac6d1e776; # multiply by e^(2^-3)
    if ((x & (ONE >> 2)) != 0):
        n = (n * 0x18ebef9eac820ae8682b9793ac6d1e778) / 0x1368b2fc6f9609fe7aceb46aa619baed4; # multiply by e^(2^-2)
    if ((x & (ONE >> 1)) != 0):
        n = (n * 0x1368b2fc6f9609fe7aceb46aa619baed5) / 0x0bc5ab1b16779be3575bd8f0520a9f21f; # multiply by e^(2^-1)
    if ((x & (ONE << 0)) != 0):
        n = (n * 0x0bc5ab1b16779be3575bd8f0520a9f21e) / 0x0454aaa8efe072e7f6ddbab84b40a55c9; # multiply by e^(2^+0)
    if ((x & (ONE << 1)) != 0):
        n = (n * 0x0454aaa8efe072e7f6ddbab84b40a55c5) / 0x00960aadc109e7a3bf4578099615711ea; # multiply by e^(2^+1)
    if ((x & (ONE << 2)) != 0):
        n = (n * 0x00960aadc109e7a3bf4578099615711d7) / 0x0002bf84208204f5977f9a8cf01fdce3d; # multiply by e^(2^+2)
    if ((x & (ONE << 3)) != 0):
        n = (n * 0x0002bf84208204f5977f9a8cf01fdc307) / 0x0000003c6ab775dd0b95b4cbee7e65d11; # multiply by e^(2^+3)

    unchecked.end()

    return Fraction256({ 'n': n, 'd': ONE });

'''
    * @dev returns a fraction with reduced components
'''
def reducedFraction(fraction: Fraction256, max: int) -> (Fraction256):
    scale = Math.ceilDiv(Math.max(fraction.n, fraction.d), max);
    reduced = Fraction256({ 'n': fraction.n / scale, 'd': fraction.d / scale });
    if (reduced.d == 0):
        revert("InvalidFraction");

    return reduced;

'''
    * @dev returns the weighted average of two fractions
'''
def weightedAverage(
    fraction1: Fraction256,
    fraction2: Fraction256,
    weight1,
    weight2
) -> (Fraction256):
    return Fraction256({
        'n': fraction1.n * fraction2.d * weight1 + fraction1.d * fraction2.n * weight2,
        'd': fraction1.d * fraction2.d * (weight1 + weight2)
    });

'''
    * @dev returns whether or not the deviation of an offset sample from a base sample is within a permitted range
    * for example, if the maximum permitted deviation is 5%, then evaluate `95% * base <= offset <= 105% * base`
'''
def isInRange(
    baseSample: Fraction256,
    offsetSample: Fraction256,
    maxDeviationPPM
) -> (bool):
    min = mul512(baseSample.n, offsetSample.d * (PPM_RESOLUTION - maxDeviationPPM));
    mid = mul512(baseSample.d, offsetSample.n * PPM_RESOLUTION);
    max = mul512(baseSample.n, offsetSample.d * (PPM_RESOLUTION + maxDeviationPPM));
    return lte512(min, mid) and lte512(mid, max);

'''
    * @dev returns an `Sint256` positive representation of an unsigned integer
'''
def toPos256(n) -> (Sint256):
    return Sint256({ 'value': n, 'isNeg': False });

'''
    * @dev returns an `Sint256` negative representation of an unsigned integer
'''
def toNeg256(n) -> (Sint256):
    return Sint256({ 'value': n, 'isNeg': True });

'''
    * @dev returns the largest integer smaller than or equal to `x * y / z`
'''
def mulDivF(
    x,
    y,
    z
) -> (uint):
    x, y, z = uint256(x), uint256(y), uint256(z)

    xy = mul512(x, y);

    # if `x * y < 2 ^ 256`
    if (xy.hi == 0):
        return xy.lo / z;

    # assert `x * y / z < 2 ^ 256`
    if (xy.hi >= z):
        revert("Overflow");

    m = _mulMod(x, y, z); # `m = x * y % z`
    n = _sub512(xy, m); # `n = x * y - m` hence `n / z = floor(x * y / z)`

    # if `n < 2 ^ 256`
    if (n.hi == 0):
        return n.lo / z;

    p = _unsafeSub(0, z) & z; # `p` is the largest power of 2 which `z` is divisible by
    q = _div512(n, p); # `n` is divisible by `p` because `n` is divisible by `z` and `z` is divisible by `p`
    r = _inv256(z / p); # `z / p = 1 mod 2` hence `inverse(z / p) = 1 mod 2 ^ 256`
    return _unsafeMul(q, r); # `q * r = (n / p) * inverse(z / p) = n / z`

'''
    * @dev returns the smallest integer larger than or equal to `x * y / z`
'''
def mulDivC(
    x,
    y,
    z
) -> (uint):
    x, y, z = uint256(x), uint256(y), uint256(z)

    w = mulDivF(x, y, z);
    if (_mulMod(x, y, z) > 0):
        if (w >= uint256.max):
            revert("Overflow");

        return w + 1;
    return w;

'''
    * @dev returns the maximum of `n1 - n2` and 0
'''
def subMax0(n1, n2) -> (uint):
    return uint256(n1 - n2 if n1 > n2 else 0);

'''
    * @dev returns the value of `x > y`
'''
def gt512(x: Uint512, y: Uint512) -> (bool):
    return x.hi > y.hi or (x.hi == y.hi and x.lo > y.lo);

'''
    * @dev returns the value of `x < y`
'''
def lt512(x: Uint512, y: Uint512) -> (bool):
    return x.hi < y.hi or (x.hi == y.hi and x.lo < y.lo);

'''
    * @dev returns the value of `x >= y`
'''
def gte512(x: Uint512, y: Uint512) -> (bool):
    return not lt512(x, y);

'''
    * @dev returns the value of `x <= y`
'''
def lte512(x: Uint512, y: Uint512) -> (bool):
    return not gt512(x, y);

'''
    * @dev returns the value of `x * y`
'''
def mul512(x, y) -> (Uint512):
    p = _mulModMax(x, y);
    q = _unsafeMul(x, y);
    if (p >= q):
        return Uint512({ 'hi': p - q, 'lo': q });
    return Uint512({ 'hi': _unsafeSub(p, q) - 1, 'lo': q });

'''
    * @dev returns the value of `x - y`, given that `x >= y`
'''
def _sub512(x: Uint512, y) -> (Uint512):
    if (x.lo >= y):
        return Uint512({ 'hi': x.hi, 'lo': x.lo - y });
    return Uint512({ 'hi': x.hi - 1, 'lo': _unsafeSub(x.lo, y) });

'''
    * @dev returns the value of `x / pow2n`, given that `x` is divisible by `pow2n`
'''
def _div512(x: Uint512, pow2n) -> (uint):
    pow2nInv = _unsafeAdd(_unsafeSub(0, pow2n) / pow2n, 1); # `1 << (256 - n)`
    return _unsafeMul(x.hi, pow2nInv) | (x.lo / pow2n); # `(x.hi << (256 - n)) | (x.lo >> n)`

'''
    * @dev returns the inverse of `d` modulo `2 ^ 256`, given that `d` is congruent to `1` modulo `2`
'''
def _inv256(d) -> (uint):
    # approximate the root of `f(x) = 1 / x - d` using the newton–raphson convergence method
    x = 1;
    for _ in range(8):
        x = _unsafeMul(x, _unsafeSub(2, _unsafeMul(x, d))); # `x = x * (2 - x * d) mod 2 ^ 256`
    return x;

'''
    * @dev returns `(x + y) % 2 ^ 256`
'''
def _unsafeAdd(x, y) -> (uint):
    unchecked.begin()
    z = uint256(x) + uint256(y);
    unchecked.end()
    return z

'''
    * @dev returns `(x - y) % 2 ^ 256`
'''
def _unsafeSub(x, y) -> (uint):
    unchecked.begin()
    z = uint256(x) - uint256(y);
    unchecked.end()
    return z

'''
    * @dev returns `(x * y) % 2 ^ 256`
'''
def _unsafeMul(x, y) -> (uint):
    unchecked.begin()
    z = uint256(x) * uint256(y);
    unchecked.end()
    return z

'''
    * @dev returns `x * y % (2 ^ 256 - 1)`
'''
def _mulModMax(x, y) -> (uint):
    return mulmod(x, y, uint256.max);

'''
    * @dev returns `x * y % z`
'''
def _mulMod(
    x,
    y,
    z
) -> (uint):
    return mulmod(x, y, z);

from bancor_research.bancor_emulator import config

if config.mode == 'float':
    def exp2(f: Fraction256) -> (Fraction256):
        return Fraction256({ 'n': uint256(2) ** (f.n / f.d), 'd': 1 });
    def reducedFraction(fraction: Fraction256, max: int) -> (Fraction256):
        return fraction;
    def mulDivF(x, y, z) -> (uint):
        return uint256(x) * y / z 
    def mulDivC(x, y, z) -> (uint):
        return uint256(x) * y / z 
    def gt512(x: Uint512, y: Uint512) -> (bool):
        return x.lo > y.lo;
    def lt512(x: Uint512, y: Uint512) -> (bool):
        return x.lo < y.lo;
    def mul512(x, y) -> (Uint512):
        return Uint512({ 'hi': 0, 'lo': uint256(x) * y });

library(vars(), MathEx)