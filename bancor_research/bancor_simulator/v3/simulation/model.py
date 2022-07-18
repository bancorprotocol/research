# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the Bprotocol Foundation (Bancor) LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Main Bancor Simulation module interface."""

import mesa
import itertools
from decimal import Decimal
from mesa.datacollection import DataCollector
from pydantic.types import Any

from bancor_research.bancor_simulator.v3.simulation.agents import Trader, LP, Protocol

"""
If you want to perform a parameter sweep, call batch_run.py instead of run.py.
For details see batch_run.py in the same directory as run.py.
"""


def track_params(model):
    return model.init_traders, model.init_lps


def track_run(model):
    return model.uid


def get_bntkn_health(model):
    bntkn_health = [a.protocol.bntkn_health for a in model.schedule.agents][0]
    return int(round(float(bntkn_health)))


def get_bnbnt_health(model):
    bnbnt_health = [a.protocol.bnbnt_health for a in model.schedule.agents][0]
    return int(round(float(bnbnt_health)))


class BancorSimulation(mesa.Model):
    """
    This is a highly abstracted, simplified model of the Bancor v3 protocol, with only two
    types of agents (Trader and LP) and a single BancorDapp instance representing their environment and state space(s).
    Note that the LPs perform those actions which are in reality only performed vy the DAO, such as changing fees, etc..
    """

    current_id = 0
    id_gen = itertools.count(1)

    # grid height
    grid_h = 20
    # grid width
    grid_w = 20
    max_steps = SIMULATION_MAX_STEPS

    def __init__(
        self,
        height=grid_h,
        width=grid_w,
        init_traders=SIMULATION_NUM_TRADERS,
        init_lps=SIMULATION_NUM_LPs,
        whale_threshold=SIMULATION_WHALE_THRESHOLD,
        trading_fee=float(DEFAULT_TRADING_FEE),
        network_fee=float(DEFAULT_NETWORK_FEE),
        withdrawal_fee=float(DEFAULT_WITHDRAWAL_FEE),
        whitelisted_tokens=None,
        target_tvl=SIMULATION_TARGET_TVL,
        price_feeds=DEFAULT_PRICE_FEEDS,
        bnt_funding_limit=float(DEFAULT_BNT_FUNDING_LIMIT),
        bnt_min_liquidity=float(DEFAULT_BNT_MIN_LIQUIDITY),
        *args: Any,
        **kwargs: Any
    ):

        if whitelisted_tokens is None:
            whitelisted_tokens = SIMULATION_WHITELISTED_TOKENS

        # create a single BancorDapp v3 instance for the model
        self.protocol = Protocol(
            self.next_id(),
            self,
            Decimal(trading_fee),
            Decimal(network_fee),
            Decimal(withdrawal_fee),
            whitelisted_tokens,
            price_feeds,
            Decimal(bnt_funding_limit),
            Decimal(bnt_min_liquidity),
        )

        super().__init__(*args, **kwargs)

        self.height = height
        self.width = width
        self.init_lps = init_lps
        self.init_traders = init_traders
        self.uid = next(self.id_gen)
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.whale_threshold = whale_threshold
        self.trading_fee = float(trading_fee)
        self.network_fee = float(network_fee)
        self.withdrawal_fee = float(withdrawal_fee)

        self.datacollector = DataCollector(
            model_reporters={
                "bnbnt_health": get_bnbnt_health,
                "bntkn_health": get_bntkn_health,
                "Model Params": track_params,
                "Run": track_run,
            },
            agent_reporters={
                "profit": "profit",
                "latest_user_name": "user_name",
                "latest_action": "latest_action",
                "latest_tkn_name": "latest_tkn_name",
                "latest_tkn_amt": "latest_tkn_amt",
                "vault_bnt": "vault_bnt",
                "erc20contracts_bntkn": "erc20contracts_bntkn",
                "staked_bnt": "staked_bnt",
                "external_protection_vault_tkn": "external_protection_vault_tkn",
                "spot_rate": "spot_rate",
                "ema_rate": "ema_rate",
                "protocol_wallet_bnbnt": "protocol_wallet_bnbnt",
                "vortex_bnt": "vortex_bnt",
                "erc20contracts_bnbnt": "erc20contracts_bnbnt",
                "vault_tkn": "vault_bnt",
                "staked_tkn": "staked_bnt",
            },
        )

        # create Traders for the model according to parameters
        for i in range(self.init_traders):
            x1 = self.random.randrange(self.width)
            y1 = self.random.randrange(self.height)
            trader = Trader(
                unique_id=self.next_id(),
                pos=(x1, y1),
                model=self,
                moore=True,
                whale_threshold=whale_threshold,
                whitelisted_tokens=whitelisted_tokens,
                target_tvl=target_tvl,
            )
            self.grid.place_agent(trader, (x1, y1))
            self.schedule.add(trader)

        # create LPs for the model according to parameters
        for i in range(self.init_lps):
            x2 = self.random.randrange(self.width)
            y2 = self.random.randrange(self.height)
            liquidity_provider = LP(
                unique_id=self.next_id(),
                pos=(x2, y2),
                model=self,
                moore=True,
                whale_threshold=whale_threshold,
                whitelisted_tokens=whitelisted_tokens,
                target_tvl=target_tvl,
            )
            self.grid.place_agent(liquidity_provider, (x2, y2))
            self.schedule.add(liquidity_provider)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # tell all the agents in the model to run their step function
        self.datacollector.collect(self)
        self.schedule.step()
        self.protocol.v3.step()

    def run_model(self):
        for i in range(self.max_steps):
            print(self.protocol.v3.global_state.timestamp)
            self.step()
