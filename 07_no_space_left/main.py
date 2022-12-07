from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
import fileinput


@dataclass
class Directory:
    name: str
    parent: Optional['Directory']
    children: Dict[str, Union['Directory', 'File']]

    @staticmethod
    def is_dir():
        return True

    def total_size(self):
        return sum(child.total_size() for child in self.children.values())


@dataclass
class File:
    name: str
    size: int

    @staticmethod
    def is_dir():
        return False

    def total_size(self):
        return self.size


def build_fs_tree():
    root = Directory(name='/', parent=None, children=dict())
    workdir = root

    for line in fileinput.input():
        if line.startswith('$ cd'):
            target = line.split()[2]
            if target == '/':
                workdir = root
            elif target == '..':
                workdir = workdir.parent
            else:
                workdir = workdir.children[target]
        elif line.startswith('$ ls'):
            pass
        elif line.startswith('dir'):
            name = line.split()[1]
            workdir.children[name] = Directory(name=name, parent=workdir, children=dict())
        elif line[0].isnumeric():
            size, name = line.split()
            workdir.children[name] = File(name=name, size=int(size))
        else:
            raise ValueError(f'no rule to handle {line}')

    return root


def display(node, indent=''):
    if node.is_dir():
        print(f'{indent}{node.name} (dir, total_size={node.total_size()})')
        for child in node.children.values():
            display(child, indent=indent + '  ')
    else:
        print(f'{indent}{node.name} (file, size={node.size})')



def walk(node):
    yield node
    if node.is_dir():
        for child in node.children.values():
            yield from walk(child)


if __name__ == '__main__':
    tree = build_fs_tree()

    display(tree)

    small_sizes = (node.total_size() for node in walk(tree) if node.is_dir() and node.total_size() <= 100000)
    print(sum(small_sizes))

    total_space = 70000000
    target_space = 30000000
    used_space = tree.total_size()
    free_space = total_space - used_space
    delete_space = target_space - free_space
    candidates = list(node for node in walk(tree) 
                      if node.is_dir() and node.total_size() >= delete_space)
    min_candidate = min(candidates, key=lambda node: node.total_size())
    print(min_candidate.total_size())
    
