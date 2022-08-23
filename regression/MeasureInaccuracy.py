from bancor_research.bancor_emulator import config
config.enable_full_precision_mode(False)

from bancor_research.bancor_simulator.v3.spec.network import BancorDapp as sBancorDapp
from bancor_research.bancor_emulator.v3.spec.network  import BancorDapp as eBancorDapp

from os.path import join, dirname
from json import loads

def execute(fileName):
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

    print('\n{}:'.format(fileName))

    for n in range(len(fileData['operations'])):
        operation = fileData['operations'][n]
        timestamp += operation['elapsed']

        for bancorDapp in bancorDapps:
            if operation['type'] == 'deposit':
                bancorDapp.deposit(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'withdraw':
                id_number = bancorDapp.begin_cooldown_by_ptkn(operation['amount'], operation['poolId'], operation['userId'], timestamp)
                bancorDapp.withdraw(operation['userId'], id_number, timestamp)
            elif operation['type'] == 'trade':
                bancorDapp.trade(operation['amount'], operation['poolId'], operation['targetPoolId'], operation['userId'], timestamp)
            elif operation['type'] == 'burnPoolToken':
                bancorDapp.burn_pool_tokens(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'joinProgram':
                bancorDapp.join_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[bancorDapp][operation['poolId']], timestamp)
            elif operation['type'] == 'leaveProgram':
                bancorDapp.leave_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[bancorDapp][operation['poolId']], timestamp)
            elif operation['type'] == 'claimRewards':
                bancorDapp.claim_standard_rewards(operation['userId'], [programIds[bancorDapp][operation['poolId']]], timestamp)
            elif operation['type'] == 'setFundingLimit':
                bancorDapp.set_bnt_funding_limit(operation['poolId'], operation['amount'], timestamp)
            elif operation['type'] == 'enableTrading':
                bancorDapp.enable_trading(operation['poolId'], operation['bntVirtualBalance'], operation['baseTokenVirtualBalance'], timestamp)
            else:
                raise Exception('unsupported operation `{}` encountered'.format(operation['type']))

    frames = [bancorDapp.describe() for bancorDapp in bancorDapps]
    for pair in [[item.astype('float128') for item in pair] for pair in zip(frames, frames[1:])]:
        print((abs(pair[0] - pair[1]) / pair[1]).fillna(0).applymap(lambda x: '{:.18f}%'.format(x * 100)))

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
