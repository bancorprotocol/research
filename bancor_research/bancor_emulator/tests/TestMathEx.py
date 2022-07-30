from bancor_research.bancor_emulator.solidity.uint.float import Decimal
from bancor_research.bancor_emulator.MathEx import MathEx, Uint512
from bancor_research.bancor_emulator.Fraction import Fraction256

MAX_UINT32 = 2 ** 32 - 1
MAX_UINT64 = 2 ** 64 - 1
MAX_UINT96 = 2 ** 96 - 1
MAX_UINT112 = 2 ** 112 - 1
MAX_UINT128 = 2 ** 128 - 1
MAX_UINT256 = 2 ** 256 - 1

TEST_ARRAY = [
    0,
    100,
    10_000,
    MAX_UINT128,
    MAX_UINT256 // 2,
    MAX_UINT256 - MAX_UINT128,
    MAX_UINT256
];

def mulDivF(x, y, z): return x * y // z
def mulDivC(x, y, z): return (x * y + z - 1) // z

def gt512(x, y): return x > y
def lt512(x, y): return x < y
def gte512(x, y): return x >= y
def lte512(x, y): return x <= y

mulDivFuncs = {
    'mulDivF': {'expected': mulDivF, 'actual': MathEx.mulDivF},
    'mulDivC': {'expected': mulDivC, 'actual': MathEx.mulDivC},
};

comp512Funcs = {
    'gt512' : {'expected': gt512 , 'actual': MathEx.gt512 },
    'lt512' : {'expected': lt512 , 'actual': MathEx.lt512 },
    'gte512': {'expected': gte512, 'actual': MathEx.gte512},
    'lte512': {'expected': lte512, 'actual': MathEx.lte512},
};

def toUint512(x):
    return Uint512({'hi': x >> 256, 'lo': x & MAX_UINT256})

def toDecimal(f):
    return Decimal(int(f.n)) / Decimal(int(f.d))

def assertAlmostEqual(expected, actual, maxErr):
    actual = toDecimal(actual)
    if actual != expected:
        error = abs(actual - expected) / expected
        assert error <= Decimal(maxErr), '\n- error = {}\n- maxErr = {}'.format(error, maxErr)

def testExp(f, maxErr):
    print('exp2({} / {})'.format(f.n, f.d));
    try:
        actual = MathEx.exp2(f);
        expected = Decimal(2) ** toDecimal(f);
        assert toDecimal(actual) <= expected
        assertAlmostEqual(expected, actual, maxErr);
        print('{} / {}'.format(actual.n, actual.d));
    except AssertionError as error:
        assert str(error) == 'Overflow'
        print('Overflow');

def testTruncatedFraction(f, maxVal, maxErr):
    print('truncatedFraction({} / {}, {})'.format(f.n, f.d, maxVal));
    try:
        actual = MathEx.truncatedFraction(f, maxVal);
        assert actual.n <= maxVal and actual.d <= maxVal
        assertAlmostEqual(toDecimal(f), actual, maxErr);
        print('{} / {}'.format(actual.n, actual.d));
    except AssertionError as error:
        assert str(error) == 'InvalidFraction'
        print('InvalidFraction');

def testWeightedAverage(f1, f2, w1, w2, maxErr):
    print('weightedAverage({} / {}, {} / {}, {}, {})'.format(f1.n, f1.d, f2.n, f2.d, w1, w2));
    expected = sum([toDecimal(f) * w for f, w in zip([f1, f2], [w1, w2])]) / sum([w1, w2]); 
    actual = MathEx.weightedAverage(f1, f2, w1, w2);
    assertAlmostEqual(expected, actual, maxErr);
    print('{} / {}'.format(actual.n, actual.d));

def testIsInRange(f1, f2, maxDeviation):
    print('isInRange({} / {}, {} / {}, {}%)'.format(f1.n, f1.d, f2.n, f2.d, maxDeviation));
    midVal = toDecimal(f1);
    minVal = toDecimal(f2) * (100 - maxDeviation) / 100;
    maxVal = toDecimal(f2) * (100 + maxDeviation) / 100;
    actual = MathEx.isInRange(f1, f2, maxDeviation * 10000);
    assert actual == (minVal <= midVal <= maxVal)
    print('true' if actual else 'false');

def testMulDiv(x, y, z):
    for funcName in mulDivFuncs.keys():
        print('{}({}, {}, {})'.format(funcName, x, y, z));
        expected = mulDivFuncs[funcName]['expected'](x, y, z);
        if (expected <= MAX_UINT256):
            actual = mulDivFuncs[funcName]['actual'](x, y, z);
            assert actual == expected
            print(actual);
        else:
            try:
                actual = mulDivFuncs[funcName]['actual'](x, y, z);
                assert False
            except AssertionError as error:
                assert str(error) == 'Overflow'
                print('Overflow');

def testSubMax0(x, y):
    print('subMax0({}, {})'.format(x, y));
    actual = MathEx.subMax0(x, y);
    assert actual == max(int(x - y), 0)
    print(actual);

def testMul512(x, y):
    print('mul512({}, {})'.format(x, y));
    actual = MathEx.mul512(x, y);
    assert int(actual.hi) << 256 | int(actual.lo) == x * y
    print('{},{}'.format(actual.hi, actual.lo));

def testComp512(a, b):
    for x in [a, (a + 1) * b]:
        for y in [b, (b + 1) * a]:
            for funcName in comp512Funcs.keys():
                print('{}({}, {})'.format(funcName, x, y));
                expected = comp512Funcs[funcName]['expected'](x, y);
                actual = comp512Funcs[funcName]['actual'](toUint512(x), toUint512(y));
                assert actual == expected
                print('true' if actual else 'false');

for n in range(10):
    for d in range(1, 10):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.00000000000000000000000000000000000006');

for d in [10 ** i for i in range(3, 9)]:
    for n in range(1, 11):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.00000000000000000000000000000000000002');

for d in [10 ** i for i in range(3, 9)]:
    for n in range(d - 10, d):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.00000000000000000000000000000000000003');

for d in [10 ** i for i in range(3, 9)]:
    for n in range(d + 1, d + 11):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.00000000000000000000000000000000000003');

for d in [10 ** i for i in range(3, 9)]:
    for n in range(2 * d - 10, 2 * d):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.00000000000000000000000000000000000004');

for d in [10 ** i for i in range(3, 9)]:
    for n in range(2 * d + 1, 2 * d + 11):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.00000000000000000000000000000000000003');

for m in [MAX_UINT128]:
    for n in range(10):
        for d in range(10):
            testTruncatedFraction(Fraction256({ 'n': m - n, 'd': m - d }), m, '0.0');
            testTruncatedFraction(Fraction256({ 'n': m - n, 'd': m + d }), m, '0.000000000000000000000000000000000000003');
            testTruncatedFraction(Fraction256({ 'n': m + n, 'd': m - d }), m, '0.000000000000000000000000000000000000003');
            testTruncatedFraction(Fraction256({ 'n': m + n, 'd': m + d }), m, '0.000000000000000000000000000000000000003');

for n in [100, 200]:
    for d in [2, 3]:
        for m in [3, 5]:
            testTruncatedFraction(Fraction256({ 'n': n, 'd': d }), m, '0.0');

for n1 in [MAX_UINT64, MAX_UINT96]:
    for d1 in [MAX_UINT64, MAX_UINT96]:
        fraction1 = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [MAX_UINT64, MAX_UINT96]:
            for d2 in [MAX_UINT64, MAX_UINT96]:
                fraction2 = Fraction256({ 'n': n2, 'd': d2 });
                for weight1 in [2, 8]:
                    for weight2 in [2, 8]:
                        testWeightedAverage(fraction1, fraction2, weight1, weight2, '5e-155');

for n1 in [MAX_UINT64, MAX_UINT96]:
    for d1 in [MAX_UINT64, MAX_UINT96]:
        baseSample = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [MAX_UINT64, MAX_UINT96]:
            for d2 in [MAX_UINT64, MAX_UINT96]:
                offsetSample = Fraction256({ 'n': n2, 'd': d2 });
                for maxDeviation in [2, 5]:
                    testIsInRange(baseSample, offsetSample, maxDeviation);

for px in [128, 192, 256]:
    for py in [128, 192, 256]:
        for pz in [128, 192, 256]:
            for ax in [3, 5, 7]:
                for ay in [3, 5, 7]:
                    for az in [3, 5, 7]:
                        x = 2 ** px // ax;
                        y = 2 ** py // ay;
                        z = 2 ** pz // az;
                        testMulDiv(x, y, z);

for x in TEST_ARRAY:
    for y in TEST_ARRAY:
        testSubMax0(x, y);
        testMul512(x, y);
        testComp512(x, y);

for n in range(100):
    for d in range(1, 100):
        testExp(Fraction256({ 'n': n, 'd': d }), '0.000000000000000000000000000000000002');

for m in [MAX_UINT96, MAX_UINT112, MAX_UINT128]:
    for n in range(10):
        for d in range(10):
            testTruncatedFraction(Fraction256({ 'n': m - n, 'd': m - d }), m, '0.0');
            testTruncatedFraction(Fraction256({ 'n': m - n, 'd': m + d }), m, '0.00000000000000000000000000002');
            testTruncatedFraction(Fraction256({ 'n': m + n, 'd': m - d }), m, '0.00000000000000000000000000002');
            testTruncatedFraction(Fraction256({ 'n': m + n, 'd': m + d }), m, '0.00000000000000000000000000002');

for m in [MAX_UINT112]:
    i = 1
    while i <= m:
        j = 1
        while j <= m:
            n = MAX_UINT256 // m * i + 1;
            d = MAX_UINT256 // m * j + 1;
            testTruncatedFraction(Fraction256({ 'n': n, 'd': d }), m, '0.04');
            j *= 10
        i *= 10

for m in [MAX_UINT96, MAX_UINT112, MAX_UINT128]:
    for i in range(96, 257, 16):
        for j in range(i - 64, i + 65, 16):
            iMax = 2 ** i - 1
            jMax = 2 ** j - 1
            for n in [
                iMax // 3,
                iMax // 2,
                iMax * 2 // 3,
                iMax * 3 // 4,
                iMax - 1,
                iMax,
                iMax + 1,
                iMax * 4 // 3,
                iMax * 3 // 2,
                iMax * 2,
                iMax * 3
            ]:
                for d in [jMax - 1, jMax, jMax + 1]:
                    if (n <= MAX_UINT256 and d <= MAX_UINT256):
                        testTruncatedFraction(Fraction256({ 'n': n, 'd': d }), m, '0.0000000005');

for n1 in [0, 1, 2, 3]:
    for d1 in [1, 2, 3, 4]:
        fraction1 = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [0, 1, 2, 3]:
            for d2 in [1, 2, 3, 4]:
                fraction2 = Fraction256({ 'n': n2, 'd': d2 });
                for weight1 in [1, 2, 4, 8]:
                    for weight2 in [1, 2, 4, 8]:
                        testWeightedAverage(fraction1, fraction2, weight1, weight2, '1e-154');

for n1 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT112]:
    for d1 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT112]:
        fraction1 = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
            for d2 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
                fraction2 = Fraction256({ 'n': n2, 'd': d2 });
                for weight1 in [1, 2, 4, 8]:
                    for weight2 in [1, 2, 4, 8]:
                        testWeightedAverage(fraction1, fraction2, weight1, weight2, '2e-154');

for n1 in [0, 1, 2, 3]:
    for d1 in [1, 2, 3, 4]:
        baseSample = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [0, 1, 2, 3]:
            for d2 in [1, 2, 3, 4]:
                offsetSample = Fraction256({ 'n': n2, 'd': d2 });
                for maxDeviation in [0, 2, 5, 10]:
                    testIsInRange(baseSample, offsetSample, maxDeviation);

for n1 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
    for d1 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
        baseSample = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
            for d2 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
                offsetSample = Fraction256({ 'n': n2, 'd': d2 });
                for maxDeviation in [0, 2, 5, 10]:
                    testIsInRange(baseSample, offsetSample, maxDeviation);

for px in [0, 64, 128, 192, 255, 256]:
    for py in [0, 64, 128, 192, 255, 256]:
        for pz in [1, 64, 128, 192, 255, 256]:
            for ax in [-1, 0, +1] if px < 256 else [-1]:
                for ay in [-1, 0, +1] if py < 256 else [-1]:
                    for az in [-1, 0, +1] if pz < 256 else [-1]:
                        x = 2 ** px + ax;
                        y = 2 ** py + ay;
                        z = 2 ** pz + az;
                        testMulDiv(x, y, z);

for px in [64, 128, 192, 256]:
    for py in [64, 128, 192, 256]:
        for pz in [64, 128, 192, 256]:
            for ax in [2 ** (px >> 1), 1]:
                for ay in [2 ** (py >> 1), 1]:
                    for az in [2 ** (pz >> 1), 1]:
                        x = 2 ** px - ax;
                        y = 2 ** py - ay;
                        z = 2 ** pz - az;
                        testMulDiv(x, y, z);

for px in [128, 192, 256]:
    for py in [128, 192, 256]:
        for pz in [128, 192, 256]:
            for ax in [3, 5, 7]:
                for ay in [3, 5, 7]:
                    for az in [3, 5, 7]:
                        x = 2 ** px // ax;
                        y = 2 ** py // ay;
                        z = 2 ** pz // az;
                        testMulDiv(x, y, z);
