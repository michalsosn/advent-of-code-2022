import collections
from dataclasses import dataclass
import fileinput
import math
import heapq


def code_to_num(code):
    base = 5
    code_values = {
        '=': -2, '-': -1, '0': 0, '1': 1, '2': 2
    }
    result = 0
    for c in code:
        val = code_values[c]
        result = result * base + val
    return result


def num_to_code(num):
    if num == 0:
        return '0'

    base = 5
    value_codes = {
        -2: '=', -1: '-', 0: '0', 1: '1', 2: '2'
    }

    digits = []
    carry = 0
    while num > 0:
        val = num % 5 + carry
        num //= 5
        carry = 0

        while val > 2:
            val -= 5
            carry += 1

        digit = value_codes[val]
        digits.append(digit)

    return ''.join(digits[::-1])


if __name__ == '__main__':
    total_num = 0
    for line in fileinput.input():
        code = line.strip()
        num = code_to_num(code)
        print(code, num)
        total_num += num
    total_code = num_to_code(total_num)
    print(total_num, total_code)
