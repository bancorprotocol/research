from common import read, assertAlmostEqual, Decimal

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

class User:
    def __init__(self, data):
        self.id         = data['id        '.strip()]
        self.tknBalance = data['tknBalance'.strip()]
        self.bntBalance = data['bntBalance'.strip()]

class State:
    def __init__(self, data):
        self.tknBalances           = data['tknBalances          '.strip()]
        self.bntBalances           = data['bntBalances          '.strip()]
        self.bntknBalances         = data['bntknBalances        '.strip()]
        self.bnbntBalances         = data['bnbntBalances        '.strip()]
        self.bntCurrentPoolFunding = data['bntCurrentPoolFunding'.strip()]
        self.tknStakedBalance      = data['tknStakedBalance     '.strip()]
        self.bntStakedBalance      = data['bntStakedBalance     '.strip()]
        self.tknTradingLiquidity   = data['tknTradingLiquidity  '.strip()]
        self.bntTradingLiquidity   = data['bntTradingLiquidity  '.strip()]
        self.averageRate           = data['averageRate          '.strip()]
        self.averageInvRate        = data['averageInvRate       '.strip()]

class Operation:
    def __init__(self, data):
        self.type     = data['type    '.strip()]
        self.userId   = data['userId  '.strip()]
        self.amount   = data['amount  '.strip()]
        self.elapsed  = data['elapsed '.strip()]
        self.expected = data['expected'.strip()]

class Flow:
    def __init__(self, data):
        self.tradingFee         = data['tradingFee        '.strip()]
        self.networkFee         = data['networkFee        '.strip()]
        self.withdrawalFee      = data['withdrawalFee     '.strip()]
        self.epVaultBalance     = data['epVaultBalance    '.strip()]
        self.tknDecimals        = data['tknDecimals       '.strip()]
        self.bntMinLiquidity    = data['bntMinLiquidity   '.strip()]
        self.bntFundingLimit    = data['bntFundingLimit   '.strip()]
        self.tknRewardsAmount   = data['tknRewardsAmount  '.strip()]
        self.tknRewardsDuration = data['tknRewardsDuration'.strip()]
        self.bntRewardsAmount   = data['bntRewardsAmount  '.strip()]
        self.bntRewardsDuration = data['bntRewardsDuration'.strip()]
        self.users              = [User     (user     ) for user      in data['users     '.strip()]]
        self.operations         = [Operation(operation) for operation in data['operations'.strip()]]

def toPPM(percent: str):
    return uint32(Decimal(str(PPM_RESOLUTION)) * Decimal(percent[:-1]) / 100)

def toInt(value, decimals: int):
    return uint256(Decimal(value) * 10 ** decimals)

def toDec(value, decimals: int):
    return Decimal(str(value)) / 10 ** decimals

def execute(fileName):
    print(fileName)

    flow = Flow(read(fileName))

    tknDecimals   = flow.tknDecimals
    bntDecimals   = DEFAULT_DECIMALS
    bntknDecimals = DEFAULT_DECIMALS
    bnbntDecimals = DEFAULT_DECIMALS

    epVaultBalance = toInt(flow.epVaultBalance, tknDecimals)
    bntknAmount = toInt(flow.tknRewardsAmount, bntknDecimals)
    bnbntAmount = toInt(flow.bntRewardsAmount, bnbntDecimals)
    tknAmount = sum([toInt(user.tknBalance, tknDecimals) for user in flow.users], uint256()) + epVaultBalance
    bntAmount = sum([toInt(user.bntBalance, bntDecimals) for user in flow.users], uint256())

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
    standardRewards    = StandardRewards(network, networkSettings, bntGovernance, vbnt, bntPool)

    networkSettings.initialize()
    network.initialize(bntPool, pendingWithdrawals, poolMigrator)
    bntPool.initialize()
    pendingWithdrawals.initialize()
    poolTokenFactory.initialize()
    standardRewards.initialize()

    networkSettings.addTokenToWhitelist(tkn)
    networkSettings.setWithdrawalFeePPM(toPPM(flow.withdrawalFee))
    networkSettings.setMinLiquidityForTrading(toInt(flow.bntMinLiquidity, bntDecimals))
    networkSettings.setFundingLimit(tkn, toInt(flow.bntFundingLimit, bntDecimals))

    pendingWithdrawals.setLockDuration(0)

    network.registerPoolCollection(poolCollection)
    network.createPools([tkn], poolCollection)
    bntkn = network.collectionByPool(tkn).poolToken(tkn)

    poolCollection.setNetworkFeePPM(toPPM(flow.networkFee))
    poolCollection.setTradingFeePPM(tkn, toPPM(flow.tradingFee))

    tkn.issue(DEPLOYER, tknAmount)
    bntGovernance.mint(DEPLOYER, bntAmount)
    tkn.connect(DEPLOYER).transfer(epVault, epVaultBalance)

    for user in flow.users:
        assert user.id != DEPLOYER
        for contract in [network, standardRewards]:
            for token in [vbnt, tkn, bnt, bntkn, bnbnt]:
                token.connect(user.id).approve(contract, MAX_UINT256)
        tkn.connect(DEPLOYER).transfer(user.id, toInt(user.tknBalance, tknDecimals))
        bnt.connect(DEPLOYER).transfer(user.id, toInt(user.bntBalance, bntDecimals))

    tknProgramId = standardRewards.createProgram(tkn, bntknAmount, block.timestamp, block.timestamp + flow.tknRewardsDuration)
    bntProgramId = standardRewards.createProgram(bnt, bnbntAmount, block.timestamp, block.timestamp + flow.bntRewardsDuration)

    for token in [vbnt, tkn, bnt, bntkn, bnbnt]:
        assert token.balanceOf(DEPLOYER) == 0

    def toWei(userId: str, amount: str, decimals: int, token: IERC20):
        if (amount.endswith('%')):
            balance = token.balanceOf(userId)
            return balance * toPPM(amount) / PPM_RESOLUTION
        return toInt(amount, decimals)

    def depositTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn)
        network.connect(userId).deposit(tkn, wei)

    def depositBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt)
        network.connect(userId).deposit(bnt, wei)

    def withdrawTKN(userId: str, amount: str):
        wei = toWei(userId, amount, bntknDecimals, bntkn)
        id = network.connect(userId).initWithdrawal(bntkn, wei)
        network.connect(userId).withdraw(id)

    def withdrawBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bnbntDecimals, bnbnt)
        id = network.connect(userId).initWithdrawal(bnbnt, wei)
        network.connect(userId).withdraw(id)

    def tradeTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn)
        network.connect(userId).tradeBySourceAmount(tkn, bnt, wei, 1, MAX_UINT256, userId)

    def tradeBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt)
        network.connect(userId).tradeBySourceAmount(bnt, tkn, wei, 1, MAX_UINT256, userId)

    def burnPoolTokenTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn)
        bntkn.connect(userId).burn(wei)

    def burnPoolTokenBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt)
        bnbnt.connect(userId).burn(wei)

    def joinTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn)
        standardRewards.connect(userId).join(tknProgramId, wei)

    def joinBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt)
        standardRewards.connect(userId).join(bntProgramId, wei)

    def leaveTKN(userId: str, amount: str):
        wei = toWei(userId, amount, tknDecimals, tkn)
        standardRewards.connect(userId).leave(tknProgramId, wei)

    def leaveBNT(userId: str, amount: str):
        wei = toWei(userId, amount, bntDecimals, bnt)
        standardRewards.connect(userId).leave(bntProgramId, wei)

    def claimRewardsTKN(userId: str):
        standardRewards.connect(userId).claimRewards([tknProgramId])

    def claimRewardsBNT(userId: str):
        standardRewards.connect(userId).claimRewards([bntProgramId])

    def setFundingLimit(amount: str):
        networkSettings.setFundingLimit(tkn, toInt(amount, bntDecimals))

    def enableTrading(bntVirtualBalance: int, tknVirtualBalance: int):
        poolCollection.enableTrading(tkn, uint256(bntVirtualBalance), uint256(tknVirtualBalance))

    def verifyState(expected):
        for user in flow.users:
            assertAlmostEqual(expected.tknBalances[user.id], toDec(tkn.balanceOf(user.id), tknDecimals), 0, '0.000000000001')
            assertAlmostEqual(expected.bntBalances[user.id], toDec(bnt.balanceOf(user.id), bntDecimals), 0, '0.000000000001')
            assertAlmostEqual(expected.bntknBalances[user.id], toDec(bntkn.balanceOf(user.id), bntknDecimals), 0, '0.000000000001')
            assertAlmostEqual(expected.bnbntBalances[user.id], toDec(bnbnt.balanceOf(user.id), bnbntDecimals), 0, '0.000000000001')

        assertAlmostEqual(expected.tknBalances['masterVault'], toDec(tkn.balanceOf(masterVault), tknDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.tknBalances['epVault'], toDec(tkn.balanceOf(epVault), tknDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.bntBalances['masterVault'], toDec(bnt.balanceOf(masterVault), bntDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.bntknBalances['erVault'], toDec(bntkn.balanceOf(erVault), bntknDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.bnbntBalances['bntPool'], toDec(bnbnt.balanceOf(bntPool), bnbntDecimals), 0, '0.000000000001')

        poolData = poolCollection.poolData(tkn)
        assertAlmostEqual(expected.bntCurrentPoolFunding, toDec(bntPool.currentPoolFunding(tkn), bntDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.tknStakedBalance, toDec(poolData.liquidity.stakedBalance, tknDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.bntStakedBalance, toDec(bntPool.stakedBalance(), bntDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.tknTradingLiquidity, toDec(poolData.liquidity.baseTokenTradingLiquidity, tknDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.bntTradingLiquidity, toDec(poolData.liquidity.bntTradingLiquidity, bntDecimals), 0, '0.000000000001')
        assertAlmostEqual(expected.averageRate, toDec(poolData.averageRates.rate.n, 0) / toDec(poolData.averageRates.rate.d, 0), 0, '0.00000000001')
        assertAlmostEqual(expected.averageInvRate, toDec(poolData.averageRates.invRate.n, 0) / toDec(poolData.averageRates.invRate.d, 0), 0, '0.00000000001')

    for n in range(len(flow.operations)):
        operation = flow.operations[n]

        print('{} out of {}: {}({})'.format(n + 1, len(flow.operations), operation.type, operation.amount))

        if (operation.elapsed > 0):
            block.number += 1
            block.timestamp += operation.elapsed

        if operation.type == 'depositTKN':
            depositTKN(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'depositBNT':
            depositBNT(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'withdrawTKN':
            withdrawTKN(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'withdrawBNT':
            withdrawBNT(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'tradeTKN':
            tradeTKN(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'tradeBNT':
            tradeBNT(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'burnPoolTokenTKN':
            burnPoolTokenTKN(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'burnPoolTokenBNT':
            burnPoolTokenBNT(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'joinTKN':
            joinTKN(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'joinBNT':
            joinBNT(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'leaveTKN':
            leaveTKN(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'leaveBNT':
            leaveBNT(operation.userId, operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'claimRewardsTKN':
            claimRewardsTKN(operation.userId)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'claimRewardsBNT':
            claimRewardsBNT(operation.userId)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'setFundingLimit':
            setFundingLimit(operation.amount)
            verifyState(State(operation.expected))
            continue

        if operation.type == 'enableTrading':
            enableTrading(operation.amount['bntVirtualBalance'], operation.amount['baseTokenVirtualBalance'])
            verifyState(State(operation.expected))
            continue

        raise Exception('unsupported operation `{}` encountered'.format(operation.type))

execute('BancorNetworkSimpleFinancialScenario1')
execute('BancorNetworkSimpleFinancialScenario2')
execute('BancorNetworkSimpleFinancialScenario3')
execute('BancorNetworkSimpleFinancialScenario4')
execute('BancorNetworkSimpleFinancialScenario5')
execute('BancorNetworkSimpleFinancialScenario6')
execute('BancorNetworkComplexFinancialScenario1')
execute('BancorNetworkComplexFinancialScenario2')
execute('BancorNetworkRewardsFinancialScenario1')
execute('BancorNetworkRewardsFinancialScenario2')
