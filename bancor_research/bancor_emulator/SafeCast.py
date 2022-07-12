from bancor_research.bancor_emulator.solidity import uint, uint8, uint16, uint32, uint64 ,uint96 ,uint128 ,uint224 ,uint256, require

'''
 * @dev Wrappers over Solidity's uintXX/intXX casting operators with added overflow
 * checks.
 *
 * Downcasting from uint256/int256 in Solidity does not revert on overflow. This can
 * easily result in undesired exploitation or bugs, since developers usually
 * assume that overflows raise errors. `SafeCast` restores this intuition by
 * reverting the transaction when such an operation overflows.
 *
 * Using this library instead of the unchecked operations eliminates an entire
 * class of bugs, so it's recommended to use it always.
 *
 * Can be combined with {SafeMath} and {SignedSafeMath} to extend it to smaller types, by performing
 * all math on `uint256` and `int256` and then downcasting.
'''
class SafeCast:
    '''
     * @dev Returns the downcasted uint224 from uint256, reverting on
     * overflow (when the input is greater than largest uint224).
     *
     * Counterpart to Solidity's `uint224` operator.
     *
     * Requirements:
     *
     * - input must fit into 224 bits
    '''
    def toUint224(value) -> (uint):
        require(value <= uint224.max, "SafeCast: value doesn't fit in 224 bits");
        return uint224(value);

    '''
     * @dev Returns the downcasted uint128 from uint256, reverting on
     * overflow (when the input is greater than largest uint128).
     *
     * Counterpart to Solidity's `uint128` operator.
     *
     * Requirements:
     *
     * - input must fit into 128 bits
    '''
    def toUint128(value) -> (uint):
        require(value <= uint128.max, "SafeCast: value doesn't fit in 128 bits");
        return uint128(value);

    '''
     * @dev Returns the downcasted uint96 from uint256, reverting on
     * overflow (when the input is greater than largest uint96).
     *
     * Counterpart to Solidity's `uint96` operator.
     *
     * Requirements:
     *
     * - input must fit into 96 bits
    '''
    def toUint96(value) -> (uint):
        require(value <= uint96.max, "SafeCast: value doesn't fit in 96 bits");
        return uint96(value);

    '''
     * @dev Returns the downcasted uint64 from uint256, reverting on
     * overflow (when the input is greater than largest uint64).
     *
     * Counterpart to Solidity's `uint64` operator.
     *
     * Requirements:
     *
     * - input must fit into 64 bits
    '''
    def toUint64(value) -> (uint):
        require(value <= uint64.max, "SafeCast: value doesn't fit in 64 bits");
        return uint64(value);

    '''
     * @dev Returns the downcasted uint32 from uint256, reverting on
     * overflow (when the input is greater than largest uint32).
     *
     * Counterpart to Solidity's `uint32` operator.
     *
     * Requirements:
     *
     * - input must fit into 32 bits
    '''
    def toUint32(value) -> (uint):
        require(value <= uint32.max, "SafeCast: value doesn't fit in 32 bits");
        return uint32(value);

    '''
     * @dev Returns the downcasted uint16 from uint256, reverting on
     * overflow (when the input is greater than largest uint16).
     *
     * Counterpart to Solidity's `uint16` operator.
     *
     * Requirements:
     *
     * - input must fit into 16 bits
    '''
    def toUint16(value) -> (uint):
        require(value <= uint16.max, "SafeCast: value doesn't fit in 16 bits");
        return uint16(value);

    '''
     * @dev Returns the downcasted uint8 from uint256, reverting on
     * overflow (when the input is greater than largest uint8).
     *
     * Counterpart to Solidity's `uint8` operator.
     *
     * Requirements:
     *
     * - input must fit into 8 bits.
    '''
    def toUint8(value) -> (uint):
        require(value <= uint8.max, "SafeCast: value doesn't fit in 8 bits");
        return uint8(value);

    '''
     * @dev Converts a signed int256 into an unsigned uint256.
     *
     * Requirements:
     *
     * - input must be greater than or equal to 0.
    '''
    def toUint256(value) -> (uint):
        require(value >= 0, "SafeCast: value must be positive");
        return uint256(value);
