import re
from dataclasses import dataclass
import fileinput


@dataclass
class Move:
    size: int
    src: int
    dst: int


def read_input():
    lines = list(fileinput.input())

    break_line = None
    for i, line in enumerate(lines):
        if line == '\n':
            break_line = i
            break

    stack_num = int(lines[break_line - 1].split()[-1])
    stacks = [[] for i in range(stack_num)]

    for line in lines[break_line - 2::-1]:
        for i, pos in enumerate(range(1, len(line), 4)):
            symbol = line[pos]
            if symbol != ' ':
                stacks[i].append(symbol)

    moves = []
    move_re = re.compile(r"move (\d+) from (\d+) to (\d+)")
    for line in lines[break_line+1:]:
        size, src, dst = move_re.match(line).groups()
        move = Move(int(size), int(src) - 1, int(dst) - 1)
        moves.append(move)

    return stacks, moves


def simulate(stacks, moves):
    for move in moves:
        stack_src = stacks[move.src]
        stack_dst = stacks[move.dst]
        size = move.size
        moved = stack_src[-size:]
        del stack_src[-size:]
        stack_dst.extend(moved)


if __name__ == '__main__':
    stacks, moves = read_input()
    print(stacks)
    # print(moves)
    simulate(stacks, moves)
    print(stacks)

    print(''.join([stack[-1] for stack in stacks]))
