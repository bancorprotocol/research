# coding=utf-8

def dao_msig_init_pools(state: State, pools: list) -> State:
    """
    Function to handle the core logic.
    """
    for token_name in pools:
        if token_name != "bnt":
            state = enable_trading(state, token_name)
    return state


class BancorNetwork:
    """
    Class that provides high-level functionality for end user (e.g., in notebooks)
    """
    def dao_msig_init_pools(self, state=State, pools=None):
        """
        Method that calls the function.
        """
        if pools is None:
            pools = ['link', 'wbtc']

        return dao_msig_init_pools(state, pools)
