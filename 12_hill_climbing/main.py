import fileinput
import collections


def read_board():
    start = None
    end = None
    board = []

    ord_a = ord('a')
    for y, line in enumerate(fileinput.input()):
        line = line.strip()
        if not line:
            break

        row = []
        for x, c in enumerate(line):
            if c == 'S':
                row.append(0)
                start = (y, x)
            elif c == 'E':
                row.append(ord('z') - ord_a)
                end = (y, x)
            else:
                row.append(ord(c) - ord_a)
        board.append(row)

    return board, start, end


def find_path(board, start, end):
    height, width = len(board), len(board[0])

    visited = [[False] * len(row) for row in board]
    queue = collections.deque()

    s_y, s_x = start
    e_y, e_x = end
    queue.append((s_y, s_x, 0))
    visited[s_y][s_x] = True
    while queue:
        p_y, p_x, p_dist = queue.popleft()

        if p_y == e_y and p_x == e_x:
            return p_dist

        p_val = board[p_y][p_x]

        def go(n_y, n_x):
            if visited[n_y][n_x]:
                return
            n_val = board[n_y][n_x]
            if n_val <= p_val + 1:
                queue.append((n_y, n_x, p_dist + 1))
                visited[n_y][n_x] = True

        if p_x > 0:
            go(p_y, p_x - 1)
        if p_x < width - 1:
            go(p_y, p_x + 1)
        if p_y > 0:
            go(p_y - 1, p_x)
        if p_y < height - 1:
            go(p_y + 1, p_x)

    return -1


def find_shortest(board, start):
    height, width = len(board), len(board[0])

    visited = [[False] * len(row) for row in board]
    queue = collections.deque()

    s_y, s_x = start
    queue.append((s_y, s_x, 0))
    visited[s_y][s_x] = True
    while queue:
        p_y, p_x, p_dist = queue.popleft()
        p_val = board[p_y][p_x]

        if p_val == 0:
            return p_dist

        def go(n_y, n_x):
            if visited[n_y][n_x]:
                return
            n_val = board[n_y][n_x]
            if p_val <= n_val + 1:
                queue.append((n_y, n_x, p_dist + 1))
                visited[n_y][n_x] = True

        if p_x > 0:
            go(p_y, p_x - 1)
        if p_x < width - 1:
            go(p_y, p_x + 1)
        if p_y > 0:
            go(p_y - 1, p_x)
        if p_y < height - 1:
            go(p_y + 1, p_x)

    return -1


if __name__ == '__main__':
    board, start, end = read_board()
    print(board, start, end)

    path = find_path(board, start, end)
    print(path)

    path = find_shortest(board, end)
    print(path)

