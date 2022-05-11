![IL Protection](../../../images/IL.png)

Insurance Vesting Time
=======================

The original economics paper explored a generic scenario where the impermanent loss associated with a user’s stake, and
the value thereof, is dissected using established models. The approach was deliberately simplistic, and conservative.
For a new protocol with a novel insurance mechanism, the constraints afforded benefits in its ease of communication, and
easily accessible analytics. It is from these calculations that the insurance vesting period was determined, which
protected the protocol from speculated risk during its launch phase.

These calculations have been repeated without these assumptions, using a Monte Carlo simulation method informed by data
gathered over the last 12 months of Bancor operations. The results support a far more optimistic insurance vesting
period, which can allow for the current schedule to be retired. Importantly, this creates an opportunity to remove the
most stubbornly difficult property associated with user positions, and effectively clears a path towards a
fully-fungible, composable, ecosystem within Bancor.

The assumptions made during the construction of the previous model resulted in a square root profile for the option
value over time; the option value grows very quickly on short time frames, and then flattens out over longer time
frames. The break-even point was deduced using a relative volatility of 100%, and approximate APY of 40%. Neither of
these assumptions have proved an accurate reflection of reality; however, it was from this data that the 100 day
protection threshold was founded. Under the new analysis, the situation is far less worrisome. The real option value is
practically linear, and ultimately benign, even on short time frames.  

