from collections import defaultdict, namedtuple
from dataclasses import dataclass
from typing import Dict, List
import fileinput


@dataclass
class Point:
    x: int
    y: int


def read_structures():
    structures = []

    for line in fileinput.input():
        line = line.strip()
        parts = [part.split(",") for part in line.split(" -> ")]
        structure = [Point(x=int(part[0]), y=int(part[1])) for part in parts]
        structures.append(structure)

    return structures


def find_max_y(structures):
    return max(point.y for structure in structures for point in structure)


def find_bottom(structures, ground=-1):
    bottom = defaultdict(lambda: ground)

    for structure in structures:
        prev_point = None
        for point in structure:
            if prev_point is not None:
                if prev_point.x == point.x:
                    bottom[point.x] = max(bottom[point.x], point.y, prev_point.y)
                elif prev_point.y == point.y:
                    from_x = min(prev_point.x, point.x)
                    to_x = max(prev_point.x, point.x)
                    for x in range(from_x, to_x + 1):
                        bottom[x] = max(bottom[x], point.y)
                else:
                    raise ValueError(f"Unexpected point {point} (prev {prev_point})")

            prev_point = point

    return bottom


class FieldEnum:
    EMPTY = 0
    BLOCK = 1
    FILL = 2

    @classmethod
    def to_symbol(cls, val):
        if val == cls.EMPTY:
            return '.'
        elif val == cls.BLOCK:
            return '#'
        elif val == cls.FILL:
            return 'o'


@dataclass
class Board:
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    bottom: Dict[int, int]
    cols: List[List[int]]

    def get(self, x, y):
        if y == self.bottom[x]:
            return FieldEnum.BLOCK
        if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y:
            return self.cols[x - self.min_x][y - self.min_y]
        return FieldEnum.EMPTY

    def set(self, x, y, val):
        if x < self.min_x and self.bottom[x] >= 0:
            diff = self.min_x - x
            for i in range(diff):
                self.cols.insert(0, [FieldEnum.EMPTY] * (self.max_y - self.min_y + 1))
            self.min_x = x
        elif x > self.max_x and self.bottom[x] >= 0:
            diff = x - self.max_x 
            for i in range(diff):
                self.cols.append([FieldEnum.EMPTY] * (self.max_y - self.min_y + 1))
            self.max_x = x
        self.cols[x - self.min_x][y - self.min_y] = val


def make_board(bottom):
    min_x = min(bottom.keys())
    max_x = max(bottom.keys())
    min_y = 0
    max_y = max(max(bottom.values()), bottom.default_factory())
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    cols = [[FieldEnum.EMPTY] * height for i in range(width)]
    return Board(min_x, max_x, min_y, max_y, bottom, cols)


def show_board(board):
    lines = []
    for y in range(board.min_y, board.max_y + 1):
        line = [FieldEnum.to_symbol(board.get(x=x, y=y)) 
                for x in range(board.min_x, board.max_x + 1)]
        line = ''.join(line)
        lines.append(line)
    return '\n'.join(lines)


def fill_board(board, structures):
    for structure in structures:
        prev_point = None
        for point in structure:
            if prev_point is not None:
                if prev_point.x == point.x:
                    x = point.x
                    from_y = min(prev_point.y, point.y)
                    to_y = max(prev_point.y, point.y)
                    for y in range(from_y, to_y + 1):
                        board.set(x=x, y=y, val=FieldEnum.BLOCK)
                elif prev_point.y == point.y:
                    y = point.y
                    from_x = min(prev_point.x, point.x)
                    to_x = max(prev_point.x, point.x)
                    for x in range(from_x, to_x + 1):
                        board.set(x=x, y=y, val=FieldEnum.BLOCK)
                else:
                    raise ValueError(f"Unexpected point {point} (prev {prev_point})")

            prev_point = point


def simulate_falling(board):
    count = 0

    while not board.get(x=500, y=0):
        sand = Point(x=500, y=0)
        while True:
            if not board.get(x=sand.x, y=sand.y + 1):
                sand.y += 1
            elif not board.get(x=sand.x - 1, y=sand.y + 1):
                sand.x -= 1
                sand.y += 1
            elif not board.get(x=sand.x + 1, y=sand.y + 1):
                sand.x += 1
                sand.y += 1
            else:
                board.set(x=sand.x, y=sand.y, val=FieldEnum.FILL)
                count += 1
                break

            if sand.y >= board.bottom[sand.x]:
                return count


    return count


if __name__ == '__main__':
    structures = read_structures()
    print(structures)

    max_y = find_max_y(structures)
    print(max_y)
    bottom = find_bottom(structures, ground=max_y + 2)
    print(bottom)

    board = make_board(bottom)
    fill_board(board, structures)
    print(show_board(board))
    print()

    count = simulate_falling(board)
    print(show_board(board))
    print(count)

