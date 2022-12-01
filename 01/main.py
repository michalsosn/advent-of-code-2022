import fileinput
import heapq


def main():
    top_sums = [0] * 3
    cur_sum = 0

    for line in fileinput.input():
        if line == '\n':
            heapq.heappushpop(top_sums, cur_sum)
            cur_sum = 0
        else:
            cur_sum += int(line)

    print(f'sum({top_sums}) = {sum(top_sums)}')


if __name__ == '__main__':
    main()
