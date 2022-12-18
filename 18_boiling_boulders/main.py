import collections
from dataclasses import dataclass
import re
from typing import List
import fileinput

@dataclass
class Block:
    x: int
    y: int
    z: int


def read_blocks():
    blocks = []
    for line in fileinput.input():
        x, y, z = map(int, line.split(','))
        block = Block(x, y, z)
        blocks.append(block)
    return blocks


EXTERIOR_SYMBOL = 'X'


def calculate_surface_area(blocks):
    max_x, max_y, max_z = 0, 0, 0

    for block in blocks:
        max_x = max(max_x, block.x)
        max_y = max(max_y, block.y)
        max_z = max(max_z, block.z)

    board = [[[None] * (max_z + 2) for y in range(max_y + 2)] for x in range(max_x + 2)]

    for block in blocks:
        board[block.x][block.y][block.z] = block

    flood(board, (max_x + 1, max_y + 1, max_z + 1))

    area = 0
    for block in blocks:
        area += board[block.x + 1][block.y][block.z] == EXTERIOR_SYMBOL
        area += board[block.x - 1][block.y][block.z] == EXTERIOR_SYMBOL
        area += board[block.x][block.y + 1][block.z] == EXTERIOR_SYMBOL
        area += board[block.x][block.y - 1][block.z] == EXTERIOR_SYMBOL
        area += board[block.x][block.y][block.z + 1] == EXTERIOR_SYMBOL
        area += board[block.x][block.y][block.z + 1] == EXTERIOR_SYMBOL

    return area

def flood(board, start):
    max_x = len(board)
    max_y = len(board[0])
    max_z = len(board[0][0])

    queue = collections.deque()

    def go(n_x, n_y, n_z):
        if board[n_x][n_y][n_z] is None:
            queue.append((n_x, n_y, n_z))
            board[n_x][n_y][n_z] = EXTERIOR_SYMBOL

    go(*start)
    while queue:
        x, y, z = queue.popleft()
        if x > 0: 
            go(x - 1, y, z)
        if x < max_x - 1: 
            go(x + 1, y, z)
        if y > 0: 
            go(x, y - 1, z)
        if y < max_y - 1: 
            go(x, y + 1, z)
        if z > 0: 
            go(x, y, z - 1)
        if z < max_z - 1: 
            go(x, y, z + 1)

if __name__ == '__main__':
    blocks = read_blocks()
    print(blocks)

    area = calculate_surface_area(blocks)
    print(area)
