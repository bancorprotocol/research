from bancor_research.bancor_emulator.solidity.uint.float import Decimal
from bancor_research.bancor_emulator.solidity import uint32, uint256, time

# TODO: get rid of the `Emulator_` prefix after renaming class `BancorNetwork` to `BancorDapp`
from bancor_research.bancor_emulator.BancorNetwork      import BancorNetwork      as Emulator_BancorNetwork     
from bancor_research.bancor_emulator.BNTPool            import BNTPool            as Emulator_BNTPool           
from bancor_research.bancor_emulator.Constants          import PPM_RESOLUTION     as Emulator_PPM_RESOLUTION         
from bancor_research.bancor_emulator.ERC20              import ERC20              as Emulator_ERC20             
from bancor_research.bancor_emulator.NetworkSettings    import NetworkSettings    as Emulator_NetworkSettings   
from bancor_research.bancor_emulator.PendingWithdrawals import PendingWithdrawals as Emulator_PendingWithdrawals
from bancor_research.bancor_emulator.PoolCollection     import PoolCollection     as Emulator_PoolCollection    
from bancor_research.bancor_emulator.PoolToken          import PoolToken          as Emulator_PoolToken         
from bancor_research.bancor_emulator.PoolTokenFactory   import PoolTokenFactory   as Emulator_PoolTokenFactory  
from bancor_research.bancor_emulator.ReserveToken       import ReserveToken       as Emulator_ReserveToken      
from bancor_research.bancor_emulator.StandardRewards    import StandardRewards    as Emulator_StandardRewards   
from bancor_research.bancor_emulator.TokenGovernance    import TokenGovernance    as Emulator_TokenGovernance   
from bancor_research.bancor_emulator.Vault              import Vault              as Emulator_Vault             

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

def toPPM(value: Decimal):
    return uint32(value * int(Emulator_PPM_RESOLUTION))

def toWei(value: Decimal, decimals: int):
    return uint256(value * 10 ** decimals)

class BancorNetwork:
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
        price_feeds_path = None,
        price_feeds = None,
        active_users: list = DEFAULT_USERS,
        transaction_id: int = 0,
        generate_json_tests: bool = False,
        emulate_solidity_results: bool = False,
    ):
        self.bnt   = Emulator_ReserveToken('BNT'  , 'BNT'  , DEFAULT_DECIMALS)
        self.vbnt  = Emulator_ReserveToken('VBNT' , 'VBNT' , DEFAULT_DECIMALS)
        self.bnbnt = Emulator_PoolToken   ('bnBNT', 'bnBNT', DEFAULT_DECIMALS, self.bnt)

        self.bntGovernance      = Emulator_TokenGovernance(self.bnt)
        self.vbntGovernance     = Emulator_TokenGovernance(self.vbnt)
        self.networkSettings    = Emulator_NetworkSettings(self.bnt)
        self.masterVault        = Emulator_Vault(self.bntGovernance, self.vbntGovernance)
        self.erVault            = Emulator_Vault(self.bntGovernance, self.vbntGovernance)
        self.epVault            = Emulator_Vault(self.bntGovernance, self.vbntGovernance)
        self.network            = Emulator_BancorNetwork(self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.epVault, self.bnbnt)
        self.bntPool            = Emulator_BNTPool(self.network, self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.bnbnt)
        self.pendingWithdrawals = Emulator_PendingWithdrawals(self.network, self.bnt, self.bntPool)
        self.poolTokenFactory   = Emulator_PoolTokenFactory()
        self.poolMigrator       = None
        self.poolCollection     = Emulator_PoolCollection(self.network, self.bnt, self.networkSettings, self.masterVault, self.bntPool, self.epVault, self.poolTokenFactory, self.poolMigrator, toPPM(network_fee))
        self.standardRewards    = Emulator_StandardRewards(self.network, self.networkSettings, self.bntGovernance, self.vbnt, self.bntPool, self.erVault)

        self.networkSettings.initialize()
        self.network.initialize(self.bntPool, self.pendingWithdrawals, self.poolMigrator)
        self.bntPool.initialize()
        self.pendingWithdrawals.initialize()
        self.poolTokenFactory.initialize()
        self.standardRewards.initialize()

        self.networkSettings.setWithdrawalFeePPM(toPPM(withdrawal_fee))
        self.networkSettings.setMinLiquidityForTrading(toWei(bnt_min_liquidity, DEFAULT_DECIMALS))

        self.pendingWithdrawals.setLockDuration(cooldown_time)

        self.network.registerPoolCollection(self.poolCollection)

        self.reserveTokens = {'bnt': self.bnt}
        self.poolTokens = {'bnbnt': self.bnbnt}
        for tkn_name in whitelisted_tokens:
            tkn = Emulator_ReserveToken(tkn_name, tkn_name, DEFAULT_DECIMALS) # TODO: support decimals per reserve token
            self.networkSettings.addTokenToWhitelist(tkn)
            self.networkSettings.setFundingLimit(tkn, toWei(bnt_funding_limit, DEFAULT_DECIMALS))
            self.network.createPools([tkn], self.poolCollection)
            self.poolCollection.setTradingFeePPM(tkn, toPPM(trading_fee))
            self.reserveTokens[tkn_name] = tkn
            self.poolTokens[tkn_name] = self.network.collectionByPool(tkn).poolToken(tkn)

    def deposit(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        timestamp: int = None,
        bntkn: Decimal = Decimal("0"),
        action_name="deposit",
    ):
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
        timestamp: int = None,
        action_name: str = "begin cooldown",
    ):
        tkn = self.poolTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        tkn.connect(user_name).approve(self.network, amt)
        return self.network.connect(user_name).initWithdrawal(tkn, amt)

    def withdraw(
        self,
        user_name: str,
        id_number: int,
        timestamp: int = None,
        tkn_name: str = None,
        tkn_amt: Decimal = None,
        transaction_type: str = "withdraw",
    ):
        return self.network.connect(user_name).withdraw(id_number)

    def burn(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        timestamp: int = 0,
        transaction_type: str = "burnPoolTokenTKN",
    ):
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
        timestamp: int = None,
    ):
        return self.standardRewards.connect(user_name).claimRewards(rewards_ids)

    def join_standard_rewards(
        self,
        tkn_name: str,
        tkn_amt: Decimal,
        user_name: str,
        timestamp: int = None,
        transaction_type="join_standard_rewards",
    ):
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
        timestamp: int = None,
        transaction_type="leave_standard_rewards",
    ):
        tkn = self.poolTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        return self.standardRewards.connect(user_name).leave(tknProgramId, amt)

    def set_user_balance(
        self,
        user_name: str,
        tkn_name: str,
        tkn_amt: Decimal,
        timestamp: int = None,
        transaction_type: str = "set user balance",
    ):
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(tkn_amt, tkn.decimals())
        func = self.bntGovernance.mint if tkn == self.bnt else tkn.issue
        func(user_name, amt)

    def set_trading_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = None,
        transaction_type: str = "set trading fee",
        user_name: str = "protocol",
    ):
        self.poolCollection.setTradingFeePPM(self.reserveTokens[tkn_name], toPPM(value))

    def set_network_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = None,
        transaction_type: str = "set network fee",
        user_name: str = "protocol",
    ):
        self.poolCollection.setNetworkFeePPM(toPPM(value))

    def set_withdrawal_fee(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = None,
        transaction_type: str = "set withdrawal fee",
        user_name: str = "protocol",
    ):
        self.networkSettings.setWithdrawalFeePPM(toPPM(value))

    def set_bnt_funding_limit(
        self,
        tkn_name: str,
        value: Decimal,
        timestamp: int = None,
        transaction_type: str = "set bnt funding limit",
        user_name: str = "protocol",
    ):
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(value, self.bnt.decimals())
        self.networkSettings.setFundingLimit(tkn, amt)

# whitelisted_tokens: list = ['bnt', 'eth', 'wbtc', 'link']
# v3 = BancorNetwork(whitelisted_tokens=whitelisted_tokens)
