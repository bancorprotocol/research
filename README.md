<p align="center">
<img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
</p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

# Bancor Protocol Contracts v3.0 (Dawn Release)

[![PyPI](https://vsrm.dev.azure.com/gcode-ai/_apis/public/Release/badge/52109c77-be71-4849-9d35-4fc861db41a6/1/1)](https://vsrm.dev.azure.com/gcode-ai/_apis/public/Release/badge/52109c77-be71-4849-9d35-4fc861db41a6/1/1)
[![bancorml-0.1.0-py3-none-any.whl package in bancorml@Release feed in Azure Artifacts](https://feeds.dev.azure.com/gcode-ai/52109c77-be71-4849-9d35-4fc861db41a6/_apis/public/Packaging/Feeds/bancorml@Release/Packages/0926c7d3-1ac4-4316-a132-cf9867850696/Badge)](https://dev.azure.com/gcode-ai/BancorML/_artifacts/feed/bancorml@Release/UPack/bancorml-0.1.0-py3-none-any.whl/0.0.16)
[![PyPI version](https://badge.fury.io/py/bancorml.svg)](https://badge.fury.io/py/bancorml)
[![Documentation Status](https://readthedocs.com/projects/gcodeai-bancorml/badge/?version=latest&token=55e06511a714e5d89e1eea25f71fe67e6a96aa5d3b813aa09547303f31b088e4)](https://gcodeai-bancorml.readthedocs-hosted.com/en/latest/?badge=latest)

## Overview

Bancor is a decentralized trading and yield protocol. Its network of on-chain automated market makers (AMMs) supports instant token-to-token trades, as well as single-sided liquidity provision, auto-compounding staking rewards and 100% [impermanent loss](https://www.youtube.com/watch?v=_m6Mowq3Ptk) protection for any listed asset.

The Dawn release includes the following features:

- Token to token trades
- Instant IL protection
- Single-sided Liquidity Provision
- Omnipool
- Infinity Pools
- Auto-compounding Rewards
- Dual Rewards
- Third Party IL Protection
- Composable PoolState Tokens
- Tokenomics Redesign
- Flash Loans

**Bancor3 Simulation** is a library built for designing, testing, validating, and optimizing Bancor v3 tokenomics and performance.


### Project setup

If you don't already have one, create a virtualenv
using [these instructions](https://docs.python.org/3/library/venv.html)

# Install

**Bancor3 Simulation** is available for Python 3.6+

To install using [pypi](https://pypi.org/project/bancor-simulation/), run this command:

````{tab} PyPI
$ pip install bancor3-simulation
````

# Bancor v3 Simulation Documentation

In addition to the codebase, this repository holds the Jupyter Book source for Bancor v3 Simulation: A hands-on demo of
features described
in [BIP15: Proposing Bancor 3](https://docs.google.com/document/d/11UeMYaI_1CWdf_Nu6veUO-vNB5uX-FcVRqTSU-ziDRk/).

## To make a change to the jupyter book and update:

1. Get your copy of this repository:

   ```
   git clone https://github.com/bancorprotocol/simulator-v3
   ```

## Build and preview the jupyter-book text locally

To build locally, `pip install -r requirements.txt` and then `jupyter-book build .`

**Follow the build instructions on the Jupyter Book guide**. The guide has information for how to use the Jupyter Book
CLI to build this book. You can find
the [Jupyter Book build instructions here](https://jupyterbook.org/start/build.html).

Build and preview the text locally

To build locally, pip install -r requirements.txt and then jupyter-book build .

Follow the build instructions on the Jupyter Book guide. The guide has information for how to use the Jupyter Book CLI to build this book. You can find the Jupyter Book build instructions here.