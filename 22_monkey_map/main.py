from dataclasses import dataclass
import fileinput
import re
from typing import Dict, List, Protocol


class Field:
    WALL = 0
    FLOOR = 1
    VOID = 2

    @classmethod
    def from_symbol(cls, val):
        if val == '#':
            return cls.WALL
        if val == '.':
            return cls.FLOOR
        if val == ' ':
            return cls.VOID
        raise ValueError(f'unknown symbol {val}')

    @classmethod
    def to_symbol(cls, val):
        if val == cls.WALL:
            return '#'
        if val == cls.FLOOR:
            return '.'
        if val == cls.VOID:
            return ' '
        raise ValueError(f'unknown value {val}')

    @staticmethod
    def show(fields):
        lines = []
        for row in fields:
            line = ''.join([Field.to_symbol(x) for x in row])
            lines.append(line)
        return '\n'.join(lines)


class Direction:
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

    @classmethod
    def horizontal(cls, val):
        return val in (cls.RIGHT, cls.LEFT)


@dataclass
class Position:
    y: int
    x: int
    direction: int

    def rotate(self, rotation, times=1):
        if rotation == 'R':
            self.direction = (self.direction + times) % 4
        elif rotation == 'L':
            self.direction = (self.direction - times) % 4
        else:
            raise ValueError(f'unknown rotation {rotation}')

    def step(self, steps=1):
        if self.direction == Direction.RIGHT:
            self.x += steps
        elif self.direction == Direction.LEFT:
            self.x -= steps
        elif self.direction == Direction.DOWN:
            self.y += steps
        elif self.direction == Direction.UP:
            self.y -= steps
        else:
            raise ValueError(f'invalid direction {self.direction}')

@dataclass
class Board:
    def __init__(self, fields):
        self.fields = fields

        height = len(fields) + 1
        width = max(len(row) for row in fields) + 1
        self.lft_edge = [width] * height
        self.rht_edge = [0] * height
        self.top_edge = [height] * width
        self.bot_edge = [0] * width

        for y, row in enumerate(self.fields):
            for x, cell in enumerate(row):
                if cell != Field.VOID:
                    self.lft_edge[y] = min(self.lft_edge[y], x)
                    self.rht_edge[y] = max(self.rht_edge[y], x)
                    self.top_edge[x] = min(self.top_edge[x], y)
                    self.bot_edge[x] = max(self.bot_edge[x], y)

    def first_position(self, direction=Direction.RIGHT):
        for y, row in enumerate(self.fields):
            for x, cell in enumerate(row):
                if cell == Field.FLOOR:
                    return Position(y=y, x=x, direction=direction)

    def move(self, position: Position, steps: int):
        for step in range(steps):
            position.step(steps=1)
            self.clip_plane(position)
            field = self.fields[position.y][position.x]
            if field == Field.WALL:
                print(f'HIT A WALL at {position}')
                position.step(steps=-1)
                self.clip_plane(position)
                break

    def clip_plane(self, position: Position):
        print(f'position {position}', end=' ')
        if Direction.horizontal(position.direction):
            self.clip_x(position)
        else:
            self.clip_y(position)
        print(f'clipped to {position}')

    def clip_y(self, position: Position):
        x = position.x
        min_y, max_y = self.top_edge[x], self.bot_edge[x]
        span_y = max_y - min_y + 1
        position.y = (position.y - min_y) % span_y + min_y

    def clip_x(self, position: Position):
        y = position.y
        min_x, max_x = self.lft_edge[y], self.rht_edge[y]
        span_x = max_x - min_x + 1
        position.x = (position.x - min_x) % span_x + min_x


def read_input(alt_mode=True):
    fields = []

    read_phase = 0
    for line in fileinput.input():
        line = line.rstrip()
        if line == '':
            read_phase = 1
        elif read_phase == 0:
            row = [Field.from_symbol(c) for c in line]
            fields.append(row)
        else:
            instructions = re.split("([RL])", line)

    board = Board(fields)
    return board, instructions


def simulate(board, position, instructions):
    print(f'initial position {position}')
    for instruction in instructions:
        print(f'executing {instruction}')
        if instruction.isnumeric():
            steps = int(instruction)
            board.move(position, steps)
        elif instruction == 'R' or instruction == 'L':
            position.rotate(instruction)
        else:
            raise ValueError(f'unknown instruction {instruction}')
        print(f'position {position}')

    return position


if __name__ == '__main__':
    board, instructions = read_input()
    print(Field.show(board.fields))
    print(instructions)

    position = board.first_position()
    position = simulate(board, position, instructions)
    print(position)
    print(1000 * (position.y + 1) + 4 * (position.x + 1) + position.direction)


