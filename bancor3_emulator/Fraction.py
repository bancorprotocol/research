from Types import uint256, uint112

class Fraction256:
    def __init__(self, f = {'n': 0, 'd': 0}) -> None:
        self.n = uint256(f['n'])
        self.d = uint256(f['d'])

class Fraction112:
    def __init__(self, f = {'n': 0, 'd': 0}) -> None:
        self.n = uint112(f['n'])
        self.d = uint112(f['d'])
