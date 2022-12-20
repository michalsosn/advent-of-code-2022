from dataclasses import dataclass
import fileinput


@dataclass
class Node:
    value: int
    prev = None
    next = None


def read_code():
    nodes = []
    for line in fileinput.input():
        value = int(line)
        node = Node(value)
        nodes.append(node)

    length = len(nodes)
    for i in range(length):
        nodes[i].prev = nodes[i - 1]
        nodes[i].next = nodes[(i + 1) % length]

    return nodes


def move(node, by):
    if by == 0:
        return

    target_before = node
    node.next.prev, node.prev.next = node.prev, node.next

    if by > 0:
        for i in range(by):
            target_before = target_before.next
    else:
        target_before = target_before.prev
        for i in range(abs(by)):
            target_before = target_before.prev

    target_after = target_before.next
    target_before.next, node.prev = node, target_before
    target_after.prev, node.next = node, target_after


def reorder(nodes):
    length = len(nodes)
    for node in nodes:
        sign = node.value // abs(node.value) if node.value else 0
        places = abs(node.value) % (length - 1)
        move(node, sign * places)


def find(nodes, value):
    for node in nodes:
        if node.value == value:
            return node


def get_nth(node, n):
    for i in range(n):
        node = node.next
    return node


def display(nodes):
    node = nodes[0]
    for i in range(len(nodes)):
        print(node.value, end=' ')
        node = node.next
    print()


if __name__ == '__main__':
    nodes = read_code()

    key = 811589153
    loops = 10

    for node in nodes:
        node.value *= key

    display(nodes)
    for i in range(loops):
        reorder(nodes)

    zero_node = find(nodes, value=0)
    length = len(nodes)
    result = [
        get_nth(zero_node, 1000 % length).value,
        get_nth(zero_node, 2000 % length).value,
        get_nth(zero_node, 3000 % length).value,
    ]
    print(result)
    print(sum(result))

