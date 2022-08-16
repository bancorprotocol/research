from bancor_research.bancor_emulator import config
config.enable_full_precision_mode(True)

from bancor_research.bancor_simulator.v3.spec.network import BancorDapp as sBancorDapp
from bancor_research.bancor_emulator.v3.spec.network  import BancorDapp as eBancorDapp

from os.path import join, dirname
from json import loads

def execute(fileName):
    print(fileName)

    fileDesc = open(join(dirname(__file__), 'data', fileName + '.json'), 'r')
    fileData = loads(fileDesc.read())
    fileDesc.close()

    timestamp = 0

    bancorDapps = [
        BancorDapp(
            timestamp = timestamp,
            log_state = False,
            cooldown_time = 0,
            bnt_min_liquidity = fileData['bnt_min_liquidity'],
            withdrawal_fee = fileData['withdrawal_fee'],
            network_fee = fileData['network_fee'],
            whitelisted_tokens = fileData['pools'],
        )
        for BancorDapp in [sBancorDapp, eBancorDapp]
    ]

    for user, balances in fileData['users'].items():
        for token, balance in balances.items():
            for bancorDapp in bancorDapps:
                bancorDapp.set_user_balance(user, token, balance, timestamp)

    programIds = {bancorDapp : {} for bancorDapp in bancorDapps}
    for poolId, programsParams in fileData['programs'].items():
        for bancorDapp in bancorDapps:
            programIds[bancorDapp][poolId] = bancorDapp.create_standard_rewards_program(
                poolId,
                programsParams['rewards'],
                timestamp,
                timestamp + programsParams['duration'],
                timestamp
            )

    def Print(title, *args):
        print('operation {} out of {}: {}'.format(n + 1, len(fileData['operations']), title.format(*args)))

    for n in range(len(fileData['operations'])):
        operation = fileData['operations'][n]
        timestamp += operation['elapsed']

        for bancorDapp in bancorDapps:
            if operation['type'] == 'deposit':
                Print('deposit {} {} reserve tokens', operation['amount'], operation['poolId'])
                bancorDapp.deposit(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'withdraw':
                Print('withdraw {} {} pool tokens', operation['amount'], operation['poolId'])
                id_number = bancorDapp.begin_cooldown_by_ptkn(operation['amount'], operation['poolId'], operation['userId'], timestamp)
                bancorDapp.withdraw(operation['userId'], id_number, timestamp)
            elif operation['type'] == 'trade':
                Print('trade {} {} reserve tokens for {} reserve tokens', operation['amount'], operation['poolId'], operation['targetPoolId'])
                bancorDapp.trade(operation['amount'], operation['poolId'], operation['targetPoolId'], operation['userId'], timestamp)
            elif operation['type'] == 'burnPoolToken':
                Print('burn {} {} pool tokens', operation['amount'], operation['poolId'])
                bancorDapp.burn_pool_tokens(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'joinProgram':
                Print('join {} {} pool tokens', operation['amount'], operation['poolId'])
                bancorDapp.join_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[bancorDapp][operation['poolId']], timestamp)
            elif operation['type'] == 'leaveProgram':
                Print('leave {} {} pool tokens', operation['amount'], operation['poolId'])
                bancorDapp.leave_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[bancorDapp][operation['poolId']], timestamp)
            elif operation['type'] == 'claimRewards':
                Print('claim {} rewards', operation['poolId'])
                bancorDapp.claim_standard_rewards(operation['userId'], [programIds[bancorDapp][operation['poolId']]], timestamp)
            elif operation['type'] == 'setFundingLimit':
                Print('set {} pool funding limit to {} bnt', operation['poolId'], operation['amount'])
                bancorDapp.set_bnt_funding_limit(operation['poolId'], operation['amount'], timestamp)
            elif operation['type'] == 'enableTrading':
                Print('enable trading with 1 {} = {}/{} bnt', operation['poolId'], operation['bntVirtualBalance'], operation['baseTokenVirtualBalance'])
                bancorDapp.enable_trading(operation['poolId'], operation['bntVirtualBalance'], operation['baseTokenVirtualBalance'], timestamp)
            else:
                raise Exception('unsupported operation `{}` encountered'.format(operation['type']))

    print(bancorDapps[0].describe(decimals=6).compare(bancorDapps[1].describe(decimals=6)))

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
