from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
import fileinput


def read_board():
    board = []

    for line in fileinput.input():
        row = [int(c) for c in line.strip()]
        board.append(row)

    return board


def find_visible(board):
    h = len(board)
    w = len(board[0])
    visible = [[False] * w for i in range(h)]

    for y in range(0, h):
        visible[y][0] = True
        max_seen = board[y][0]
        for x in range(1, w - 1):
            if board[y][x] > max_seen:
                visible[y][x] = True
            max_seen = max(max_seen, board[y][x])

        visible[y][-1] = True
        max_seen = board[y][-1]
        for x in range(w - 2, 0, -1):
            if board[y][x] > max_seen:
                visible[y][x] = True
            max_seen = max(max_seen, board[y][x])

    for x in range(1, w - 1):
        visible[0][x] = True
        max_seen = board[0][x]
        for y in range(1, h - 1):
            if board[y][x] > max_seen:
                visible[y][x] = True
            max_seen = max(max_seen, board[y][x])

        visible[-1][x] = True
        max_seen = board[-1][x]
        for y in range(h - 2, 0, -1):
            if board[y][x] > max_seen:
                visible[y][x] = True
            max_seen = max(max_seen, board[y][x])

    return visible


def find_best_score(board):
    h = len(board)
    w = len(board[0])
    best_score = 0

    def score(y, x):
        center_val = board[y][x]

        right_score = 0
        for c_x in range(x + 1, w):
            right_score += 1
            if board[y][c_x] >= center_val:
                break

        left_score = 0
        for c_x in range(x - 1, -1, -1):
            left_score += 1
            if board[y][c_x] >= center_val:
                break

        down_score = 0
        for c_y in range(y + 1, h):
            down_score += 1
            if board[c_y][x] >= center_val:
                break

        up_score = 0
        for c_y in range(y - 1, -1, -1):
            up_score += 1
            if board[c_y][x] >= center_val:
                break

        return right_score * left_score * down_score * up_score


    for y in range(1, h - 1):
        for x in range(1, w - 1):
            cur_score = score(y, x)
            best_score = max(cur_score, best_score)

    return best_score


def display_board_int(board):
    return '\n'.join(''.join(str(int(cell)) for cell in row) for row in board)


if __name__ == '__main__':
    board = read_board()
    print(display_board_int(board))
    print()

    visible = find_visible(board)
    print(display_board_int(visible))
    print()

    print('visible', sum(sum(row) for row in visible))

    best_score = find_best_score(board)
    print('best scenic score', best_score)
