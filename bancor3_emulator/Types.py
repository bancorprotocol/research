FIXED_POINT = True

def uint256(val = 0): return uint(True, 256, val)
def uint128(val = 0): return uint(True, 128, val)
def uint112(val = 0): return uint(True, 112, val)
def uint32 (val = 0): return uint(True,  32, val)

def unsafe_uint256(val = 0): return uint(False, 256, val)
def unsafe_uint128(val = 0): return uint(False, 128, val)
def unsafe_uint112(val = 0): return uint(False, 112, val)
def unsafe_uint32 (val = 0): return uint(False,  32, val)

class uint:
    def __init__(self, safe: bool, size: int, other) -> None:
        self.safe = safe
        self.size = size
        self.val = uint._check(safe, size, other.val if type(other) is uint else other)

    def __add__(self, other):
        return uint(self.safe, self.size, self.val + uint(self.safe, self.size, other).val)

    def __sub__(self, other):
        return uint(self.safe, self.size, self.val - uint(self.safe, self.size, other).val)

    def __mul__(self, other):
        return uint(self.safe, self.size, self.val * uint(self.safe, self.size, other).val)

    def __truediv__(self, other):
        return uint(self.safe, self.size, self.val // uint(self.safe, self.size, other).val if FIXED_POINT else self.val / uint(self.safe, self.size, other).val)

    def __mod__(self, other):
        return uint(self.safe, self.size, self.val % uint(self.safe, self.size, other).val)

    def __lshift__(self, other):
        return uint(self.safe, self.size, self.val << uint(self.safe, self.size, other).val)

    def __rshift__(self, other):
        return uint(self.safe, self.size, self.val >> uint(self.safe, self.size, other).val)

    def __and__(self, other):
        return uint(self.safe, self.size, self.val & uint(self.safe, self.size, other).val)

    def __xor__(self, other):
        return uint(self.safe, self.size, self.val ^ uint(self.safe, self.size, other).val)

    def __or__(self, other):
        return uint(self.safe, self.size, self.val | uint(self.safe, self.size, other).val)

    def __lt__(self, other):
        return self.val < uint(self.safe, self.size, other).val

    def __le__(self, other):
        return self.val <= uint(self.safe, self.size, other).val

    def __eq__(self, other):
        return self.val == uint(self.safe, self.size, other).val

    def __ne__(self, other):
        return self.val != uint(self.safe, self.size, other).val

    def __gt__(self, other):
        return self.val > uint(self.safe, self.size, other).val

    def __ge__(self, other):
        return self.val >= uint(self.safe, self.size, other).val

    def __int__(self):
        return int(self.val)

    def __str__(self):
        return str(self.val)

    @staticmethod
    def _check(safe: bool, size: int, val: int) -> int:
        if safe:
            assert 0 <= val <= 2 ** size - 1
            return val
        return val & (2 ** size - 1)
