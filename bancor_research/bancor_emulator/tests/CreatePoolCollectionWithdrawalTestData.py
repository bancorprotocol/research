from common import read, write

from bancor_research.bancor_emulator import config
config.enable_full_precision_mode(True)

from bancor_research.bancor_emulator.PoolCollectionWithdrawal import PoolCollectionWithdrawal

for fileName in ['PoolCollectionWithdrawalCoverage{}'.format(n + 1) for n in range(8)]:
    table = read(fileName)

    for row in table:
        a, b, c, e, w, m, n, x = [row[z] for z in 'a, b, c, e, w, m, n, x'.split(', ')]
        actual = PoolCollectionWithdrawal.calculateWithdrawalAmounts(a, b, c, e, w, m, n, x)
        row['p'] = '{:.12f}'.format(actual.p.value.data * (-1 if actual.p.isNeg else 1))
        row['q'] = '{:.12f}'.format(actual.q.value.data * (-1 if actual.q.isNeg else 1))
        row['r'] = '{:.12f}'.format(actual.r.value.data * (-1 if actual.r.isNeg else 1))
        row['s'] = '{:.12f}'.format(actual.s.data)
        row['t'] = '{:.12f}'.format(actual.t.data)
        row['u'] = '{:.12f}'.format(actual.u.data)
        row['v'] = '{:.12f}'.format(actual.v.data)

    write(fileName, table)
    print(fileName)
