const MathEx = artifacts.require("TestMathEx");

const BN = web3.utils.BN;

const MAX_UINT32 = new BN(1).shln(32).subn(1);
const MAX_UINT64 = new BN(1).shln(64).subn(1);
const MAX_UINT96 = new BN(1).shln(96).subn(1);
const MAX_UINT112 = new BN(1).shln(112).subn(1);
const MAX_UINT128 = new BN(1).shln(128).subn(1);
const MAX_UINT256 = new BN(1).shln(256).subn(1);

const TEST_ARRAY = [
    new BN(0),
    new BN(100),
    new BN(10_000),
    MAX_UINT128,
    MAX_UINT256.divn(2),
    MAX_UINT256.sub(MAX_UINT128),
    MAX_UINT256
];

const mulDivFuncs = {
    mulDivF: (x, y, z) => x.mul(y).div(z),
    mulDivC: (x, y, z) => x.mul(y).add(z).subn(1).div(z)
};

const cmp512Funcs = {
    gt512: (x, y) => x.gt(y),
    lt512: (x, y) => x.lt(y),
    gte512: (x, y) => x.gte(y),
    lte512: (x, y) => x.lte(y)
};

const toUint512 = (x) => [x.shrn(256), x.maskn(256)];

contract('MathEx', () => {
    let mathEx;

    before(async () => {
        mathEx = await MathEx.new();
    });

    const testExp = async (f) => {
        console.log(`exp2(${f.n} / ${f.d})`);
        try {
            const actual = await mathEx.exp2([f.n, f.d]);
            console.log(`${actual.n} / ${actual.d}`);
        }
        catch (error) {
            assert(error.message.includes('Overflow'), error.message);
            console.log('Overflow');
        }
    };

    const testTruncatedFraction = async (f, max) => {
        console.log(`truncatedFraction(${f.n} / ${f.d}, ${max})`);
        try {
            const actual = await mathEx.truncatedFraction([f.n, f.d], max);
            console.log(`${actual.n} / ${actual.d}`);
        }
        catch (error) {
            assert(error.message.includes('InvalidFraction'), error.message);
            console.log('InvalidFraction');
        }
    };

    const testWeightedAverage = async (f1, f2, w1, w2) => {
        console.log(`weightedAverage(${f1.n} / ${f1.d}, ${f2.n} / ${f2.d}, ${w1}, ${w2})`);
        const actual = await mathEx.weightedAverage([f1.n, f1.d], [f2.n, f2.d], w1, w2);
        console.log(`${actual.n} / ${actual.d}`);
    };

    const testIsInRange = async (f1, f2, maxDeviation) => {
        console.log(`isInRange(${f1.n} / ${f1.d}, ${f2.n} / ${f2.d}, ${maxDeviation}%)`);
        const actual = await mathEx.isInRange([f1.n, f1.d], [f2.n, f2.d], maxDeviation * 10000);
        console.log(actual);
    };

    const testMulDiv = async (x, y, z) => {
        for (const funcName in mulDivFuncs) {
            console.log(`${funcName}(${x}, ${y}, ${z})`);
            const expectedFunc = mulDivFuncs[funcName];
            const actualFunc = mathEx[funcName];
            const expected = expectedFunc(new BN(x), new BN(y), new BN(z));
            if (expected.lte(MAX_UINT256)) {
                const actual = await actualFunc(x, y, z);
                console.log(actual.toString());
            } else {
                try {
                    await actualFunc(x, y, z);
                    throw new Error('');
                }
                catch (error) {
                    assert(error.message.includes('Overflow'), error.message);
                    console.log('Overflow');
                }
            }
        }
    };

    const testSubMax0 = async (x, y) => {
        console.log(`subMax0(${x}, ${y})`);
        const actual = await mathEx.subMax0(x, y);
        console.log(actual.toString());
    };

    const testMul512 = async (x, y) => {
        console.log(`mul512(${x}, ${y})`);
        const actual = await mathEx.mul512(x, y);
        console.log(actual.toString());
    };

    const testCmp512 = async (a, b) => {
        for (const x of [a, a.addn(1).mul(b)]) {
            for (const y of [b, b.addn(1).mul(a)]) {
                for (const funcName in cmp512Funcs) {
                    console.log(`${funcName}(${x}, ${y})`);
                    const actual = await mathEx[funcName](toUint512(x), toUint512(y));
                    console.log(actual);
                }
            }
        }
    };

    it('', async () => {
        console.log();

        for (let n = 0; n < 10; n++) {
            for (let d = 1; d < 10; d++) {
                await testExp({ n, d });
            }
        }

        for (let d = 1000; d < 1000000000; d *= 10) {
            for (let n = 1; n <= 10; n++) {
                await testExp({ n, d });
            }
        }

        for (let d = 1000; d < 1000000000; d *= 10) {
            for (let n = d - 10; n <= d - 1; n++) {
                await testExp({ n, d });
            }
        }

        for (let d = 1000; d < 1000000000; d *= 10) {
            for (let n = d + 1; n <= d + 10; n++) {
                await testExp({ n, d });
            }
        }

        for (let d = 1000; d < 1000000000; d *= 10) {
            for (let n = 2 * d - 10; n <= 2 * d - 1; n++) {
                await testExp({ n, d });
            }
        }

        for (let d = 1000; d < 1000000000; d *= 10) {
            for (let n = 2 * d + 1; n <= 2 * d + 10; n++) {
                await testExp({ n, d });
            }
        }

        for (const max of [MAX_UINT128]) {
            for (let n = 0; n < 10; n++) {
                for (let d = 0; d < 10; d++) {
                    await testTruncatedFraction({ n: max.subn(n), d: max.subn(d) }, max);
                    await testTruncatedFraction({ n: max.subn(n), d: max.addn(d) }, max);
                    await testTruncatedFraction({ n: max.addn(n), d: max.subn(d) }, max);
                    await testTruncatedFraction({ n: max.addn(n), d: max.addn(d) }, max);
                }
            }
        }

        for (const n of [100, 200]) {
            for (const d of [2, 3]) {
                for (const max of [3, 5]) {
                    await testTruncatedFraction({ n, d }, max);
                }
            }
        }

        for (const n of [MAX_UINT64, MAX_UINT96]) {
            for (const d of [MAX_UINT64, MAX_UINT96]) {
                const fraction1 = { n, d };
                for (const n of [MAX_UINT64, MAX_UINT96]) {
                    for (const d of [MAX_UINT64, MAX_UINT96]) {
                        const fraction2 = { n, d };
                        for (const weight1 of [2, 8]) {
                            for (const weight2 of [2, 8]) {
                                await testWeightedAverage(fraction1, fraction2, weight1, weight2);
                            }
                        }
                    }
                }
            }
        }

        for (const n of [MAX_UINT64, MAX_UINT96]) {
            for (const d of [MAX_UINT64, MAX_UINT96]) {
                const baseSample = { n, d };
                for (const n of [MAX_UINT64, MAX_UINT96]) {
                    for (const d of [MAX_UINT64, MAX_UINT96]) {
                        const offsetSample = { n, d };
                        for (const maxDeviation of [2, 5]) {
                            await testIsInRange(baseSample, offsetSample, maxDeviation);
                        }
                    }
                }
            }
        }

        for (const px of [128, 192, 256]) {
            for (const py of [128, 192, 256]) {
                for (const pz of [128, 192, 256]) {
                    for (const ax of [3, 5, 7]) {
                        for (const ay of [3, 5, 7]) {
                            for (const az of [3, 5, 7]) {
                                const x = new BN(1).shln(px).divn(ax);
                                const y = new BN(1).shln(py).divn(ay);
                                const z = new BN(1).shln(pz).divn(az);
                                await testMulDiv(x, y, z);
                            }
                        }
                    }
                }
            }
        }

        for (const x of TEST_ARRAY) {
            for (const y of TEST_ARRAY) {
                await testSubMax0(x, y);
                await testMul512(x, y);
                await testCmp512(x, y);
            }
        }

        for (let n = 0; n < 100; n++) {
            for (let d = 1; d < 100; d++) {
                await testExp({ n, d });
            }
        }

        for (const max of [MAX_UINT96, MAX_UINT112, MAX_UINT128]) {
            for (let n = 0; n < 10; n++) {
                for (let d = 0; d < 10; d++) {
                    await testTruncatedFraction({ n: max.subn(n), d: max.subn(d) }, max);
                    await testTruncatedFraction({ n: max.subn(n), d: max.addn(d) }, max);
                    await testTruncatedFraction({ n: max.addn(n), d: max.subn(d) }, max);
                    await testTruncatedFraction({ n: max.addn(n), d: max.addn(d) }, max);
                }
            }
        }

        for (const max of [MAX_UINT112]) {
            for (let i = new BN(1); i.lte(max); i = i.muln(10)) {
                for (let j = new BN(1); j.lte(max); j = j.muln(10)) {
                    const n = MAX_UINT256.div(max).mul(i).addn(1);
                    const d = MAX_UINT256.div(max).mul(j).addn(1);
                    await testTruncatedFraction({ n, d }, max);
                }
            }
        }

        for (const max of [MAX_UINT96, MAX_UINT112, MAX_UINT128]) {
            for (let i = 96; i <= 256; i += 16) {
                for (let j = i - 64; j <= i + 64; j += 16) {
                    const iMax = new BN(1).shln(i).subn(1);
                    const jMax = new BN(1).shln(j).subn(1);
                    for (const n of [
                        iMax.divn(3),
                        iMax.divn(2),
                        iMax.muln(2).divn(3),
                        iMax.muln(3).divn(4),
                        iMax.subn(1),
                        iMax,
                        iMax.addn(1),
                        iMax.muln(4).divn(3),
                        iMax.muln(3).divn(2),
                        iMax.muln(2),
                        iMax.muln(3)
                    ]) {
                        for (const d of [jMax.subn(1), jMax, jMax.addn(1)]) {
                            if (n.lte(MAX_UINT256) && d.lte(MAX_UINT256)) {
                                await testTruncatedFraction({ n, d }, max);
                            }
                        }
                    }
                }
            }
        }

        for (const n of [0, 1, 2, 3]) {
            for (const d of [1, 2, 3, 4]) {
                const fraction1 = { n, d };
                for (const n of [0, 1, 2, 3]) {
                    for (const d of [1, 2, 3, 4]) {
                        const fraction2 = { n, d };
                        for (const weight1 of [1, 2, 4, 8]) {
                            for (const weight2 of [1, 2, 4, 8]) {
                                await testWeightedAverage(fraction1, fraction2, weight1, weight2);
                            }
                        }
                    }
                }
            }
        }

        for (const n of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT112]) {
            for (const d of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT112]) {
                const fraction1 = { n, d };
                for (const n of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]) {
                    for (const d of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]) {
                        const fraction2 = { n, d };
                        for (const weight1 of [1, 2, 4, 8]) {
                            for (const weight2 of [1, 2, 4, 8]) {
                                await testWeightedAverage(fraction1, fraction2, weight1, weight2);
                            }
                        }
                    }
                }
            }
        }

        for (const n of [0, 1, 2, 3]) {
            for (const d of [1, 2, 3, 4]) {
                const baseSample = { n, d };
                for (const n of [0, 1, 2, 3]) {
                    for (const d of [1, 2, 3, 4]) {
                        const offsetSample = { n, d };
                        for (const maxDeviation of [0, 2, 5, 10]) {
                            await testIsInRange(baseSample, offsetSample, maxDeviation);
                        }
                    }
                }
            }
        }

        for (const n of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]) {
            for (const d of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]) {
                const baseSample = { n, d };
                for (const n of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]) {
                    for (const d of [MAX_UINT32, MAX_UINT64, MAX_UINT96, MAX_UINT128]) {
                        const offsetSample = { n, d };
                        for (const maxDeviation of [0, 2, 5, 10]) {
                            await testIsInRange(baseSample, offsetSample, maxDeviation);
                        }
                    }
                }
            }
        }

        for (const px of [0, 64, 128, 192, 255, 256]) {
            for (const py of [0, 64, 128, 192, 255, 256]) {
                for (const pz of [1, 64, 128, 192, 255, 256]) {
                    for (const ax of px < 256 ? [-1, 0, +1] : [-1]) {
                        for (const ay of py < 256 ? [-1, 0, +1] : [-1]) {
                            for (const az of pz < 256 ? [-1, 0, +1] : [-1]) {
                                const x = new BN(1).shln(px).addn(ax);
                                const y = new BN(1).shln(py).addn(ay);
                                const z = new BN(1).shln(pz).addn(az);
                                await testMulDiv(x, y, z);
                            }
                        }
                    }
                }
            }
        }

        for (const px of [64, 128, 192, 256]) {
            for (const py of [64, 128, 192, 256]) {
                for (const pz of [64, 128, 192, 256]) {
                    for (const ax of [new BN(1).shln(px >> 1), new BN(1)]) {
                        for (const ay of [new BN(1).shln(py >> 1), new BN(1)]) {
                            for (const az of [new BN(1).shln(pz >> 1), new BN(1)]) {
                                const x = new BN(1).shln(px).sub(ax);
                                const y = new BN(1).shln(py).sub(ay);
                                const z = new BN(1).shln(pz).sub(az);
                                await testMulDiv(x, y, z);
                            }
                        }
                    }
                }
            }
        }

        for (const px of [128, 192, 256]) {
            for (const py of [128, 192, 256]) {
                for (const pz of [128, 192, 256]) {
                    for (const ax of [3, 5, 7]) {
                        for (const ay of [3, 5, 7]) {
                            for (const az of [3, 5, 7]) {
                                const x = new BN(1).shln(px).divn(ax);
                                const y = new BN(1).shln(py).divn(ay);
                                const z = new BN(1).shln(pz).divn(az);
                                await testMulDiv(x, y, z);
                            }
                        }
                    }
                }
            }
        }
    });
});
