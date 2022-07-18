from bancor_research.bancor_emulator.solidity import uint, uint128, uint256, revert
from bancor_research.bancor_emulator.utils import library, using

from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION as M
from bancor_research.bancor_emulator.MathEx import Sint256, Uint512, MathEx

'''
 * @dev This library implements the mathematics behind base-token withdrawal.
 * It exposes a single function which takes the following input values:
 * `a` - BNT trading liquidity
 * `b` - base token trading liquidity
 * `c` - base token excess amount
 * `e` - base token staked amount
 * `w` - base token external protection vault balance
 * `m` - trading fee in PPM units
 * `n` - withdrawal fee in PPM units
 * `x` - base token withdrawal amount
 * And returns the following output values:
 * `p` - BNT amount to add to the trading liquidity and to the master vault
 * `q` - BNT amount to add to the protocol equity
 * `r` - base token amount to add to the trading liquidity
 * `s` - base token amount to transfer from the master vault to the provider
 * `t` - BNT amount to mint directly for the provider
 * `u` - base token amount to transfer from the external protection vault to the provider
 * `v` - base token amount to keep in the pool as a withdrawal fee
 * The following table depicts the actual formulae based on the current state of the system:
 * +-----------+---------------------------------------------------------+----------------------------------------------------------+
 * |           |                         Deficit                         |                       Surplus                            |
 * +-----------+---------------------------------------------------------+----------------------------------------------------------+
 * |           | p = a*x*(e*(1-n)-b-c)*(1-m)/(b*e-x*(e*(1-n)-b-c)*(1-m)) | p = -a*x*(b+c-e*(1-n))/(b*e*(1-m)+x*(b+c-e*(1-n))*(1-m)) |
 * |           | q = 0                                                   | q = 0                                                    |
 * |           | r = -x*(e*(1-n)-b-c)/e                                  | r = x*(b+c-e*(1-n))/e                                    |
 * | Arbitrage | s = x*(1-n)                                             | s = x*(1-n)                                              |
 * |           | t = 0                                                   | t = 0                                                    |
 * |           | u = 0                                                   | u = 0                                                    |
 * |           | v = x*n                                                 | v = x*n                                                  |
 * +-----------+---------------------------------------------------------+----------------------------------------------------------+
 * |           | p = -a*z/(b*e) where z = max(x*(1-n)*b-c*(e-x*(1-n)),0) | p = -a*z/b where z = max(x*(1-n)-c,0)                    |
 * |           | q = -a*z/(b*e) where z = max(x*(1-n)*b-c*(e-x*(1-n)),0) | q = -a*z/b where z = max(x*(1-n)-c,0)                    |
 * |           | r = -z/e       where z = max(x*(1-n)*b-c*(e-x*(1-n)),0) | r = -z     where z = max(x*(1-n)-c,0)                    |
 * | Default   | s = x*(1-n)*(b+c)/e                                     | s = x*(1-n)                                              |
 * |           | t = see function `externalProtection`                   | t = 0                                                    |
 * |           | u = see function `externalProtection`                   | u = 0                                                    |
 * |           | v = x*n                                                 | v = x*n                                                  |
 * +-----------+---------------------------------------------------------+----------------------------------------------------------+
 * |           | p = 0                                                   | p = 0                                                    |
 * |           | q = 0                                                   | q = 0                                                    |
 * |           | r = 0                                                   | r = 0                                                    |
 * | Bootstrap | s = x*(1-n)*c/e                                         | s = x*(1-n)                                              |
 * |           | t = see function `externalProtection`                   | t = 0                                                    |
 * |           | u = see function `externalProtection`                   | u = 0                                                    |
 * |           | v = x*n                                                 | v = x*n                                                  |
 * +-----------+---------------------------------------------------------+----------------------------------------------------------+
 * Note that for the sake of illustration, both `m` and `n` are assumed normalized (between 0 and 1).
 * During runtime, it is taken into account that they are given in PPM units (between 0 and 1000000).
'''
class PoolCollectionWithdrawal:
    using(MathEx, uint)
    calculateWithdrawalAmounts = None

class Output:
    def __init__(self):
        self.p = Sint256();
        self.q = Sint256();
        self.r = Sint256();
        self.s = uint256();
        self.t = uint256();
        self.u = uint256();
        self.v = uint256();

'''
    * @dev returns `p`, `q`, `r`, `s`, `t`, `u` and `v` according to the current state:
    * +-------------------+-----------------------------------------------------------+
    * | `e > (b+c)/(1-n)` | bootstrap deficit or default deficit or arbitrage deficit |
    * +-------------------+-----------------------------------------------------------+
    * | `e < (b+c)`       | bootstrap surplus or default surplus or arbitrage surplus |
    * +-------------------+-----------------------------------------------------------+
    * | otherwise         | bootstrap surplus or default surplus                      |
    * +-------------------+-----------------------------------------------------------+
'''
def calculateWithdrawalAmounts(
    a, # <= 2**128-1
    b, # <= 2**128-1
    c, # <= 2**128-1
    e, # <= 2**128-1
    w, # <= 2**128-1
    m, # <= M == 1000000
    n, # <= M == 1000000
    x ## <= e <= 2**128-1
) -> (Output):
    output = Output()

    a = uint256(a)
    b = uint256(b)
    c = uint256(c)
    e = uint256(e)
    w = uint256(w)
    m = uint256(m)
    n = uint256(n)
    x = uint256(x)

    if (
        a > uint128.max or
        b > uint128.max or
        c > uint128.max or
        e > uint128.max or
        w > uint128.max or
        m > M or
        n > M or
        x > e
    ):
        revert("PoolCollectionWithdrawalInputInvalid");

    y = (x * (M - n)) / M;

    if ((e * (M - n)) / M > b + c):
        f = (e * (M - n)) / M - (b + c);
        g = e - (b + c);
        if (isStable(b, c, e, x) and affordableDeficit(b, e, f, g, m, n, x)):
            output = arbitrageDeficit(a, b, e, f, m, x, y);
        elif (a > 0):
            output = defaultDeficit(a, b, c, e, y);
            (output.t, output.u) = externalProtection(a, b, e, g, y, w);
        else:
            output.s = (y * c) / e;
            (output.t, output.u) = externalProtection(a, b, e, g, y, w);
    else:
        f = MathEx.subMax0(b + c, e);
        if (f > 0 and isStable(b, c, e, x) and affordableSurplus(b, e, f, m, n, x)):
            output = arbitrageSurplus(a, b, e, f, m, n, x, y);
        elif (a > 0):
            output = defaultSurplus(a, b, c, y);
        else:
            output.s = y;

    output.v = x - y;

    return output

'''
    * @dev returns `x < e*c/(b+c)`
'''
def isStable(
    b, # <= 2**128-1
    c, # <= 2**128-1
    e, # <= 2**128-1
    x ## <= e <= 2**128-1
) -> (bool):
    return b * x < c * (e - x);

'''
    * @dev returns `b*e*((e*(1-n)-b-c)*m+e*n) > (e*(1-n)-b-c)*x*(e-b-c)*(1-m)`
'''
def affordableDeficit(
    b, # <= 2**128-1
    e, # <= 2**128-1
    f, # == e*(1-n)-b-c <= e <= 2**128-1
    g, # == e-b-c <= e <= 2**128-1
    m, # <= M == 1000000
    n, # <= M == 1000000
    x ## <  e*c/(b+c) <= e <= 2**128-1
) -> (bool):
    # temporarily disabled
    #Uint512 memory lhs = MathEx.mul512(b * e, f * m + e * n);
    #Uint512 memory rhs = MathEx.mul512(f * x, g * (M - m));
    #return MathEx.gt512(lhs, rhs);
    return False;

'''
    * @dev returns `b*e*((b+c-e)*m+e*n) > (b+c-e)*x*(b+c-e*(1-n))*(1-m)`
'''
def affordableSurplus(
    b, # <= 2**128-1
    e, # <= 2**128-1
    f, # == b+c-e <= 2**129-2
    m, # <= M == 1000000
    n, # <= M == 1000000
    x ## <  e*c/(b+c) <= e <= 2**128-1
) -> (bool):
    lhs: Uint512 = MathEx.mul512(b * e, (f * m + e * n) * M);
    rhs: Uint512 = MathEx.mul512(f * x, (f * M + e * n) * (M - m));
    return MathEx.gt512(lhs, rhs); # `x < e*c/(b+c)` --> `f*x < e*c*(b+c-e)/(b+c) <= e*c <= 2**256-1`

'''
    * @dev returns:
    * `p = a*x*(e*(1-n)-b-c)*(1-m)/(b*e-x*(e*(1-n)-b-c)*(1-m))`
    * `q = 0`
    * `r = -x*(e*(1-n)-b-c)/e`
    * `s = x*(1-n)`
'''
def arbitrageDeficit(
    a, # <= 2**128-1
    b, # <= 2**128-1
    e, # <= 2**128-1
    f, # == e*(1-n)-b-c <= e <= 2**128-1
    m, # <= M == 1000000
    x, # <= e <= 2**128-1
    y ## == x*(1-n) <= x <= e <= 2**128-1
) -> (Output):
    output = Output()
    i = f * (M - m);
    j = mulSubMulDivF(b, e * M, x, i, 1);
    output.p = MathEx.mulDivF(a * x, i, j).toPos256();
    output.r = MathEx.mulDivF(x, f, e).toNeg256();
    output.s = y;
    return output

'''
    * @dev returns:
    * `p = -a*x*(b+c-e*(1-n))/(b*e*(1-m)+x*(b+c-e*(1-n))*(1-m))`
    * `q = 0`
    * `r = x*(b+c-e*(1-n))/e`
    * `s = x*(1-n)`
'''
def arbitrageSurplus(
    a, # <= 2**128-1
    b, # <= 2**128-1
    e, # <= 2**128-1
    f, # == b+c-e <= 2**129-2
    m, # <= M == 1000000
    n, # <= M == 1000000
    x, # <= e <= 2**128-1
    y ## == x*(1-n) <= x <= e <= 2**128-1
) -> (Output):
    output = Output()
    i = f * M + e * n;
    j = mulAddMulDivF(b, e * (M - m), x, i * (M - m), M);
    output.p = MathEx.mulDivF(a * x, i, j).toNeg256();
    output.r = MathEx.mulDivF(x, i, e * M).toPos256();
    output.s = y;
    return output

'''
    * @dev returns:
    * `p = -a*z/(b*e)` where `z = max(x*(1-n)*b-c*(e-x*(1-n)),0)`
    * `q = -a*z/(b*e)` where `z = max(x*(1-n)*b-c*(e-x*(1-n)),0)`
    * `r = -z/e` where `z = max(x*(1-n)*b-c*(e-x*(1-n)),0)`
    * `s = x*(1-n)*(b+c)/e`
'''
def defaultDeficit(
    a, # <= 2**128-1
    b, # <= 2**128-1
    c, # <= 2**128-1
    e, # <= 2**128-1
    y ## == x*(1-n) <= x <= e <= 2**128-1
) -> (Output):
    output = Output()
    z = MathEx.subMax0(y * b, c * (e - y));
    output.p = MathEx.mulDivF(a, z, b * e).toNeg256();
    output.q = output.p;
    output.r = (z / e).toNeg256();
    output.s = MathEx.mulDivF(y, b + c, e);
    return output

'''
    * @dev returns:
    * `p = -a*z/b` where `z = max(x*(1-n)-c,0)`
    * `q = -a*z/b` where `z = max(x*(1-n)-c,0)`
    * `r = -z` where `z = max(x*(1-n)-c,0)`
    * `s = x*(1-n)`
'''
def defaultSurplus(
    a, # <= 2**128-1
    b, # <= 2**128-1
    c, # <= 2**128-1
    y ## == x*(1-n) <= x <= e <= 2**128-1
) -> (Output):
    output = Output()
    z = MathEx.subMax0(y, c);
    output.p = MathEx.mulDivF(a, z, b).toNeg256();
    output.q = output.p;
    output.r = z.toNeg256();
    output.s = y;
    return output

'''
    * @dev returns `t` and `u` according to the current state:
    * +-----------------------+-------+---------------------------+-------------------+
    * | x*(1-n)*(e-b-c)/e > w | a > 0 | t                         | u                 |
    * +-----------------------+-------+---------------------------+-------------------+
    * | true                  | true  | a*(x*(1-n)*(e-b-c)/e-w)/b | w                 |
    * +-----------------------+-------+---------------------------+-------------------+
    * | true                  | false | 0                         | w                 |
    * +-----------------------+-------+---------------------------+-------------------+
    * | false                 | true  | 0                         | x*(1-n)*(e-b-c)/e |
    * +-----------------------+-------+---------------------------+-------------------+
    * | false                 | false | 0                         | x*(1-n)*(e-b-c)/e |
    * +-----------------------+-------+---------------------------+-------------------+
'''
def externalProtection(
    a, # <= 2**128-1
    b, # <= 2**128-1
    e, # <= 2**128-1
    g, # == e-b-c <= e <= 2**128-1
    y, # == x*(1-n) <= x <= e <= 2**128-1
    w ## <= 2**128-1
):
    yg = y * g;
    we = w * e;
    if (yg > we):
        t = MathEx.mulDivF(a, yg - we, b * e) if a > 0 else uint256(0);
        u = w;
    else:
        t = uint256(0);
        u = yg / e;
    return [t, u]

'''
    * @dev returns `a*b+x*y/z`
'''
def mulAddMulDivF(
    a,
    b,
    x,
    y,
    z
):
    return a * b + MathEx.mulDivF(x, y, z);

'''
    * @dev returns `a*b-x*y/z`
'''
def mulSubMulDivF(
    a,
    b,
    x,
    y,
    z
):
    return a * b - MathEx.mulDivF(x, y, z);

library(vars(), PoolCollectionWithdrawal)