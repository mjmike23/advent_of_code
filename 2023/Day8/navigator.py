from typing import List, Dict
from dataclasses import dataclass

STARTING_POSITION = 'AAA'
FINAL_POSITION = 'ZZZ'

@dataclass
class Coordinate:

    position: str
    pos_left: str
    pos_right: str

    @staticmethod
    def from_description(description: str) -> 'Coordinate':
        pos_elements = description.rstrip().split('=')
        position = pos_elements[0].strip()
        lr_elements = pos_elements[1].replace('(','').replace(')','').split(',')
        pos_left = lr_elements[0].strip()
        pos_right = lr_elements[1].strip()
        return Coordinate(position=position, pos_left=pos_left, pos_right=pos_right)

@dataclass
class Map:

    coordinates: Dict[str, Coordinate]

    def from_list_of_coordinates(coordinates: List[Coordinate]) -> 'Map':
        return Map(coordinates={coordinate.position: coordinate  for coordinate in coordinates})
    
    def get_coordinate(self, position: str) -> Coordinate:
        return self.coordinates[position]
    
    def go_left(self, starting_position: str) -> str:
        return self.coordinates[starting_position].pos_left
    
    def go_left_all(self, starting_positions: List[str]) -> List[str]:
        return [self.go_left(starting_position) for starting_position in starting_positions]
    
    def go_right(self, starting_position: str) -> str:
        return self.coordinates[starting_position].pos_right
    
    def gor_right_all(self, starting_positions: List[str]) -> List[str]:
        return [self.go_right(starting_position) for starting_position in starting_positions]

    @staticmethod
    def is_destination_reached(current_position: str, final_position: str) -> bool:
        return current_position == final_position

    @staticmethod
    def is_destination_reached_all(current_positions: List[str]) -> bool:
        return len([1 for current_position in current_positions if current_position[-1] != 'Z']) == 0

    def get_number_steps_from_start_to_end(self, path: str, starting_position: str=None, final_position: str=None) -> int:
        starting_position = starting_position if starting_position is not None else STARTING_POSITION
        final_position = final_position if final_position is not None else FINAL_POSITION
        i = 0
        if starting_position == FINAL_POSITION:
            return i
        while(True):
            for turn in path:
                i += 1
                # print(f'step {i}: start from {starting_position} to go {turn}')
                if turn == 'L':
                    starting_position=self.go_left(starting_position=starting_position)
                elif turn == 'R':
                    starting_position=self.go_right(starting_position=starting_position)
                # print(f'step {i}: reached position {starting_position}')
                if self.is_destination_reached(current_position=starting_position, final_position=final_position):
                    return i

    # enhance above
    def get_number_steps_from_start_to_end_all(self, path: str, starting_positions: List[str]=None) -> int:
        starting_positions = starting_positions if starting_positions is not None else [STARTING_POSITION]
        i = 0
        if starting_positions == [FINAL_POSITION]:
            return i
        while(True):
            for turn in path:
                i += 1
                # print(f'step {i}: start from {starting_position} to go {turn}')
                if turn == 'L':
                    starting_positions=self.go_left_all(starting_positions=starting_positions)
                elif turn == 'R':
                    starting_positions=self.gor_right_all(starting_positions=starting_positions)
                # print(f'step {i}: reached position {starting_position}')
                if self.is_destination_reached_all(current_positions=starting_positions):
                    return i

if __name__ == '__main__':
    # pos_test_description = 'GDS = (PJT, DBD)'
    # pos_test = Coordinate.from_description(pos_test_description)
    # print(pos_test)
    # test_map_p1 = [
    #     'AAA = (BBB, CCC)',
    #     'BBB = (DDD, EEE)',
    #     'CCC = (ZZZ, GGG)',
    #     'DDD = (DDD, DDD)',
    #     'EEE = (EEE, EEE)',
    #     'GGG = (GGG, GGG)',
    #     'ZZZ = (ZZZ, ZZZ)',
    # ]
    # test_map_1 = Map.from_list_of_coordinates(coordinates=[Coordinate.from_description(coord_description) for coord_description in test_map_p1])
    # # print(test_map_1)
    # print(test_map_1.get_number_steps_from_start_to_end(path='RL'))
    # test_map_p2 = [
    #     'AAA = (BBB, BBB)',
    #     'BBB = (AAA, ZZZ)',
    #     'ZZZ = (ZZZ, ZZZ)',
    # ]
    # test_map_2 = Map.from_list_of_coordinates(coordinates=[Coordinate.from_description(coord_description) for coord_description in test_map_p2])
    # # print(test_map_1)
    # print(test_map_2.get_number_steps_from_start_to_end(path='LLR'))
    # print(Map.is_destination_reached_all(current_positions=['AAZ', 'DSZ', 'SDF']))
    # print(Map.is_destination_reached_all(current_positions=['AAZ', 'DSZ', 'SDZ']))
    # test_map_g = [
    #     '11A = (11B, XXX)',
    #     '11B = (XXX, 11Z)',
    #     '11Z = (11B, XXX)',
    #     '22A = (22B, XXX)',
    #     '22B = (22C, 22C)',
    #     '22C = (22Z, 22Z)',
    #     '22Z = (22B, 22B)',
    #     'XXX = (XXX, XXX)',
    # ]
    # test_map_g = Map.from_list_of_coordinates(coordinates=[Coordinate.from_description(coord_description) for coord_description in test_map_g])
    # startings_g_a = [coord_position for coord_position in test_map_g.coordinates.keys() if coord_position[-1] == 'A']
    # print(startings_g_a)
    # print(test_map_g.get_number_steps_from_start_to_end_all(path='LR', starting_positions=startings_g_a))
    
    coordinates = []
    with open('.\map_instructions.txt', "r") as fr:
        for i, line in enumerate(fr):
            if i == 0:
                path = line.rstrip()
                continue
            if len(line) <= 1:
                continue
            coordinates.append(Coordinate.from_description(line))
    map = Map.from_list_of_coordinates(coordinates=coordinates)
    # print(path)
    # print(map)
    steps_start_to_end = map.get_number_steps_from_start_to_end(path=path)
    print(f'steps from start to end required following path are {steps_start_to_end}')
    starting_positions = [coord_position for coord_position in map.coordinates.keys() if coord_position[-1] == 'A']
    print(starting_positions)
    steps_start_to_end_ghosts = map.get_number_steps_from_start_to_end_all(path=path, starting_positions=starting_positions)
    print(f'steps from start to end for ghosts (end with A) required following path are {steps_start_to_end_ghosts}')
    