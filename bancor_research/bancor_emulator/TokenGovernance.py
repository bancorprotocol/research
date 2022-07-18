from bancor_research.bancor_emulator.utils import contract

# @title The Token Governance contract is used to govern a mintable ERC20 token by restricting its launch-time initial
# administrative privileges.
class TokenGovernance(contract):
    # @dev Initializes the contract.
    #
    # @param mintableToken The address of the mintable ERC20 token.
    def __init__(self, mintableToken):
        contract.__init__(self)

        self._token = mintableToken;

    # @dev Mints new tokens. Only allowed by the MINTER role.
    #
    # @param to Account to receive the new amount.
    # @param amount Amount to increase the supply by.
    #
    def mint(self, to, amount):
        self._token.issue(to, amount);

    # @dev Burns tokens from the caller.
    #
    # @param amount Amount to decrease the supply by.
    #
    def burn(self, amount):
        self._token.destroy(self.msg_sender, amount);

    def token(self):
        return self._token;
