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


def find_best_route(nodes, matrix, start, time_limit, actor_num):
    opened = {name: node.flow == 0 for name, node in nodes.items()}
    start_positions = [(0, start)] * actor_num
    bestest_flow = [0]

    def visit(positions, time_left, flow):
        node_name = positions[0][1]
        other_positions = positions[1:]
        other_min_distance = None
        if other_positions:
            other_min_distance = min(pos[0] for pos in other_positions)

        flow_gain = nodes[node_name].flow * time_left
        new_flow = flow + flow_gain
        best_flow = new_flow

        opened_any = False
        for neighbor_name, distance in matrix[node_name].items():
            if not opened[neighbor_name] and time_left > distance:
                opened_any = True
                opened[neighbor_name] = True

                if not other_positions:
                    min_distance = distance
                    new_positions = [(0, neighbor_name)]
                else:
                    min_distance = min(distance, other_min_distance)

                    new_positions = [(distance - min_distance, name)
                                     for distance, name in other_positions]
                    new_positions.append((distance - min_distance, neighbor_name))
                    new_positions.sort()

                child_flow = visit(
                    new_positions, time_left - min_distance, new_flow
                )
                if child_flow > best_flow:
                    best_flow = child_flow

                opened[neighbor_name] = False

        if not opened_any and other_positions:
            new_positions = [(distance - other_min_distance, name)
                             for distance, name in other_positions]
            child_flow = visit(
                new_positions, time_left - other_min_distance, new_flow
            )
            best_flow = max(best_flow, child_flow)
            bestest_flow[0] = max(bestest_flow[0], best_flow)
            print(bestest_flow[0])

        return best_flow

    best_flow = visit(
        positions=start_positions, time_left=time_limit, flow=0
    )

    return best_flow


if __name__ == '__main__':
    nodes = read_map()
    print(nodes)

    matrix = make_connection_matrix(nodes)
    print(len(matrix))

    #result = find_best_route(nodes, matrix, start='AA', time_limit=30, actor_num=1)
    #print(result)

    result = find_best_route(nodes, matrix, start='AA', time_limit=26, actor_num=2)
    print(result)
