from common import read, assertAlmostEqual, LesserOrEqual, GreaterOrEqual

from bancor_research.bancor_emulator.PoolCollectionWithdrawal import PoolCollectionWithdrawal

maxErrors = {
    'PoolCollectionWithdrawalCoverage1': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000002' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000002' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000008' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000000003' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage2': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000002' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000002' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.000000000000000008' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000000003' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage3': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000000000000006' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000000000000006' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000000000000000002' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000000000000000002' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage4': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000002' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000002' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.003' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.003' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage5': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.000000000002' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.000000000002' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000004' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000004' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage6': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000002' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000000002' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000003' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000000000003' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage7': {
        'p': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000000006' },
        'q': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000000006' },
        'r': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.000000000000000000000000000005' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.00000003', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.003' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.003' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    },

    'PoolCollectionWithdrawalCoverage8': {
        'p': { 'maxAbsoluteError': 0, 'maxRelativeError': '0' },
        'q': { 'maxAbsoluteError': 0, 'maxRelativeError': '0' },
        'r': { 'maxAbsoluteError': 0, 'maxRelativeError': '0' },
        's': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': LesserOrEqual },
        't': { 'maxAbsoluteError': 0, 'maxRelativeError': '0' },
        'u': { 'maxAbsoluteError': 1, 'maxRelativeError': '0.0000002' },
        'v': { 'maxAbsoluteError': 1, 'maxRelativeError': '0', 'relation': GreaterOrEqual }
    }
}

for fileName in maxErrors:
    table = read(fileName)

    for row in table:
        a, b, c, e, w, m, n, x = [row[z] for z in 'a, b, c, e, w, m, n, x'.split(', ')]
        p, q, r, s, t, u, v = [row[z] for z in 'p, q, r, s, t, u, v'.split(', ')]
        actual = PoolCollectionWithdrawal.calculateWithdrawalAmounts(a, b, c, e, w, m, n, x)
        actual.p = actual.p.value.data * (-1 if actual.p.isNeg else 1)
        actual.q = actual.q.value.data * (-1 if actual.q.isNeg else 1)
        actual.r = actual.r.value.data * (-1 if actual.r.isNeg else 1)
        actual.s = actual.s.data
        actual.t = actual.t.data
        actual.u = actual.u.data
        actual.v = actual.v.data
        print(
            fileName + ':',
            actual.p,
            actual.q,
            actual.r,
            actual.s,
            actual.t,
            actual.u,
            actual.v
        )
        assertAlmostEqual(p, actual.p, **maxErrors[fileName]['p'])
        assertAlmostEqual(q, actual.q, **maxErrors[fileName]['q'])
        assertAlmostEqual(r, actual.r, **maxErrors[fileName]['r'])
        assertAlmostEqual(s, actual.s, **maxErrors[fileName]['s'])
        assertAlmostEqual(t, actual.t, **maxErrors[fileName]['t'])
        assertAlmostEqual(u, actual.u, **maxErrors[fileName]['u'])
        assertAlmostEqual(v, actual.v, **maxErrors[fileName]['v'])
