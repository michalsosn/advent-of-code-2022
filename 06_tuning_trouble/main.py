from collections import defaultdict
# import fileinput


def find_unique_window(signal, target_size):
    last_seen_map = defaultdict(lambda: -1)

    unique_seq_start = 0
    for i, c in enumerate(signal):
        last_seen_i = last_seen_map[c]
        last_seen_map[c] = i
        unique_seq_start = max(unique_seq_start, last_seen_i + 1)
        unique_seq_size = i - unique_seq_start + 1
        if unique_seq_size >= target_size:
            return i + 1


if __name__ == '__main__':
    line = input().strip()
    pos = find_unique_window(signal=line, target_size=4)
    print(pos)
    pos = find_unique_window(signal=line, target_size=14)
    print(pos)
