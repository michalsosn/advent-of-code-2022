import collections
from dataclasses import dataclass
import fileinput
import numpy as np
import re
from typing import List


class Resource:
    ORE = 0
    CLAY = 1
    OBSIDIAN = 2
    GEODE = 3
    SIZE = 4


@dataclass
class Blueprint:
    costs: np.ndarray


def read_blueprints():
    blueprints = []

    ore_re = re.compile(r"Each ore robot costs (\d+) ore.")
    clay_re = re.compile(r"Each clay robot costs (\d+) ore.")
    obsidian_re = re.compile(r"Each obsidian robot costs (\d+) ore and (\d+) clay.")
    geode_re = re.compile(r"Each geode robot costs (\d+) ore and (\d+) obsidian.")

    for line in fileinput.input():
        costs = np.zeros((Resource.SIZE, Resource.SIZE))
        costs[Resource.ORE][Resource.ORE], = map(int, ore_re.search(line).groups())
        costs[Resource.CLAY][Resource.ORE], = map(int, clay_re.search(line).groups())
        costs[Resource.OBSIDIAN][Resource.ORE], costs[Resource.OBSIDIAN][Resource.CLAY] = map(int, obsidian_re.search(line).groups())
        costs[Resource.GEODE][Resource.ORE], costs[Resource.GEODE][Resource.OBSIDIAN] = map(int, geode_re.search(line).groups())
        blueprint = Blueprint(costs)
        blueprints.append(blueprint)

    return blueprints


def calculate_max_geodes(blueprint, time_limit):
    costs = blueprint.costs

    producers = np.zeros(Resource.SIZE)
    producers[Resource.ORE] = 1
    resources = np.zeros(Resource.SIZE)

    def visit(time):
        if time == time_limit:
            return resources[Resource.GEODE]

        max_geodes = 0
        resources[:] += producers

        for resource_type in range(Resource.SIZE - 1, -1, -1):
            cost_row = costs[resource_type]

            if (resources >= cost_row).all():
                resources[:] -= cost_row
                producers[resource_type] += 1
                max_geodes = max(max_geodes, visit(time + 1))
                producers[resource_type] -= 1
                resources[:] += cost_row

                if resource_type == Resource.GEODE:
                    break

        max_geodes = max(max_geodes, visit(time + 1))

        resources[:] -= producers
        return max_geodes
    
    visit(0)

    return max_geodes


if __name__ == '__main__':
    blueprints = read_blueprints()
    print(blueprints)

    quality = 0
    for i, blueprint in enumerate(blueprints):
        geodes = calculate_max_geodes(blueprint, time_limit=24)
        quality += (i + 1) * geodes

    print(quality)
