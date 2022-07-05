import inspect

class uint:
    sizes = [(n + 1) * 8 for n in range(32)]

    def __init__(self, size, other):
        assert size in uint.sizes
        self.size = size
        self.data = uint._data(other) % 2 ** size

    def clone(self):
        return uint(self.size, self.data)

    def __add__(self, other):
        return self._new(other, int.__add__)

    def __sub__(self, other):
        return self._new(other, int.__sub__)

    def __mul__(self, other):
        return self._new(other, int.__mul__)

    def __truediv__(self, other):
        return self._new(other, int.__floordiv__)

    def __mod__(self, other):
        return self._new(other, int.__mod__)

    def __lshift__(self, other):
        return self._new(other, int.__lshift__)

    def __rshift__(self, other):
        return self._new(other, int.__rshift__)

    def __and__(self, other):
        return self._new(other, int.__and__)

    def __xor__(self, other):
        return self._new(other, int.__xor__)

    def __or__(self, other):
        return self._new(other, int.__or__)

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

    def __ilshift__(self, other):
        return self._set(self << other)

    def __irshift__(self, other):
        return self._set(self >> other)

    def __iand__(self, other):
        return self._set(self & other)

    def __ixor__(self, other):
        return self._set(self ^ other)

    def __ior__(self, other):
        return self._set(self | other)

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

    def __int__(self):
        return int(self.data)

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
        assert unchecked.scope() or 0 <= data <= 2 ** size - 1
        return uint(size, data)

    @staticmethod
    def _data(other):
        return other.data if type(other) is uint else int(other)

    @staticmethod
    def _size(other):
        return other.size if type(other) is uint else (len(hex(other)) - 1) // 2 * 8

class unchecked:
    stack = []

    @staticmethod
    def begin():
        unchecked.stack.append(unchecked._depth())

    @staticmethod
    def end():
        unchecked.stack.pop()

    @staticmethod
    def scope():
        return len(unchecked.stack) > 0 and unchecked.stack[-1] == unchecked._depth()

    @staticmethod
    def _depth():
        return sum(frame_info.filename != __file__ for frame_info in inspect.stack(0))
