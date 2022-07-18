from decimal import Decimal
from decimal import getcontext
from decimal import ROUND_FLOOR
from decimal import ROUND_CEILING

getcontext().prec = len(str(Decimal(2 ** 512 - 1)))

class uint:
    sizes = [(n + 1) * 8 for n in range(32)]

    def __init__(self, size, other):
        assert size in uint.sizes
        self.size = size
        self.data = uint._data(other)

    def clone(self):
        return uint(self.size, self.data)

    def floor(self):
        return self.data.to_integral_exact(rounding=ROUND_FLOOR)

    def ceil(self):
        return self.data.to_integral_exact(rounding=ROUND_CEILING)

    def __add__(self, other):
        return self._new(other, Decimal.__add__)

    def __sub__(self, other):
        return self._new(other, Decimal.__sub__)

    def __mul__(self, other):
        return self._new(other, Decimal.__mul__)

    def __truediv__(self, other):
        return self._new(other, Decimal.__truediv__)

    def __mod__(self, other):
        return self._new(other, Decimal.__mod__)

    def __pow__(self, other):
        return self._new(other, Decimal.__pow__)

    def __iadd__(self, other):
        return self._set(self + other)

    def __isub__(self, other):
        return self._set(self - other)

    def __imul__(self, other):
        return self._set(self * other)

    def __itruediv__(self, other):
        return self._set(self / other)

    def __imod__(self, other):
        return self._set(self % other)

    def __ipow__(self, other):
        return self._set(self ** other)

    def __lt__(self, other):
        return self.data < uint._data(other)

    def __le__(self, other):
        return self.data <= uint._data(other)

    def __eq__(self, other):
        return self.data == uint._data(other)

    def __ne__(self, other):
        return self.data != uint._data(other)

    def __gt__(self, other):
        return self.data > uint._data(other)

    def __ge__(self, other):
        return self.data >= uint._data(other)

    def __str__(self):
        return str(self.data)

    def __hash__(self):
        return hash(self.data)

    def _set(self, other):
        assert self.size >= other.size
        self.data = other.data
        return self

    def _new(self, other, op):
        data = op(self.data, uint._data(other))
        size = max(self.size, uint._size(other))
        return uint(size, data)

    @staticmethod
    def _data(other):
        return other.data if type(other) is uint else Decimal(other)

    @staticmethod
    def _size(other):
        return other.size if type(other) is uint else (len(hex(int(other))) - 1) // 2 * 8

class unchecked:

    @staticmethod
    def begin():
        pass

    @staticmethod
    def end():
        pass
