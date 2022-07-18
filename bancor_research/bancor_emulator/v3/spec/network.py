from bancor_research.bancor_emulator.solidity.uint.float import Decimal
from bancor_research.bancor_emulator.solidity import uint32, uint256, time, block

from bancor_research.bancor_emulator.BancorNetwork      import BancorNetwork     
from bancor_research.bancor_emulator.BNTPool            import BNTPool           
from bancor_research.bancor_emulator.Constants          import PPM_RESOLUTION    
from bancor_research.bancor_emulator.NetworkSettings    import NetworkSettings   
from bancor_research.bancor_emulator.PendingWithdrawals import PendingWithdrawals
from bancor_research.bancor_emulator.PoolCollection     import PoolCollection    
from bancor_research.bancor_emulator.PoolToken          import PoolToken         
from bancor_research.bancor_emulator.PoolTokenFactory   import PoolTokenFactory  
from bancor_research.bancor_emulator.ReserveToken       import ReserveToken      
from bancor_research.bancor_emulator.StandardRewards    import StandardRewards   
from bancor_research.bancor_emulator.TokenGovernance    import TokenGovernance   
from bancor_research.bancor_emulator.Vault              import Vault             

import pandas as pd
import warnings
from pydantic.fields import TypeVar

warnings.filterwarnings("ignore", category=RuntimeWarning)
PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")

DEFAULT_TIMESTAMP = 0
DEFAULT_WHITELIST = ["dai", "eth", "link", "bnt", "tkn", "wbtc"]
DEFAULT_USERS = ["alice", "bob", "charlie", "trader", "user", "protocol"]
DEFAULT_DECIMALS = 18
DEFAULT_QDECIMALS = Decimal(10) ** -DEFAULT_DECIMALS
DEFAULT_WITHDRAWAL_FEE = Decimal("0.0025")
DEFAULT_TRADING_FEE = Decimal("0.01")
DEFAULT_NETWORK_FEE = Decimal("0.2")
DEFAULT_BNT_FUNDING_LIMIT = Decimal("1000000")
DEFAULT_BNT_MIN_LIQUIDITY = Decimal("10000")
DEFAULT_COOLDOWN_TIME = time.days * 7
DEFAULT_ALPHA = Decimal("0.2").quantize(DEFAULT_QDECIMALS)
SECONDS_PER_DAY = 86400
DEFAULT_NUM_TIMESTAMPS = SECONDS_PER_DAY * 30
DEFAULT_PRICE_FEEDS_PATH = (
    "https://bancorml.s3.us-east-2.amazonaws.com/price_feeds.parquet"
)
DEFAULT_PRICE_FEEDS = pd.DataFrame(
    {
        "INDX": (0 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "vbnt": (1.0 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "tkn": (2.5 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "bnt": (2.5 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "link": (15.00 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "eth": (2500.00 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
        "wbtc": (40000.00 for _ in range(DEFAULT_NUM_TIMESTAMPS)),
    }
)

def toPPM(value: Decimal):
    return uint32(value * int(PPM_RESOLUTION))

def toWei(value: Decimal, decimals: int):
    return uint256(value * 10 ** decimals)

def updateBlock(timestamp):
    if block.timestamp < timestamp:
        block.timestamp = timestamp
        block.number += 1
    else:
        assert block.timestamp == timestamp

class BancorDapp:
    def __init__(
        self,
        timestamp: int = DEFAULT_TIMESTAMP,
        alpha: Decimal = DEFAULT_ALPHA,
        bnt_min_liquidity: Decimal = DEFAULT_BNT_MIN_LIQUIDITY,
        withdrawal_fee: Decimal = DEFAULT_WITHDRAWAL_FEE,
        cooldown_time: int = DEFAULT_COOLDOWN_TIME,
        bnt_funding_limit: Decimal = DEFAULT_BNT_FUNDING_LIMIT,
        network_fee: Decimal = DEFAULT_NETWORK_FEE,
        trading_fee: Decimal = DEFAULT_TRADING_FEE,
        whitelisted_tokens=DEFAULT_WHITELIST,
        price_feeds_path: str = DEFAULT_PRICE_FEEDS_PATH,
        price_feeds: PandasDataFrame = DEFAULT_PRICE_FEEDS,
        active_users: list = DEFAULT_USERS,
        transaction_id: int = 0,
        generate_json_tests: bool = False,
        emulate_solidity_results: bool = False,
    ):
        block.timestamp = 0
        block.number = 0
        updateBlock(timestamp)

        self.bnt   = ReserveToken('BNT'  , 'BNT'  , DEFAULT_DECIMALS)
        self.vbnt  = ReserveToken('VBNT' , 'VBNT' , DEFAULT_DECIMALS)
        self.bnbnt = PoolToken   ('bnBNT', 'bnBNT', DEFAULT_DECIMALS, self.bnt)

        self.bntGovernance      = TokenGovernance(self.bnt)
        self.vbntGovernance     = TokenGovernance(self.vbnt)
        self.networkSettings    = NetworkSettings(self.bnt)
        self.masterVault        = Vault(self.bntGovernance, self.vbntGovernance)
        self.erVault            = Vault(self.bntGovernance, self.vbntGovernance)
        self.epVault            = Vault(self.bntGovernance, self.vbntGovernance)
        self.network            = BancorNetwork(self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.epVault, self.bnbnt)
        self.bntPool            = BNTPool(self.network, self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.bnbnt)
        self.pendingWithdrawals = PendingWithdrawals(self.network, self.bnt, self.bntPool)
        self.poolTokenFactory   = PoolTokenFactory()
        self.poolMigrator       = None
        self.poolCollection     = PoolCollection(self.network, self.bnt, self.networkSettings, self.masterVault, self.bntPool, self.epVault, self.poolTokenFactory, self.poolMigrator, toPPM(network_fee))
        self.standardRewards    = StandardRewards(self.network, self.networkSettings, self.bntGovernance, self.vbnt, self.bntPool, self.erVault)

        self.networkSettings.initialize()
        self.network.initialize(self.bntPool, self.pendingWithdrawals, self.poolMigrator)
        self.bntPool.initialize()
        self.pendingWithdrawals.initialize()
        self.poolTokenFactory.initialize()
        self.standardRewards.initialize()

        self.networkSettings.setWithdrawalFeePPM(toPPM(withdrawal_fee))
        self.networkSettings.setMinLiquidityForTrading(toWei(bnt_min_liquidity * 2, DEFAULT_DECIMALS))

        self.pendingWithdrawals.setLockDuration(cooldown_time)

        self.network.registerPoolCollection(self.poolCollection)

        self.reserveTokens = {'bnt': self.bnt}
        self.poolTokens = {'bnbnt': self.bnbnt}
        for tkn_name in [tkn_name for tkn_name in whitelisted_tokens if tkn_name != 'bnt']:
            tkn = ReserveToken(tkn_name, tkn_name, DEFAULT_DECIMALS) # TODO: support decimals per reserve token
            self.networkSettings.addTokenToWhitelist(tkn)
            self.networkSettings.setFundingLimit(tkn, toWei(bnt_funding_limit, DEFAULT_DECIMALS))
            self.network.createPools([tkn], self.poolCollection)
            self.poolCollection.setTradingFeePPM(tkn, toPPM(trading_fee))
            self.reserveTokens[tkn_name] = tkn
            self.poolTokens[tkn_name] = self.network.collectionByPool(tkn).poolToken(tkn)

        if price_feeds is None:
            price_feeds = pd.read_parquet(price_feeds_path)
            price_feeds.columns = [col.lower() for col in price_feeds.columns]
        self.price_feeds = price_feeds

    def deposit(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        timestamp: int = 0,
        bntkn: Decimal = Decimal("0"),
        action_name="deposit",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        tkn.connect(user_name).approve(self.network, amt)
        return self.network.connect(user_name).deposit(tkn, amt)

    def trade(
        self,
        tkn_amt: Decimal,
        source_token: str,
        target_token: str,
        user_name: str,
        timestamp: int,
        transaction_type: str = "trade",
    ):
        updateBlock(timestamp)
        src_tkn = self.reserveTokens[source_token]
        trg_tkn = self.reserveTokens[target_token]
        src_amt = toWei(tkn_amt, src_tkn.decimals())
        src_tkn.connect(user_name).approve(self.network, src_amt)
        return self.network.connect(user_name).tradeBySourceAmount(src_tkn, trg_tkn, src_amt, 1, uint256.max, user_name)

    def begin_cooldown(
        self,
        tkn_amt: Decimal,
        tkn_name: str,
        user_name: str,
        timestamp: int = 0,
        action_name: str = "begin cooldown",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        tkn.connect(user_name).approve(self.network, amt)
        return self.network.connect(user_name).initWithdrawal(tkn, amt)

    def withdraw(
        self,
        user_name: str,
        id_number: int,
        timestamp: int = 0,
        tkn_name: str = None,
        tkn_amt: Decimal = None,
        transaction_type: str = "withdraw",
    ):
        updateBlock(timestamp)
        return self.network.connect(user_name).withdraw(id_number)

    def burn(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        timestamp: int = 0,
        transaction_type: str = "burnPoolTokenTKN",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        tkn.connect(user_name).burn(amt)

    def claim_standard_rewards(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        rewards_ids: list[int],
        transaction_type: str = "claim_standard_rewards",
        timestamp: int = 0,
    ):
        updateBlock(timestamp)
        return self.standardRewards.connect(user_name).claimRewards(rewards_ids)

    def join_standard_rewards(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        timestamp: int = 0,
        transaction_type="join_standard_rewards",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        tkn.connect(user_name).approve(self.standardRewards, amt)
        return self.standardRewards.connect(user_name).join(tknProgramId, amt)

    def leave_standard_rewards(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        id_number: int,
        timestamp: int = 0,
        transaction_type="leave_standard_rewards",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        return self.standardRewards.connect(user_name).leave(tknProgramId, amt)

    def set_user_balance(
        self,
        user_name: str,
        tkn_name: str,
        tkn_amt: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set user balance",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        func = self.bntGovernance.mint if tkn == self.bnt else tkn.issue
        func(user_name, amt)

    def set_trading_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set trading fee",
        user_name: str = "protocol",
    ):
        updateBlock(timestamp)
        self.poolCollection.setTradingFeePPM(self.reserveTokens[tkn_name], toPPM(value))

    def set_network_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set network fee",
        user_name: str = "protocol",
    ):
        updateBlock(timestamp)
        self.poolCollection.setNetworkFeePPM(toPPM(value))

    def set_withdrawal_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set withdrawal fee",
        user_name: str = "protocol",
    ):
        updateBlock(timestamp)
        self.networkSettings.setWithdrawalFeePPM(toPPM(value))

    def set_bnt_funding_limit(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = 0,
        transaction_type: str = "set bnt funding limit",
        user_name: str = "protocol",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(value, self.bnt.decimals())
        self.networkSettings.setFundingLimit(tkn, amt)

    def dao_msig_init_pools(
        self,
        pools: list,
        tkn_name: str = None,
        timestamp: int = 0,
        transaction_type: str = "enableTrading",
        user_name: str = "protocol",
    ) -> None:
        updateBlock(timestamp)
        for pool in [pool for pool in pools if self.reserveTokens[pool] != self.bnt]:
            tknPrice = self.price_feeds.at[timestamp, pool]
            bntPrice = self.price_feeds.at[timestamp, "bnt"]
            while tknPrice != int(tknPrice) or bntPrice != int(bntPrice):
                tknPrice *= 10
                bntPrice *= 10
            self.poolCollection.enableTrading(self.reserveTokens[pool], tknPrice, bntPrice)

    def create_user(self, user_name: str, timestamp: int = 0):
        pass

    def describe(self, rates: bool = False, decimals: int = 6):
        pass

# whitelisted_tokens: list = ['bnt', 'eth', 'wbtc', 'link']
# v3 = BancorDapp(whitelisted_tokens=whitelisted_tokens)
