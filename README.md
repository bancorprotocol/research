<p align="center">
<img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
</p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

# Bancor Simulator

[![PyPI](https://vsrm.dev.azure.com/gcode-ai/_apis/public/Release/badge/52109c77-be71-4849-9d35-4fc861db41a6/1/1)](https://vsrm.dev.azure.com/gcode-ai/_apis/public/Release/badge/52109c77-be71-4849-9d35-4fc861db41a6/1/1)
[![bancorml-0.1.0-py3-none-any.whl package in bancorml@Release feed in Azure Artifacts](https://feeds.dev.azure.com/gcode-ai/52109c77-be71-4849-9d35-4fc861db41a6/_apis/public/Packaging/Feeds/bancorml@Release/Packages/0926c7d3-1ac4-4316-a132-cf9867850696/Badge)](https://dev.azure.com/gcode-ai/BancorML/_artifacts/feed/bancorml@Release/UPack/bancorml-0.1.0-py3-none-any.whl/0.0.16)
[![PyPI version](https://badge.fury.io/py/bancorml.svg)](https://badge.fury.io/py/bancorml)
[![Documentation Status](https://readthedocs.com/projects/gcodeai-bancorml/badge/?version=latest&token=55e06511a714e5d89e1eea25f71fe67e6a96aa5d3b813aa09547303f31b088e4)](https://gcodeai-bancorml.readthedocs-hosted.com/en/latest/?badge=latest)


* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

**Bancor Simulator** is an open-source python package developed by the **Bancor Research Team**. It aims to assist the design, testing, and validation of Bancor v3 tokenomics.

See [official documentation](https://simulator.bancor.network/chapters/bancor-simulator.html) for complete details.

**Warning**: The docs are a work in progress with potentially broken links, unfinished sections, and a non-exhuastive overview of commands and example usage. Moreover, the entirety of the codebase and documentation is subject to change without warning.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

## Introduction

All state transition functions and accompanying data structures described in the product specification [BIP15: Proposing Bancor 3](https://docs.google.com/document/d/11UeMYaI_1CWdf_Nu6veUO-vNB5uX-FcVRqTSU-ziDRk/edit?usp=sharing) are the core system level operations of this library. 

## Organization

This is the project directory structure:

```
bancor_analytics/            <------- Tableau Dashboard Project
bancor_emulator/             <------- Solidity Emulation Project
bancor_simulator/            <------- ** Spec & Simulation Project **
├── v3/                      <------- Current Version
│   └── simulation/          <------- Agent-based simulation module
│   │     └── agents.py      <------- Mesa Agent-based implementations of the Bancor protocol.
│   │     └── batch_run.py   <------- Script used to perform a parameter sweep.
│   │     └── model.py       <------- Main Bancor Simulation module interface.
│   │     └── random_walk.py <------- Generalized behavior for random walking
│   │     └── run.py         <------- Runs the simulation server with browser-based UI
│   │     └── server.py      <------- Configures the browser-based interface.
│   │     └── utils.py       <------- Misc utility functions
│   │ 
│   └── spec/                <------- State transition functions and data structures described in BIP15.
│         └── actions.py     <------- Deposit, trade, & withdrawal algorithm logic.
│         └── emulation.py   <------- Verifies solidity result parity.
│         └── network.py     <------- Main BancorDapp application interface.
│         └── rewards.py     <------- Autocompounding and standard rewards logic.
│         └── state.py       <------- State variables, constants, data structures, and CRUD interfaces.
│         └── utils.py       <------- Misc utility functions
│ 
└── main.py                  <------- Application

** These docs apply.
```

## Notation

Code snippets appearing in `this style` are to be interpreted as Python 3 code.

## Formatting & Style

Code is formatted according to [PEP8](https://peps.python.org/pep-0008/), which is the official Python style guide. In order to overcome the burden on the developers to fix formatting, we use [Black](https://black.readthedocs.io/en/stable/) which reports on format errors and automatically fixes them.

## Project setup

If you don't already have one, create a virtualenv
using [these instructions](https://docs.python.org/3/library/venv.html)

## Install

**Bancor3 Simulation** is available for Python 3.6+

To install using [pypi](https://pypi.org/project/bancor-simulation/), run this command:

````{tab} PyPI
$ pip install bancor-simulator
````

## Documentation

In addition to the codebase, this repository holds the Jupyter Book source for Bancor v3 Simulation: A hands-on demo of
features described
in [BIP15: Proposing Bancor 3](https://docs.google.com/document/d/11UeMYaI_1CWdf_Nu6veUO-vNB5uX-FcVRqTSU-ziDRk/).

### To make a change to the jupyter book and update:

1. Get your copy of this repository:

   ```
   git clone https://github.com/bancorprotocol/research
   ```

### Build and preview the jupyter-book text locally

To build locally, `pip install -r requirements.txt` and then `jupyter-book build .`

**Follow the build instructions on the Jupyter Book guide**. The guide has information for how to use the Jupyter Book
CLI to build this book. You can find
the [Jupyter Book build instructions here](https://jupyterbook.org/start/build.html).

Build and preview the text locally

To build locally, pip install -r requirements.txt and then jupyter-book build .

Follow the build instructions on the Jupyter Book guide. The guide has information for how to use the Jupyter Book CLI to build this book. You can find the Jupyter Book build instructions here.