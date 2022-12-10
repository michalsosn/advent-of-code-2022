from dataclasses import dataclass
import fileinput


def simulate_instructions_count():
    result = 0

    time = 1
    register = 1

    for line in fileinput.input():
        instruction, *args = line.split()

        if instruction == 'noop':
            delay = 1
        elif instruction == 'addx':
            delay = 2
        else:
            raise ValueError(f'Unrecognized instruction {instruction}')

        for i in range(delay):
            if (time - 20) % 40 == 0:
                result += register * time
            time += 1

        if instruction == 'addx':
            change = int(args[0])
            register += change

    return result


def simulate_instructions_draw():
    result = ['.'] * 240

    time = 0
    register = 1

    for line in fileinput.input():
        instruction, *args = line.split()

        if instruction == 'noop':
            delay = 1
        elif instruction == 'addx':
            delay = 2
        else:
            raise ValueError(f'Unrecognized instruction {instruction}')

        for i in range(delay):
            x = time % 40
            if abs(x - register) <= 1:
                result[time] = '#'
            time = time + 1

        if instruction == 'addx':
            change = int(args[0])
            register += change

    return result


if __name__ == '__main__':
    #result = simulate_instructions_count()
    #print(result)

    display = simulate_instructions_draw()
    for i in range(0, 240, 40):
        print(''.join(display[i:i+40]))

