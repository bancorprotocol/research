import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from PoolCollectionWithdrawal import PoolCollectionWithdrawal
import json

from decimal import Decimal
from decimal import getcontext

getcontext().prec = 155

class Relation:
    LesserOrEqual = 1
    GreaterOrEqual = 2

maxErrors = {
    'PoolCollectionWithdrawalCoverage1': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000002') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000002') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000000003') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000000003') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage2': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000002') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000002') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000000003') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000000003') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage3': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000000000000006') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000000000000006') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000000000000000000004') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000000000000000000004') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage4': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000002') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000002') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.003') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.003') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage5': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000000002') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000000002') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000007') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000007') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage6': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000002') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000000002') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000003') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000000000003') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage7': {
        'p': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000000006') },
        'q': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000000006') },
        'r': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000000000000000000000000005') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.00000003'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000002') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.000000002') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage8': {
        'p': { 'maxAbsoluteError': Decimal(0), 'maxRelativeError': Decimal('0') },
        'q': { 'maxAbsoluteError': Decimal(0), 'maxRelativeError': Decimal('0') },
        'r': { 'maxAbsoluteError': Decimal(0), 'maxRelativeError': Decimal('0') },
        's': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.LesserOrEqual },
        't': { 'maxAbsoluteError': Decimal(0), 'maxRelativeError': Decimal('0') },
        'u': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0.0000002') },
        'v': { 'maxAbsoluteError': Decimal(1), 'maxRelativeError': Decimal('0'), 'relation': Relation.GreaterOrEqual }
    }
}

def assertAlmostEqual(expected, actual, maxError):
    actual = Decimal(actual);
    expected = Decimal(expected);
    if actual != expected:
        if 'relation' in maxError:
            if maxError['relation'] == Relation.LesserOrEqual:
                assert actual <= expected
            if maxError['relation'] == Relation.GreaterOrEqual:
                assert actual >= expected
        absoluteError = abs(actual - expected);
        relativeError = absoluteError / expected;
        assert absoluteError <= maxError['maxAbsoluteError'] or relativeError <= maxError['maxRelativeError']

for fileName in maxErrors:
    file = open(os.path.dirname(__file__) + '/project/tests/data/' + fileName + '.json')
    table = json.loads(file.read());
    file.close()
    for row in table:
        a, b, c, e, w, m, n, x = [int(row[z]) for z in 'a, b, c, e, w, m, n, x'.split(', ')]
        p, q, r, s, t, u, v = [Decimal(row[z]) for z in 'p, q, r, s, t, u, v'.split(', ')]
        actual = PoolCollectionWithdrawal.calculateWithdrawalAmounts(a, b, c, e, w, m, n, x);
        actual.p = int(actual.p.value) * (-1 if actual.p.isNeg else 1);
        actual.q = int(actual.q.value) * (-1 if actual.q.isNeg else 1);
        actual.r = int(actual.r.value) * (-1 if actual.r.isNeg else 1);
        actual.s = int(actual.s);
        actual.t = int(actual.t);
        actual.u = int(actual.u);
        actual.v = int(actual.v);
        print(
            fileName + ':',
            actual.p,
            actual.q,
            actual.r,
            actual.s,
            actual.t,
            actual.u,
            actual.v
        );
        assertAlmostEqual(p, actual.p, maxErrors[fileName]['p'])
        assertAlmostEqual(q, actual.q, maxErrors[fileName]['q'])
        assertAlmostEqual(r, actual.r, maxErrors[fileName]['r'])
        assertAlmostEqual(s, actual.s, maxErrors[fileName]['s'])
        assertAlmostEqual(t, actual.t, maxErrors[fileName]['t'])
        assertAlmostEqual(u, actual.u, maxErrors[fileName]['u'])
        assertAlmostEqual(v, actual.v, maxErrors[fileName]['v'])
