import collections
from dataclasses import dataclass
import re
from typing import List
import fileinput


@dataclass
class Node:
    name: int
    flow: int
    neighbors: List[str]


def read_map():
    nodes = {}

    node_re = re.compile(r"Valve (.+) has flow rate=(.+); tunnels? leads? to valves? (.+)")
    for line in fileinput.input():
        match = node_re.match(line)
        name, flow, neighbors = match.groups()
        flow = int(flow)
        neighbors = neighbors.split(', ')
        node = Node(name, flow, neighbors)
        nodes[name] = node

    return nodes


def calculate_distances(nodes, start):
    distances = {}

    queue = collections.deque()
    distances[start] = 1
    queue.append((1, start))
    while queue:
        distance, node_name = queue.popleft()
        node = nodes[node_name]
        for neighbor_name in node.neighbors:
            if neighbor_name not in distances:
                distances[neighbor_name] = distance + 1
                queue.append((distance + 1, neighbor_name))
    return distances


def make_connection_matrix(nodes):
    matrix = {}

    for start in nodes.keys():
        distances = calculate_distances(nodes, start)
        matrix[start] = distances

    return matrix


def find_best_route(nodes, matrix, start, time_limit):
    opened = {name: node.flow == 0 for name, node in nodes.items()}

    def visit(node_name, time_left, flow):
        opened[node_name] = True
        flow_gain = nodes[node_name].flow * time_left
        new_flow = flow + flow_gain
        best_flow = new_flow

        for neighbor_name, distance in matrix[node_name].items():
            if not opened[neighbor_name] and time_left > distance:
                child_flow = visit(neighbor_name, time_left - distance, new_flow)
                best_flow = max(best_flow, child_flow)

        opened[node_name] = False
        return best_flow

    best_flow = visit(node_name=start, time_left=time_limit, flow=0)

    return best_flow


if __name__ == '__main__':
    nodes = read_map()
    print(nodes)

    matrix = make_connection_matrix(nodes)
    #print(matrix)

    start = 'AA'
    time_limit = 30
    result = find_best_route(nodes, matrix, start, time_limit)
    print(result)
