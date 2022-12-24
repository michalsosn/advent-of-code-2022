import collections
import fileinput


def read_input():
    elves = set()

    for y, line in enumerate(fileinput.input()):
        line = line.strip()
        for x, symbol in enumerate(line):
            if symbol == '#':
                elves.add((y, x))

    return elves


def simulate(elves, rounds):
    surrounding = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1),
    ]
    moves = [
        [(-1, -1), (-1,  0), (-1,  1)],
        [( 1, -1), ( 1,  0), ( 1,  1)],
        [(-1, -1), ( 0, -1), ( 1, -1)],
        [(-1,  1), ( 0,  1), ( 1,  1)],
    ]

    print('s', len(elves))
    for r in range(rounds):
        new_elves = set()

        active_elves = set()
        for elf in elves:
            if all((elf[0] + s[0], elf[1] + s[1]) not in elves
                   for s in surrounding):
                new_elves.add(elf)
            else:
                active_elves.add(elf)
        print('inactive', len(new_elves))
        print('active', len(active_elves))

        if not active_elves:
            print(f'no active in round {r}')
            return elves

        propositions = collections.defaultdict(int)
        for elf in active_elves:
            for move in moves:
                if all((elf[0] + m[0], elf[1] + m[1]) not in elves
                       for m in move):
                    mid = move[1]
                    new_elf = (elf[0] + mid[0], elf[1] + mid[1])
                    propositions[new_elf] += 1
                    break
        for elf in active_elves:
            for move in moves:
                if all((elf[0] + m[0], elf[1] + m[1]) not in elves
                       for m in move):
                    mid = move[1]
                    new_elf = (elf[0] + mid[0], elf[1] + mid[1])
                    if propositions[new_elf] == 1:
                        new_elves.add(new_elf)
                    else:
                        new_elves.add(elf)
                    break
            else:
                new_elves.add(elf)

        elves = new_elves
        moves = moves[1:] + [moves[0]]
        print('round', r + 1, len(elves))
    return elves


if __name__ == '__main__':
    elves = read_input()
    elves = simulate(elves, rounds=10000)

    y_min = min(elf[0] for elf in elves)
    y_max = max(elf[0] for elf in elves)
    x_min = min(elf[1] for elf in elves)
    x_max = max(elf[1] for elf in elves)
    print(y_min, y_max, x_min, x_max, len(elves))
    print((x_max - x_min + 1) * (y_max - y_min + 1) - len(elves))
