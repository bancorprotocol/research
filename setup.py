import re

from setuptools import find_packages, setup

with open("bancor_research/__init__.py") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

with open("README.md", "r", encoding="utf8") as fh:
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
    }
)
