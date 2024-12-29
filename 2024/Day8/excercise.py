from typing import List
from itertools import permutations
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class Pos:

    antenna: str
    antinodes: List[str]

    def __init__(self, antenna: str):
        self.antenna = antenna
        self.antinodes = []

with open("puzzle.txt", "r") as fr:
    base_map: List[List[Pos]] = []
    for line in fr:
        base_map.append([Pos(antenna=antenna) for antenna in line.rstrip()])
    distinct_antennas = set()
    for line in base_map:
        line_distinct_antennas = {pos.antenna for pos in line if pos.antenna != '.'}
        distinct_antennas = distinct_antennas.union(line_distinct_antennas)
    # print(f'The antennas are {distinct_antennas}')

    full_antennas_positions = {}
    for antenna in distinct_antennas:
        antennas_positions =[]
        for i, line in enumerate(base_map):
            for j, item in enumerate(line):
                if item.antenna == antenna:
                    antennas_positions.append((i, j))
        full_antennas_positions[antenna] = antennas_positions
    
    # single antinode echo
    s_map = deepcopy(base_map)
    for antenna, positions in full_antennas_positions.items():
        # print(f'Antenna {antenna} is in following positions {positions}')
        for coupled_antennas in set(permutations(positions, 2)):
            d_i = coupled_antennas[1][0] - coupled_antennas[0][0]
            d_j = coupled_antennas[1][1] - coupled_antennas[0][1]
            # print(f'{coupled_antennas} distance i {d_i}, j {d_j}')
            first_antinode_pos = (coupled_antennas[0][0] - d_i, coupled_antennas[0][1] - d_j)
            second_antinode_pos = (coupled_antennas[1][0] + d_i, coupled_antennas[1][1] + d_j)
            antinodes = [first_antinode_pos, second_antinode_pos]
            for antinode_pos in antinodes:
                if antinode_pos[0] < 0 or antinode_pos[1] < 0:
                    # out of bound
                    continue
                try:
                    p: Pos = s_map[antinode_pos[0]][antinode_pos[1]]
                    # print(f'valid antinode in position {antinode_pos[0]}, {antinode_pos[1]}')
                    p.antinodes.append(antenna)
                except IndexError:
                    # out of bound
                    continue

    antinodes_position_n = 0
    for i, line in enumerate(s_map):
        for j, item in enumerate(line):
            if len(item.antinodes) > 0:
                antinodes_position_n += 1
    print(antinodes_position_n)  # solution a

    # multi antinode echo
    m_map = deepcopy(base_map)
    for antenna, positions in full_antennas_positions.items():
        # print(f'Antenna {antenna} is in following positions {positions}')
        for coupled_antennas in set(permutations(positions, 2)):
            d_i = coupled_antennas[1][0] - coupled_antennas[0][0]
            d_j = coupled_antennas[1][1] - coupled_antennas[0][1]
            # print(f'{coupled_antennas} distance i {d_i}, j {d_j}')
            first_echo_iteration = 0
            second_echo_iteration = 0
            first_antinode_echo_pos = (coupled_antennas[0][0] - first_echo_iteration*d_i, coupled_antennas[0][1] - first_echo_iteration*d_j)
            second_antinode_echo_pos = (coupled_antennas[1][0] + second_echo_iteration*d_i, coupled_antennas[1][1] + second_echo_iteration*d_j)
            # first echo
            while True:
                if first_antinode_echo_pos[0] < 0 or first_antinode_echo_pos[1] < 0:
                    # out of bound
                    break
                try:
                    p: Pos = m_map[first_antinode_echo_pos[0]][first_antinode_echo_pos[1]]
                    # print(f'valid antinode in position {first_antinode_echo_pos[0]}, {first_antinode_echo_pos[1]}')
                    p.antinodes.append(antenna)
                    first_echo_iteration += 1
                    first_antinode_echo_pos = (coupled_antennas[0][0] - first_echo_iteration*d_i, coupled_antennas[0][1] - first_echo_iteration*d_j)
                except IndexError:
                    # out of bound
                    break
            # second echo
            while True:
                if second_antinode_echo_pos[0] < 0 or second_antinode_echo_pos[1] < 0:
                    # out of bound
                    break
                try:
                    p: Pos = m_map[second_antinode_echo_pos[0]][second_antinode_echo_pos[1]]
                    # print(f'valid antinode in position {second_antinode_echo_pos[0]}, {second_antinode_echo_pos[1]}')
                    p.antinodes.append(antenna)
                    second_echo_iteration += 1
                    second_antinode_echo_pos = (coupled_antennas[1][0] + second_echo_iteration*d_i, coupled_antennas[1][1] + second_echo_iteration*d_j)
                except IndexError:
                    # out of bound
                    break

    antinodes_multi_position_n = 0
    for i, line in enumerate(m_map):
        for j, item in enumerate(line):
            if len(item.antinodes) > 0:
                antinodes_multi_position_n += 1
    print(antinodes_multi_position_n)  # solution b


    