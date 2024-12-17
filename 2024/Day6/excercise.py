from typing import List, Tuple
from copy import deepcopy

def run_the_loop(map_lines: List) -> int:
    """Return 1 if exit the map, -1 inf ina loop."""
    curr_position = [0, 0]
    strafe_h = 0  # positive toward est
    strafe_v = 0  # positive toward sud
    for y, line in enumerate(map_lines):
        for x, item in enumerate(line):
            if item in ['^', 'V', '<', '>']:
                curr_position = [y, x]
                if item == '^':
                    strafe_v = -1
                    break
                if item == 'V':
                    strafe_v = 1
                    break
                if item == '<':
                    strafe_h = -1
                    break
                if item == '>':
                    strafe_h = 1
                    break
    # print(map_lines[curr_position[0]][curr_position[1]])
    # print(f'found guard at {curr_position}, s_h {strafe_h}, s_v {strafe_v}')
    # walked steps details as y_x_strafe_h_strafe_v walked
    detail_walked_steps: List[str] = []
    # set step walked also first step
    map_lines[curr_position[0]][curr_position[1]] = 'S'
    detail_walked_steps.append((curr_position[0], curr_position[1], strafe_h, strafe_v))
    while True:
        new_position = [curr_position[0] + strafe_v, curr_position[1] + strafe_h]
        if new_position[0] < 0 or new_position[1] < 0:
            # print(f'last position reached is {curr_position}')
            return 1
        try:
            faced_item = map_lines[new_position[0]][new_position[1]]
        except IndexError:
            # print(f'last position reached is {curr_position}')
            return 1
        if faced_item == '#':
            # print('Sbam! Need to turn right!')
            # the turn right
            if strafe_v == 1 and strafe_h == 0:
                strafe_h = -1
                strafe_v = 0
                continue
            if strafe_v == -1 and strafe_h == 0:
                strafe_h = 1
                strafe_v = 0
                continue
            if strafe_v == 0 and strafe_h == 1:
                strafe_h = 0
                strafe_v = 1
                continue
            if strafe_v == 0 and strafe_h == -1:
                strafe_h = 0
                strafe_v = -1
                continue
            raise Exception(f's_v {strafe_v} s_h {strafe_h} unreachable condition!')
        # if new position is alredy walked same way as before, then we are in a loop
        detail_step = f'{new_position[0]}_{new_position[1]}_{strafe_h}_{strafe_v}'
        if faced_item == 'X' and detail_step in detail_walked_steps:
            # print('you are in a loop!')
            return -1
        # transform step walked
        if faced_item != 'S':
            map_lines[new_position[0]][new_position[1]] = 'X'
        detail_walked_steps.append(detail_step)
        curr_position = new_position


with open("puzzle.txt", "r") as fr:
    puzzle_map_lines = [list(line.rstrip()) for line in fr]
    walked_puzzle_map_lines = deepcopy(puzzle_map_lines)
    run_the_loop(map_lines=walked_puzzle_map_lines)
    print(sum([map_line.count('X') + map_line.count('S') for map_line in walked_puzzle_map_lines]))  # solution a

loop_obstacles = []
for i, map_line in enumerate(walked_puzzle_map_lines):
    for j, item in enumerate(map_line):
        if item == 'X':
            new_map = deepcopy(puzzle_map_lines)
            new_map[i][j] = '#'
            if run_the_loop(map_lines=new_map) == -1:
                loop_obstacles.append((i, j))
            del new_map
print(len(loop_obstacles))  # solution b (wait couple of mins)

    