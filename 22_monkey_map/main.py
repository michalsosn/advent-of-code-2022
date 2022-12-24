import collections
from dataclasses import dataclass
import fileinput
import math
import numpy as np
import re

class Rotation:
    RIGHT = 'R'
    LEFT = 'L'


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


class Position:
    ROTATION_CW = np.array([[0, 1], [-1, 0]])
    ROTATION_CCW = np.array([[0, -1], [1, 0]])

    def __init__(self, coords, direction, side):
        self.coords = coords
        self.direction = direction
        self.side = side

    @staticmethod
    def initial(x, y):
        return Position(
            coords=np.array([x, y, -1]),    # one is = -1 or size
            direction=np.array([1, 0, 0]),  # e.g. [0, 1, 0] or [0, -1, 0]
            side=np.array([0, 0, 1])
        )

    def copy(self):
        return Position(
            coords=self.coords.copy(),
            direction=self.direction.copy(),
            side=self.side.copy()
        )

    def __repr__(self):
        return f'Position(coords={self.coords}, direction={self.direction}, side={self.side})'

    def side_ix(self):
        return (np.flatnonzero(self.side)[0] + 1) * self.side.sum()

    def rotate(self, rotation, times=1):
        if times < 0:
            times = -times
            rotation = Rotation.LEFT if rotation == Rotation.RIGHT else Rotation.RIGHT

        print(f'rotation {self} {rotation} {times} times')
        if (rotation == Rotation.RIGHT) == (self.side[0] == 1 or self.side[1] == -1 or self.side[2] == 1):
            # y side is inverted bc we should rotate axes in order [z, x], not [x, z]
            rotation_m = self.ROTATION_CW
        else:
            rotation_m = self.ROTATION_CCW

        for i in range(times):
            self.direction[self.side == 0] = self.direction[self.side == 0] @ rotation_m
        print(f'rotated {self}')

    def step(self, size, times=1):
        print(f'move {self}')
        for i in range(times):
            self.coords[:] += self.direction
            self.clip_cube(size)
        print(f'moved {self}')

    def clip_cube(self, size):
        on_side = self.coords[self.side == 0]
        if (0 <= on_side).all() and (on_side < size).all():
            return
        print(f'cut from {self}')
        # np. p[4 0 -1] d[1 0 0] s[0 0 1] -> p[4 0 0] d[0 0 -1] s[-1 0 0]
        # np. p[-1 0 -1] d[-1 0 0] s[0 0 1] -> p[-1 0 0] d[0 0 -1] s[1 0 0]
        # np. p[0 4 -1] d[0 1 0] s[0 0 1] -> p[0 4 0] d[0 0 -1] s[0 -1 0]
        self.coords[:] += self.side
        self.direction = self.side
        self.side = (self.coords == size).astype(int) * -1 \
                  + (self.coords == -1).astype(int) 
        print(f'cut to {self}')


@dataclass
class RegionMapping:
    texture_y: int
    texture_x: int
    cube_position: Position
    #y_to_coord_a: np.ndarray
    #y_to_coord_b: np.ndarray
    #x_to_coord_a: np.ndarray
    #x_to_coord_b: np.ndarray


class Texture:
    def __init__(self, fields, size):
        self.fields = fields

        height = len(fields)
        width = max(len(row) for row in fields)
        grid_h = height // size
        grid_w = width // size
        print(size, height, width, grid_h, grid_w)

        first_region = None
        grid = [[0] * grid_w for y in range(grid_h)]
        for yi in range(grid_h):
            for xi in range(grid_w):
                if xi * size >= len(fields[yi * size]):
                    continue
                cell = fields[yi * size][xi * size]
                if cell != Field.VOID:
                    grid[yi][xi] = 1
                    if first_region is None:
                        first_region = (yi, xi)

        mappings = {}
        queue = collections.deque()
        dydx_to_r_rotations = {
            (0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3,
        }

        def visit(yi, xi, p_yi, p_xi):
            if grid[yi][xi] != 1:
                return

            if p_yi is None:
                position = Position.initial(0, 0)
                mapping = RegionMapping(
                    texture_x=xi * size, texture_y=yi * size, 
                    cube_position=position,
                    #y_to_coord_a=np.array([0, 1, 0]),
                    #y_to_coord_b=np.array([0, 0, 0]),
                    #x_to_coord_a=np.array([1, 0, 0]),
                    #x_to_coord_b=np.array([0, 0, 0]),
                )
            else:
                p_mapping = mappings[(p_yi, p_xi)]

                dy, dx = yi - p_yi, xi - p_xi
                r_rotations = dydx_to_r_rotations[(dy, dx)]
                position = p_mapping.cube_position.copy()
                position.rotate(Rotation.RIGHT, times=r_rotations)
                position.step(times=size, size=size)
                position.rotate(Rotation.RIGHT, times=-r_rotations)

                mapping = RegionMapping(
                    texture_x=xi * size, texture_y=yi * size, 
                    cube_position=position,
                )

            mappings[(yi, xi)] = mapping
            grid[yi][xi] = 2
            queue.append((yi, xi))

        visit(first_region[0], first_region[1], p_yi=None, p_xi=None)
        while queue:
            y, x = queue.popleft()
            if y > 0: 
                visit(y - 1, x, p_yi=y, p_xi=x)
            if y < grid_h - 1: 
                visit(y + 1, x, p_yi=y, p_xi=x)
            if x > 0: 
                visit(y, x - 1, p_yi=y, p_xi=x)
            if x < grid_w - 1: 
                visit(y, x + 1, p_yi=y, p_xi=x)

        side_ix_to_mapping = {}
        for mapping in mappings.values():
            side_ix = mapping.cube_position.side_ix()
            side_ix_to_mapping[side_ix] = mapping
        print(side_ix_to_mapping)
        self.side_ix_to_mapping = side_ix_to_mapping

    def cube_to_grid_coords(self, x, y, z):
        return 0, 0

    def cube_to_grid_direction(self, direction):
        return 0

    def get_field(self, x, y, z):
        grid_y, grid_x = self.cube_to_grid_coords(x, y, z)
        return self.fields[grid_y][grid_x]


class Board:
    def __init__(self, size, texture):
        self.size = size
        self.texture = texture

    def first_position(self):
        for y in range(size):
            for x in range(size):
                field = self.texture.get_field(y=y, x=x, z=0)
                if field == Field.FLOOR:
                    return Position.initial(y=y, x=x)

    def move(self, position: Position, steps: int):
        for step in range(steps):
            position.step(times=1, size=self.size)
            field = self.texture.get_field(*position.coords)
            if field == Field.WALL:
                print(f'wall! {position}')
                position.step(times=-1, size=self.size)
                break


def read_input():
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

    return fields, instructions


def guess_size(fields):
    height = len(fields)
    width = max(len(row) for row in fields)
    size = math.gcd(height, width)
    grid_h = height // size
    grid_w = width // size
    if grid_h * grid_w < 8:
        size /= 2
    return size


def simulate(board, position, instructions):
    print(f'init {position}')
    for instruction in instructions:
        print(f'executing {instruction}')
        if instruction.isnumeric():
            steps = int(instruction)
            board.move(position, steps)
        elif instruction == 'R' or instruction == 'L':
            position.rotate(instruction)
        else:
            raise ValueError(f'unknown instruction {instruction}')
        print(position)

    return position


if __name__ == '__main__':
    fields, instructions = read_input()
    print(Field.show(fields))
    print(instructions)
    size = guess_size(fields)
    print('size', size)

    texture = Texture(fields=fields, size=size)
    board = Board(size=size, texture=texture)

    raise ValueError()
    position = board.first_position()
    position = simulate(board, position, instructions)

    grid_y, grid_x = texture.cube_to_grid_coords(*position.coords)
    grid_direction = texture.cube_to_grid_direction(position.direction)
    print(1000 * (grid_y + 1) + 4 * (grid_x + 1) + grid_direction)


