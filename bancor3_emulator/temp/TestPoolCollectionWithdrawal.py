import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from PoolCollectionWithdrawal import PoolCollectionWithdrawal
import json

for n in range(8):
    fileName = 'PoolCollectionWithdrawalCoverage{}'.format(n + 1)
    file = open(os.path.dirname(__file__) + '/project/tests/data/' + fileName + '.json')
    table = json.loads(file.read());
    file.close()
    for row in table:
        a, b, c, e, w, m, n, x = [int(row[z]) for z in 'a, b, c, e, w, m, n, x'.split(', ')]
        actual = PoolCollectionWithdrawal.calculateWithdrawalAmounts(a, b, c, e, w, m, n, x);
        actualZp = int(actual.p.value) * (-1 if actual.p.isNeg else 1);
        actualZq = int(actual.q.value) * (-1 if actual.q.isNeg else 1);
        actualZr = int(actual.r.value) * (-1 if actual.r.isNeg else 1);
        print(
            fileName + ':',
            int(actualZp),
            int(actualZq),
            int(actualZr),
            int(actual.s),
            int(actual.t),
            int(actual.u),
            int(actual.v)
        );
