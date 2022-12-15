from collections import defaultdict, namedtuple
from dataclasses import dataclass
import re
from typing import Dict, List
import fileinput


@dataclass
class Sensor:
    x: int
    y: int
    detect_range: int

    def covers(self, x, y):
        dist = abs(self.x - x) + abs(self.y - y)
        return self.detect_range >= dist


@dataclass
class Beacon:
    x: int
    y: int


def read_map():
    sensors = []
    beacons = []

    sensor_re = re.compile(r"Sensor at x=(.+), y=(.+): closest beacon is at x=(.+), y=(.+)")
    for line in fileinput.input():
        match = sensor_re.match(line)
        x, y, b_x, b_y = map(int, match.groups())
        detect_range = abs(x - b_x) + abs(y - b_y)
        sensor = Sensor(x, y, detect_range)
        beacon = Beacon(b_x, b_y)
        sensors.append(sensor)
        beacons.append(beacon)

    return sensors, beacons


def find_covered_at_y(sensors, target_y):
    covered = set()

    for sensor in sensors:
        target_dist = abs(sensor.y - target_y)
        if target_dist > sensor.detect_range:
            continue
        target_span = sensor.detect_range - target_dist

        new_covered = range(sensor.x - target_span, sensor.x + target_span + 1)
        covered.update(new_covered)

    return covered


def find_beacons_at_y(beacons, target_y):
    xs = set()
    for beacon in beacons:
        if beacon.y == target_y:
            xs.add(beacon.x)
    return xs


def find_unique_uncovered(sensors, min_x, max_x, min_y, max_y):
    for y in range(min_y, max_y + 1):
        x = min_x
        while x <= max_x:
            for sensor in sensors:
                if sensor.covers(x, y):
                    target_dist = abs(sensor.y - y)
                    target_span = sensor.detect_range - target_dist
                    x = sensor.x + target_span + 1
                    break
            else:
                return Beacon(x=x, y=y)


if __name__ == '__main__':
    sensors, beacons = read_map()
    sensors.sort(key=lambda s: s.detect_range, reverse=True)
    print(sensors)

    target_y = 2000000
    covered = find_covered_at_y(sensors, target_y=target_y)
    beacon_xs = find_beacons_at_y(beacons, target_y=target_y)
    new_covered = covered - beacon_xs
    print(len(new_covered))

    #max_valid = 20
    max_valid = 4000000
    uncovered = find_unique_uncovered(sensors, 0, max_valid, 0, max_valid)
    print(uncovered)
    print(uncovered.x * 4000000 + uncovered.y)

