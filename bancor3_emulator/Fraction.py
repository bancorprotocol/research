from Solidity import uint256, uint112

class Fraction:
    def __init__(self, cast, f) -> None:
        self.n = cast(f['n'])
        self.d = cast(f['d'])
    def __str__(self) -> str:
        return '{} / {}'.format(int(self.n), int(self.d))

class Fraction256(Fraction):
    def __init__(self, f = {'n': 0, 'd': 0}) -> None:
        super().__init__(uint256, f)

class Fraction112(Fraction):
    def __init__(self, f = {'n': 0, 'd': 0}) -> None:
        super().__init__(uint112, f)
