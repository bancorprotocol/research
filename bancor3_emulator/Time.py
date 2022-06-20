from Types import uint, uint32

'''
 * @dev this contract abstracts the block timestamp in order to allow for more flexible control in tests
'''
class Time:
    def __init__(self, block) -> None:
        self.block = block

    '''
     * @dev returns the current time
    '''
    def _time(self) -> (uint):
        return uint32(self.block.timestamp);
