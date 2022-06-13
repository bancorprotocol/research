from Types import uint
from Types import uint256

def add(x, y): return x + y
def sub(x, y): return x - y
def mul(x, y): return x * y
def div(x, y): return x / y if type(x) is uint else x // y

ops = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': div,
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

uint.UNCHECKED = True
for op in ops.keys():
    print('Test unchecked {}:'.format(op))
    for x in [n for n in arr if type(n) is not int]:
        for y in arr:
            z = ops[op](x, y)
            Print(op, x, y, z)
            assert int(z) == ops[op](int(x), int(y)) % 2 ** max(uint._size(x), uint._size(y)), 'arithmetic error'
uint.UNCHECKED = False
