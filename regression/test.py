import sys

options = {
    '1': {'desc': 'full-precision enabled' , 'mode': True },
    '2': {'desc': 'full-precision disabled', 'mode': False},
}

option = sys.argv[1] if len(sys.argv) > 1 else None
while option not in options:
    option = input(''.join('{} - {}\n'.format(key, value['desc']) for key, value in options.items()) + 'enter your choice: ')

desc = options[option]['desc']
mode = options[option]['mode']

from bancor_research.bancor_emulator import config
config.enable_full_precision_mode(mode)

from bancor_research.bancor_simulator.v3.spec.network import BancorDapp as sBancorDapp
from bancor_research.bancor_emulator.v3.spec.network  import BancorDapp as eBancorDapp

from os.path import join, dirname
from json import loads

def execute(fileName, decimals):
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

    print('\n{} ({}):'.format(fileName, desc))

    def Info(string, *args):
        return 'operation {} out of {}: {}'.format(n + 1, len(fileData['operations']), string.format(*args))

    for n in range(len(fileData['operations'])):
        operation = fileData['operations'][n]
        timestamp += operation['elapsed']

        for bancorDapp in bancorDapps:
            if operation['type'] == 'deposit':
                info = Info('deposit {} {} reserve tokens', operation['amount'], operation['poolId'])
                bancorDapp.deposit(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'withdraw':
                info = Info('withdraw {} {} pool tokens', operation['amount'], operation['poolId'])
                id_number = bancorDapp.begin_cooldown_by_ptkn(operation['amount'], operation['poolId'], operation['userId'], timestamp)
                bancorDapp.withdraw(operation['userId'], id_number, timestamp)
            elif operation['type'] == 'trade':
                info = Info('trade {} {} reserve tokens for {} reserve tokens', operation['amount'], operation['poolId'], operation['targetPoolId'])
                bancorDapp.trade(operation['amount'], operation['poolId'], operation['targetPoolId'], operation['userId'], timestamp)
            elif operation['type'] == 'burnPoolToken':
                info = Info('burn {} {} pool tokens', operation['amount'], operation['poolId'])
                bancorDapp.burn_pool_tokens(operation['poolId'], operation['amount'], operation['userId'], timestamp)
            elif operation['type'] == 'joinProgram':
                info = Info('join {} {} pool tokens', operation['amount'], operation['poolId'])
                bancorDapp.join_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[bancorDapp][operation['poolId']], timestamp)
            elif operation['type'] == 'leaveProgram':
                info = Info('leave {} {} pool tokens', operation['amount'], operation['poolId'])
                bancorDapp.leave_standard_rewards_program(operation['poolId'], operation['amount'], operation['userId'], programIds[bancorDapp][operation['poolId']], timestamp)
            elif operation['type'] == 'claimRewards':
                info = Info('claim {} rewards', operation['poolId'])
                bancorDapp.claim_standard_rewards(operation['userId'], [programIds[bancorDapp][operation['poolId']]], timestamp)
            elif operation['type'] == 'setFundingLimit':
                info = Info('set {} pool funding limit to {} bnt', operation['poolId'], operation['amount'])
                bancorDapp.set_bnt_funding_limit(operation['poolId'], operation['amount'], timestamp)
            elif operation['type'] == 'enableTrading':
                info = Info('enable trading with 1 {} = {}/{} bnt', operation['poolId'], operation['bntVirtualBalance'], operation['baseTokenVirtualBalance'])
                bancorDapp.enable_trading(operation['poolId'], operation['bntVirtualBalance'], operation['baseTokenVirtualBalance'], timestamp)
            else:
                raise Exception('unsupported operation `{}` encountered'.format(operation['type']))

        frames = [bancorDapp.describe(decimals) for bancorDapp in bancorDapps]
        for diff in [pair[0].compare(pair[1]) for pair in zip(frames, frames[1:])]:
            assert diff.empty, '{}\n{}'.format(info, diff)

    frames = [bancorDapp.describe() for bancorDapp in bancorDapps]
    for pair in [[item.astype('float128') for item in pair] for pair in zip(frames, frames[1:])]:
        print((abs(pair[0] - pair[1]) / pair[1]).fillna(0).applymap(lambda x: '{:.18f}%'.format(x * 100)))

execute('BancorNetworkSimpleFinancialScenario1' , 147 if mode else 147)
execute('BancorNetworkSimpleFinancialScenario2' , 147 if mode else  17)
execute('BancorNetworkSimpleFinancialScenario3' , 147 if mode else  17)
execute('BancorNetworkSimpleFinancialScenario4' , 147 if mode else  16)
execute('BancorNetworkSimpleFinancialScenario5' , 150 if mode else 150)
execute('BancorNetworkSimpleFinancialScenario6' , 150 if mode else 150)
execute('BancorNetworkComplexFinancialScenario1', 142 if mode else  12)
execute('BancorNetworkComplexFinancialScenario2', 143 if mode else  12)
execute('BancorNetworkRewardsFinancialScenario1', 143 if mode else  10)
execute('BancorNetworkRewardsFinancialScenario2', 143 if mode else  10)
