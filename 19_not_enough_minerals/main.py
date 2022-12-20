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
    np.seterr(divide='ignore', invalid='ignore')

    costs = blueprint.costs

    producers = np.zeros(Resource.SIZE)
    producers[Resource.ORE] = 1
    total_resources = np.zeros(Resource.SIZE)
    resources = np.zeros(Resource.SIZE)
    max_producers = costs.max(axis=0)
    max_producers[-1] = np.inf
    total_resources_cache = {}
    best_geodes = [0]

    def visit(time):
        if time >= time_limit:
            if best_geodes[0] < resources[Resource.GEODE]:
                # print(f"{time:02d} {resources} {producers} fin")
                best_geodes[0] = resources[Resource.GEODE]
                #print(f"{best_geodes[0]}")

        time_left = time_limit - time

        cache_key = (time,) + tuple(producers)
        cache_val = tuple(resources)
        retrieved_cache_val = total_resources_cache.get(cache_key)
        if retrieved_cache_val is not None and retrieved_cache_val[0] <= cache_val[0] and retrieved_cache_val[1] <= cache_val[1] and retrieved_cache_val[2] <= cache_val[2] and retrieved_cache_val[3] <= cache_val[3]:
            return
        total_resources_cache[cache_key] = cache_val

        possible_geodes = resources[Resource.GEODE] + time_left * (2 * producers[Resource.GEODE] + time_left - 1) // 2
        if possible_geodes <= best_geodes[0]:
            return

        for resource_type in range(Resource.SIZE - 1, -1, -1):
            if producers[resource_type] >= max_producers[resource_type]:
                continue
            if resources[resource_type] + producers[resource_type] * time_left >= max_producers[resource_type] * time_left:
                continue

            cost_row = costs[resource_type]
            resources_required = cost_row - resources
            time_required = max(
                0,
                int(np.ceil(np.nan_to_num(resources_required / producers).max()))
            ) + 1

            if time + time_required >= time_limit:
                continue

            total_resources[:] += producers * time_required
            resources[:] += producers * time_required
            resources[:] -= cost_row
            producers[resource_type] += 1
            visit(time + time_required)
            producers[resource_type] -= 1
            resources[:] += cost_row
            resources[:] -= producers * time_required
            total_resources[:] -= producers * time_required

        final_geodes = resources[Resource.GEODE] + producers[Resource.GEODE] * time_left
        if best_geodes[0] <= final_geodes:
            best_geodes[0] = final_geodes
    
    visit(0)

    return best_geodes[0]


if __name__ == '__main__':
    blueprints = read_blueprints()[:3]
    print(blueprints)

    quality = 0
    for i, blueprint in enumerate(blueprints):
        geodes = calculate_max_geodes(blueprint, time_limit=32)
        print(i, geodes)
        quality += (i + 1) * geodes

    print(quality)

