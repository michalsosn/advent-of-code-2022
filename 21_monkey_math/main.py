from dataclasses import dataclass
import fileinput
import re
from typing import Dict, List, Protocol


class Expression(Protocol):
    def evaluate(self, environment: Dict[str, int]) -> int:
        ...

@dataclass
class Const(Expression):
    value: int

    def evaluate(self, environment: Dict[str, Expression]) -> 'Self':
        return self

@dataclass
class Var(Expression):
    name: str

    def evaluate(self, environment: Dict[str, Expression]) -> 'Self':
        return self

@dataclass
class BinOp(Expression):
    a: Expression
    b: Expression
    op: str

    def evaluate(self, environment: Dict[str, Expression]) -> Expression:
        a_val = environment[self.a.name]
        b_val = environment[self.b.name]

        if isinstance(a_val, Const) and  isinstance(b_val, Const):
            res_val = BinOp.apply_op(self.op, a_val.value, b_val.value)
            return Const(res_val)
        else:
            return BinOp(a_val, b_val, self.op)

    def can_invert(self):
        return isinstance(self.a, Const) or isinstance(self.b, Const)

    def invert(self, other: Const):
        a_val = self.a
        b_val = self.b

        if self.op in ('-', '/'):
            if isinstance(a_val, Const):
                result = BinOp.apply_op(self.op, a_val.value, other.value)
                return b_val, Const(result)
            elif isinstance(b_val, Const):
                result = BinOp.apply_op(BinOp.invert_op(self.op), b_val.value, other.value)
                return a_val, Const(result)
        else:
            if isinstance(a_val, Const):
                result = BinOp.apply_op(BinOp.invert_op(self.op), other.value, a_val.value)
                return b_val, Const(result)
            elif isinstance(b_val, Const):
                result = BinOp.apply_op(BinOp.invert_op(self.op), other.value, b_val.value)
                return a_val, Const(result)


    @staticmethod
    def invert_op(op: str):
        return {'+': '-', '-': '+', '*': '/', '/': '*'}[op]

    @staticmethod
    def apply_op(op: str, a_int: int, b_int: int):
        if op == '+':
            return a_int + b_int
        elif op == '-':
            return a_int - b_int
        elif op == '*':
            return a_int * b_int
        elif op == '/':
            return a_int // b_int
        else:
            raise ValueError(f"Unrecognized operation '{op}'")



@dataclass
class BinRel(Expression):
    a: str
    b: str
    op: str

    def evaluate(self, environment: Dict[str, Expression]) -> Expression:
        a_val = environment[self.a.name]
        b_val = environment[self.b.name]
        
        while isinstance(a_val, BinOp) and isinstance(b_val, Const) and a_val.can_invert():
            a_val, b_val = a_val.invert(b_val)

        return BinRel(a_val, b_val, self.op)


def read_input(alt_mode=True):
    MONKEY_CONST_RE = re.compile(r"([a-z]{4}): (\d+)")
    MONKEY_BINOP_RE = re.compile(r"([a-z]{4}): ([a-z]{4}) (.) ([a-z]{4})")

    monkeys = {}

    for line in fileinput.input():
        line = line.strip()
        if match := MONKEY_CONST_RE.match(line):
            key, value = match.groups()
            if alt_mode and key == 'humn':
                monkeys[key] = Var(name=key)
            else:
                monkeys[key] = Const(value=int(value))
        elif match := MONKEY_BINOP_RE.match(line):
            key, a, op, b = match.groups()
            if alt_mode and key == 'root':
                monkeys[key] = BinRel(a=Var(a), op='=', b=Var(b))
            else:
                monkeys[key] = BinOp(a=Var(a), op=op, b=Var(b))
        elif line == '':
            pass
        else:
            raise ValueError(f"Failed to match {line}")

    return monkeys


def evaluate(monkeys):
    unevaluated = {}
    environment = {}

    for key, monkey in monkeys.items():
        if isinstance(monkey, Const) or isinstance(monkey, Var):
            environment[key] = monkey.evaluate(environment)
        else:
            unevaluated[key] = monkey

    while unevaluated:
        new_unevaluated = {}
        for key, monkey in unevaluated.items():
            if monkey.a.name in environment and monkey.b.name in environment:
                environment[key] = monkey.evaluate(environment)
            else:
                new_unevaluated[key] = monkey
        unevaluated = new_unevaluated

    return environment


if __name__ == '__main__':
    monkeys = read_input()
    print(monkeys)
    values = evaluate(monkeys)
    print(values)
    print(values['root'])

