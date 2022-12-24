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

    def rotate(self, rotation, times=1):
        if times < 0:
            times = -times
            rotation = Rotation.LEFT if rotation == Rotation.RIGHT else Rotation.RIGHT

        #print(f'rotation {self} {rotation} {times} times')
        if (rotation == Rotation.RIGHT) == (self.side[0] == 1 or self.side[1] == -1 or self.side[2] == 1):
            # y side is inverted bc we should rotate axes in order [z, x], not [x, z]
            rotation_m = self.ROTATION_CW
        else:
            rotation_m = self.ROTATION_CCW

        for i in range(times):
            self.direction[self.side == 0] = self.direction[self.side == 0] @ rotation_m
        #print(f'rotated {self}')

    def step(self, size, times=1):
        #print(f'move {self}')
        for i in range(times):
            self.coords[:] += self.direction
            self.clip_cube(size)
        #print(f'moved {self}')

    def clip_cube(self, size):
        on_side = self.coords[self.side == 0]
        if (0 <= on_side).all() and (on_side < size).all():
            return
        #print(f'cut from {self}')
        # np. p[4 0 -1] d[1 0 0] s[0 0 1] -> p[4 0 0] d[0 0 -1] s[-1 0 0]
        # np. p[-1 0 -1] d[-1 0 0] s[0 0 1] -> p[-1 0 0] d[0 0 -1] s[1 0 0]
        # np. p[0 4 -1] d[0 1 0] s[0 0 1] -> p[0 4 0] d[0 0 -1] s[0 -1 0]
        self.coords[:] += self.side
        self.direction = self.side
        self.side = (self.coords == size).astype(int) * -1 \
                  + (self.coords == -1).astype(int) 
        #print(f'cut to {self}')


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
        self.size = size

        height = len(fields)
        width = max(len(row) for row in fields)

        def find_first():
            for y in range(height):
                for x in range(width):
                    if x >= len(fields[y]):
                        continue
                    cell = fields[y][x]
                    if cell != Field.VOID:
                        return (y, x)
        first_yx = find_first()

        mappings = {}
        visited = [[False] * width for y in range(height)]
        queue = collections.deque()
        dydx_to_r_rotations = {
            (0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3,
        }

        def visit(y, x, p_y, p_x):
            if x >= len(fields[y]):
                return
            if fields[y][x] == Field.VOID:
                return
            if visited[y][x]:
                return

            if p_y is None:
                position = Position.initial(0, 0)
                mapping = RegionMapping(
                    texture_x=x, texture_y=y, 
                    cube_position=position,
                )
            else:
                p_mapping = mappings[(p_y, p_x)]

                dy, dx = y - p_y, x - p_x
                r_rotations = dydx_to_r_rotations[(dy, dx)]
                position = p_mapping.cube_position.copy()
                position.rotate(Rotation.RIGHT, times=r_rotations)
                position.step(times=1, size=size)
                position.rotate(Rotation.LEFT, times=r_rotations)

                mapping = RegionMapping(
                    texture_x=x, texture_y=y, 
                    cube_position=position,
                )

            mappings[(y, x)] = mapping
            visited[y][x] = True
            queue.append((y, x))

        visit(first_yx[0], first_yx[1], p_y=None, p_x=None)
        while queue:
            y, x = queue.popleft()
            if y > 0: 
                visit(y - 1, x, p_y=y, p_x=x)
            if y < height - 1: 
                visit(y + 1, x, p_y=y, p_x=x)
            if x > 0: 
                visit(y, x - 1, p_y=y, p_x=x)
            if x < width - 1: 
                visit(y, x + 1, p_y=y, p_x=x)

        cube_to_texture_mapping = {}
        for mapping in mappings.values():
            cube_point = tuple(mapping.cube_position.coords)
            cube_to_texture_mapping[cube_point] = mapping
        print(sorted(cube_to_texture_mapping.keys()))
        print(len(cube_to_texture_mapping))
        print(cube_to_texture_mapping[(0, 0, -1)])
        self.cube_to_texture_mapping = cube_to_texture_mapping

    def cube_to_texture_coords(self, x, y, z):
        mapping = self.cube_to_texture_mapping[(x, y, z)]
        return mapping.texture_y, mapping.texture_x

    def cube_to_texture_direction(self, position):
        mapping = self.cube_to_texture_mapping[tuple(position.coords)]

        if (position.direction == mapping.cube_position.direction).all():
            return 0

        shadow = position.copy()
        for i in range(3):
            shadow.rotate(Rotation.LEFT, times=1)
            if (shadow.direction == mapping.cube_position.direction).all():
                return i + 1

        raise ValueError('never matched direction')

    def get_field(self, x, y, z):
        texture_y, texture_x = self.cube_to_texture_coords(x, y, z)
        return self.fields[texture_y][texture_x]


class Board:
    def __init__(self, size, texture):
        self.size = size
        self.texture = texture

    def first_position(self):
        for y in range(size):
            for x in range(size):
                field = self.texture.get_field(y=y, x=x, z=-1)
                if field == Field.FLOOR:
                    return Position.initial(y=y, x=x)

    def move(self, position: Position, steps: int):
        for step in range(steps):
            shadow = position.copy()
            shadow.step(times=1, size=self.size)
            field = self.texture.get_field(*shadow.coords)
            if field != Field.WALL:
                position.step(times=1, size=self.size)


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

    position = board.first_position()
    position = simulate(board, position, instructions)

    texture_y, texture_x = texture.cube_to_texture_coords(*position.coords)
    texture_direction = texture.cube_to_texture_direction(position)
    print('end', texture_y, texture_x, texture_direction)
    print(1000 * (texture_y + 1) + 4 * (texture_x + 1) + texture_direction)


