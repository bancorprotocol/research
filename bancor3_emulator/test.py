from Types import uint
from Types import uint32
from Types import uint112
from Types import uint128
from Types import uint256
from Fraction import Fraction112
from Fraction import Fraction256
from Constants import PPM_RESOLUTION

def TypeName(n):
    return 'uint{}'.format(n.size) if type(n) is uint else type(n).__name__

def Print(x, op, y, z):
    print('    {}({}) {} {}({}) = {}({})'.format(TypeName(x), x, op, TypeName(y), y, TypeName(z), z))

arr = [x for xs in [[cast(n) for cast in [int, uint32, uint112, uint128, uint256]] for n in [5, 6]] for x in xs]

print('\nTest addition:')
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        Print(x, '+', y, x + y)
        assert x + y == int(x) + int(y)

print('\nTest subtraction:')
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        if x >= y:
            Print(x, '-', y, x - y)
            assert x - y == int(x) - int(y)
        else:
            try:
                Print(x, '-', y, x - y)
                raise Exception
            except AssertionError as error:
                Print(x, '-', y, 'reverted')
                assert not str(error)

print('\nTest multiplication:')
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        Print(x, '*', y, x * y)
        assert x * y == int(x) * int(y)

print('\nTest division:')
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        Print(x, '/', y, x / y)
        assert x / y == int(x) // int(y)

print('\nTest unchecked subtraction:')
uint.UNCHECKED = True
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        if x >= y:
            Print(x, '-', y, x - y)
            assert x - y == int(x) - int(y)
        else:
            Print(x, '-', y, x - y)
            assert x - y == int(x) - int(y) + 2 ** x.size
uint.UNCHECKED = False

arr = [x for xs in [[2 ** (size - 1), 2 ** size - 1, uint(size, 2 ** (size - 1)), uint(size, 2 ** size - 1)] for size in [32, 112, 128, 256]] for x in xs]

print('\nTest addition of large values:')
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        try:
            Print(x, '+', y, x + y)
        except AssertionError as error:
            Print(x, '+', y, 'reverted')
            assert not str(error) and int(x) + int(y) > 2 ** x.size - 1

print('\nTest unchecked addition of large values:')
uint.UNCHECKED = True
for x in [n for n in arr if type(n) is not int]:
    for y in arr:
        Print(x, '+', y, x + y)
        assert x + y == (int(x) + int(y)) % (2 ** x.size)
uint.UNCHECKED = False
