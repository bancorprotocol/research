from datetime import datetime
from math import ceil
import pandas as pd
from fractions import Fraction
from decimal import Decimal
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any
from bancor3_simulator.core.settings import GlobalSettings as Settings

settings = Settings()
timestep = settings.timestep
whitelisted_tokens = settings.whitelisted_tokens
network_fee = settings.network_fee
withdrawal_fee = settings.withdrawal_fee
bnt_min_liquidity = settings.bnt_min_liquidity
cooldown_time = settings.cooldown_time
active_users = settings.active_users
alpha = settings.alpha
bnt_funding_limit = settings.bnt_funding_limit
trading_fee = settings.trading_fee


@dataclass
class GlobalSettings:
    """Main storage component to hold global variables."""

    network_fee = network_fee
    withdrawal_fee = withdrawal_fee
    bnt_min_liquidity = bnt_min_liquidity
    cooldown_time = cooldown_time


@dataclass
class CooldownState(GlobalSettings):
    """Main storage component to track pending withdrawals."""

    timestep: int
    user_name: str
    withdrawal_id: int
    tkn_name: str
    tkn_amt: Decimal
    pool_token_amt: Decimal
    is_complete: bool


@dataclass
class Wallet(GlobalSettings):
    """Main wallet level storage component."""

    tkn_name: str
    tkn_amt: Decimal = Decimal("0")
    bntkn_amt: Decimal = Decimal("0")
    pending_withdrawals: Dict[int, CooldownState] = field(
        default_factory=lambda: defaultdict(CooldownState)
    )
    vbnt_amt: Decimal = Decimal("0")


@dataclass
class User(GlobalSettings):
    """Main user level storage component."""

    user_name: str
    wallet: Dict[str, Wallet] = field(default_factory=lambda: defaultdict(Wallet))


@dataclass
class Users(GlobalSettings):
    """Main storage component to group users."""

    usernames: list = field(default_factory=list)
    users: Dict[str, User] = field(default_factory=lambda: defaultdict(User))
    history: List[Dict[str, User]] = field(default_factory=list)


@dataclass
class Transaction(GlobalSettings):
    """Main transaction level storage component."""

    timestep: int = 0
    vault_tkn: Decimal = Decimal("0")
    erc20contracts_bntkn: Decimal = Decimal("0")
    staked_tkn: Decimal = Decimal("0")
    trading_enabled: bool = False
    bnt_trading_liquidity: Decimal = Decimal("0")
    tkn_trading_liquidity: Decimal = Decimal("0")
    trading_fee: Decimal = Decimal("0.005")
    bnt_funding_limit: Decimal = Decimal("0")
    bnt_remaining_funding: Decimal = Decimal("0")
    bnt_funding_amount: Decimal = Decimal("0")
    external_protection_vault: Decimal = Decimal("0")
    spot_rate: Decimal = Decimal("0")
    ema_rate: Decimal = Decimal("0")
    ema_last_updated: Decimal = Decimal("0")

    @property
    def is_price_stable(self):
        """Computes the deviation between the spot and ema bnt/tkn rates. True if the deviation is less than 1%."""
        return (
                Decimal("0.99") * self.ema_rate
                <= self.spot_rate
                <= Decimal("1.01") * self.ema_rate
        )

    @property
    def avg_tkn_trading_liquidity(self):
        """Computes the tkn trading liquidity, adjusted by the ema."""
        return self.bnt_trading_liquidity / self.ema_rate

    @property
    def tkn_excess(self):
        """Computes the difference between the masterVault tknBalance and the average averageTknTradingLiquidity."""
        return self.vault_tkn - self.avg_tkn_trading_liquidity

    @property
    def tkn_excess_bnt_equivalence(self):
        """Computes the equivalent bnt value of the non-trading tkn balance of the masterVault."""
        return self.tkn_excess * self.ema_rate

    @property
    def bnt_bootstrap_liquidity(self):
        """Computes the bntMinLiquidity multiplied by 2."""
        return 2 * self.bnt_min_liquidity

    @property
    def ema(self) -> Fraction:
        """Returns a fraction as two separate outputs"""
        return Fraction(self.ema_rate)

    @property
    def scaled_ema(self) -> int:
        """Ensures that the ema can be stored as a maximum 112-bit number."""
        return ceil((max(self.ema.numerator, self.ema.denominator) / (2 ** 112 - 1)))

    @property
    def ema_compressed_numerator(self) -> int:
        """Used to measure the deviation of solidity fixed point math on protocol calclulations."""
        if self.scaled_ema > 0:
            return int(self.ema.numerator / self.scaled_ema)
        else:
            return 0

    @property
    def ema_compressed_denominator(self) -> int:
        """Used to measure the deviation of solidity fixed point math on protocol calclulations."""
        if self.scaled_ema > 0:
            return int(self.ema.denominator / self.scaled_ema)
        else:
            return 0

    @property
    def is_ema_update_allowed(self) -> bool:
        """Returns True if the moving average has not been updated on the existing block."""
        return int(self.timestep) != int(self.ema_last_updated)

    @property
    def ema_deviation(self) -> Decimal:
        """Returns the deviation between these values as emaRate/emaCompressedRate."""
        if self.ema_compressed_numerator > 0:
            return self.ema_rate * Decimal(
                self.ema_compressed_denominator / self.ema_compressed_numerator
            )
        else:
            return Decimal("0")


@dataclass
class State(GlobalSettings):
    "Main system state storage component."
    latest_tkn: str = None
    latest_amt: Decimal = Decimal("0")
    latest_user_name: str = None
    latest_action: str = None
    withdrawal_ids: List[Dict[str, CooldownState]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    timestep: int = timestep
    network_fee: Decimal = network_fee
    trading_fee: Decimal = trading_fee
    bnt_min_liquidity: Decimal = bnt_min_liquidity
    cooldown_time: int = cooldown_time
    bnt_funding_limit: Decimal = bnt_funding_limit
    alpha: Decimal = alpha
    whitelisted_tokens: list = field(default_factory=lambda: whitelisted_tokens)
    staked_bnt: Decimal = Decimal("0")
    vault_bnt: Decimal = Decimal("0")
    erc20contracts_bnbnt: Decimal = Decimal("0")
    protocol_wallet_bnbnt: Decimal = Decimal("0")
    vortex_bnt: Decimal = Decimal("0")
    vortex_vbnt_burned: Decimal = Decimal("0")
    tokens: Dict[str, Transaction] = field(
        default_factory=lambda: defaultdict(Transaction)
    )
    transactions: List[Dict[str, Transaction]] = field(default_factory=list)
    users: Users = Users()
    history: list = field(default_factory=list)

    @property
    def bnbnt_rate(self):
        """Determines the bnbnt issuance rate, used for bnbnt issuance for the protocol during tkn deposits.
        Also used to determine the exchange between users and the protocol during bnt deposits.

        Returns:
            Output is determined by the bnt balance of the staking ledger and the current bnbnt supply.

        """
        if self.staked_bnt == 0 and self.erc20contracts_bnbnt == 0:
            bnbnt_rate = Decimal(1)
        else:
            bnbnt_rate = Decimal(self.erc20contracts_bnbnt / self.staked_bnt)
        return bnbnt_rate

    def step(self):
        """Increments the timestep +1"""
        self.timestep += 1

    def list_users(self):
        """

        Returns: List of all active users.

        """
        return [usr for usr in self.users.usernames]

    def list_tokens(self):
        """

        Returns: List of all active whitelisted_tokens.

        """
        return [tkn for tkn in self.whitelisted_tokens]

    def create_user(self, user_name):
        """Creates a new system user agent.

        Args:
            user_name: A unique name identifier for the user.
        """
        if user_name not in self.users.usernames:
            self.users.usernames.append(user_name)
            self.users.users[user_name] = User(user_name=user_name)
            for tkn_name in whitelisted_tokens:
                self.users.users[user_name].wallet[tkn_name] = Wallet(tkn_name=tkn_name)

    def init_protocol(self, whitelisted_tokens: List[str], usernames: List[str]):
        """On system genesis this method builds initial wallet placeholders and users.

        Args:
            whitelisted_tokens: List of whitelisted tokens.
            usernames: List of users to initialize the system with.
        """
        for tkn_name in whitelisted_tokens:
            if tkn_name not in self.whitelisted_tokens:
                self.whitelist_tkn(tkn_name)
                self.tokens[tkn_name] = Transaction(tkn_name)

        for usr in usernames:
            if usr not in self.users.usernames:
                self.create_user(usr)

        return self

    def get_prices(self, tkn_name, price_feeds):
        """Takes tokenName and timestamp as inputs.
        Takes an optional third argument, priceFeeds, which is a csv file.
        The priceFeed argument uses the default priceFeed set at system creation if none is passed.
        Returns tokenPrice, bntPrice for the current timestamp.

        Args:
            tkn_name:
            price_feeds:

        Returns:

        """
        _timestep = self.timestep
        bnt_price = Decimal(price_feeds.at[_timestep, "bnt"])
        if tkn_name == "vbnt":

            bnbnt_rate = self.bnbnt_rate

            # vbnt_price
            tkn_price = bnt_price / bnbnt_rate
        else:
            tkn_price = Decimal(price_feeds.at[_timestep, tkn_name])
        return self, tkn_price, bnt_price

    def check_pool_shutdown(self, tkn_name):
        """
        Checks that the bnt_min_trading_liquidity threshold has not been breached.
        This function is called after changes in the bnt funding limits of a pool, after tkn deposits, and before tkn withdrawals.
        This function returns nothing.
        """
        trading_enabled = self.tokens[tkn_name].trading_enabled
        _bnt_min_liquidity = self.bnt_min_liquidity
        bnt_trading_liquidity = self.tokens[tkn_name].bnt_trading_liquidity
        if bnt_trading_liquidity < _bnt_min_liquidity and trading_enabled:
            self.shutdown_pool(tkn_name)
        return self

    def shutdown_pool(self, tkn_name):
        """
        This function is called when the bnt_min_trading_liquidity threshold is breached.
        All bnt trading liquidty is renounced, and the pool is disabled for trading.
        This function returns nothing.
        """

        bnt_trading_liquidity = self.tokens[tkn_name].bnt_trading_liquidity
        bnbnt_renounced = self.bnbnt_amt(bnt_trading_liquidity)

        # actuator tasks
        self.tokens[tkn_name].trading_enabled = False
        self.tokens[tkn_name].bnt_trading_liquidity = Decimal("0")
        self.staked_bnt -= bnt_trading_liquidity
        self.vault_bnt -= bnt_trading_liquidity
        self.erc20contracts_bnbnt -= bnbnt_renounced
        self.protocol_wallet_bnbnt -= bnbnt_renounced
        self.tokens[tkn_name].bnt_funding_amount -= bnt_trading_liquidity
        self.tokens[tkn_name].bnt_remaining_funding += bnt_trading_liquidity
        self.tkn_trading_liquidity = Decimal("0")
        return self

    def update_spot_rate(self, tkn_name):
        """Updates the spot rate.

        Args:
            tkn_name: Name of the token being transacted.
        """
        if (
                self.tokens[tkn_name].bnt_trading_liquidity == 0
                and self.tokens[tkn_name].tkn_trading_liquidity == 0
        ):
            spot_rate = Decimal(0)
        else:
            spot_rate = (
                    self.tokens[tkn_name].bnt_trading_liquidity
                    / self.tokens[tkn_name].tkn_trading_liquidity
            )
        self.tokens[tkn_name].spot_rate = spot_rate

    def bntkn_rate(self, tkn_name):
        """Computes the bntkn issuance rate for tkn deposits, based on the staking ledger and the current bntkn supply"""
        if (
                self.tokens[tkn_name].erc20contracts_bntkn == 0
                and self.tokens[tkn_name].staked_tkn == 0
        ):
            bntkn_rate = Decimal("1")
        else:
            bntkn_rate = (
                    self.tokens[tkn_name].erc20contracts_bntkn
                    / self.tokens[tkn_name].staked_tkn
            )
        return bntkn_rate

    def bnbnt_amt(self, tkn_amt: Decimal) -> Decimal:
        """Returns the quantity of bntkn to issue to the user during deposits.
        When called during withdrawal of tkn, it is the amount of bnbnt renounced by the protocol.

        Args:
            tkn_amt: Name of the token being transacted.

        Returns:
            bnbnt_amt: bntkn to issue to the user during deposits.
        """
        return self.bnbnt_rate * tkn_amt

    def whitelist_tkn(self, tkn_name):
        """Adds a new tkn_name to the whitelisted_tokens if the token is not already whitelisted"""
        if tkn_name not in self.whitelisted_tokens:
            self.whitelisted_tokens.append(tkn_name)

    def bnt_amt(self, withdraw_value):
        return withdraw_value * (1 - self.withdrawal_fee)

    def bntkn_amt(self, tkn_name, tkn_amt):
        """Used to determine the issuance of bntkn during deposits,
        and the required bntkn amount for a given tkn amount during withdrawal.

        Args:
            tkn_name: Name of the token being transacted.
            tkn_amt: Amoount of the token being transcated.

        Returns:
            The product of bntknRate and tknAmount.
        """
        return self.bntkn_rate(tkn_name) * tkn_amt

    def virtual_rate(self, bnt_price, tkn_price):
        """
        Takes bntVirtualBalance and tknTokenVirtualBalance as inputs.
        Returns bntVirtualBalance/tknTokenVirtualBalance.
        """
        bnt_virtual_balance = Decimal("1") / bnt_price
        tkn_virtual_balance = Decimal("1") / tkn_price
        return bnt_virtual_balance / tkn_virtual_balance

    def tkn_bootstrap_liquidity(self, bnt_bootstrap_liquidity, bnt_price, tkn_price):
        """
        Returns the bntBootstrapLiquidity divided by virtualRate.
        This is the tkn equivalnce of twice the bntMinLiquidity (i.e. the bntBootstrapLiquidity)
        """
        return bnt_bootstrap_liquidity / self.virtual_rate(bnt_price, tkn_price)

    def pool_tkn_amt(self, user_name: str, tkn_name: str, withdraw_value: Decimal):
        """The users bntkn is converted into its tkn equivalent, and these values are stored in the pending_withdrawals with the current timestamp number.

        Args:
            user_name: Name of the user performing the transaction.
            tkn_name: Name of the token being transacted.
            withdraw_value: Amount of the transaction

        Returns:
            withdraw_value converted into pool token units
        """
        user_bntkn_amt = self.users.users[user_name].wallet[tkn_name].bntkn_amt
        if withdraw_value > user_bntkn_amt:
            raise ValueError(
                f"User cannot withdraw more than their current wallet holdings allow.available {tkn_name}={user_bntkn_amt}"
            )
        pool_token_supply = self.tokens[tkn_name].erc20contracts_bntkn
        staked_amt = self.tokens[tkn_name].staked_tkn
        return (lambda a, b, c: a * b / c)(
            pool_token_supply, withdraw_value, staked_amt
        )

    def protocol_bnt_check(self):
        """
        Asserts that the total bnt balance of the system is equal to the total trading liquidity + vortex ledger bnt balance.
        """

        total_bnt_trading_liquidity = sum(
            self.tokens[tkn_name].bnt_trading_liquidity
            for tkn_name in self.whitelisted_tokens
            if tkn_name != "bnt"
        )

        vortex_bnt = self.vortex_bnt
        vault_bnt = self.vault_bnt
        protocol_bnt_discrepancy = vault_bnt - vortex_bnt - total_bnt_trading_liquidity
        # TODO: Replace assertion statement here.

    def log_transaction(self):
        """Logs main parameters after each action."""
        for tkn_name in self.list_tokens():
            state_variables = {
                "timestep": [self.timestep],
                "latest_action": [self.latest_action],
                "latest_amt": [self.latest_amt],
                "latest_user_name": [self.latest_user_name],
                "latest_tkn": [self.latest_tkn],
                "tkn_name": [tkn_name],
                "vault_tkn": [self.tokens[tkn_name].vault_tkn],
                "erc20contracts_bntkn": [self.tokens[tkn_name].erc20contracts_bntkn],
                "staked_tkn": [self.tokens[tkn_name].staked_tkn],
                "trading_enabled": [self.tokens[tkn_name].trading_enabled],
                "bnt_trading_liquidity": [self.tokens[tkn_name].bnt_trading_liquidity],
                "tkn_trading_liquidity": [self.tokens[tkn_name].tkn_trading_liquidity],
                "trading_fee": [self.tokens[tkn_name].trading_fee],
                "bnt_funding_limit": [self.tokens[tkn_name].bnt_funding_limit],
                "bnt_remaining_funding": [self.tokens[tkn_name].bnt_remaining_funding],
                "bnt_funding_amount": [self.tokens[tkn_name].bnt_funding_amount],
                "external_protection_vault": [
                    self.tokens[tkn_name].external_protection_vault
                ],
                "spot_rate": [self.tokens[tkn_name].spot_rate],
                "ema_rate": [self.tokens[tkn_name].ema_rate],
                "scaled_ema": [self.tokens[tkn_name].scaled_ema],
                "ema_compressed_numerator": [
                    self.tokens[tkn_name].ema_compressed_numerator
                ],
                "ema_compressed_denominator": [
                    self.tokens[tkn_name].ema_compressed_denominator
                ],
                "ema_deviation": [self.tokens[tkn_name].ema_deviation],
                "ema_last_updated": [self.tokens[tkn_name].ema_last_updated],
                "network_fee": [self.network_fee],
                "withdrawal_fee": [self.withdrawal_fee],
                "bnt_min_liquidity": [self.bnt_min_liquidity],
                "cooldown_time": [self.cooldown_time],
                "protocol_wallet_bnbnt": [self.protocol_wallet_bnbnt],
                "vortex_bnt": [self.vortex_bnt],
                "vortex_vbnt_burned": [self.vortex_vbnt_burned],
                "erc20contracts_bnbnt": [self.erc20contracts_bnbnt],
                "vault_bnt": [self.vault_bnt],
                "staked_bnt": [self.staked_bnt],
                "bnbnt_rate": [self.bnbnt_rate],
            }
            self.history.append(pd.DataFrame(state_variables))
