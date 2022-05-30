<p align="center">
<img width="100%" src="https://d9hhrg4mnvzow.cloudfront.net/try.bancor.network/5edb37d6-open-graph-bancor3_1000000000000000000028.png" alt="bancor3" />
</p>


# Background

Bancor is among the most overlooked and misunderstood DeFi native projects, and its complexities can leave even the
savviest DeFi natives scratching their heads. With that said, it's maintained a TVL of >$1B for over a year now, and
continues to have one of the strongest and most intellectually diverse teams in the space.

Before we dig into where Bancor is headed, we must first understand the intricacies of their past.

**A Bit About Bancor's History**


**Before there was Defi, there was Bancor** It got its name from John Maynard Keynes' currency concept, called the '
International Clearing Union' (ICU). The ICU used 'bancor' as a unit of account to encourage international trade in the
1940s. While Bancor was founded in 2016, it wasn't until February 13, 2017, that Bancor released its first whitepaper.
Fast forward four months to June 12, 2017, and, at last, the prodigal child was born. They officially launched with what
was, at the time, the largest ICO (initial coin offering) ever, raising over $153 million

Bancor is one of the founding fathers of DeFi. It all began when they noticed that the influx of tokens pouring into the
space needed a marketplace to harbor and facilitate their exchange and pricing -- somewhere safe and far away from the
constraints of a centralized monetary system. In 2016, this thought led to the creation of the AMM (Automated Market
Making) model, the crypto primitive that sparked DeFi Summer and led to the glorious bull run of 2020.

Innovation is never a straightforward task. In 2018, Bancor suffered a security breach that allowed the hacker to steal
`$10` million worth of protocol-owned BNT, `$12.5` million ETH, and `$1` million NPXS tokens. The company responded by
freezing the BNT tokens that were stolen and spoke with multiple exchanges in an attempt to track down and retrieve the
rest of the stolen tokens. Unfortunately, at the end of the day, they were only able to save the BNT, netting a total
exploit loss of `$13.5` million.

This sparked a controversy within the space. It wasn't the exploit that people were upset about- it was the team's
ability to freeze BNT whenever they wanted. That mechanism created a single point of failure and brought protocol
security into focus, something no investor wants to question. Bancor listened to the community and immediately began to
take action.

That was their first and last exploit. Since their infancy, the team not only changed their OPSEC system and removed the
BNT freeze function from the protocol, but also completely revamped their codebase. As a result, the protocol has run
smoothly with no security issues since.

**Enter Bancor v1**

Bancor invented liquidity pools, calling them "relays" or "smart tokens" at the time. The bonding curve mechanism that
we all know and love came from this, and enabled protocols like Uniswap or Sushiswap to exist in the way they do now.

Before we dive deeper into Bancor, it's essential that we take some time to emphasize how vital the AMM model truly is.

**What exactly is an Automated Market Maker(AMM)?**

An AMM is the underlying protocol that makes up decentralized exchanges (DEXs). In centralized exchanges, you have order
books managed by professional market-making entities. An AMM eliminates both the need for a custodial entity to create
markets, and the necessity for trade counter-parties.

**So what's the benefit of using an AMM?**

AMMs were created to decentralize the decision-making process of pricing different assets. With AMMs, Bancor developed
an alternative to the traditional order-book-based model and facilitated liquidity bootstrapping on-chain by utilizing
algorithmically-managed token reserves.

Gone are the days where you have to wait for a centralized exchange to provide consistent liquidity. With liquidity
pools (LP), anyone could provide trading depth using their favorite tokens, and were incentivized to do so via liquidity
mining rewards paid out from exchange fees. This created a healthy environment in which AMM liquidity pools were
mutually beneficial to both the token holders and the token issuers. New tokens were enabled to generate liquidity
without spending money on bootstrapping initial liquidity themselves, and hiring market makers to help maintain it.

**How do AMMs work?**

AMMs work by creating a bonding curve consisting of the equation x*y=k. In this formula, x represents the value of
ReserveTKN1 and y represents the value of ReserveTKN2. K remains a constant. Let's go through a mini case study to best
paint the picture of how the AMM bonding curve works.

[![](https://research.thetie.io/wp-content/uploads/2022/03/image.png)](https://research.thetie.io/wp-content/uploads/2022/03/image.png)

**AMM Equation using our example**

In this example, Bob is a Link Marine who bought his very first LINK back in 2018 and, to date, hasn't sold a single
penny's worth -- we like Bob. However, it's now early May in 2021, and Bob feels like the market will reverse soon.
Because of this, he decides to break his wedding vows and cash out some of his $LINK into something he deems is a safer
benchmark asset, like ETH. What happens in this situation is Bob is removing ETH from the LINK/ETH pool while at the
same time adding LINK to it. Our bonding curve responds to this by increasing the price of ETH and decreasing the price
of LINK in order to keep the pool balanced.

It's important to note that the AMM does not change its price based on the other markets around them. The price of an
asset inside the pool only moves as the ratio of the reserve shifts. This creates discrepancies between the price of an
asset across different AMMs, opening up arbitrage opportunities. These mispricing events are normally scooped up by
bots, but opportunities still exist on the lesser-known AMM-based DEXs for the keen investor. While AMMs have been
incredibly successful over the past few years, they do come with their own set of shortcomings.

**Being The First Has Its Perks**

![](https://research.thetie.io/wp-content/uploads/2022/03/image-2.png)

After Bancor launched their V1, they sat in a unique position to lay back and observe the world as it interacted with
DeFi. They witnessed more and more DEXs adopt their formula, and determined that the most prominent issues revolved
around slippage, forced token exposure, high network fees and the big one -- impermanent loss.

**Let's talk about slippage and why it's important**

Slippage occurs when there isn't enough liquidity to fulfill an order at the exact price it was executed. This can cause
a substantial shift in the price of an asset from the time an order is placed, to when it gets completely filled. This
is especially true when a user is trying to place a market order with relatively large size. This forces larger
investors to default to execution strategies such as TWAP(Time Weight Average Price).

Slippage can also occur when trading activity is high. This is especially true for ecosystems such as Ethereum, which
currently uses a PoW (Proof-of-Work) consensus, limiting their capability to process transactions. When executing a
trade on a DEX, your transaction is put in a queue. The longer the queue, the longer it takes for your transaction to
process on the blockchain, and the greater a chance of a disparity between the price you thought you were getting, and
the price you actually got filled at.

**Impermanent Loss**

Impermanent Loss is the difference in value between holding tokens in your wallet and a liquidity pool. Earlier in the
article, we talked about how AMMs are consistently rebalancing themselves based on token withdrawals/deposits. This
means that as prices of the reserve tokens start to fluctuate, the side that's rising is being sold by the AMM and put
into its counterparty asset in order to keep the liquidity pool at a predetermined ratio.

**Why would anyone subject themselves to IL?**

![](https://research.thetie.io/wp-content/uploads/2022/03/image-3.png)

Believe it or not, it took people a long time to wrap their heads around the idea of impermanent loss. When the idea of
being a liquidity provider started blowing up in mid-2020, it was very easy to put on rose-colored glasses and repeat
maxims like "it isn't a realized loss until I sell!". As staking grew, and all everyone cared about was "passive income"
through yield generating assets. The idea was, if the trading fees that you generate from LP were greater than your IL,
then the strategy was profitable with very little effort -- or so it was thought.

Due to the lack of transparency from DEXs on IL, there have since been multiple external studies showing the truth
behind LP profitability. Bancor and Topaz Blue published a study stating that 49.5% of LPs lose money. The Defiant found
that 52% of LPs utilizing Uniswap V3 were also unprofitable. Considering the volatility that crypto has seen over the
past 2 years, these numbers aren't the least bit surprising in hindsight.

[![](https://research.thetie.io/wp-content/uploads/2022/03/image-4.png)](https://research.thetie.io/wp-content/uploads/2022/03/image-4.png)

While IL is a natural occurrence stemming from crypto's' current state, the real innovation since has come via protocols
finding clever ways to tackle issues and improve user experience.

**A Better Model -- Enter Bancor v2.1**

As time wore down the novelty of Bancor V1, different protocols have taken the standard CPMM formula and devised their
own. Noteworthy unique approaches include Curve, which utilizes a hybrid CFMM. That said, most AMMs still have a
prescribed counterparty asset that LPs are required to contribute- think ETH (Base Asset) / USDC (Counterparty Asset).
This is extremely inconvenient for LPs, as it means they are forced to divide up asset exposure to meet the requirements
for providing liquidity inside a pool.

Bancor v2.1 addresses this issue directly by giving LPs the ability to provide liquidity to a pool while maintaining
100% exposure to a single asset(single-sided staking). Through this, Bancor **substantially** reduces slippage and
promotes extremely deep liquidity. Now, liquidity of a token dispersed between multiple pools (e.g. TKN/ETH, TKN/WETH,
TKN/LINK), all of the liquidity for a single token is concentrated into one pool.

These pools then consistently accrue fees for both LPs and the protocol. Once a user withdraws their liquidity position,
the fees earned by the protocol are then used to pay back the LPs impermanent loss. In a situation where the impermanent
loss of a pool is greater than the fees that it's generated, the protocol then mints BNT from the DAO co-investment in
order to pay back the remaining IL. At first glance, this sounds like a great way to dilute token supply, but small
changes have big consequences. In this next section, we look into BNTs tokenomics to clarify our understanding of these
effects.

**Tokenomics**

All of the features that came with the v2.1 upgrade are made possible through the utilization of BNTs elastic supply,
which allows the protocol to mint and burn BNT as it deems necessary.

Whenever a protocol wants to whitelist their token on Bancor, they need to formally make a proposal within the Bancor
DAO for BNT holders to vote on. If the proposal passes, the DAO then votes on a co-investment (in BNT) for the liquidity
pool. In this instance, the DAO is essentially given the ability to mint BNT, which is used to match user deposits into
the pool and guarantees impermanent loss insurance.

![](https://research.thetie.io/wp-content/uploads/2022/03/image-5.png)

**An Example of how this works**

Joe is looking for somewhere to earn yield on his LINK. He notices that there's a LINK pool on Bancor that allows him
to stake his LINK single-sided(LINK/BNT). Joe then proceeds to deposit $100,000 worth of LINK into that pool. The
protocol simultaneously mints an equivalent dollar amount in BNT to match Joes' position in the pool. Now, both the
protocol (Chainlink) and the user (Joe) are accruing fees.

In another scenario, if Joe withdrew his liquidity, the protocol would then burn the corresponding BNT. On paper, it
sounds like a zero-sum game, but it actually makes up a key deflationary component of Bancor v2s tokenomics. While Joe
was staking his LINK inside Bancor, the LINK/BNT pool was generating fees that were being paid out in BNT. Assuming that
the fees generated were greater than the Impermanent loss, the network would end up with more BNT than it had initially
contributed when Joe made his deposit---resulting in a deflationary system that consistently burns BNT as LPs withdraw
their position.

Since BNT is the denominated asset for pool rewards, some investors fear the consistent sell pressure that comes with
the inflationary nature of 'farm tokens'. Coupled with the other inflationary elements we've touched upon, skepticism
about effectiveness of the deflationary systems is completely warranted. While there are going to be times when
inflationary feedback loops outperform deflationary feedback loops,the aim is to have risk diversified among several
pools, resulting in an averaged net positive result.

**The Bancor Vortex & vBNT**

The Vortex launched on Feb 17th, 2021, a couple months after the release of Bancor v2.1. With its launch, it introduced
new ways for users to interact with BNT, along with a few additional deflationary features to supplement BNTs
tokenomics. This was accomplished through the use of a derivative that was introduced with this update-vBNT.

When $BNT is staked on the platform, the protocol mints vBNT at a rate of 1:1. This token represents the depositor's
share of the pool, while also offering a few additional use-cases, such as:

- Liquidity- vBNT is liquid with BNT,which is liquid with every single token on Bancor. Stakers now have the option to
  leverage their vBNT by swapping it for any platform asset.
- Governance -- vBNT is the token used to vote for protocol changes and whitelist proposals in the Bancor DAO. This
  allows staked users to vote.
- Yield -- Stakers earn yield with vBNT by staking it in the vBNT/BNT pool, securing a share of the swap fees.

Let's bring Joe back to demonstrate use cases for the Vortex, and highlight a few important nuances.

- Our friend Joe deposits 500 BNT in the LINK/BNT pool. The protocol mints 500 vBNT to represent pool share.
- Joe sees that AAVE dropped to a key support level, and thinks it's a good time to buy. So, heswaps his vBNT for $AAVE
- Joe then decides that he wants to hold onto his newly bought $AAVE for a while, and decides to use it to provide
  liquidity to the BNT/AAVE pool.
- Fast forward 12 months and now, due to all of the fees Joe has accumulated, his BNT stake has tripled and is now worth
  1500 BNT. He decides it's a good time to cash out and buy that house he's been looking at.
- In order for Joe to withdraw his LP, he needs to have the same amount of vBNT in his wallet that was given to him when
  he first deposited -in this case, 500 vBNT.
- Joe uses some USDC in his wallet to buy 500 vBNT. Hecan now withdraw his staked BNT from the LINK/BNT pool. This burns
  the 500 vBNT, and returns 1500 BNT.

Notice that despite the amount of BNT that Joe had staked in the pool tripled, the amount of vBNT he needed in his
wallet to withdraw his BNT stayed the same.

[![](https://research.thetie.io/wp-content/uploads/2022/03/image-6-1024x287.png)](https://research.thetie.io/wp-content/uploads/2022/03/image-6.png)

**Dune Chart -- if you had sold your vBNT during the summer of 2021, it would cost twice as much to buy it back at the
current vBNT price.**

While the implementation of leverage on Bancor was a great addition to the protocol, it's still leverage, and there are
always risks. Borrowing against staked BNT is effectively a bet against the vBNT/BNT peg. Cost to play s the result of
the difference between the price of vBNT at the time you swapped it compared when you buy back in.

![](https://research.thetie.io/wp-content/uploads/2022/03/image-7.png)

Bancor foresaw difficulties with the complexity of the system. Despite best efforts to emphasize risk, there were bound
to be groups of people who put on irresponsible leverage. With these users in mind, Bancor introduced a few different
deflationary tokenomics to vBNT to help offset some of the risk involved with leverage and help the protocol as a whole.

**Feel the BURN**

On April 4th, 2021, Bancor announced that Bancor Vortex Burner was officially deployed, which meant vBNT burning was
live. vBNT burns enabled:

- Increased liquidity depth, by locking a portion of every swap into the protocol.
- Reduced borrow risk, by offsetting the continuous upside pressure of vBNT with consistent burns.
- Permanent reduction in the circulating supply of BNT, by continuously buying and locking up BNT for good.
- Increased the amount of protocol-owned liquidity throughthe treasury, giving them the ability to sponsor more room for
  a liquidity pool and pay for insurance.

The full vortex going live introduced an important element in Bancor's monetary policy. Vortex enables the protocol to
adjust the burn rate of vBNT, by collecting up to 15% of swap revenues. Remember,for every vBNT that exists, there's 1
BNT equivalent. So, a consistent burn of vBNT is equivalent to locking away BNT into the protocol forever.

[![](https://research.thetie.io/wp-content/uploads/2022/03/image-8.png)](https://research.thetie.io/wp-content/uploads/2022/03/image-8.png)

It's been less than a year since the burning has started, and to date, there's been a total of `$4,314,188.26` vBNT burned
and `$7,325,296.08` BNT locked inside the protocol.

**V2.1 Limitations**

It's no question that Bancor v2.1 succeeded at delivering a solution to the limitations that came with the first
generation AMMs. While this may be true, that isn't to say that this version of the protocol didn't come with its own
limitations. We ran through a few of the key factors below:

![](https://research.thetie.io/wp-content/uploads/2022/03/image-9.png)

**Enter Bancor V3**

Bancor V3 proposes a considerable upgrade to the architecture of the protocol with the purpose of hitting all of the
primary issues present in V2 and improving user experience by introducing several new features including:

- **Instant** impermanent loss protection
- A redesigned framework for **Single Side PoolState Tokens**
- **Unlimited cap** for deposits with the introduction of "Superfluid Liquidity" and Infinity Pools
- Flash Loans
- Deeper liquidity & reduced transaction costs by using Bancor's new **Omnipool**
- **Dual-sided** reward issuance.
- Auto-compounding rewards on a **contract level**.
- **External** impermanent loss protection
- New integrations, Multichain & L2 Support, a revamped UI, **and more**.

Be on the look out for the next section of this two-part series where we break down each of these components in greater
detail.

* * * * *

This report is not investment or trading advice. Please conduct your own research before making any investment
decisions. Past performance of an asset is not indicative of future results. The Author may be holding the
cryptocurrencies or using the strategies mentioned in this report.
