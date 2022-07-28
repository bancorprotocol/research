from common import read, write

from bancor_research.bancor_emulator.solidity.uint.float import Decimal
from bancor_research.bancor_emulator.solidity import uint32, uint256, block

from bancor_research.bancor_emulator.BancorNetwork import BancorNetwork
from bancor_research.bancor_emulator.BNTPool import BNTPool
from bancor_research.bancor_emulator.Constants import PPM_RESOLUTION
from bancor_research.bancor_emulator.ERC20 import ERC20 as IERC20
from bancor_research.bancor_emulator.NetworkSettings import NetworkSettings
from bancor_research.bancor_emulator.PendingWithdrawals import PendingWithdrawals
from bancor_research.bancor_emulator.PoolCollection import PoolCollection
from bancor_research.bancor_emulator.PoolToken import PoolToken
from bancor_research.bancor_emulator.PoolTokenFactory import PoolTokenFactory
from bancor_research.bancor_emulator.ReserveToken import ReserveToken
from bancor_research.bancor_emulator.StandardRewards import StandardRewards
from bancor_research.bancor_emulator.TokenGovernance import TokenGovernance
from bancor_research.bancor_emulator.Vault import Vault

DEPLOYER = 'DEPLOYER'
DEFAULT_DECIMALS = 18
MAX_UINT256 = 2 ** 256 - 1

def toPPM(percentStr):
    return uint32(Decimal(percentStr[:-1]) / 100 * int(PPM_RESOLUTION))

def decimalToInteger(value, decimals: int):
    return uint256(Decimal(value) * 10 ** decimals)

def integerToDecimal(value, decimals: int):
    return Decimal(int(value)) / 10 ** decimals

def integerToDecimalToStr(value, decimals: int):
    return str(integerToDecimal(value, decimals))

def execute(fileName):
    print(fileName)

    flow = read(fileName)

    tknDecimals   = flow['tknDecimals']
    bntDecimals   = DEFAULT_DECIMALS
    bntknDecimals = DEFAULT_DECIMALS
    bnbntDecimals = DEFAULT_DECIMALS

    epVaultBalance = decimalToInteger(flow['epVaultBalance'], tknDecimals)
    bntknAmount = decimalToInteger(flow['tknRewardsAmount'], bntknDecimals)
    bnbntAmount = decimalToInteger(flow['bntRewardsAmount'], bnbntDecimals)
    tknAmount = sum([decimalToInteger(user['tknBalance'], tknDecimals) for user in flow['users']], uint256()) + epVaultBalance
    bntAmount = sum([decimalToInteger(user['bntBalance'], bntDecimals) for user in flow['users']], uint256())

    bnt   = ReserveToken('BNT'  , 'BNT'  , bntDecimals)
    vbnt  = ReserveToken('VBNT' , 'VBNT' , bntDecimals)
    tkn   = ReserveToken('TKN'  , 'TKN'  , tknDecimals)
    bnbnt = PoolToken   ('bnBNT', 'bnBNT', bnbntDecimals, bnt)

    bntGovernance      = TokenGovernance(bnt)
    vbntGovernance     = TokenGovernance(vbnt)
    networkSettings    = NetworkSettings(bnt)
    masterVault        = Vault(bntGovernance, vbntGovernance)
    epVault            = Vault(bntGovernance, vbntGovernance)
    erVault            = Vault(bntGovernance, vbntGovernance)
    network            = BancorNetwork(bntGovernance, vbntGovernance, networkSettings, masterVault, epVault, bnbnt)
    bntPool            = BNTPool(network, bntGovernance, vbntGovernance, networkSettings, masterVault, bnbnt)
    pendingWithdrawals = PendingWithdrawals(network, bnt, bntPool)
    poolTokenFactory   = PoolTokenFactory()
    poolMigrator       = None
    poolCollection     = PoolCollection(network, bnt, networkSettings, masterVault, bntPool, epVault, poolTokenFactory, poolMigrator)
    standardRewards    = StandardRewards(network, networkSettings, bntGovernance, vbnt, bntPool);

    networkSettings.initialize()
    network.initialize(bntPool, pendingWithdrawals, poolMigrator)
    bntPool.initialize()
    pendingWithdrawals.initialize()
    poolTokenFactory.initialize()
    standardRewards.initialize()

    networkSettings.addTokenToWhitelist(tkn);
    networkSettings.setWithdrawalFeePPM(toPPM(flow['withdrawalFee']));
    networkSettings.setMinLiquidityForTrading(decimalToInteger(flow['bntMinLiquidity'], bntDecimals));
    networkSettings.setFundingLimit(tkn, decimalToInteger(flow['bntFundingLimit'], bntDecimals));

    pendingWithdrawals.setLockDuration(0);

    network.registerPoolCollection(poolCollection)
    network.createPools([tkn], poolCollection)
    bntkn = network.collectionByPool(tkn).poolToken(tkn)

    poolCollection.setNetworkFeePPM(toPPM(flow['networkFee']));
    poolCollection.setTradingFeePPM(tkn, toPPM(flow['tradingFee']));

    tkn.issue(DEPLOYER, tknAmount);
    bntGovernance.mint(DEPLOYER, bntAmount);
    tkn.connect(DEPLOYER).transfer(epVault, epVaultBalance);

    for user in flow['users']:
        assert user['id'] != DEPLOYER
        for contract in [network, standardRewards]:
            for token in [vbnt, tkn, bnt, bntkn, bnbnt]:
                token.connect(user['id']).approve(contract, MAX_UINT256);
        tkn.connect(DEPLOYER).transfer(user['id'], decimalToInteger(user['tknBalance'], tknDecimals));
        bnt.connect(DEPLOYER).transfer(user['id'], decimalToInteger(user['bntBalance'], bntDecimals));

    tknProgramId = standardRewards.createProgram(tkn, bntknAmount, block.timestamp, block.timestamp + flow['tknRewardsDuration']);
    bntProgramId = standardRewards.createProgram(bnt, bnbntAmount, block.timestamp, block.timestamp + flow['bntRewardsDuration']);

    for token in [vbnt, tkn, bnt, bntkn, bnbnt]:
        assert token.balanceOf(DEPLOYER) == 0;

    def toWei(userId: str, amount: str, decimals: int, token: IERC20):
        if (amount.endswith('%')):
            balance = token.balanceOf(userId);
            return balance * (toPPM(amount)) / (PPM_RESOLUTION);
        return decimalToInteger(amount, decimals);

    def depositTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn);
        network.connect(userId).deposit(tkn, wei);

    def depositBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt);
        network.connect(userId).deposit(bnt, wei);

    def withdrawTKN(userId: str, amount: str):
        wei = toWei(userId, amount, bntknDecimals, bntkn);
        id = network.connect(userId).initWithdrawal(bntkn, wei);
        network.connect(userId).withdraw(id);

    def withdrawBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bnbntDecimals, bnbnt);
        id = network.connect(userId).initWithdrawal(bnbnt, wei);
        network.connect(userId).withdraw(id);

    def tradeTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn);
        network.connect(userId).tradeBySourceAmount(tkn, bnt, wei, 1, MAX_UINT256, userId);

    def tradeBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt);
        network.connect(userId).tradeBySourceAmount(bnt, tkn, wei, 1, MAX_UINT256, userId);

    def burnPoolTokenTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn);
        bntkn.connect(userId).burn(wei);

    def burnPoolTokenBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt);
        bnbnt.connect(userId).burn(wei);

    def joinTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn);
        standardRewards.connect(userId).join(tknProgramId, wei);

    def joinBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt);
        standardRewards.connect(userId).join(bntProgramId, wei);

    def leaveTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn);
        standardRewards.connect(userId).leave(tknProgramId, wei);

    def leaveBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt);
        standardRewards.connect(userId).leave(bntProgramId, wei);

    def claimRewardsTKN(userId: str):
        standardRewards.connect(userId).claimRewards([tknProgramId]);

    def claimRewardsBNT(userId: str):
        standardRewards.connect(userId).claimRewards([bntProgramId]);

    def setFundingLimit(amount: str):
        networkSettings.setFundingLimit(tkn, decimalToInteger(amount, bntDecimals));

    def enableTrading(bntVirtualBalance: int, tknVirtualBalance: int):
        poolCollection.enableTrading(tkn, uint256(bntVirtualBalance), uint256(tknVirtualBalance));

    def getState():
        state = {
            'tknBalances': {},
            'bntBalances': {},
            'bntknBalances': {},
            'bnbntBalances': {},
            'bntCurrentPoolFunding': '0',
            'tknStakedBalance': '0',
            'bntStakedBalance': '0',
            'tknTradingLiquidity': '0',
            'bntTradingLiquidity': '0',
            'averageRateN': '0',
            'averageRateD': '0',
            'averageInvRateN': '0',
            'averageInvRateD': '0'
        };

        for user in flow['users']:
            state['tknBalances'][user['id']] = integerToDecimalToStr(tkn.balanceOf(user['id']), tknDecimals);
            state['bntBalances'][user['id']] = integerToDecimalToStr(bnt.balanceOf(user['id']), bntDecimals);
            state['bntknBalances'][user['id']] = integerToDecimalToStr(bntkn.balanceOf(user['id']), bntknDecimals);
            state['bnbntBalances'][user['id']] = integerToDecimalToStr(bnbnt.balanceOf(user['id']), bnbntDecimals);

        state['tknBalances']['masterVault'] = integerToDecimalToStr(tkn.balanceOf(masterVault), tknDecimals);
        state['tknBalances']['epVault'] = integerToDecimalToStr(tkn.balanceOf(epVault), tknDecimals);
        state['bntBalances']['masterVault'] = integerToDecimalToStr(bnt.balanceOf(masterVault), bntDecimals);
        state['bntknBalances']['erVault'] = integerToDecimalToStr(bntkn.balanceOf(erVault), bntknDecimals);
        state['bnbntBalances']['bntPool'] = integerToDecimalToStr(bnbnt.balanceOf(bntPool), bnbntDecimals);

        poolData = poolCollection.poolData(tkn);
        state['bntCurrentPoolFunding'] = integerToDecimalToStr(bntPool.currentPoolFunding(tkn), bntDecimals);
        state['tknStakedBalance'] = integerToDecimalToStr(poolData.liquidity.stakedBalance, tknDecimals);
        state['bntStakedBalance'] = integerToDecimalToStr(bntPool.stakedBalance(), bntDecimals);
        state['tknTradingLiquidity'] = integerToDecimalToStr(poolData.liquidity.baseTokenTradingLiquidity, tknDecimals);
        state['bntTradingLiquidity'] = integerToDecimalToStr(poolData.liquidity.bntTradingLiquidity, bntDecimals);
        state['averageRateN'] = integerToDecimalToStr(poolData.averageRates.rate.n, 0);
        state['averageRateD'] = integerToDecimalToStr(poolData.averageRates.rate.d, 0);
        state['averageInvRateN'] = integerToDecimalToStr(poolData.averageRates.invRate.n, 0);
        state['averageInvRateD'] = integerToDecimalToStr(poolData.averageRates.invRate.d, 0);

        return state;

    for n in range(len(flow['operations'])):
        operation = flow['operations'][n]

        print('{} out of {}: {}({})'.format(n + 1, len(flow['operations']), operation['type'], operation['amount']))

        if (operation['elapsed'] > 0):
            block.number += 1;
            block.timestamp += operation['elapsed'];

        if operation['type'] == 'depositTKN':
            depositTKN(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'depositBNT':
            depositBNT(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'withdrawTKN':
            withdrawTKN(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'withdrawBNT':
            withdrawBNT(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'tradeTKN':
            tradeTKN(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'tradeBNT':
            tradeBNT(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'burnPoolTokenTKN':
            burnPoolTokenTKN(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'burnPoolTokenBNT':
            burnPoolTokenBNT(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'joinTKN':
            joinTKN(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'joinBNT':
            joinBNT(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'leaveTKN':
            leaveTKN(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'leaveBNT':
            leaveBNT(operation['userId'], operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'claimRewardsTKN':
            claimRewardsTKN(operation['userId']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'claimRewardsBNT':
            claimRewardsBNT(operation['userId']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'setFundingLimit':
            setFundingLimit(operation['amount']);
            operation['expected'] = getState();
            continue

        if operation['type'] == 'enableTrading':
            enableTrading(operation['amount']['bntVirtualBalance'], operation['amount']['baseTokenVirtualBalance']);
            operation['expected'] = getState();
            continue

        raise Exception('unsupported operation `{}` encountered'.format(operation['type']));

    write(fileName, flow)

execute('BancorNetworkSimpleFinancialScenario1');
execute('BancorNetworkSimpleFinancialScenario2');
execute('BancorNetworkSimpleFinancialScenario3');
execute('BancorNetworkSimpleFinancialScenario4');
execute('BancorNetworkSimpleFinancialScenario5');
execute('BancorNetworkSimpleFinancialScenario6');
execute('BancorNetworkComplexFinancialScenario1');
execute('BancorNetworkComplexFinancialScenario2');
execute('BancorNetworkRewardsFinancialScenario1');
execute('BancorNetworkRewardsFinancialScenario2');
