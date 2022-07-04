const PoolToken = artifacts.require("PoolToken");
const ERC20 = artifacts.require("ERC20");

contract.only('PoolToken', () => {
    const POOL_TOKEN_NAME = 'Pool Token';
    const POOL_TOKEN_SYMBOL = 'POOL';
    const POOL_TOKEN_DECIMALS = 10;

    const RESERVE_TOKEN_NAME = 'Reserve Token';
    const RESERVE_TOKEN_SYMBOL = 'Reserve';

    let poolToken;
    let reserveToken;

    beforeEach(async () => {
        reserveToken = await ERC20.new(RESERVE_TOKEN_NAME, RESERVE_TOKEN_SYMBOL);
    });

    describe('construction', () => {
        it('should be properly initialized', async () => {
            poolToken = await PoolToken.new(POOL_TOKEN_NAME, POOL_TOKEN_SYMBOL, POOL_TOKEN_DECIMALS, reserveToken.address);

            assert.equal(await poolToken.name(), POOL_TOKEN_NAME);
            assert.equal(await poolToken.symbol(), POOL_TOKEN_SYMBOL);
            assert.equal(await poolToken.decimals(), POOL_TOKEN_DECIMALS);
            assert.equal(await poolToken.totalSupply(), 0);
            assert.equal(await poolToken.reserveToken(), reserveToken.address);
        });
    });
});
