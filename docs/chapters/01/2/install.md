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

# Install

`Bancor Simulator` is available for Python 3.6+. It can be installed from [pypi](https://pypi.org/project/bancor_simulator/), or from [source](https://github.com/bancorprotocol/simulator-v3).

To install `Bancor Simulator` with all dependencies, run the following command:

```bash
$ pip install bancor_simulator
```

## Windows Additional Requirements & Troubleshooting

If you are using `pip` to install bancor_simulator on Windows, it is recommended you first install the following packages using conda:
* `numba` (needed for `shap` and prediction explanations). Install with `conda install -c conda-forge numba`
* `graphviz` if you're using bancor_simulator's plotting utilities. Install with `conda install -c conda-forge python-graphviz`

## Mac Additional Requirements & Troubleshooting

Additionally, `graphviz` can be installed by running:

```bash
brew install graphviz
```

+++
