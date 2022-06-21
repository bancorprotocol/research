class Block:
    def __init__(self) -> None:
        self.number = 0
        self.timestamp = 0

    def set(self, **kwargs) -> None:
        self.number = kwargs.get('number', self.number)
        self.timestamp = kwargs.get('timestamp', self.timestamp)
