# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""
Script used to perform a parameter sweep.

Note:
    This version of the model has a BatchRunner at the bottom. This
    is for collecting data on parameter sweeps. It is not meant to
    be run with run.py, since run.py starts up a server for visualization, which
    isn't necessary for the BatchRunner. To run a parameter sweep, call
    batch_run.py in the command line.

    The BatchRunner is set up to collect step by step data of the model. It does
    this by collecting the DataCollector object in a model_reporter (i.e. the
    DataCollector is collecting itself every step).

    The end result of the batch run will be a CSV file created in the same
    directory from which Python was run. The CSV file will contain the data from
    every step of every run.
"""
import os

# Add any desired parameters to sweep below.
br_params = {
    "trading_fee": [
        DEFAULT_TRADING_FEE - Decimal("0.001"),
        DEFAULT_TRADING_FEE,
        DEFAULT_TRADING_FEE + Decimal("0.001"),
    ]
}

if __name__ == "__main__":
    data = mesa.batch_run(
        model_cls=BancorSimulation,
        parameters=br_params,
        data_collection_period=1,
        max_steps=SIMULATION_MAX_STEPS,
    )
    br_df = pd.DataFrame(data)

    overwrite_dir = True
    os.makedirs(SIMULATION_OUTPUT_PATH, exist_ok=overwrite_dir)

    br_df.to_csv(SIMULATION_OUTPUT_PATH)
