from bancor_research.bancor_emulator.solidity import uint256, uint112
from bancor_research.bancor_emulator.utils import parse

class Fraction:
    def __init__(self, cast, f) -> None:
        self.n = parse(cast, f, 'n')
        self.d = parse(cast, f, 'd')

    def __str__(self) -> str:
        return '{} / {}'.format(self.n, self.d)

class Fraction256(Fraction):
    def __init__(self, f) -> None:
        super().__init__(uint256, f)

class Fraction112(Fraction):
    def __init__(self, f) -> None:
        super().__init__(uint112, f)
