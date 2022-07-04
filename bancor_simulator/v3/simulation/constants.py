# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Simulation constants and default state variables."""
from decimal import Decimal

SIMULATION_TARGET_TVL: Decimal = Decimal("160000000")
SIMULATION_TARGET_TRADE_VOLUME: Decimal = Decimal("20000000")
SIMULATION_WHALE_THRESHOLD: Decimal = Decimal("1000000")
SIMULATION_TARGET_NUM_TRADES_PER_DAY: int = 200
SIMULATION_TARGET_NUM_DEPOSITS_PER_DAY: int = 200
SIMULATION_TARGET_NUM_WITHDRAWALS_PER_DAY: int = 200
SIMULATION_NUM_TRADERS = 2
SIMULATION_NUM_LPs = 2
SIMULATION_WHITELISTED_TOKENS = ["tkn", "bnt"]
SIMULATION_MAX_STEPS = 100
SIMULATION_OUTPUT_PATH: str = "data/simulation_output.csv"
