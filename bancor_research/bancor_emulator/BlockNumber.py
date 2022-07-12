from bancor_research.bancor_emulator.solidity import uint, uint32, block

'''
 * @dev this contract abstracts the block number in order to allow for more flexible control in tests
'''
class BlockNumber:
    '''
     * @dev returns the current block-number
    '''
    def _blockNumber(self) -> (uint):
        return uint32(block.number);
