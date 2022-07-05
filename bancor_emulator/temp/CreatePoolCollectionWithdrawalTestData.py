import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

import json

import config
config.mode = 'float'

from PoolCollectionWithdrawal import PoolCollectionWithdrawal

for fileName in ['PoolCollectionWithdrawalCoverage{}'.format(n + 1) for n in range(8)]:
    file = open(os.path.dirname(__file__) + '/project/tests/data/' + fileName + '.json')
    table = json.loads(file.read());
    file.close()

    for row in table:
        a, b, c, e, w, m, n, x = [row[z] for z in 'a, b, c, e, w, m, n, x'.split(', ')]
        actual = PoolCollectionWithdrawal.calculateWithdrawalAmounts(a, b, c, e, w, m, n, x);
        row['p'] = '{:.12f}'.format(actual.p.value.data * (-1 if actual.p.isNeg else 1));
        row['q'] = '{:.12f}'.format(actual.q.value.data * (-1 if actual.q.isNeg else 1));
        row['r'] = '{:.12f}'.format(actual.r.value.data * (-1 if actual.r.isNeg else 1));
        row['s'] = '{:.12f}'.format(actual.s.data);
        row['t'] = '{:.12f}'.format(actual.t.data);
        row['u'] = '{:.12f}'.format(actual.u.data);
        row['v'] = '{:.12f}'.format(actual.v.data);

    file = open(os.path.dirname(__file__) + '/project/tests/data/' + fileName + '.json', "w")
    file.write(json.dumps(table, indent = 2));
    file.close()

    print(fileName)
