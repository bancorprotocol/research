from bancor_research.bancor_emulator.solidity import uint, uint256, unchecked, mapping
from bancor_research.bancor_emulator.utils import contract

'''
 * @dev Implementation of the {IERC20} interface.
 *
 * This implementation is agnostic to the way tokens are created. This means
 * that a supply mechanism has to be added in a derived contract using {_mint}.
 * For a generic mechanism see {ERC20PresetMinterPauser}.
 *
 * TIP: For a detailed writeup see our guide
 * https://forum.zeppelin.solutions/t/how-to-implement-erc20-supply-mechanisms/226[How
 * to implement supply mechanisms].
 *
 * We have followed general OpenZeppelin Contracts guidelines: functions revert
 * instead returning `false` on failure. This behavior is nonetheless
 * conventional and does not conflict with the expectations of ERC20
 * applications.
 *
 * Additionally, an {Approval} event is emitted on calls to {transferFrom}.
 * This allows applications to reconstruct the allowance for all accounts just
 * by listening to said events. Other implementations of the EIP may not emit
 * these events, as it isn't required by the specification.
 *
 * Finally, the non-standard {decreaseAllowance} and {increaseAllowance * functions have been added to mitigate the well-known issues around setting
 * allowances. See {IERC20-approve}.
'''
class ERC20(contract):
    '''
     * @dev Sets the values for {name} and {symbol}.
     *
     * The default value of {decimals} is 18. To select a different value for
     * {decimals} you should overload it.
     *
     * All two of these values are immutable: they can only be set once during
     * construction.
    '''
    def __init__(self, name_: str, symbol_: str) -> None:
        contract.__init__(self)

        self._name = name_;
        self._symbol = symbol_;
        self._balances = mapping(lambda: uint256());
        self._allowances = mapping(lambda: mapping(lambda: uint256()));
        self._totalSupply = uint256();

    '''
     * @dev Returns the name of the token.
    '''
    def name(self) -> (str):
        return self._name;

    '''
     * @dev Returns the symbol of the token, usually a shorter version of the
     * name.
    '''
    def symbol(self) -> (str):
        return self._symbol;

    '''
     * @dev Returns the number of decimals used to get its user representation.
     * For example, if `decimals` equals `2`, a balance of `505` tokens should
     * be displayed to a user as `5.05` (`505 / 10 ** 2`).
     *
     * Tokens usually opt for a value of 18, imitating the relationship between
     * Ether and Wei. This is the value {ERC20} uses, unless this def is
     * overridden;
     *
     * NOTE: This information is only used for _display_ purposes: it in
     * no way affects any of the arithmetic of the contract, including
     * {IERC20-balanceOf} and {IERC20-transfer}.
    '''
    def decimals(self) -> (int):
        return 18;

    '''
     * @dev See {IERC20-totalSupply}.
    '''
    def totalSupply(self) -> (uint):
        return self._totalSupply.clone();

    '''
     * @dev See {IERC20-balanceOf}.
    '''
    def balanceOf(self, account) -> (uint):
        return self._balances[account].clone();

    '''
     * @dev See {IERC20-transfer}.
     *
     * Requirements:
     *
     * - `to` cannot be the zero address.
     * - the caller must have a balance of at least `amount`.
    '''
    def transfer(self, to, amount) -> (bool):
        owner = self.msg_sender;
        self._transfer(owner, to, amount);
        return True;

    '''
     * @dev See {IERC20-allowance}.
    '''
    def allowance(self, owner, spender) -> (uint):
        return self._allowances[owner][spender].clone();

    '''
     * @dev See {IERC20-approve}.
     *
     * NOTE: If `amount` is the maximum `uint256`, the allowance is not updated on
     * `transferFrom`. This is semantically equivalent to an infinite approval.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
    '''
    def approve(self, spender, amount) -> (bool):
        owner = self.msg_sender;
        self._approve(owner, spender, amount);
        return True;

    '''
     * @dev See {IERC20-transferFrom}.
     *
     * Emits an {Approval} event indicating the updated allowance. This is not
     * required by the EIP. See the note at the beginning of {ERC20}.
     *
     * NOTE: Does not update the allowance if the current allowance
     * is the maximum `uint256`.
     *
     * Requirements:
     *
     * - `from` and `to` cannot be the zero address.
     * - `from` must have a balance of at least `amount`.
     * - the caller must have allowance for ``from``'s tokens of at least
     * `amount`.
    '''
    def transferFrom(self,
        from_,
        to,
        amount
    ) -> (bool):
        spender = self.msg_sender;
        self._spendAllowance(from_, spender, amount);
        self._transfer(from_, to, amount);
        return True;

    '''
     * @dev Atomically increases the allowance granted to `spender` by the caller.
     *
     * This is an alternative to {approve} that can be used as a mitigation for
     * problems described in {IERC20-approve}.
     *
     * Emits an {Approval} event indicating the updated allowance.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
    '''
    def increaseAllowance(self, spender, addedValue) -> (bool):
        owner = self.msg_sender;
        self._approve(owner, spender, self._allowances[owner][spender] + addedValue);
        return True;

    '''
     * @dev Atomically decreases the allowance granted to `spender` by the caller.
     *
     * This is an alternative to {approve} that can be used as a mitigation for
     * problems described in {IERC20-approve}.
     *
     * Emits an {Approval} event indicating the updated allowance.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     * - `spender` must have allowance for the caller of at least
     * `subtractedValue`.
    '''
    def decreaseAllowance(self, spender, subtractedValue) -> (bool):
        owner = self.msg_sender;
        currentAllowance = self._allowances[owner][spender];
        assert currentAllowance >= subtractedValue, "ERC20: decreased allowance below zero";
        unchecked.begin()
        self._approve(owner, spender, currentAllowance - subtractedValue);
        unchecked.end()

        return True;

    '''
     * @dev Moves `amount` of tokens from `sender` to `recipient`.
     *
     * This internal def is equivalent to {transfer}, and can be used to
     * e.g. implement automatic token fees, slashing mechanisms, etc.
     *
     * Emits a {Transfer} event.
     *
     * Requirements:
     *
     * - `from` cannot be the zero address.
     * - `to` cannot be the zero address.
     * - `from` must have a balance of at least `amount`.
    '''
    def _transfer(self,
        from_,
        to,
        amount
    ):
        fromBalance = self._balances[from_];
        assert fromBalance >= amount, "ERC20: transfer amount exceeds balance";
        unchecked.begin()
        self._balances[from_] = fromBalance - amount;
        unchecked.end()
        self._balances[to] += amount;

    ''' @dev Creates `amount` tokens and assigns them to `account`, increasing
     * the total supply.
     *
     * Emits a {Transfer} event with `from` set to the zero address.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
    '''
    def _mint(self, account, amount):
        self._totalSupply += amount;
        self._balances[account] += amount;

    '''
     * @dev Destroys `amount` tokens from `account`, reducing the
     * total supply.
     *
     * Emits a {Transfer} event with `to` set to the zero address.
     *
     * Requirements:
     *
     * - `account` cannot be the zero address.
     * - `account` must have at least `amount` tokens.
    '''
    def _burn(self, account, amount):
        accountBalance = self._balances[account];
        assert accountBalance >= amount, "ERC20: burn amount exceeds balance";
        unchecked.begin()
        self._balances[account] = accountBalance - amount;
        unchecked.end()
        self._totalSupply -= amount;

    '''
     * @dev Sets `amount` as the allowance of `spender` over the `owner` s tokens.
     *
     * This internal def is equivalent to `approve`, and can be used to
     * e.g. set automatic allowances for certain subsystems, etc.
     *
     * Emits an {Approval} event.
     *
     * Requirements:
     *
     * - `owner` cannot be the zero address.
     * - `spender` cannot be the zero address.
    '''
    def _approve(self,
        owner,
        spender,
        amount
    ):
        self._allowances[owner][spender] = uint256(amount);

    '''
     * @dev Spend `amount` form the allowance of `owner` toward `spender`.
     *
     * Does not update the allowance amount in case of infinite allowance.
     * Revert if not enough allowance is available.
     *
     * Might emit an {Approval} event.
    '''
    def _spendAllowance(self,
        owner,
        spender,
        amount
    ):
        currentAllowance = self.allowance(owner, spender);
        if (currentAllowance != uint256.max):
            assert currentAllowance >= amount, "ERC20: insufficient allowance";
            unchecked.begin()
            self._approve(owner, spender, currentAllowance - amount);
            unchecked.end()
