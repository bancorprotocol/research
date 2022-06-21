class Block:
    def __init__(self) -> None:
        self.number = 0
        self.timestamp = 0

    def set(self, **kwargs) -> None:
        self.number = kwargs.pop('number', self.number)
        self.timestamp = kwargs.pop('timestamp', self.timestamp)
