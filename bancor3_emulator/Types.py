def uint256(data = 0): return uint(256, data)
def uint128(data = 0): return uint(128, data)
def uint112(data = 0): return uint(112, data)
def uint32 (data = 0): return uint( 32, data)

class uint:
    UNCHECKED = False

    def __init__(self, size, other):
        self.size = size
        self.data = uint._get(self, other)

    def __add__(self, other):
        return uint(self.size, self.data + uint._get(self, other))

    def __sub__(self, other):
        return uint(self.size, self.data - uint._get(self, other))

    def __mul__(self, other):
        return uint(self.size, self.data * uint._get(self, other))

    def __truediv__(self, other):
        return uint(self.size, self.data // uint._get(self, other))

    def __mod__(self, other):
        return uint(self.size, self.data % uint._get(self, other))

    def __lshift__(self, other):
        return uint(self.size, self.data << uint._get(self, other))

    def __rshift__(self, other):
        return uint(self.size, self.data >> uint._get(self, other))

    def __and__(self, other):
        return uint(self.size, self.data & uint._get(self, other))

    def __xor__(self, other):
        return uint(self.size, self.data ^ uint._get(self, other))

    def __or__(self, other):
        return uint(self.size, self.data | uint._get(self, other))

    def __lt__(self, other):
        return self.data < uint._get(self, other)

    def __le__(self, other):
        return self.data <= uint._get(self, other)

    def __eq__(self, other):
        return self.data == uint._get(self, other)

    def __ne__(self, other):
        return self.data != uint._get(self, other)

    def __gt__(self, other):
        return self.data > uint._get(self, other)

    def __ge__(self, other):
        return self.data >= uint._get(self, other)

    def __int__(self):
        return int(self.data)

    def __str__(self):
        return str(self.data)

    @staticmethod
    def _get(this, other):
        data = other.data if type(other) is uint else other
        if uint.UNCHECKED:
            return data & (2 ** this.size - 1)
        assert 0 <= data <= 2 ** this.size - 1
        return data
