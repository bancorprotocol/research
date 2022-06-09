from Types import uint256, uint112

class Fraction256:
    def __init__(self) -> None:
        self.n = uint256()
        self.d = uint256()

class Fraction112:
    def __init__(self) -> None:
        self.n = uint112()
        self.d = uint112()
