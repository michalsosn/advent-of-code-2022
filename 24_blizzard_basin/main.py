import collections
from dataclasses import dataclass
import fileinput
import math
import heapq


class Field:
    FLOOR = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    UP = 4
    CLOSED = 5

    @classmethod
    def from_symbol(cls, val):
        if val == '.':
            return cls.FLOOR
        if val == '>':
            return cls.RIGHT
        if val == 'v':
            return cls.DOWN
        if val == '<':
            return cls.LEFT
        if val == '^':
            return cls.UP
        if val == '#':
            return cls.CLOSED
        raise ValueError(f'unknown symbol {val}')

    @classmethod
    def to_symbol(cls, val):
        if val == cls.FLOOR:
            return '.'
        if val == cls.RIGHT:
            return '>'
        if val == cls.DOWN:
            return 'v'
        if val == cls.LEFT:
            return '<'
        if val == cls.UP:
            return '^'
        if val == cls.CLOSED:
            return '#'
        raise ValueError(f'unknown value {val}')

    @staticmethod
    def show(fields):
        lines = []
        for row in fields:
            line = ''.join([Field.to_symbol(x) for x in row])
            lines.append(line)
        return '\n'.join(lines)


def read_input():
    fields = []

    for line in fileinput.input():
        line = line.rstrip()
        if '##' in line:
            continue
        row = [Field.from_symbol(c) for c in line[1:-1]]
        fields.append(row) 

    return fields


def generate_states(fields):
    height, width = len(fields), len(fields[0])
    state_num = math.lcm(height, width)

    states = [[[Field.FLOOR] * width for y in range(height)] 
              for t in range(state_num)]

    for y in range(height):
        for x in range(width):
            field = fields[y][x]
            if field == Field.RIGHT:
                dy, dx = 0, 1
            elif field == Field.DOWN:
                dy, dx = 1, 0
            elif field == Field.LEFT:
                dy, dx = 0, -1
            elif field == Field.UP:
                dy, dx = -1, 0
            else:
                continue

            for t in range(state_num):
                cy = (y + dy * t) % height
                cx = (x + dx * t) % width
                states[t][cy][cx] = Field.CLOSED

    return states


def find_end_time(states, min_t, start_y, start_x, end_y, end_x):
    state_num, height, width = len(states), len(states[0]), len(states[0][0])

    start_ts = []
    for t in range(min_t, state_num + min_t):
        t_mod = t % state_num
        if states[t_mod][start_y][start_x] == Field.FLOOR:
            start_ts.append(t)

    queue = []
    seen = set()

    def heuristic(t, y, x):
        return t + abs(end_y - y) + abs(end_x - x)

    def visit(t, y, x):
        t_mod = t % state_num
        if states[t_mod][y][x] != Field.FLOOR:
            return
        if (t, y, x) in seen:
            return
        #print(t, y, x)
        seen.add((t, y, x))
        w = heuristic(t, y, x)
        item = (w, t, y, x)
        heapq.heappush(queue, item)
    
    for start_t in start_ts:
        visit(start_t, start_y, start_x)
    while queue:
        _, t, y, x = heapq.heappop(queue)
        if y == end_y and x == end_x:
            return t
        if y > 0: 
            visit(t + 1, y - 1, x)
        if y < height - 1: 
            visit(t + 1, y + 1, x)
        if x > 0: 
            visit(t + 1, y, x - 1)
        if x < width - 1: 
            visit(t + 1, y, x + 1)
        visit(t + 1, y, x)


if __name__ == '__main__':
    fields = read_input()
    print(Field.show(fields))
    print()

    states = generate_states(fields)
    print('state num', len(states))

    state_num, height, width = len(states), len(states[0]), len(states[0][0])
    end0_t = find_end_time(
        states, min_t=1, start_y=0, start_x=0, end_y=height-1, end_x=width-1
    ) + 1
    print('end0_t', end0_t)
    end1_t = find_end_time(
        states, min_t=end0_t+1, start_y=height-1, start_x=width-1, end_y=0, end_x=0
    ) + 1
    print('end1_t', end1_t)
    end2_t = find_end_time(
        states, min_t=end1_t+1, start_y=0, start_x=0, end_y=height-1, end_x=width-1
    ) + 1
    print('end2_t', end2_t)
