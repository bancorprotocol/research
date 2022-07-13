from bancor_research.bancor_emulator.solidity import address, revert
from bancor_research.bancor_emulator.utils import contract

'''
 * @dev this contract provides support and utilities for contract ownership
'''
class Owned(contract):
    '''
     * @dev initializes the contract
    '''
    def __init__(self) -> None:
        contract.__init__(self)

        self._owner = address(0);
        self._newOwner = address(0);

        self._setOwnership(self.msg_sender);

    '''
     * @inheritdoc IOwned
    '''
    def owner(self) -> (any):
        return self._owner;

    '''
     * @inheritdoc IOwned
    '''
    def transferOwnership(self, ownerCandidate) -> None:
        if (ownerCandidate == self._owner):
            revert("SameOwner");

        self._newOwner = ownerCandidate;

    '''
     * @inheritdoc IOwned
    '''
    def acceptOwnership(self) -> None:
        if (self.msg_sender != self._newOwner):
            revert("AccessDenied");

        self._setOwnership(self._newOwner);

    '''
     * @dev returns the address of the new owner candidate
    '''
    def newOwner(self) -> (any):
        return self._newOwner;

    '''
     * @dev sets the new owner internally
    '''
    def _setOwnership(self, ownerCandidate) -> None:
        prevOwner = self._owner;

        self._owner = ownerCandidate;
        self._newOwner = address(0);
