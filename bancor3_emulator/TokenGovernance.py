# @title The Token Governance contract is used to govern a mintable ERC20 token by restricting its launch-time initial
# administrative privileges.
class TokenGovernance:
    # @dev Initializes the contract.
    #
    # @param mintableToken The address of the mintable ERC20 token.
    def __init__(self, mintableToken):
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
    def burn(self, _msgSender, amount):
        self._token.destroy(_msgSender, amount);

    def token(self):
        return self._token;
