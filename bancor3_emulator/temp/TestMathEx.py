import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

import MathEx
from Fraction import Fraction256

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
    MAX_UINT256 // (2),
    MAX_UINT256 - (MAX_UINT128),
    MAX_UINT256
];

def mulDivF(x, y, z): return x * y // z
def mulDivC(x, y, z): return (x * y + z - 1) // z

mulDivFuncs = {
    'mulDivF': {'expected': mulDivF, 'actual': MathEx.mulDivF},
    'mulDivC': {'expected': mulDivC, 'actual': MathEx.mulDivC},
};

comp512Funcs = {
    'gt512' : MathEx.gt512,
    'lt512' : MathEx.lt512,
    'gte512': MathEx.gte512,
    'lte512': MathEx.lte512,
};

def toUint512(x): return MathEx.Uint512({'hi': x >> 256, 'lo': x & MAX_UINT256})

def testExp(f):
    print('exp2({} / {})'.format(int(f.n), int(f.d)));
    try:
        actual = MathEx.exp2(f);
        print('{} / {}'.format(int(actual.n), int(actual.d)));
    except AssertionError as error:
        assert str(error) == 'Overflow'
        print('Overflow');

def testReducedFraction(f, max):
    print('reducedFraction({} / {}, {})'.format(int(f.n), int(f.d), int(max)));
    try:
        actual = MathEx.reducedFraction(f, max);
        print('{} / {}'.format(int(actual.n), int(actual.d)));
    except AssertionError as error:
        assert str(error) == 'InvalidFraction'
        print('InvalidFraction');

def testWeightedAverage(f1, f2, w1, w2):
    print('weightedAverage({} / {}, {} / {}, {}, {})'.format(int(f1.n), int(f1.d), int(f2.n), int(f2.d), int(w1), int(w2)));
    actual = MathEx.weightedAverage(f1, f2, w1, w2);
    print('{} / {}'.format(int(actual.n), int(actual.d)));

def testIsInRange(f1, f2, maxDeviation):
    print('isInRange({} / {}, {} / {}, {}%)'.format(int(f1.n), int(f1.d), int(f2.n), int(f2.d), int(maxDeviation)));
    actual = MathEx.isInRange(f1, f2, maxDeviation * 10000);
    print('true' if actual else 'false');

def testMulDiv(x, y, z):
    for funcName in mulDivFuncs.keys():
        print('{}({}, {}, {})'.format(funcName, int(x), int(y), int(z)));
        expected = mulDivFuncs[funcName]['expected'](x, y, z);
        if (expected <= MAX_UINT256):
            actual = mulDivFuncs[funcName]['actual'](x, y, z);
            print(int(actual));
        else:
            try:
                actual = mulDivFuncs[funcName]['actual'](x, y, z);
                assert False
            except AssertionError as error:
                assert str(error) == 'Overflow'
                print('Overflow');

def testSubMax0(x, y):
    print('subMax0({}, {})'.format(int(x), int(y)));
    actual = MathEx.subMax0(x, y);
    print(int(actual));

def testMul512(x, y):
    print('mul512({}, {})'.format(int(x), int(y)));
    actual = MathEx.mul512(x, y);
    print('{},{}'.format(int(actual.hi), int(actual.lo)));

def testComp512(a, b):
    for x in [a, (a + 1) * b]:
        for y in [b, (b + 1) * a]:
            for funcName in comp512Funcs.keys():
                print('{}({}, {})'.format(funcName, int(x), int(y)));
                actual = comp512Funcs[funcName](toUint512(x), toUint512(y));
                print('true' if actual else 'false');

for n in range(10):
    for d in range(1, 10):
        testExp(Fraction256({ 'n': n, 'd': d }));

for d in [10 ** i for i in range(3, 9)]:
    for n in range(1, 11):
        testExp(Fraction256({ 'n': n, 'd': d }));

for d in [10 ** i for i in range(3, 9)]:
    for n in range(d - 10, d):
        testExp(Fraction256({ 'n': n, 'd': d }));

for d in [10 ** i for i in range(3, 9)]:
    for n in range(d + 1, d + 11):
        testExp(Fraction256({ 'n': n, 'd': d }));

for d in [10 ** i for i in range(3, 9)]:
    for n in range(2 * d - 10, 2 * d):
        testExp(Fraction256({ 'n': n, 'd': d }));

for d in [10 ** i for i in range(3, 9)]:
    for n in range(2 * d + 1, 2 * d + 11):
        testExp(Fraction256({ 'n': n, 'd': d }));

for max in [MAX_UINT128]:
    for n in range(10):
        for d in range(10):
            testReducedFraction(Fraction256({ 'n': max - (n), 'd': max - (d) }), max);
            testReducedFraction(Fraction256({ 'n': max - (n), 'd': max + (d) }), max);
            testReducedFraction(Fraction256({ 'n': max + (n), 'd': max - (d) }), max);
            testReducedFraction(Fraction256({ 'n': max + (n), 'd': max + (d) }), max);

for n in [100, 200]:
    for d in [2, 3]:
        for max in [3, 5]:
            testReducedFraction(Fraction256({ 'n': n, 'd': d }), max);

for n1 in [MAX_UINT64, MAX_UINT96]:
    for d1 in [MAX_UINT64, MAX_UINT96]:
        fraction1 = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [MAX_UINT64, MAX_UINT96]:
            for d2 in [MAX_UINT64, MAX_UINT96]:
                fraction2 = Fraction256({ 'n': n2, 'd': d2 });
                for weight1 in [2, 8]:
                    for weight2 in [2, 8]:
                        testWeightedAverage(fraction1, fraction2, weight1, weight2);

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
                        x = 2 ** (px) // (ax);
                        y = 2 ** (py) // (ay);
                        z = 2 ** (pz) // (az);
                        testMulDiv(x, y, z);

for x in TEST_ARRAY:
    for y in TEST_ARRAY:
        testSubMax0(x, y);
        testMul512(x, y);
        testComp512(x, y);

for n in range(100):
    for d in range(1, 100):
        testExp(Fraction256({ 'n': n, 'd': d }));

for max in [MAX_UINT96, MAX_UINT112, MAX_UINT128]:
    for n in range(10):
        for d in range(10):
            testReducedFraction(Fraction256({ 'n': max - (n), 'd': max - (d) }), max);
            testReducedFraction(Fraction256({ 'n': max - (n), 'd': max + (d) }), max);
            testReducedFraction(Fraction256({ 'n': max + (n), 'd': max - (d) }), max);
            testReducedFraction(Fraction256({ 'n': max + (n), 'd': max + (d) }), max);

for max in [MAX_UINT112]:
    i = 1
    while i <= max:
        j = 1
        while j <= max:
            n = MAX_UINT256 // (max) * (i) + (1);
            d = MAX_UINT256 // (max) * (j) + (1);
            testReducedFraction(Fraction256({ 'n': n, 'd': d }), max);
            j *= 10
        i *= 10

for max in [MAX_UINT96, MAX_UINT112, MAX_UINT128]:
    for i in range(96, 257, 16):
        for j in range(i - 64, i + 65, 16):
            iMax = 2 ** i - 1
            jMax = 2 ** j - 1
            for n in [
                iMax // (3),
                iMax // (2),
                iMax * (2) // (3),
                iMax * (3) // (4),
                iMax - (1),
                iMax,
                iMax + (1),
                iMax * (4) // (3),
                iMax * (3) // (2),
                iMax * (2),
                iMax * (3)
            ]:
                for d in [jMax - (1), jMax, jMax + (1)]:
                    if (n <= MAX_UINT256 and d <= MAX_UINT256):
                        testReducedFraction(Fraction256({ 'n': n, 'd': d }), max);

for n1 in [0, 1, 2, 3]:
    for d1 in [1, 2, 3, 4]:
        fraction1 = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [0, 1, 2, 3]:
            for d2 in [1, 2, 3, 4]:
                fraction2 = Fraction256({ 'n': n2, 'd': d2 });
                for weight1 in [1, 2, 4, 8]:
                    for weight2 in [1, 2, 4, 8]:
                        testWeightedAverage(fraction1, fraction2, weight1, weight2);

for n1 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT112]:
    for d1 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT112]:
        fraction1 = Fraction256({ 'n': n1, 'd': d1 });
        for n2 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
            for d2 in [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]:
                fraction2 = Fraction256({ 'n': n2, 'd': d2 });
                for weight1 in [1, 2, 4, 8]:
                    for weight2 in [1, 2, 4, 8]:
                        testWeightedAverage(fraction1, fraction2, weight1, weight2);

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
                        x = 2 ** (px) + (ax);
                        y = 2 ** (py) + (ay);
                        z = 2 ** (pz) + (az);
                        testMulDiv(x, y, z);

for px in [64, 128, 192, 256]:
    for py in [64, 128, 192, 256]:
        for pz in [64, 128, 192, 256]:
            for ax in [2 ** (px >> 1), 1]:
                for ay in [2 ** (py >> 1), 1]:
                    for az in [2 ** (pz >> 1), 1]:
                        x = 2 ** (px) - (ax);
                        y = 2 ** (py) - (ay);
                        z = 2 ** (pz) - (az);
                        testMulDiv(x, y, z);

for px in [128, 192, 256]:
    for py in [128, 192, 256]:
        for pz in [128, 192, 256]:
            for ax in [3, 5, 7]:
                for ay in [3, 5, 7]:
                    for az in [3, 5, 7]:
                        x = 2 ** (px) // (ax);
                        y = 2 ** (py) // (ay);
                        z = 2 ** (pz) // (az);
                        testMulDiv(x, y, z);
