from bancor_research.bancor_emulator.solidity import uint, uint32, block

'''
 * @dev this contract abstracts the block timestamp in order to allow for more flexible control in tests
'''
class Time:
    '''
     * @dev returns the current time
    '''
    def _time(self) -> (uint):
        return uint32(block.timestamp);
