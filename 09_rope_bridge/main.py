from dataclasses import dataclass
import fileinput


@dataclass
class Position:
    x: int
    y: int


def simulate_moves(segment_num):
    segments = [Position(0, 0) for i in range(segment_num)]
    head, tail = segments[0], segments[-1]

    unique_positions = set()

    for line in fileinput.input():
        direction, steps = line.split()

        for step in range(int(steps)):
            if direction == 'R':
                head.x += 1
            elif direction == 'L':
                head.x -= 1
            elif direction == 'U':
                head.y += 1
            else:
                head.y -= 1

            for i in range(1, segment_num):
                leader = segments[i - 1]
                follower = segments[i]
                dx = leader.x - follower.x
                dy = leader.y - follower.y

                if dy == 0 and abs(dx) == 2:
                    follower.x += dx / abs(dx)
                elif dx == 0 and abs(dy) == 2:
                    follower.y += dy / abs(dy)
                elif abs(dx) + abs(dy) >= 3:
                    follower.x += dx / abs(dx)
                    follower.y += dy / abs(dy)
            
            unique_positions.add((tail.x, tail.y))

    return unique_positions


if __name__ == '__main__':
    #unique_positions = simulate_moves(2)
    #print(len(unique_positions))

    unique_positions = simulate_moves(10)
    print(len(unique_positions))
