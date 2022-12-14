import fileinput
import json


def compare_numbers(left, right):
    if left < right:
        return -1
    elif left > right:
        return 1
    else:
        return 0


def compare_lists(left, right):
    for l, r in zip(left, right):
        result = compare_packets(l, r)
        if result != 0:
            return result
    return compare_numbers(len(left), len(right))


def compare_packets(left, right):
    if isinstance(left, int) and isinstance(right, int):
        return compare_numbers(left, right)
    elif isinstance(left, int):
        return compare_lists([left], right)
    elif isinstance(right, int):
        return compare_lists(left, [right])
    else:
        return compare_lists(left, right)


def load_packet_pairs():
    left = None
    right = None
    pair_i = 1
    equal_sum = 0

    for i, line in enumerate(fileinput.input()):
        line = line.strip()

        if i % 3 == 0:
            left = json.loads(line)
        elif i % 3 == 1:
            right = json.loads(line)
            if compare_packets(left, right) == -1:
                equal_sum += pair_i
        else:
            pair_i += 1

    return equal_sum


def load_packets():
    packets = []

    for i, line in enumerate(fileinput.input()):
        line = line.strip()

        if line:
            packet = json.loads(line)
            packets.append(packet)

    return packets


if __name__ == '__main__':
    # equal_sum = load_packet_pairs()
    # print(equal_sum)

    packets = load_packets()

    divisors = [[[6]], [[2]]]
    less_than_divisor_counts = [1, 0]

    for packet in packets:
        for i, divisor in enumerate(divisors):
            if compare_packets(divisor, packet) == -1:
                break
            less_than_divisor_counts[i] += 1

    result = 1
    for count in less_than_divisor_counts:
        result *= count + 1
    print(result)

