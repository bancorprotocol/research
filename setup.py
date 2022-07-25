import re

from setuptools import find_packages, setup

with open("bancor_research/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {}
extras_require['complete'] = sorted(set(sum(extras_require.values(), [])))

setup(
    name='bancor_research',
    version=version,
    author='Bancor Network',
    author_email='mike@bancor.network',
    description='Bancor v3 python spec and simulation library. '
                'This is an open-source python package developed by the Bancor Research Team.'
                'It is meant to assist in the design, testing, and validating of Bancor v3 behavior.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/bancorprotocol/research',
    install_requires=open('requirements.txt').readlines(),
    extras_require=extras_require,
    tests_require=open('test-requirements.txt').readlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
          'bancor_simulator = bancor_research.bancor_simulator.__main__:cli'
        ]
    },
    data_files=[
        (
            'bancor_research', [
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkSimpleFinancialScenario1.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkSimpleFinancialScenario2.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkSimpleFinancialScenario3.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkSimpleFinancialScenario4.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkSimpleFinancialScenario5.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkSimpleFinancialScenario6.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkComplexFinancialScenario1.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkComplexFinancialScenario2.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkRewardsFinancialScenario1.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/BancorNetworkRewardsFinancialScenario2.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage1.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage2.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage3.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage4.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage5.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage6.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage7.json',
                # 'bancor_research/bancor_emulator/tests/project/tests/data/PoolCollectionWithdrawalCoverage8.json',
            ],
        )
    ],
)
