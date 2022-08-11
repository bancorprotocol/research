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
            cooldown_time = 0,
            bnt_min_liquidity = fileData['bnt_min_liquidity'],
            withdrawal_fee = fileData['withdrawal_fee'],
            network_fee = fileData['network_fee'],
            whitelisted_tokens = fileData['pools'],
        )
        for BancorDapp in [eBancorDapp]
    ]

    for user, balances in fileData['users'].items():
        for token, balance in balances.items():
            for bancorDapp in bancorDapps:
                bancorDapp.set_user_balance(user, token, balance, timestamp)

    programIds = {}
    for poolId, programsParams in fileData['programs'].items():
        programIds[poolId] = bancorDapp.create_standard_rewards_program(
            poolId,
            programsParams['rewards'],
            timestamp,
            timestamp + programsParams['duration'],
            timestamp
        )

    for n in range(len(fileData['operations'])):
        operation = fileData['operations'][n]

        print('{} out of {}: '.format(n + 1, len(fileData['operations'])), end = '')

        timestamp += operation['elapsed']

        for bancorDapp in bancorDapps:
            if operation['type'] == 'deposit':
                print('deposit {} {} reserve tokens'.format(operation['amount'], operation['poolId']))
                bancorDapp.deposit(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'withdraw':
                print('withdraw {} {} pool tokens'.format(operation['amount'], operation['poolId']))
                id_number = bancorDapp.begin_cooldown(operation['amount'], operation['poolId'], operation['userId'], timestamp)
                bancorDapp.withdraw(operation['userId'], id_number, timestamp)
            elif operation['type'] == 'trade':
                print('trade {} {} reserve tokens for {} reserve tokens'.format(operation['amount'], operation['poolId'], operation['targetPoolId']))
                bancorDapp.trade(operation['amount'], operation['poolId'], operation['targetPoolId'], operation['userId'], timestamp)
            elif operation['type'] == 'burnPoolToken':
                print('burn {} {} pool tokens'.format(operation['amount'], operation['poolId']))
                bancorDapp.burn_pool_tokens(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'joinProgram':
                print('join {} {} pool tokens'.format(operation['amount'], operation['poolId']))
                bancorDapp.join_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[operation['poolId']], timestamp)
            elif operation['type'] == 'leaveProgram':
                print('leave {} {} pool tokens'.format(operation['amount'], operation['poolId']))
                bancorDapp.leave_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[operation['poolId']], timestamp)
            elif operation['type'] == 'claimRewards':
                print('claim {} rewards'.format(operation['poolId']))
                bancorDapp.claim_standard_rewards(operation['userId'], [programIds[operation['poolId']]], timestamp)
            elif operation['type'] == 'setFundingLimit':
                print('set {} pool funding limit to {} bnt'.format(operation['poolId'], operation['amount']))
                bancorDapp.set_bnt_funding_limit(operation['poolId'], operation['amount'], timestamp)
            elif operation['type'] == 'enableTrading':
                print('enable trading with 1 {} = {}/{} bnt'.format(operation['poolId'], operation['bntVirtualBalance'], operation['baseTokenVirtualBalance']))
                bancorDapp.price_feeds.at[timestamp, operation['poolId']] = operation['bntVirtualBalance']
                bancorDapp.price_feeds.at[timestamp, 'bnt'] = operation['baseTokenVirtualBalance']
                bancorDapp.enable_trading(operation['poolId'], timestamp)
            else:
                raise Exception('unsupported operation `{}` encountered'.format(operation['type']))

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
