const TestTypes = artifacts.require("TestTypes");

const BN = web3.utils.BN;

contract("TestTypes", () => {
    let testTypes;

    before(async () => {
        testTypes = await TestTypes.new();
    });

    function add(x, y) {return x.data.add(y.data);}
    function sub(x, y) {return x.data.sub(y.data);}
    function mul(x, y) {return x.data.mul(y.data);}
    function div(x, y) {return x.data.div(y.data);}

    const ops = {
        '+': add,
        '-': sub,
        '*': mul,
        '/': div,
    }

    function TypeName(n) {
        return n.type === 'uint' ? `uint${n.size}` : 'int';
    }

    function Print(op, x, y, z) {
        console.log(`    ${TypeName(x)}(${x.data}) ${op} ${TypeName(y)}(${y.data}) = uint${Math.max(x.size, y.size)}(${z})`);
    }

    function PrintError(op, x, y) {
        console.log(`    ${TypeName(x)}(${x.data}) ${op} ${TypeName(y)}(${y.data}) = str(reverted)`);
    }

    const arr = [];

    for (const data of [1, 2]) {
        arr.push({type: 'int', size: 32, data: new BN(data)});
    }

    for (const size of [32, 112, 128, 256]) {
        arr.push({type: 'int' , size: size, data: new BN(1).shln(size - 1).subn(1)});
        arr.push({type: 'int' , size: size, data: new BN(1).shln(size - 1).subn(0)});
        arr.push({type: 'int' , size: size, data: new BN(1).shln(size - 0).subn(2)});
        arr.push({type: 'int' , size: size, data: new BN(1).shln(size - 0).subn(1)});
        arr.push({type: 'uint', size: size, data: new BN(1).shln(size - 1).subn(1)});
        arr.push({type: 'uint', size: size, data: new BN(1).shln(size - 1).subn(0)});
        arr.push({type: 'uint', size: size, data: new BN(1).shln(size - 0).subn(2)});
        arr.push({type: 'uint', size: size, data: new BN(1).shln(size - 0).subn(1)});
        arr.push({type: 'uint', size: size, data: new BN(2)                       });
        arr.push({type: 'uint', size: size, data: new BN(1)                       });
    }

    const sorted_arr = arr.sort((a, b) => a.data.cmp(b.data));

    it('', async () => {
        console.log();

        for (const n of [0, 2, 32, 112, 128, 256]) {
            for (const k of [-1, 0, +1]) {
                const x = new BN(1).shln(n).addn(k);
                for (const cast of [32, 112, 128, 256]) {
                    const y = await testTypes[`to_uint_${cast}`](x.maskn(256));
                    console.log(`uint${cast}(${x}) = ${y}`);
                    assert(y.bitLength() <= cast);
                    assert(y.eq(x.maskn(cast)));
                }
            }
        }

        for (const op in ops) {
            console.log(`Test ${op}:`)
            for (const x of sorted_arr.filter(x => x.type ==='uint')) {
                for (const y of sorted_arr) {
                    try {
                        const z = await testTypes[`${ops[op].name}_${x.size}_${y.size}`](x.data, y.data);
                        Print(op, x, y, z);
                        assert(z.eq(ops[op](x, y)), 'arithmetic error');
                    }
                    catch (error) {
                        PrintError(op, x, y);
                        assert(error.message.includes('reverted with panic code'), error.message);
                        assert(ops[op](x, y).ltn(0) || ops[op](x, y).gt(new BN(1).shln(x.size).subn(1)), 'logical error');
                    }
                }
            }
        }

        for (const op in ops) {
            console.log(`Test unchecked ${op}:`)
            for (const x of sorted_arr.filter(x => x.type ==='uint')) {
                for (const y of sorted_arr) {
                    const z = await testTypes[`unchecked_${ops[op].name}_${x.size}_${y.size}`](x.data, y.data);
                    Print(op, x, y, z);
                    assert(z.eq(ops[op](x, y).add(new BN(1).shln(512)).maskn(Math.max(x.size, y.size))), 'arithmetic error');
                }
            }
        }

        console.log('Test +=')
        for (const n of [0, 2, 32, 112, 128, 256]) {
            for (const k of [-1, 0, +1]) {
                const m = new BN(1).shln(n).addn(k);
                for (const lcast of [32, 112, 128, 256]) {
                    for (const rcast of [32, 112, 128, 256]) {
                        console.log(`    uint${lcast}(${m}) += uint${rcast}(${m})`);
                        try {
                            const x = await testTypes[`iadd_${lcast}_${rcast}`](m.maskn(lcast), m.maskn(rcast));
                            assert(x.eq(m.maskn(lcast).add(m.maskn(rcast))), 'arithmetic error');
                        }
                        catch (error) {
                            assert(error.message.includes(lcast >= rcast ? 'reverted with panic code' : 'is not a function'), error.message);
                        }
                    }
                }
            }
        }

        console.log('Test unchecked +=')
        for (const n of [0, 2, 32, 112, 128, 256]) {
            for (const k of [-1, 0, +1]) {
                const m = new BN(1).shln(n).addn(k);
                for (const lcast of [32, 112, 128, 256]) {
                    for (const rcast of [32, 112, 128, 256]) {
                        console.log(`    uint${lcast}(${m}) += uint${rcast}(${m})`);
                        try {
                            const x = await testTypes[`unchecked_iadd_${lcast}_${rcast}`](m.maskn(lcast), m.maskn(rcast));
                            assert(x.eq(m.maskn(lcast).add(m.maskn(rcast)).maskn(lcast)), 'arithmetic error');
                        }
                        catch (error) {
                            assert(error.message.includes(lcast >= rcast ? 'reverted with panic code' : 'is not a function'), error.message);
                        }
                    }
                }
            }
        }

        console.log('Test *=')
        for (const n of [0, 2, 32, 112, 128, 256]) {
            for (const k of [-1, 0, +1]) {
                const m = new BN(1).shln(n).addn(k);
                for (const lcast of [32, 112, 128, 256]) {
                    for (const rcast of [32, 112, 128, 256]) {
                        console.log(`    uint${lcast}(${m}) *= uint${rcast}(${m})`);
                        try {
                            const x = await testTypes[`imul_${lcast}_${rcast}`](m.maskn(lcast), m.maskn(rcast));
                            assert(x.eq(m.maskn(lcast).mul(m.maskn(rcast))), 'arithmetic error');
                        }
                        catch (error) {
                            assert(error.message.includes(lcast >= rcast ? 'reverted with panic code' : 'is not a function'), error.message);
                        }
                    }
                }
            }
        }

        console.log('Test unchecked *=')
        for (const n of [0, 2, 32, 112, 128, 256]) {
            for (const k of [-1, 0, +1]) {
                const m = new BN(1).shln(n).addn(k);
                for (const lcast of [32, 112, 128, 256]) {
                    for (const rcast of [32, 112, 128, 256]) {
                        console.log(`    uint${lcast}(${m}) *= uint${rcast}(${m})`);
                        try {
                            const x = await testTypes[`unchecked_imul_${lcast}_${rcast}`](m.maskn(lcast), m.maskn(rcast));
                            assert(x.eq(m.maskn(lcast).mul(m.maskn(rcast)).maskn(lcast)), 'arithmetic error');
                        }
                        catch (error) {
                            assert(error.message.includes(lcast >= rcast ? 'reverted with panic code' : 'is not a function'), error.message);
                        }
                    }
                }
            }
        }
    });
});
