<p align="center">
<img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
</p>

[![PyPI](https://vsrm.dev.azure.com/gcode-ai/_apis/public/Release/badge/52109c77-be71-4849-9d35-4fc861db41a6/1/1)](https://vsrm.dev.azure.com/gcode-ai/_apis/public/Release/badge/52109c77-be71-4849-9d35-4fc861db41a6/1/1)
[![bancorml-0.1.0-py3-none-any.whl package in bancorml@Release feed in Azure Artifacts](https://feeds.dev.azure.com/gcode-ai/52109c77-be71-4849-9d35-4fc861db41a6/_apis/public/Packaging/Feeds/bancorml@Release/Packages/0926c7d3-1ac4-4316-a132-cf9867850696/Badge)](https://dev.azure.com/gcode-ai/BancorML/_artifacts/feed/bancorml@Release/UPack/bancorml-0.1.0-py3-none-any.whl/0.0.16)
[![PyPI version](https://badge.fury.io/py/bancorml.svg)](https://badge.fury.io/py/bancorml)
[![Documentation Status](https://readthedocs.com/projects/gcodeai-bancorml/badge/?version=latest&token=55e06511a714e5d89e1eea25f71fe67e6a96aa5d3b813aa09547303f31b088e4)](https://gcodeai-bancorml.readthedocs-hosted.com/en/latest/?badge=latest)

**Bancor3 Simulation** simulation library is built with common open-source Python packages for designing, testing, and
validating complex data science and multi-agent systems.

In Bancor3 simulations `v1.0.01` we demonstrate how **real-world transactions** can be routed through the Bancor3
simulations model. Moreover, we add **external price feeds** to showcase how various data sources can be combined for
a **most realistic simulation scenario**, while the **prototyping features** for new Bancor3 designs is **
demonstrated** throughout. Additionally, we've used real-world transaction data
to[verify if the model is producing accurate and credible results](https://tenderly.co).

In developing this code we try to
follow [SOLID principles](https://towardsdatascience.com/solid-coding-in-python-1281392a6a94):

- The **S**ingle-Responsibility Principle (SRP)
- The **O**pen-Closed Principle (OCP)
- The **L**iskov Substitution Principle (LSP)
- The **I**nterface Segregation Principle (ISP)
- The **D**ependency inversion Principle (DIP)

We also generally adhear to many of
the [cadCAD System Model Standards](https://github.com/cadCAD-org/cadCAD/tree/master/documentation), such as:

- State Variables to describe the mathematical "state" of the pool
- State Update Functions, changing the state variables in discrete events according to on-chain transactions and price
  updates
- Policy Functions, defining the rules of the system, in our case mapping transactions to the right method in the model
  to update the state
- Partial State Update Blocks, which are sets of state updates and policy functions

### Project setup

If you don't already have one, create a virtualenv
using [these instructions](https://docs.python.org/3/library/venv.html)

# Install

**Bancor3 Simulation** is available for Python 3.6+

To install using [pypi](https://pypi.org/project/bancor-simulation/), run this command:

````{tab} PyPI
$ pip install bancor3-simulation
````

# Start

# Bancor v3 Simulation Documentation

In addition to the codebase, this repository holds the Jupyter Book source for Bancor v3 Simulation: A hands-on demo of
features described
in [BIP15: Proposing Bancor 3](https://docs.google.com/document/d/11UeMYaI_1CWdf_Nu6veUO-vNB5uX-FcVRqTSU-ziDRk/).

## To make a change to the book and update:

1. Get your copy of this repository:

   ```
   git clone https://github.com/bancorprotocol/simulator-v3-public
   ```
2. Change the file you wish and commit it to the repository.
3. Push your change back to the `bancorprotocol/simulator-v3-public` repository (ideally via a pull request).
4. That's it a GitHub Action will build the book and deploy it
   to [simulations.bancor.network](https://try.bancor.network)

## How this repository is deployed to `simulations.bancor.network`

* The textbook at `simulations.bancor.network` is actually being served from this repository:

  https://github.com/bancorprotocol/simulator-v3

  **You should not ever directly edit the inferentialthinking.github.io repository**
* When you make a change to this repository and push it to the `bancorprotocol/simulator-v3` `main`
  branch, the book's HTML will automatically be pushed to https://github.com/bancorprotocol/simulator-v3
* This process is handled by [this GitHub Action](.github/workflows/deploy.yml)

## Build and preview the text locally

To build locally, `pip install -r requirements.txt` and then `jupyter-book build .`

**Follow the build instructions on the Jupyter Book guide**. The guide has information for how to use the Jupyter Book
CLI to build this book. You can find
the [Jupyter Book build instructions here](https://jupyterbook.org/start/build.html).
