from . types import uint256

def addmod(x, y, k):
    return uint256((int(x) + int(y)) % int(k))

def mulmod(x, y, k):
    return uint256((int(x) * int(y)) % int(k))
