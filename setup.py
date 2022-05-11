from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {}
extras_require['complete'] = sorted(set(sum(extras_require.values(), [])))

setup(
    name='bancor3_simulator',
    version='1.0.0',
    author='Bancor Network',
    author_email='mike@bancor.network',
    description='Bancor3 Simulator is an open-source python package developed by the Bancor Research Team. It’s meant to assist designing, testing, and validating Bancor v3 behavior.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gcode-ai/bancor3_simulator',
    install_requires=open('requirements.txt').readlines(),
    extras_require=extras_require,
    tests_require=open('test-requirements.txt').readlines(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
          'bancor3_simulator = bancor3_simulator.__main__:cli'
        ]
    },
    data_files=[
        ('bancor3_simulator/tests/data', [
                                'bancor3_simulator/tests/data/scenarios_2.json'
                              ])
                ],
)
