from common import read, write, Decimal

from bancor_research.bancor_emulator import config
config.enable_full_precision_mode(True)

from bancor_research.bancor_emulator.solidity import uint, uint32, uint256, block

from bancor_research.bancor_emulator.BancorNetwork import BancorNetwork
from bancor_research.bancor_emulator.BancorNetworkInfo import BancorNetworkInfo
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

DEFAULT_TOKEN_DECIMALS = 18
DEFAULT_RATIO_DECIMALS = 12

def toPPM(percent: str):
    return uint32(Decimal(str(PPM_RESOLUTION)) * Decimal(percent[:-1]) / 100)

def toInt(token: IERC20, amount: str):
    return uint256(Decimal(amount) * 10 ** token.decimals())

def toDec(token: IERC20, amount: uint):
    return Decimal(str(amount)) / 10 ** token.decimals()

def toValue(token: IERC20, amount: uint):
    return toString(toDec(token, amount), token.decimals())

def toRatio(n: uint, d: uint, decimals: int = DEFAULT_RATIO_DECIMALS):
    return 'NaN' if n == d == 0 else toString(Decimal(str(n)) / Decimal(str(d)), decimals)

def toString(amount: Decimal, decimals: int):
    return '{{:.{}f}}'.format(decimals).format(amount).rstrip('0').rstrip('.')

def userAmount(token: IERC20, userId: str, amount: str):
    if (amount.endswith('%')):
        balance = token.balanceOf(userId)
        return balance * toPPM(amount) / PPM_RESOLUTION
    return toInt(token, amount)

def execute(fileName):
    print(fileName)

    flow = read(fileName)

    bnt   = ReserveToken('bnt'  , 'bnt'  , DEFAULT_TOKEN_DECIMALS)
    vbnt  = ReserveToken('vbnt' , 'vbnt' , DEFAULT_TOKEN_DECIMALS)
    bnbnt = PoolToken   ('bnbnt', 'bnbnt', DEFAULT_TOKEN_DECIMALS, bnt)

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
    networkInfo        = BancorNetworkInfo(network, bntGovernance, vbntGovernance, networkSettings, masterVault, epVault, erVault, bntPool, pendingWithdrawals, poolMigrator)

    networkSettings.initialize()
    network.initialize(bntPool, pendingWithdrawals, poolMigrator)
    bntPool.initialize()
    pendingWithdrawals.initialize()
    poolTokenFactory.initialize()
    standardRewards.initialize()
    networkInfo.initialize()

    networkSettings.setWithdrawalFeePPM(toPPM(flow['withdrawal_fee']))
    networkSettings.setMinLiquidityForTrading(toInt(bnt, flow['bnt_min_liquidity']))

    pendingWithdrawals.setLockDuration(0)

    poolCollection.setNetworkFeePPM(toPPM(flow['network_fee']))

    network.registerPoolCollection(poolCollection)

    reserveTokens = {bnt.symbol(): bnt}
    poolTokens = {bnt.symbol(): bnbnt}
    for tkn_name, pool_params in flow['pools'].items():
        token = ReserveToken(tkn_name, tkn_name, pool_params['decimals'])
        token.issue(epVault, toInt(token, pool_params['ep_vault_balance']))
        networkSettings.addTokenToWhitelist(token)
        networkSettings.setFundingLimit(token, toInt(bnt, pool_params['bnt_funding_limit']))
        network.createPools([token], poolCollection)
        poolCollection.setTradingFeePPM(token, toPPM(pool_params['trading_fee']))
        reserveTokens[tkn_name] = token
        poolTokens[tkn_name] = network.collectionByPool(token).poolToken(token)

    for userId, balances in flow['users'].items():
        for tokenId, balance in balances.items():
            token = reserveTokens[tokenId]
            amount = toInt(token, balance)
            (bntGovernance.mint if token is bnt else token.issue)(userId, amount)

    programIds = {}
    for poolId, programsParams in flow['programs'].items():
        programIds[poolId] = standardRewards.createProgram(
            reserveTokens[poolId],
            toInt(bnt, programsParams['rewards']),
            block.timestamp,
            block.timestamp + programsParams['duration'],
        )

    def deposit(poolId: str, userId: str, amount: str):
        token = reserveTokens[poolId]
        amount = userAmount(token, userId, amount)
        token.connect(userId).approve(network, amount)
        network.connect(userId).deposit(token, amount)

    def withdraw(poolId: str, userId: str, amount: str):
        token = poolTokens[poolId]
        amount = userAmount(token, userId, amount)
        token.connect(userId).approve(network, amount)
        if token is bnbnt: vbnt.connect(userId).approve(network, amount)
        network.connect(userId).withdraw(network.connect(userId).initWithdrawal(token, amount))

    def trade(sourcePoolId: str, targetPoolId: str, userId: str, amount: str):
        token = reserveTokens[sourcePoolId]
        amount = userAmount(token, userId, amount)
        token.connect(userId).approve(network, amount)
        network.connect(userId).tradeBySourceAmount(token, reserveTokens[targetPoolId], amount, 1, uint256.max, userId)

    def burnPoolToken(poolId: str, userId: str, amount: str):
        token = poolTokens[poolId]
        amount = userAmount(token, userId, amount)
        token.connect(userId).burn(amount)

    def joinProgram(poolId: str, userId: str, amount: str):
        token = poolTokens[poolId]
        amount = userAmount(token, userId, amount)
        token.connect(userId).approve(standardRewards, amount)
        standardRewards.connect(userId).join(programIds[poolId], amount)

    def leaveProgram(poolId: str, userId: str, amount: str):
        token = poolTokens[poolId]
        amount = userAmount(token, userId, amount)
        standardRewards.connect(userId).leave(programIds[poolId], amount)

    def claimRewards(poolId: str, userId: str):
        standardRewards.connect(userId).claimRewards([programIds[poolId]])

    def setFundingLimit(poolId: str, amount: str):
        token = reserveTokens[poolId]
        amount = userAmount(bnt, None, amount)
        networkSettings.setFundingLimit(token, amount)

    def enableTrading(poolId: str, bntVirtualBalance: int, tknVirtualBalance: int):
        token = reserveTokens[poolId]
        poolCollection.enableTrading(token, uint256(bntVirtualBalance), uint256(tknVirtualBalance))

    def getState():
        state = {}

        reserveTokenValues = list(reserveTokens.values())
        poolTokenValues = list(poolTokens.values())

        # Iterate all tokens
        for token in reserveTokenValues + poolTokenValues + [vbnt]:
            state[token.symbol()] = {}
            for account in [user for user in token._balances.keys() if type(user) is str]:
                state[token.symbol()]['account_' + account] = toValue(token, token.balanceOf(account))

        # Iterate all reserve tokens except bnt
        for token in [reserveToken for reserveToken in reserveTokenValues if reserveToken is not bnt]:
            stakedBalance = networkInfo.stakedBalance(token)
            tradingLiquidity = networkInfo.tradingLiquidity(token)
            currentPoolFunding = bntPool.currentPoolFunding(token)

            spotRateN       = poolCollection._poolData[token].liquidity.bntTradingLiquidity
            spotRateD       = poolCollection._poolData[token].liquidity.baseTokenTradingLiquidity
            averageRateN    = poolCollection._poolData[token].averageRates.rate.n
            averageRateD    = poolCollection._poolData[token].averageRates.rate.d
            averageInvRateN = poolCollection._poolData[token].averageRates.invRate.n
            averageInvRateD = poolCollection._poolData[token].averageRates.invRate.d

            state[token.symbol()]['pool_tknStakedBalance'   ] = toValue(token, stakedBalance)
            state[token.symbol()]['pool_tknTradingLiquidity'] = toValue(token, tradingLiquidity.baseTokenTradingLiquidity)
            state[token.symbol()]['pool_bntTradingLiquidity'] = toValue(bnt  , tradingLiquidity.bntTradingLiquidity)
            state[token.symbol()]['pool_bntCurrentFunding'  ] = toValue(bnt  , currentPoolFunding)
            state[token.symbol()]['pool_spotRate'           ] = toRatio(spotRateN      , spotRateD      )
            state[token.symbol()]['pool_averageRate'        ] = toRatio(averageRateN   , averageRateD   )
            state[token.symbol()]['pool_averageInverseRate' ] = toRatio(averageInvRateN, averageInvRateD)

        # Iterate all reserve tokens
        for token in reserveTokenValues:
            state[token.symbol()]['contract_masterVault'] = toValue(token, token.balanceOf(masterVault))
            state[token.symbol()]['contract_epVault'    ] = toValue(token, token.balanceOf(epVault    ))

        # Iterate all pool tokens
        for token in poolTokenValues:
            state[token.symbol()]['contract_erVault'] = toValue(token, token.balanceOf(erVault))
            state[token.symbol()]['contract_bntPool'] = toValue(token, token.balanceOf(bntPool))

        return state

    for n in range(len(flow['operations'])):
        operation = flow['operations'][n]

        print('{} out of {}: {}({})'.format(n + 1, len(flow['operations']), operation['type'], operation['amount']))

        if (operation['elapsed'] > 0):
            block.number += 1
            block.timestamp += operation['elapsed']

        if operation['type'] == 'deposit':
            deposit(operation['poolId'], operation['userId'], operation['amount'])
        elif operation['type'] == 'withdraw':
            withdraw(operation['poolId'], operation['userId'], operation['amount'])
        elif operation['type'] == 'trade':
            trade(operation['sourcePoolId'], operation['targetPoolId'], operation['userId'], operation['amount'])
        elif operation['type'] == 'burnPoolToken':
            burnPoolToken(operation['poolId'], operation['userId'], operation['amount'])
        elif operation['type'] == 'joinProgram':
            joinProgram(operation['poolId'], operation['userId'], operation['amount'])
        elif operation['type'] == 'leaveProgram':
            leaveProgram(operation['poolId'], operation['userId'], operation['amount'])
        elif operation['type'] == 'claimRewards':
            claimRewards(operation['poolId'], operation['userId'])
        elif operation['type'] == 'setFundingLimit':
            setFundingLimit(operation['poolId'], operation['amount'])
        elif operation['type'] == 'enableTrading':
            enableTrading(operation['poolId'], operation['amount']['bntVirtualBalance'], operation['amount']['baseTokenVirtualBalance'])
        else:
            raise Exception('unsupported operation `{}` encountered'.format(operation['type']))

        operation['expected'] = getState()

    write(fileName, flow)

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
