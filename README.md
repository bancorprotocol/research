<p align="center">
<img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
</p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# Bancor Simulator

[![PyPI version](https://badge.fury.io/py/bancor-research.svg)](https://badge.fury.io/py/bancor-research)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Jupyter Book Badge](https://jupyterbook.org/badge.svg)](https://simulator.bancor.network/chapters/bancor-research.html)
[![Netlify Status](https://api.netlify.com/api/v1/badges/b4173988-e380-443b-94b1-78918e13a013/deploy-status)](https://app.netlify.com/sites/incandescent-kelpie-250f0e/deploys)
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

**Bancor Simulator** is an open-source python package developed by **Bancor Research**. It aims to assist the design, testing, and validation of Bancor v3 tokenomics.

See [official documentation](https://simulator.bancor.network/chapters/bancor-simulator.html) for complete details.

**Warning**: The docs are a work in progress with potentially broken links, unfinished sections, and a non-exhaustive overview of commands and example usage. Moreover, the entirety of the codebase and documentation is subject to change without warning.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

## Introduction

All state transition functions and accompanying data structures described in the product specification [BIP15: Proposing Bancor 3](https://docs.google.com/document/d/11UeMYaI_1CWdf_Nu6veUO-vNB5uX-FcVRqTSU-ziDRk/edit?usp=sharing) are the core system level operations of this library. 

## Organization

This is the project directory structure:

```
bancor_research/                   <------- ** General Research Project **
└───── bancor_emulator/            <------- Solidity Emulation Project
   └── bancor_simulator/           <------- ** Spec & Simulation Project **
      │   ├── v3/                  <------- Current Version
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
$ pip install bancor-research
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

**Follow the build instructions on the Jupyter Book guide**. The guide has information on how to use the Jupyter Book
CLI to build this book. You can find
the [Jupyter Book build instructions here](https://jupyterbook.org/start/build.html).

Build and preview the text locally

To build locally, pip install -r requirements.txt and then jupyter-book build .

Follow the build instructions on the Jupyter Book guide. The guide has information on how to use the Jupyter Book CLI to build this book. You can find the Jupyter Book build instructions here.
