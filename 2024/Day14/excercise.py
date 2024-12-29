from dataclasses import dataclass
from typing import List

@dataclass
class Robot:

    id: int
    vel_x: int
    vel_y: int
    pos_x: int
    pos_y: int

def get_map(tiles_tall, tiles_wide) -> List[List[List]]:
    map: List[List[List]] = []
    for _ in range(tiles_tall):
        map.append([[] for _ in range(tiles_wide)])
    return map

def fit_robots_in_map(map: List[List[List]], robots: List[Robot]):
    for robot in robots:
        # pos_details x, y
        map[robot.pos_y][robot.pos_x].append(robot)

def represents_map(map: List[List[List]]):
    for line in map:
        repr_str = ''.join([str(len(x)) for x in line])
        repr_str = repr_str.replace('0', '.')
        print(repr_str)


with open("puzzle.txt", "r") as fr:
    robots: List[Robot] = []
    robot_id = 0
    for line in fr:
        line = line.rstrip()
        details = line.split(' ')
        pos_details = details[0].replace('p=', '').split(',')
        v_details = details[1].replace('v=', '').split(',')
        robot = Robot(id=robot_id, vel_x = int(v_details[0]), vel_y = int(v_details[1]), pos_x = int(pos_details[0]), pos_y = int(pos_details[1]))
        robots.append(robot)
        robot_id += 1

    tiles_tall = 103  # 7 as test
    tiles_wide = 101  # 11 as test
    initial_map = get_map(tiles_tall=tiles_tall, tiles_wide=tiles_wide)
    fit_robots_in_map(map=initial_map, robots=robots)
    # print('initial state')
    # represents_map(map=initial_map)

    n_iterations = 100
    robots_n_iter: List[Robot] = []
    for r in robots:
        final_pos_x =  (r.pos_x + (n_iterations * r.vel_x)) % tiles_wide
        final_pos_y =  (r.pos_y + (n_iterations * r.vel_y)) % tiles_tall
        robot_n_iter = Robot(id=r.id, vel_x=r.vel_x, vel_y=r.vel_y, pos_x=final_pos_x, pos_y=final_pos_y)
        robots_n_iter.append(robot_n_iter)

    n_iter_map = get_map(tiles_tall=tiles_tall, tiles_wide=tiles_wide)
    fit_robots_in_map(map=n_iter_map, robots=robots_n_iter)
    # print(f'state after {n_iterations} iterations')
    # represents_map(map=n_iter_map)

    half_tall = tiles_tall // 2
    half_wide = tiles_wide // 2
    # print(half_tall)
    # print(half_wide)

    # first quadrant
    n_r_q1 = 0
    for line in n_iter_map[:half_tall]:
        n_r_q1 += sum([len(x) for x in line[:half_wide]])
    # print(f'first quadrant robots: {n_r_q1}')

    # second quadrant
    n_r_q2 = 0
    for line in n_iter_map[:half_tall]:
        n_r_q2 += sum([len(x) for x in line[half_wide + 1:]])
    # print(f'second quadrant robots: {n_r_q2}')

    # third quadrant
    n_r_q3 = 0
    for line in n_iter_map[half_tall + 1:]:
        n_r_q3 += sum([len(x) for x in line[:half_wide]])
    # print(f'third quadrant robots: {n_r_q3}')

    # forth quadrant
    n_r_q4 = 0
    for line in n_iter_map[half_tall + 1:]:
        n_r_q4 += sum([len(x) for x in line[half_wide + 1:]])
    # print(f'forth quadrant robots: {n_r_q4}')

    print(n_r_q1 * n_r_q2 * n_r_q3 * n_r_q4)  # solution a