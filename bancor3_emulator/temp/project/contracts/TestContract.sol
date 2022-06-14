// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

contract TestContract {
    function to_uint_32 (uint256 x) external pure returns (uint32 ) {return uint32 (x);}
    function to_uint_112(uint256 x) external pure returns (uint112) {return uint112(x);}
    function to_uint_128(uint256 x) external pure returns (uint128) {return uint128(x);}
    function to_uint_256(uint256 x) external pure returns (uint256) {return uint256(x);}

    function add_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x + y;}
    function sub_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x - y;}
    function mul_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x * y;}
    function div_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x / y;}
    function add_32_112 (uint32  x, uint112 y) external pure returns (uint256) {return x + y;}
    function sub_32_112 (uint32  x, uint112 y) external pure returns (uint256) {return x - y;}
    function mul_32_112 (uint32  x, uint112 y) external pure returns (uint256) {return x * y;}
    function div_32_112 (uint32  x, uint112 y) external pure returns (uint256) {return x / y;}
    function add_32_128 (uint32  x, uint128 y) external pure returns (uint256) {return x + y;}
    function sub_32_128 (uint32  x, uint128 y) external pure returns (uint256) {return x - y;}
    function mul_32_128 (uint32  x, uint128 y) external pure returns (uint256) {return x * y;}
    function div_32_128 (uint32  x, uint128 y) external pure returns (uint256) {return x / y;}
    function add_32_256 (uint32  x, uint256 y) external pure returns (uint256) {return x + y;}
    function sub_32_256 (uint32  x, uint256 y) external pure returns (uint256) {return x - y;}
    function mul_32_256 (uint32  x, uint256 y) external pure returns (uint256) {return x * y;}
    function div_32_256 (uint32  x, uint256 y) external pure returns (uint256) {return x / y;}
    function add_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x + y;}
    function sub_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x - y;}
    function mul_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x * y;}
    function div_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x / y;}
    function add_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x + y;}
    function sub_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x - y;}
    function mul_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x * y;}
    function div_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x / y;}
    function add_112_128(uint112 x, uint128 y) external pure returns (uint256) {return x + y;}
    function sub_112_128(uint112 x, uint128 y) external pure returns (uint256) {return x - y;}
    function mul_112_128(uint112 x, uint128 y) external pure returns (uint256) {return x * y;}
    function div_112_128(uint112 x, uint128 y) external pure returns (uint256) {return x / y;}
    function add_112_256(uint112 x, uint256 y) external pure returns (uint256) {return x + y;}
    function sub_112_256(uint112 x, uint256 y) external pure returns (uint256) {return x - y;}
    function mul_112_256(uint112 x, uint256 y) external pure returns (uint256) {return x * y;}
    function div_112_256(uint112 x, uint256 y) external pure returns (uint256) {return x / y;}
    function add_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x + y;}
    function sub_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x - y;}
    function mul_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x * y;}
    function div_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x / y;}
    function add_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x + y;}
    function sub_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x - y;}
    function mul_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x * y;}
    function div_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x / y;}
    function add_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x + y;}
    function sub_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x - y;}
    function mul_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x * y;}
    function div_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x / y;}
    function add_128_256(uint128 x, uint256 y) external pure returns (uint256) {return x + y;}
    function sub_128_256(uint128 x, uint256 y) external pure returns (uint256) {return x - y;}
    function mul_128_256(uint128 x, uint256 y) external pure returns (uint256) {return x * y;}
    function div_128_256(uint128 x, uint256 y) external pure returns (uint256) {return x / y;}
    function add_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x + y;}
    function sub_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x - y;}
    function mul_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x * y;}
    function div_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x / y;}
    function add_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x + y;}
    function sub_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x - y;}
    function mul_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x * y;}
    function div_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x / y;}
    function add_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x + y;}
    function sub_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x - y;}
    function mul_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x * y;}
    function div_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x / y;}
    function add_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x + y;}
    function sub_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x - y;}
    function mul_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x * y;}
    function div_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x / y;}

    function unchecked_add_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_32_112 (uint32  x, uint112 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_32_112 (uint32  x, uint112 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_32_112 (uint32  x, uint112 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_32_112 (uint32  x, uint112 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_32_128 (uint32  x, uint128 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_32_128 (uint32  x, uint128 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_32_128 (uint32  x, uint128 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_32_128 (uint32  x, uint128 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_32_256 (uint32  x, uint256 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_32_256 (uint32  x, uint256 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_32_256 (uint32  x, uint256 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_32_256 (uint32  x, uint256 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_112_128(uint112 x, uint128 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_112_128(uint112 x, uint128 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_112_128(uint112 x, uint128 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_112_128(uint112 x, uint128 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_112_256(uint112 x, uint256 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_112_256(uint112 x, uint256 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_112_256(uint112 x, uint256 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_112_256(uint112 x, uint256 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_128_256(uint128 x, uint256 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_128_256(uint128 x, uint256 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_128_256(uint128 x, uint256 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_128_256(uint128 x, uint256 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x / y;}}
    function unchecked_add_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x + y;}}
    function unchecked_sub_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x - y;}}
    function unchecked_mul_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x * y;}}
    function unchecked_div_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x / y;}}

    function iadd_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x += y;}
    function isub_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x -= y;}
    function imul_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x *= y;}
    function idiv_32_32  (uint32  x, uint32  y) external pure returns (uint256) {return x /= y;}
    function iadd_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x += y;}
    function isub_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x -= y;}
    function imul_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x *= y;}
    function idiv_112_32 (uint112 x, uint32  y) external pure returns (uint256) {return x /= y;}
    function iadd_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x += y;}
    function isub_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x -= y;}
    function imul_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x *= y;}
    function idiv_112_112(uint112 x, uint112 y) external pure returns (uint256) {return x /= y;}
    function iadd_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x += y;}
    function isub_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x -= y;}
    function imul_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x *= y;}
    function idiv_128_32 (uint128 x, uint32  y) external pure returns (uint256) {return x /= y;}
    function iadd_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x += y;}
    function isub_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x -= y;}
    function imul_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x *= y;}
    function idiv_128_112(uint128 x, uint112 y) external pure returns (uint256) {return x /= y;}
    function iadd_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x += y;}
    function isub_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x -= y;}
    function imul_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x *= y;}
    function idiv_128_128(uint128 x, uint128 y) external pure returns (uint256) {return x /= y;}
    function iadd_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x += y;}
    function isub_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x -= y;}
    function imul_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x *= y;}
    function idiv_256_32 (uint256 x, uint32  y) external pure returns (uint256) {return x /= y;}
    function iadd_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x += y;}
    function isub_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x -= y;}
    function imul_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x *= y;}
    function idiv_256_112(uint256 x, uint112 y) external pure returns (uint256) {return x /= y;}
    function iadd_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x += y;}
    function isub_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x -= y;}
    function imul_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x *= y;}
    function idiv_256_128(uint256 x, uint128 y) external pure returns (uint256) {return x /= y;}
    function iadd_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x += y;}
    function isub_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x -= y;}
    function imul_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x *= y;}
    function idiv_256_256(uint256 x, uint256 y) external pure returns (uint256) {return x /= y;}

    function unchecked_iadd_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_32_32  (uint32  x, uint32  y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_112_32 (uint112 x, uint32  y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_112_112(uint112 x, uint112 y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_128_32 (uint128 x, uint32  y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_128_112(uint128 x, uint112 y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_128_128(uint128 x, uint128 y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_256_32 (uint256 x, uint32  y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_256_112(uint256 x, uint112 y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_256_128(uint256 x, uint128 y) external pure returns (uint256) {unchecked{return x /= y;}}
    function unchecked_iadd_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x += y;}}
    function unchecked_isub_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x -= y;}}
    function unchecked_imul_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x *= y;}}
    function unchecked_idiv_256_256(uint256 x, uint256 y) external pure returns (uint256) {unchecked{return x /= y;}}
}
