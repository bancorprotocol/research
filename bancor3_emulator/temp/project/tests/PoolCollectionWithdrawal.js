const PoolCollectionWithdrawal = artifacts.require("TestPoolCollectionWithdrawal");

const fs = require("fs");
const path = require("path");

const BN = web3.utils.BN;

contract.only('PoolCollectionWithdrawal', () => {
    let poolCollectionWithdrawal;

    before(async () => {
        poolCollectionWithdrawal = await PoolCollectionWithdrawal.new();
    });

    it('', async () => {
        console.log();

        for (let n = 1; n <=8; n++) {
            const fileName = `PoolCollectionWithdrawalCoverage${n}`;
            const table = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', fileName + '.json'), { encoding: 'utf8' }));
            for (const { a, b, c, e, w, m, n, x } of table) {
                const actual = await poolCollectionWithdrawal.calculateWithdrawalAmountsT(a, b, c, e, w, m, n, x);
                const actualZp = new BN(actual.p.value).muln(actual.p.isNeg ? -1 : 1);
                const actualZq = new BN(actual.q.value).muln(actual.q.isNeg ? -1 : 1);
                const actualZr = new BN(actual.r.value).muln(actual.r.isNeg ? -1 : 1);
                console.log(
                    fileName + ':',
                    actualZp.toString(),
                    actualZq.toString(),
                    actualZr.toString(),
                    actual.s.toString(),
                    actual.t.toString(),
                    actual.u.toString(),
                    actual.v.toString()
                );
            }
        };
    });
});
