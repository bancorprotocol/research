from bancor_research.bancor_emulator.solidity.uint.float import Decimal
from bancor_research.bancor_emulator.solidity import uint, uint32, uint256, block

from bancor_research.bancor_emulator.BancorNetwork      import BancorNetwork     
from bancor_research.bancor_emulator.BancorNetworkInfo  import BancorNetworkInfo 
from bancor_research.bancor_emulator.BNTPool            import BNTPool           
from bancor_research.bancor_emulator.Constants          import PPM_RESOLUTION    
from bancor_research.bancor_emulator.ERC20              import ERC20             
from bancor_research.bancor_emulator.NetworkSettings    import NetworkSettings   
from bancor_research.bancor_emulator.PendingWithdrawals import PendingWithdrawals
from bancor_research.bancor_emulator.PoolCollection     import PoolCollection    
from bancor_research.bancor_emulator.PoolToken          import PoolToken         
from bancor_research.bancor_emulator.PoolTokenFactory   import PoolTokenFactory  
from bancor_research.bancor_emulator.ReserveToken       import ReserveToken      
from bancor_research.bancor_emulator.StandardRewards    import StandardRewards   
from bancor_research.bancor_emulator.TokenGovernance    import TokenGovernance   
from bancor_research.bancor_emulator.Vault              import Vault             

from bancor_research import DEFAULT, PandasDataFrame, read_price_feeds, pd

def toPPM(percent: str):
    return uint32(PPM_RESOLUTION.data * Decimal(percent[:-1]) / 100)

def toWei(amount: str, decimals: int):
    return uint256(Decimal(amount) * 10 ** decimals)

def fromWei(amount: uint, decimals: int):
    return Decimal(amount.data) / 10 ** decimals

def fromFraction(n: uint, d: uint):
    return Decimal('nan') if n == d == 0 else Decimal(n.data) / Decimal(d.data)

def userAmount(token: ERC20, userId: str, amount: str):
    if (amount.endswith('%')):
        n, d = Decimal(amount[:-1]).as_integer_ratio()
        return token.balanceOf(userId) * n / (d * 100)
    return toWei(amount, token.decimals())

def updateBlock(timestamp):
    if block.timestamp < timestamp:
        block.timestamp = timestamp
        block.number += 1
    else:
        assert block.timestamp == timestamp

class BancorDapp:
    def __init__(
        self,
        timestamp: int = DEFAULT.TIMESTAMP,
        bnt_min_liquidity: str = DEFAULT.BNT_MIN_LIQUIDITY,
        withdrawal_fee: str = DEFAULT.WITHDRAWAL_FEE,
        cooldown_time: int = DEFAULT.COOLDOWN_TIME,
        network_fee: str = DEFAULT.NETWORK_FEE,
        whitelisted_tokens = DEFAULT.WHITELIST,
        price_feeds_path: str = DEFAULT.PRICE_FEEDS_PATH,
        price_feeds: PandasDataFrame = DEFAULT.PRICE_FEEDS,
    ):
        block.timestamp = 0
        block.number = 0
        updateBlock(timestamp)

        self.bnt   = ReserveToken('bnt'  , 'bnt'  , DEFAULT.DECIMALS)
        self.vbnt  = ReserveToken('vbnt' , 'vbnt' , DEFAULT.DECIMALS)
        self.bnbnt = PoolToken   ('bnbnt', 'bnbnt', DEFAULT.DECIMALS, self.bnt)

        self.bntGovernance      = TokenGovernance(self.bnt)
        self.vbntGovernance     = TokenGovernance(self.vbnt)
        self.networkSettings    = NetworkSettings(self.bnt)
        self.masterVault        = Vault(self.bntGovernance, self.vbntGovernance)
        self.epVault            = Vault(self.bntGovernance, self.vbntGovernance)
        self.erVault            = Vault(self.bntGovernance, self.vbntGovernance)
        self.network            = BancorNetwork(self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.epVault, self.bnbnt)
        self.bntPool            = BNTPool(self.network, self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.bnbnt)
        self.pendingWithdrawals = PendingWithdrawals(self.network, self.bnt, self.bntPool)
        self.poolTokenFactory   = PoolTokenFactory()
        self.poolMigrator       = None
        self.poolCollection     = PoolCollection(self.network, self.bnt, self.networkSettings, self.masterVault, self.bntPool, self.epVault, self.poolTokenFactory, self.poolMigrator)
        self.standardRewards    = StandardRewards(self.network, self.networkSettings, self.bntGovernance, self.vbnt, self.bntPool)
        self.networkInfo        = BancorNetworkInfo(self.network, self.bntGovernance, self.vbntGovernance, self.networkSettings, self.masterVault, self.epVault, self.erVault, self.bntPool, self.pendingWithdrawals, self.poolMigrator)

        self.networkSettings.initialize()
        self.network.initialize(self.bntPool, self.pendingWithdrawals, self.poolMigrator)
        self.bntPool.initialize()
        self.pendingWithdrawals.initialize()
        self.poolTokenFactory.initialize()
        self.standardRewards.initialize()
        self.networkInfo.initialize()

        self.networkSettings.setWithdrawalFeePPM(toPPM(withdrawal_fee))
        self.networkSettings.setMinLiquidityForTrading(toWei(bnt_min_liquidity, self.bnt.decimals()))

        self.pendingWithdrawals.setLockDuration(cooldown_time)

        self.poolCollection.setNetworkFeePPM(toPPM(network_fee))

        self.network.registerPoolCollection(self.poolCollection)

        self.reserveTokens = {self.bnt.symbol(): self.bnt}
        self.poolTokens = {self.bnt.symbol(): self.bnbnt}
        for tkn_name, pool_params in whitelisted_tokens.items():
            tkn = ReserveToken(tkn_name, tkn_name, pool_params['decimals'])
            tkn.issue(self.epVault, toWei(pool_params['ep_vault_balance'], tkn.decimals()))
            self.networkSettings.addTokenToWhitelist(tkn)
            self.networkSettings.setFundingLimit(tkn, toWei(pool_params['bnt_funding_limit'], self.bnt.decimals()))
            self.network.createPools([tkn], self.poolCollection)
            self.poolCollection.setTradingFeePPM(tkn, toPPM(pool_params['trading_fee']))
            self.reserveTokens[tkn_name] = tkn
            self.poolTokens[tkn_name] = self.network.collectionByPool(tkn).poolToken(tkn)

        self.price_feeds = price_feeds if price_feeds is not None else read_price_feeds(price_feeds_path)

    def deposit(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        timestamp: int = 0,
        action_name="deposit",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        amt = userAmount(tkn, user_name, tkn_amt)
        tkn.connect(user_name).approve(self.network, amt)
        return self.network.connect(user_name).deposit(tkn, amt)

    def trade(
        self,
        tkn_amt: str,
        source_token: str,
        target_token: str,
        user_name: str,
        timestamp: int,
        transaction_type: str = "trade",
    ):
        updateBlock(timestamp)
        src_tkn = self.reserveTokens[source_token]
        trg_tkn = self.reserveTokens[target_token]
        src_amt = userAmount(src_tkn, user_name, tkn_amt)
        src_tkn.connect(user_name).approve(self.network, src_amt)
        return self.network.connect(user_name).tradeBySourceAmount(src_tkn, trg_tkn, src_amt, 1, uint256.max, user_name)

    def begin_cooldown(
        self,
        tkn_amt: str,
        tkn_name: str,
        user_name: str,
        timestamp: int = 0,
        by_ptkn_amt: bool = False,
        action_name: str = "begin cooldown",
    ):
        assert by_ptkn_amt, "not yet supported"
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = userAmount(tkn, user_name, tkn_amt)
        tkn.connect(user_name).approve(self.network, amt)
        if tkn is self.bnbnt: self.vbnt.connect(user_name).approve(self.network, amt)
        return self.network.connect(user_name).initWithdrawal(tkn, amt)

    def withdraw(
        self,
        user_name: str,
        id_number: int,
        timestamp: int = 0,
        transaction_type: str = "withdraw",
    ):
        updateBlock(timestamp)
        return self.network.connect(user_name).withdraw(id_number)

    def burn_pool_tokens(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        timestamp: int = 0,
        transaction_type: str = "burnPoolTokenTKN",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = userAmount(tkn, user_name, tkn_amt)
        tkn.connect(user_name).burn(amt)

    def create_standard_rewards_program(
        self,
        tkn_name: str,
        rewards_amt: str,
        start_time: int,
        end_time: int,
        timestamp: int = 0,
        transaction_type="create_standard_rewards_program",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(rewards_amt, self.bnt.decimals())
        return self.standardRewards.createProgram(tkn, amt, start_time, end_time)

    def join_standard_rewards_program(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        program_id: int,
        timestamp: int = 0,
        transaction_type="join_standard_rewards_program",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = userAmount(tkn, user_name, tkn_amt)
        tkn.connect(user_name).approve(self.standardRewards, amt)
        return self.standardRewards.connect(user_name).join(program_id, amt)

    def leave_standard_rewards_program(
        self,
        tkn_name: str,
        tkn_amt: str,
        user_name: str,
        program_id: int,
        timestamp: int = 0,
        transaction_type="leave_standard_rewards_program",
    ):
        updateBlock(timestamp)
        tkn = self.poolTokens[tkn_name]
        amt = userAmount(tkn, user_name, tkn_amt)
        return self.standardRewards.connect(user_name).leave(program_id, amt)

    def claim_standard_rewards(
        self,
        user_name: str,
        program_ids: list[int],
        timestamp: int = 0,
        transaction_type: str = "claim_standard_rewards",
    ):
        updateBlock(timestamp)
        return self.standardRewards.connect(user_name).claimRewards(program_ids)

    def set_user_balance(
        self,
        user_name: str,
        tkn_name: str,
        tkn_amt: str,
        timestamp: int = 0,
        transaction_type: str = "set user balance",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        balance = tkn.balanceOf(user_name)
        amount = toWei(tkn_amt, tkn.decimals())
        if tkn is self.bnt:
            if amount > balance:
                self.bntGovernance.mint(user_name, amount - balance)
            elif balance > amount:
                self.bntGovernance.burn(user_name, balance - amount)
        else:
            if amount > balance:
                tkn.issue(user_name, amount - balance)
            elif balance > amount:
                tkn.destroy(user_name, balance - amount)

    def set_trading_fee(
        self,
        tkn_name: str,
        percent: str,
        timestamp: int = 0,
        transaction_type: str = "set trading fee",
    ):
        updateBlock(timestamp)
        self.poolCollection.setTradingFeePPM(self.reserveTokens[tkn_name], toPPM(percent))

    def set_network_fee(
        self,
        tkn_name: str,
        percent: str,
        timestamp: int = 0,
        transaction_type: str = "set network fee",
    ):
        updateBlock(timestamp)
        self.poolCollection.setNetworkFeePPM(toPPM(percent))

    def set_withdrawal_fee(
        self,
        tkn_name: str,
        percent: str,
        timestamp: int = 0,
        transaction_type: str = "set withdrawal fee",
    ):
        updateBlock(timestamp)
        self.networkSettings.setWithdrawalFeePPM(toPPM(percent))

    def set_bnt_funding_limit(
        self,
        tkn_name: str,
        amount: str,
        timestamp: int = 0,
        transaction_type: str = "set bnt funding limit",
    ):
        updateBlock(timestamp)
        tkn = self.reserveTokens[tkn_name]
        amt = toWei(amount, self.bnt.decimals())
        self.networkSettings.setFundingLimit(tkn, amt)

    def enable_trading(
        self,
        tkn_name: str,
        timestamp: int = 0,
        transaction_type: str = "enableTrading",
    ) -> None:
        updateBlock(timestamp)
        tknPrice = self.price_feeds.at[timestamp, tkn_name]
        bntPrice = self.price_feeds.at[timestamp, self.bnt.symbol()]
        while tknPrice != int(tknPrice) or bntPrice != int(bntPrice):
            tknPrice *= 10
            bntPrice *= 10
        self.poolCollection.enableTrading(self.reserveTokens[tkn_name], tknPrice, bntPrice)

    def create_user(self, user_name: str, timestamp: int = 0):
        pass

    def describe(self, decimals: int = -1):
        table = {}

        reserveTokens = list(self.reserveTokens.values())
        poolTokens = list(self.poolTokens.values())

        # Iterate all tokens
        for token in reserveTokens + poolTokens + [self.vbnt]:
            table[token.symbol()] = {}
            for account in [user for user in token._balances.keys() if type(user) is str]:
                table[token.symbol()][tuple([1, 'Account', account])] = fromWei(token.balanceOf(account), token.decimals())

        # Iterate all reserve tokens except bnt
        for token in [reserveToken for reserveToken in reserveTokens if reserveToken is not self.bnt]:
            stakedBalance = self.networkInfo.stakedBalance(token)
            tradingLiquidity = self.networkInfo.tradingLiquidity(token)
            currentPoolFunding = self.bntPool.currentPoolFunding(token)

            spotRateN       = self.poolCollection._poolData[token].liquidity.bntTradingLiquidity
            spotRateD       = self.poolCollection._poolData[token].liquidity.baseTokenTradingLiquidity
            averageRateN    = self.poolCollection._poolData[token].averageRates.rate.n
            averageRateD    = self.poolCollection._poolData[token].averageRates.rate.d
            averageInvRateN = self.poolCollection._poolData[token].averageRates.invRate.n
            averageInvRateD = self.poolCollection._poolData[token].averageRates.invRate.d

            table[token.symbol()][tuple([2, 'Pool', 'a: TKN Staked Balance'   ])] = fromWei(stakedBalance, token.decimals())
            table[token.symbol()][tuple([2, 'Pool', 'b: TKN Trading Liquidity'])] = fromWei(tradingLiquidity.baseTokenTradingLiquidity, token.decimals())
            table[token.symbol()][tuple([2, 'Pool', 'c: BNT Trading Liquidity'])] = fromWei(tradingLiquidity.bntTradingLiquidity, self.bnt.decimals())
            table[token.symbol()][tuple([2, 'Pool', 'd: BNT Current Funding'  ])] = fromWei(currentPoolFunding, self.bnt.decimals())
            table[token.symbol()][tuple([2, 'Pool', 'e: Spot Rate'            ])] = fromFraction(spotRateN      , spotRateD      )
            table[token.symbol()][tuple([2, 'Pool', 'f: Average Rate'         ])] = fromFraction(averageRateN   , averageRateD   )
            table[token.symbol()][tuple([2, 'Pool', 'g: Average Inverse Rate' ])] = fromFraction(averageInvRateN, averageInvRateD)

        # Iterate all reserve tokens
        for token in reserveTokens:
            table[token.symbol()][tuple([3, 'Network', 'Master Vault'    ])] = fromWei(token.balanceOf(self.masterVault), token.decimals())
            table[token.symbol()][tuple([3, 'Network', 'Protection Vault'])] = fromWei(token.balanceOf(self.epVault    ), token.decimals())

        # Iterate all pool tokens
        for token in poolTokens:
            table[token.symbol()][tuple([3, 'Network', 'Rewards Vault'  ])] = fromWei(token.balanceOf(self.erVault), token.decimals())
            table[token.symbol()][tuple([3, 'Network', 'Protocol Equity'])] = fromWei(token.balanceOf(self.bntPool), token.decimals())

        df = pd.DataFrame(table).sort_index()
        return df.applymap(lambda x: round(x, decimals)) if decimals >= 0 else df

# whitelisted_tokens: list = ['bnt', 'eth', 'wbtc', 'link']
# v3 = BancorDapp(whitelisted_tokens=whitelisted_tokens)
