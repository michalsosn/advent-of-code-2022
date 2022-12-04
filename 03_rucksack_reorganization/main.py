import fileinput


def get_priority(c):
    if c <= 'Z':
        return ord(c) - ord('A') + 27
    else:
        return ord(c) - ord('a') + 1


def find_duplicate(left, right):
    left_elems = set(left) 
    for c in right:
        if c in left_elems:
            return c


def find_rucksack_duplicates():
    result = 0

    for line in fileinput.input():
        half_len = len(line) // 2
        left, right = line[:half_len], line[half_len:]

        duplicate = find_duplicate(left, right)
        priority = get_priority(duplicate)

        result += priority

    print(result)


def find_common_element(xs, ys, zs):
    xs_elems = set(xs)
    ys_elems = set(ys)
    zs_elems = set(zs)
    intersection = xs_elems.intersection(ys_elems).intersection(zs_elems)
    return next(iter(intersection))


def find_groups_common_element():
    result = 0

    lines = list(line.strip() for line in fileinput.input())
    for i in range(0, len(lines), 3):
        sacks = lines[i:i+3]

        common = find_common_element(*sacks)
        priority = get_priority(common)

        result += priority

    print(result)


if __name__ == '__main__':
    # find_rucksack_duplicates()
    find_groups_common_element()
