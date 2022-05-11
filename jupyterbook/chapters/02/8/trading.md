Trading
=======================

### Trading and Fees: Implementation Note

The equations depicted here describe the transition between states; not the method. In the paragraphs below, the nature
of the trades and fees on Bancor, including the Bancor Vortex is described. A portion of the swap revenue is collected
and swapped back for BNT atomically, as part of the trade. This is how the contracts behave mathematically. After the
vortex fee amount is determined, the swap function is simply called using this number as the input. The equations below
are inclusive of all steps, but aren’t featured in the code. 

