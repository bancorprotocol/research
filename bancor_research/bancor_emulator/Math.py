from bancor_research.bancor_emulator.solidity import uint256

'''
* @dev Standard math utilities missing in the Solidity language.
'''
class Math:
    '''
        * @dev Returns the largest of two numbers.
    '''
    def max(a, b):
        a, b = uint256(a), uint256(b)
        return a if a >= b else b;

    '''
        * @dev Returns the smallest of two numbers.
    '''
    def min(a, b):
        a, b = uint256(a), uint256(b)
        return a if a < b else b;

    '''
        * @dev Returns the average of two numbers. The result is rounded towards
        * zero.
    '''
    def average(a, b):
        # (a + b) / 2 can overflow.
        a, b = uint256(a), uint256(b)
        return (a & b) + (a ^ b) / 2;

    '''
        * @dev Returns the ceiling of the division of two numbers.
        *
        * This differs from standard division with `/` in that it rounds up instead
        * of rounding down.
    '''
    def ceilDiv(a, b):
        # (a + b - 1) / b can overflow on addition, so we distribute.
        a, b = uint256(a), uint256(b)
        return a / b + (0 if a % b == 0 else 1);
