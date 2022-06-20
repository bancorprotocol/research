from Types import uint, uint32

'''
 * @dev this contract abstracts the block number in order to allow for more flexible control in tests
'''
class BlockNumber:
    def __init__(self, block) -> None:
        self.block = block

    '''
     * @dev returns the current block-number
    '''
    def _blockNumber(self) -> (uint):
        return uint32(self.block.number);
