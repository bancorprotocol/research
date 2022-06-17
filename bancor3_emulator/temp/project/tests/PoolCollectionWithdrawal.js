const PoolCollectionWithdrawal = artifacts.require("TestPoolCollectionWithdrawal");

const fs = require("fs");
const path = require("path");

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
                const actualZp = actual.p.isNeg && actual.p.value !== '0' ? '-' + actual.p.value : actual.p.value;
                const actualZq = actual.q.isNeg && actual.q.value !== '0' ? '-' + actual.q.value : actual.q.value;
                const actualZr = actual.r.isNeg && actual.r.value !== '0' ? '-' + actual.r.value : actual.r.value;
                console.log(
                    fileName + ':',
                    actualZp,
                    actualZq,
                    actualZr,
                    actual.s,
                    actual.t,
                    actual.u,
                    actual.v
                );
            }
        };
    });
});
