'''
 * @dev Library for managing
 * https:#en.wikipedia.org/wiki/Set_(abstract_data_type)[sets] of primitive
 * types.
 *
 * Sets have the following properties:
 *
 * - Elements are added, removed, and checked for existence in constant time
 * (O(1)).
 * - Elements are enumerated in O(n). No guarantees are made on the ordering.
 *
 * ```
 * contract Example {
 *     # Add the library methods
 *     using EnumerableSet for EnumerableSet.AddressSet;
 *
 *     # Declare a set state variable
 *     EnumerableSet.AddressSet private mySet;
 * }
 * ```
 *
 * As of v3.3.0, sets of type `bytes32` (`Bytes32Set`), `address` (`AddressSet`)
 * and `uint256` (`UintSet`) are supported.
'''
class EnumerableSet:
    # To implement this library for multiple types with as little code
    # repetition as possible, we write it in terms of a generic Set type with
    # bytes32 values.
    # The Set implementation uses private functions, and user-facing
    # implementations (such as AddressSet) are just wrappers around the
    # underlying Set.
    # This means that we can only create new EnumerableSets for types that fit
    # in bytes32.

    def __init__(self):
        self.set = set()

    '''
     * @dev Add a value to a set. O(1).
     *
     * Returns true if the value was added to the set, that is if it was not
     * already present.
    '''
    def add(self, value):
        if (not self.contains(value)):
            self.set.add(value);
            return True;
        else:
            return False;

    '''
     * @dev Removes a value from a set. O(1).
     *
     * Returns true if the value was removed from the set, that is if it was
     * present.
    '''
    def remove(self, value):
        if (self.contains(value)):
            self.set.remove(value);
            return True;
        else:
            return False;

    '''
     * @dev Returns true if the value is in the set. O(1).
    '''
    def contains(self, value):
        return value in self.set;

    '''
     * @dev Returns the number of values on the set. O(1).
    '''
    def length(self):
        return len(self.set);

    '''
     * @dev Returns the value stored at position `index` in the set. O(1).
     *
     * Note that there are no guarantees on the ordering of values inside the
     * array, and it may change when more values are added or removed.
     *
     * Requirements:
     *
     * - `index` must be strictly less than {length}.
    '''
    def at(self, index):
        return list(self.set)[index];

    '''
     * @dev Return the entire set in an array
     *
     * WARNING: This operation will copy the entire storage to memory, which can be quite expensive. This is designed
     * to mostly be used by view accessors that are queried without any gas fees. Developers should keep in mind that
     * this function has an unbounded cost, and using it as part of a state-changing function may render the function
     * uncallable if the set grows to a point where copying to memory consumes too much gas to fit in a block.
    '''
    def values(self):
        return list(self.set);
