import collections
from dataclasses import dataclass
import re
from typing import List
import fileinput


class Move:
    LEFT = 0
    RIGHT = 1
    
    @classmethod
    def parse(cls, symbol):
        if symbol == '<':
            return cls.LEFT
        if symbol == '>':
            return cls.RIGHT

    @classmethod
    def to_symbol(cls, val):
        if val == cls.LEFT:
            return '<'
        elif val == cls.RIGHT:
            return '>'


def read_moves():
    line = input()
    moves = [Move.parse(c) for c in line]
    return moves


class Field:
    EMPTY = 0
    BLOCK = 1

    @classmethod
    def to_symbol(cls, val):
        if val == cls.EMPTY:
            return '.'
        elif val == cls.BLOCK:
            return '#'

    def show(fields):
        lines = []
        for row in fields:
            line = ''.join([Field.to_symbol(x) for x in row])
            lines.append(line)
        return '\n'.join(lines)


@dataclass
class Shape:
    fields: List[List[int]]

    @property
    def height(self):
        return len(self.fields)

    @property
    def width(self):
        return len(self.fields[0])

    def count_blocks(self):
        count = 0
        for row in self.fields:
            for cell in row:
                if cell == Field.BLOCK:
                    count += 1
        return count


def make_shapes():
    return [
        Shape([[1, 1, 1, 1]]),
        Shape([[0, 1, 0], [1, 1, 1], [0, 1, 0]]),
        Shape([[1, 1, 1], [0, 0, 1], [0, 0, 1]]),
        Shape([[1], [1], [1], [1]]),
        Shape([[1, 1], [1, 1]]),
    ]


@dataclass
class Block:
    x: int
    y: int
    shape: Shape

    @property
    def height(self):
        return self.shape.height

    @property
    def width(self):
        return self.shape.width

    def move(self, move):
        if move == Move.LEFT:
            x = self.x - 1
        elif move == Move.RIGHT:
            x = self.x + 1
        return Block(x=x, y=self.y, shape=self.shape)

    def fall(self):
        return Block(x=self.x, y=self.y - 1, shape=self.shape) 


@dataclass
class Board:
    width: int
    fields: List[List[int]]

    def __init__(self, width):
        self.width = width
        self.fields = []

    @property
    def height(self):
        return len(self.fields)

    def extend(self, height):
        diff = height - self.height
        for i in range(diff):
            self.fields.append([Field.EMPTY] * self.width)

    def check_collides(self, block):
        if block.x < 0 or block.x + block.width > board.width or block.y < 0:
            return True
        if block.y > board.height:
            return False

        for i, y in enumerate(range(block.y, min(block.y + block.height, board.height))):
            for j, x in enumerate(range(block.x, block.x + block.width)):
                if block.shape.fields[i][j] == Field.BLOCK \
                   and board.fields[y][x] == Field.BLOCK:
                       return True
        
        return False

    def add(self, block):
        self.extend(block.y + block.height)
        for i in range(block.height):
            for j in range(block.width):
                if board.fields[block.y + i][block.x + j] == Field.EMPTY:
                    board.fields[block.y + i][block.x + j] = block.shape.fields[i][j]

    def count_blocks(self):
        count = 0
        for row in self.fields:
            for cell in row:
                if cell == Field.BLOCK:
                    count += 1
        return count

    def signature(self, last_rows):
        result = 0
        for row in self.fields[:-last_rows-1:-1]:
            for cell in row:
                result = 2 * result + cell
        return result


def simulate(board, shapes, moves, block_num, signature_size):
    block_i = 0
    move_i = 0

    signatures_seen = {}

    while block_i < block_num:
        shape = shapes[block_i % len(shapes)]
        block = Block(x=2, y=board.height + 3, shape=shape)

        while True:
            move = moves[move_i % len(moves)]
            move_i += 1

            #print(f"Block is at {block.x} {block.y} {block.width} {block.height}")
            #print(f'Move {Move.to_symbol(move)}')
            shadow = block.move(move)
            if not board.check_collides(shadow):
                block = shadow

            shadow = block.fall()
            if not board.check_collides(shadow):
                block = shadow
            else:
                board.add(block)
                break

        if signature_size and board.height >= signature_size:
            signature = (
                block_i % len(shapes), 
                move_i % len(moves), 
                board.signature(signature_size)
            )
            if signature in signatures_seen:
                last_seen_i, last_seen_height = signatures_seen[signature]
                cycle_height = board.height - last_seen_height
                if cycle_height <= signature_size:
                    cycle_i = block_i - last_seen_i
                    print(f"At block {block_i} seen the same signature "
                          f"as at {last_seen_i} (cycle of {cycle_i} steps).")
                    skip_cycles = (block_num - block_i) // cycle_i
                    skip_blocks = skip_cycles * cycle_i
                    skip_height = skip_cycles * cycle_height
                    print(f"Skipping {skip_cycles} cycles of size {cycle_i} "
                          f"(a total of {skip_blocks} blocks)")
                    print(f"Height after {last_seen_i} blocks was {last_seen_height} "
                          f"and after {block_i} it is {board.height}. The cycle adds "
                          f"{cycle_height} height. So skipped {skip_cycles} add "
                          f"{skip_height} height")
                    block_i += skip_blocks
                    print(f"Skipped to {block_i}")
                    signature_size = 0
            elif board.height > signature_size * 2:
                print(f'Failed to find a cycle for the signature size {signature_size}')
                return
            signatures_seen[signature] = (block_i, board.height)

        block_i += 1


if __name__ == '__main__':
    board = Board(width=7)
    print('Board')
    print(Field.show(board.fields[::-1]))
    print()

    shapes = make_shapes()
    print('Shapes')
    for shape in shapes:
        print(Field.show(shape.fields[::-1]))
        print()

    moves = read_moves()
    print('Moves')
    print(' '.join([Move.to_symbol(move) for move in moves]))
    print()

    simulate(board, shapes, moves, block_num=1000000000000, signature_size=3000)
    #print('Board')
    #print(Field.show(board.fields[::-1]))
    #print()
    print('Result')
    print(board.height)
