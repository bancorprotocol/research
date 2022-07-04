---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.7
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Simulation

The library currently supports a limited random walker style simulation scenario.

## Parameter Sweeps (Batch Runs)
Parameters sweeps can be done via the [mesa](https://github.com/projectmesa/mesa) BatchRunner instance defined at the bottom of file *batch_run.py* in the simulation directory. This instance is for collecting data on parameter sweeps. It is not meant to be run with run.py, since run.py starts up a server for visualization, which isn't necessary for the BatchRunner. To run a parameter sweep, call batch_run.py in the command line from the project directory as follows:

```
python bancor_simulator/v3/simulation/batch_run.py
```

The BatchRunner is set up to collect step by step data of the model. It does this by collecting the DataCollector object in a model_reporter (i.e. the DataCollector is collecting itself every step).

The end result of the batch run will be a CSV file created in the same directory from which Python was run. The CSV file will contain the data from every step of every run.

## GUI Visualization (Single Runs)

To run the model interactively, run the following command from the project directory:
```
mesa runserver
```
Then open your browser to http://127.0.0.1:8521/, select the model parameters, press Reset, then Start.

