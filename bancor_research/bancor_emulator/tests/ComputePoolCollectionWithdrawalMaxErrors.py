import os
import json

from bancor_research.bancor_emulator.solidity.uint.float import Decimal
from bancor_research.bancor_emulator.PoolCollectionWithdrawal import PoolCollectionWithdrawal

maxErrors = {}

def fix(err):
    i = 2;
    while (err[i] == '0'):
        i += 1;
    if (err[i] == '9'):
        return err[0: i - 1] + '1';
    return err[0: i] + str(int(err[i]) + 1);

def getMaxErr(x, y, maxDiff, maxErr):
    z = Decimal(x);
    w = Decimal(y);
    maxDiff = Decimal(maxDiff)
    if not (z - maxDiff <= w <= z + maxDiff):
        err = abs(w / z - 1) if z != 0 else 1;
        if (err > Decimal(maxErr)):
            return fix('{:.200f}'.format(err));
    return maxErr;

for fileName in ['PoolCollectionWithdrawalCoverage{}'.format(n + 1) for n in range(8)]:
    file = open('{}/project/tests/data/{}.json'.format(os.path.dirname(__file__), fileName)))
    table = json.loads(file.read());
    file.close()

    maxErrors[fileName] = {
        'p': '0',
        'q': '0',
        'r': '0',
        's': '0',
        't': '0',
        'u': '0',
        'v': '0',
    }

    for row in table:
        a, b, c, e, w, m, n, x = [row[z] for z in 'a, b, c, e, w, m, n, x'.split(', ')]
        p, q, r, s, t, u, v = [row[z] for z in 'p, q, r, s, t, u, v'.split(', ')]
        actual = PoolCollectionWithdrawal.calculateWithdrawalAmounts(a, b, c, e, w, m, n, x);
        actual.p = actual.p.value.data * (-1 if actual.p.isNeg else 1);
        actual.q = actual.q.value.data * (-1 if actual.q.isNeg else 1);
        actual.r = actual.r.value.data * (-1 if actual.r.isNeg else 1);
        actual.s = actual.s.data;
        actual.t = actual.t.data;
        actual.u = actual.u.data;
        actual.v = actual.v.data;
        maxErrors[fileName]['p'] = getMaxErr(p, actual.p, '1', maxErrors[fileName]['p']);
        maxErrors[fileName]['q'] = getMaxErr(q, actual.q, '1', maxErrors[fileName]['q']);
        maxErrors[fileName]['r'] = getMaxErr(r, actual.r, '1', maxErrors[fileName]['r']);
        maxErrors[fileName]['s'] = getMaxErr(s, actual.s, '1', maxErrors[fileName]['s']);
        maxErrors[fileName]['t'] = getMaxErr(t, actual.t, '1', maxErrors[fileName]['t']);
        maxErrors[fileName]['u'] = getMaxErr(u, actual.u, '1', maxErrors[fileName]['u']);
        maxErrors[fileName]['v'] = getMaxErr(v, actual.v, '1', maxErrors[fileName]['v']);

    print("            test('{}', {{".format(fileName));
    print("                p: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }},".format(maxErrors[fileName]['p']));
    print("                q: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }},".format(maxErrors[fileName]['q']));
    print("                r: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }},".format(maxErrors[fileName]['r']));
    print("                s: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }},".format(maxErrors[fileName]['s']));
    print("                t: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }},".format(maxErrors[fileName]['t']));
    print("                u: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }},".format(maxErrors[fileName]['u']));
    print("                v: {{ maxAbsoluteError: new Decimal(1), maxRelativeError: new Decimal('{}') }}" .format(maxErrors[fileName]['v']));
    print("            });\n");
