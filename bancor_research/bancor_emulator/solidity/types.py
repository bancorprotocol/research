from . uint import uint
from collections import defaultdict

def address(obj):
    return obj

def payable(obj):
    return obj

mapping = defaultdict

for size in uint.sizes:
    exec('def uint{}(data = 0): return uint({}, data)'.format(size, size))
    exec('uint{}.max = uint{}(2 ** {} - 1)'.format(size, size, size))
