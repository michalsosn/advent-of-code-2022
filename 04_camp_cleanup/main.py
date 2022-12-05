import fileinput


def contains(a_start, a_end, b_start, b_end):
    return a_start <= b_start and b_end <= a_end


def either_contains(a_start, a_end, b_start, b_end):
    return contains(a_start, a_end, b_start, b_end) or \
           contains(b_start, b_end, a_start, a_end)


def overlap(a_start, a_end, b_start, b_end):
    #print(a_start, a_end, b_start, b_end)
    #print(a_end < b_start, a_start > b_end)
    return not (a_end < b_start or a_start > b_end)


def find_ranges(relation):
    count = 0

    for line in fileinput.input():
        range_a, range_b = line.split(',')
        a_start, a_end = map(int, range_a.split('-'))
        b_start, b_end = map(int, range_b.split('-'))

        if relation(a_start, a_end, b_start, b_end):
           count += 1

    print(count)


if __name__ == '__main__':
    #find_ranges(either_contains)
    find_ranges(overlap)
