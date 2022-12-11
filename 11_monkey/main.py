import re
from dataclasses import dataclass
import fileinput
from typing import Dict, List, Protocol


class Expression(Protocol):
    def evaluate(self, environment: Dict[str, int]) -> int:
        ...

    @staticmethod
    def parse(line: str):
        def const_or_var(token):
            if token.isnumeric():
                return Const(int(token))
            else:
                return Var(token)

        tokens = line.split()
        return BinOp(
            a=const_or_var(tokens[0]),
            op=tokens[1],
            b=const_or_var(tokens[2]),
        )

@dataclass
class Var(Expression):
    name: str

    def evaluate(self, environment: Dict[str, int]) -> int:
        return environment[self.name]

@dataclass
class Const(Expression):
    value: int

    def evaluate(self, environment: Dict[str, int]) -> int:
        return self.value

@dataclass
class BinOp(Expression):
    a: Expression
    b: Expression
    op: str

    def evaluate(self, environment: Dict[str, int]) -> int:
        a_val = self.a.evaluate(environment)
        b_val = self.b.evaluate(environment)
        if self.op == '+':
            return a_val + b_val
        elif self.op == '*':
            return a_val * b_val
        else:
            raise ValueError(f"Unrecognized operation '{op}'")


@dataclass
class Monkey:
    items: List[int]
    operation_expr: Expression
    test_divisor: int
    test_target_true: int
    test_target_false: int


def parse_input():
    monkeys = []

    NEW_MONKEY_RE = re.compile(r"Monkey (\d+):")
    ITEMS_RE = re.compile(r"Starting items: ([0-9, ]+)")
    OPERATION_RE = re.compile(r"Operation: new = (.+)")
    TEST_RE = re.compile(r"Test: divisible by (\d+)")
    TEST_TRUE_RE = re.compile(r"If true: throw to monkey (\d+)")
    TEST_FALSE_RE = re.compile(r"If false: throw to monkey (\d+)")

    monkey = None

    for line in fileinput.input():
        line = line.strip()
        if match := NEW_MONKEY_RE.match(line):
            if monkey is not None:
                monkeys.append(monkey)
            monkey = Monkey([], Var("old"), 0, 0, 0)
        elif match := ITEMS_RE.match(line):
            items = [int(v) for v in match.group(1).split(', ')]
            monkey.items = items
        elif match := OPERATION_RE.match(line):
            operation_expr = Expression.parse(match.group(1))
            monkey.operation_expr = operation_expr
        elif match := TEST_RE.match(line):
            test_divisor = int(match.group(1))
            monkey.test_divisor = test_divisor
        elif match := TEST_TRUE_RE.match(line):
            test_target_true = int(match.group(1))
            monkey.test_target_true = test_target_true
        elif match := TEST_FALSE_RE.match(line):
            test_target_false = int(match.group(1))
            monkey.test_target_false = test_target_false
        elif line == '':
            pass
        else:
            raise ValueError(f"Failed to match {line}")

    if monkey is not None:
        monkeys.append(monkey)
    return monkeys


def simulate_throws(monkeys, rounds, worry_mod):
    counts = [0] * len(monkeys)

    for round in range(rounds):
        for i, monkey in enumerate(monkeys):
            for item in monkey.items:
                counts[i] += 1
                new_item = monkey.operation_expr.evaluate(dict(old=item))
                new_item %= worry_mod
                if new_item % monkey.test_divisor == 0:
                    monkeys[monkey.test_target_true].items.append(new_item)
                else:
                    monkeys[monkey.test_target_false].items.append(new_item)
            monkey.items.clear()

        if round % (rounds // 20) == 0:
            print('Round', round)
            for monkey in monkeys:
                print(monkey.items)

    return counts


if __name__ == '__main__':
    monkeys = parse_input()
    for monkey in monkeys:
        print(monkey)

    worry_mod = 1
    for monkey in monkeys:
        worry_mod *= monkey.test_divisor

    counts = simulate_throws(monkeys, rounds=10000, worry_mod=worry_mod)
    print(counts)

    counts.sort(reverse=True)
    print(counts[0] * counts[1])

