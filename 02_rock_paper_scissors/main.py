import fileinput


LOSS_SCORE = 0
DRAW_SCORE = 3
WIN_SCORE = 6


def score_for_given_move():
    op_ord_start = ord('A')
    my_ord_start = ord('X')

    result = 0
    for line in fileinput.input():
        op_move, my_move = line.split()
        op_value = ord(op_move) - op_ord_start
        my_value = ord(my_move) - my_ord_start

        if my_value == op_value:
            score = DRAW_SCORE
        elif my_value == (op_value + 1) % 3:
            score = WIN_SCORE
        else:
            score = LOSS_SCORE

        score += my_value + 1

        result += score

    print(result)


def score_for_given_result():
    op_ord_start = ord('A')
    target_ord_start = ord('X')

    result = 0
    for line in fileinput.input():
        op_move, target = line.split()
        op_value = ord(op_move) - op_ord_start

        if target == 'X':
            my_value = LOSS_SCORE + (op_value - 1) % 3
            score = my_value + 1
        elif target == 'Y':
            my_value = op_value
            score = DRAW_SCORE + my_value + 1
        else:
            my_value = (op_value + 1) % 3
            score = WIN_SCORE + my_value + 1

        result += score

    print(result)


if __name__ == '__main__':
    # score_for_given_move()
    score_for_given_result()
