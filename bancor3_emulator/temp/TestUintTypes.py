import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from solidity import uint
from solidity import uint32
from solidity import uint112
from solidity import uint128
from solidity import uint256
from solidity import unchecked

for n in [0, 2, 32, 112, 128, 256]:
    for k in [-1, 0, +1]:
        x = 2 ** n + k
        for cast in [uint32, uint112, uint128, uint256]:
            y = cast(x)
            print('{}({}) = {}'.format(cast.__name__, x, int(y)))
            assert y.size == int(cast.__name__[4:])
            assert int(y) == x & (2 ** y.size - 1)
            assert y == cast(y) == uint256(y)

def checked_add(x, y): return x + y
def checked_sub(x, y): return x - y
def checked_mul(x, y): return x * y
def checked_div(x, y): return x / y if type(x) is uint else x // y

def unchecked_add(x, y): unchecked.begin(); z = x + y; unchecked.end(); return z
def unchecked_sub(x, y): unchecked.begin(); z = x - y; unchecked.end(); return z
def unchecked_mul(x, y): unchecked.begin(); z = x * y; unchecked.end(); return z
def unchecked_div(x, y): unchecked.begin(); z = x / y if type(x) is uint else x // y; unchecked.end(); return z

checked_ops = {
    '+': checked_add,
    '-': checked_sub,
    '*': checked_mul,
    '/': checked_div,
}

unchecked_ops = {
    '+': unchecked_add,
    '-': unchecked_sub,
    '*': unchecked_mul,
    '/': unchecked_div,
}

def TypeName(n):
    return 'uint{}'.format(n.size) if type(n) is uint else type(n).__name__

def Print(op, x, y, z):
    print('    {}({}) {} {}({}) = {}({})'.format(TypeName(x), x, op, TypeName(y), y, TypeName(z), z))

arr = [1, 2]
for size in [32, 112, 128, 256]:
    arr.append(2 ** (size - 1) - 1)
    arr.append(2 ** (size - 1) - 0)
    arr.append(2 ** (size - 0) - 2)
    arr.append(2 ** (size - 0) - 1)
    arr.append(uint(size, 2 ** (size - 1) - 1))
    arr.append(uint(size, 2 ** (size - 1) - 0))
    arr.append(uint(size, 2 ** (size - 0) - 2))
    arr.append(uint(size, 2 ** (size - 0) - 1))
    arr.append(uint(size, 2))
    arr.append(uint(size, 1))
arr.sort(key=uint256)

ops = checked_ops
for op in ops.keys():
    print('Test {}:'.format(op))
    for x in [n for n in arr if type(n) is not int]:
        for y in arr:
            try:
                z = ops[op](x, y)
                Print(op, x, y, z)
                assert int(z) == ops[op](int(x), int(y)), 'arithmetic error'
            except AssertionError as error:
                Print(op, x, y, 'reverted')
                assert not str(error)
                assert not (0 <= ops[op](int(x), int(y)) <= 2 ** x.size - 1), 'logical error'

ops = unchecked_ops
for op in ops.keys():
    print('Test unchecked {}:'.format(op))
    for x in [n for n in arr if type(n) is not int]:
        for y in arr:
            z = ops[op](x, y)
            Print(op, x, y, z)
            assert int(z) == ops[op](int(x), int(y)) % 2 ** max(uint._size(x), uint._size(y)), 'arithmetic error'

print('Test +=')
for n in [0, 2, 32, 112, 128, 256]:
    for k in [-1, 0, +1]:
        m = 2 ** n + k
        for lcast in [uint32, uint112, uint128, uint256]:
            for rcast in [uint32, uint112, uint128, uint256]:
                print('    {}({}) += {}({})'.format(lcast.__name__, m, rcast.__name__, m))
                x = lcast(m)
                try:
                    x += rcast(m)
                    assert x == int(lcast(m)) + int(rcast(m)), 'arithmetic error'
                except AssertionError as error:
                    assert not str(error)
                    assert x.size < max(rcast(m).size, len(bin(m + m)) - 2), 'logical error'

unchecked.begin()
print('Test unchecked +=')
for n in [0, 2, 32, 112, 128, 256]:
    for k in [-1, 0, +1]:
        m = 2 ** n + k
        for lcast in [uint32, uint112, uint128, uint256]:
            for rcast in [uint32, uint112, uint128, uint256]:
                print('    {}({}) += {}({})'.format(lcast.__name__, m, rcast.__name__, m))
                x = lcast(m)
                try:
                    x += rcast(m)
                    assert x == (int(lcast(m)) + int(rcast(m))) % 2 ** x.size, 'arithmetic error'
                except AssertionError as error:
                    assert not str(error)
                    assert x.size < max(rcast(m).size, len(bin(m + m)) - 2), 'logical error'
unchecked.end()

print('Test *=')
for n in [0, 2, 32, 112, 128, 256]:
    for k in [-1, 0, +1]:
        m = 2 ** n + k
        for lcast in [uint32, uint112, uint128, uint256]:
            for rcast in [uint32, uint112, uint128, uint256]:
                print('    {}({}) *= {}({})'.format(lcast.__name__, m, rcast.__name__, m))
                x = lcast(m)
                try:
                    x *= rcast(m)
                    assert x == int(lcast(m)) * int(rcast(m)), 'arithmetic error'
                except AssertionError as error:
                    assert not str(error)
                    assert x.size < max(rcast(m).size, len(bin(m * m)) - 2), 'logical error'

unchecked.begin()
print('Test unchecked *=')
for n in [0, 2, 32, 112, 128, 256]:
    for k in [-1, 0, +1]:
        m = 2 ** n + k
        for lcast in [uint32, uint112, uint128, uint256]:
            for rcast in [uint32, uint112, uint128, uint256]:
                print('    {}({}) *= {}({})'.format(lcast.__name__, m, rcast.__name__, m))
                x = lcast(m)
                try:
                    x *= rcast(m)
                    assert x == (int(lcast(m)) * int(rcast(m))) % 2 ** x.size, 'arithmetic error'
                except AssertionError as error:
                    assert not str(error)
                    assert x.size < max(rcast(m).size, len(bin(m * m)) - 2), 'logical error'
unchecked.end()