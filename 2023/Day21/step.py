import numpy as np
from dataclasses import dataclass
from typing import List, Set

GARDEN = '.'
ROCK = '#'
POSSIBLE_STEP = 'O'
START_POINT = 'S'

@dataclass(frozen=True)
class Coordinate:

    x: int
    y: int

    def get_adjiacent_coordinates(self) -> List['Coordinate']:
        return [
            Coordinate(y=self.y, x=self.x + 1),
            Coordinate(y=self.y, x=self.x - 1),
            Coordinate(y=self.y + 1, x=self.x),
            Coordinate(y=self.y - 1, x=self.x),
        ]

class OutOfMap(Exception):

    pass

@dataclass
class Map:

    tiles: np.ndarray
    start_coordinate: Coordinate

    @staticmethod
    def from_lines(lines: List[str]) -> 'Map':
        tiles = np.array([list(line.rstrip()) for line in lines])
        i, j = np.where(tiles == START_POINT)
        return Map(tiles=tiles, start_coordinate=Coordinate(y=i[0], x=j[0]))

    def set_tile(self, coordinate: Coordinate, element: str) -> None:
        self.tiles[coordinate.y, coordinate.x] = element

    def get_element_from_coordinate(self, coordinate: Coordinate) -> str:
        if coordinate.y < 0 or coordinate.x < 0:
            raise OutOfMap(f'coordinate {coordinate} is out of border')
        try:
            return self.tiles[coordinate.y][coordinate.x]
        except IndexError:
            raise OutOfMap(f'coordinate {coordinate} is out of border')

    def filter_out_available_walk_positions(self, coordinates: List[Coordinate]) -> List[Coordinate]:
        available_walk_coordinates = []
        for coordinate in coordinates:
            try:
                element = self.get_element_from_coordinate(coordinate=coordinate)
                if element != ROCK:
                    available_walk_coordinates.append(coordinate)
            except OutOfMap:
                # element would be out of border
                pass
        return available_walk_coordinates

    def get_and_set_steps_from_a_coordinate(self, coordinate: Coordinate) -> List[Coordinate]:
        adjacent_coordinates = coordinate.get_adjiacent_coordinates()
        available_walk_positions = self.filter_out_available_walk_positions(coordinates=adjacent_coordinates)
        self.set_tile(coordinate = coordinate, element=GARDEN)
        for step_coordinate in available_walk_positions:
            self.set_tile(coordinate = step_coordinate, element=POSSIBLE_STEP)
        return available_walk_positions

    def do_n_steps(self, n_steps: int, verbose: bool = False) -> None:
        current_coordinates = {self.start_coordinate}
        i = 0
        while i < n_steps:
            if verbose:
                print(f'iteration {i}')
            new_step_coordinates_overall: List[Coordinate] = []
            for coordinate in current_coordinates:
                new_step_coordinates = self.get_and_set_steps_from_a_coordinate(coordinate=coordinate)
                new_step_coordinates_overall.extend(new_step_coordinates)
            current_coordinates = set(new_step_coordinates_overall.copy())  # list to set really fundamental: if seme coordinate pops up from different ones, must be then evaluated once only. That removal of redundancy is fundamental!
            i += 1

    def get_n_possible_steps(self) -> int:
        n_possible_steps = 0
        for i in range(self.tiles.shape[0]):
            n_possible_steps += len([tile for tile in self.tiles[i,:] if tile == POSSIBLE_STEP])
        return n_possible_steps

    def print_graph(self) -> None:
        for i in range(self.tiles.shape[0]):
            print(''.join(self.tiles[i,:]))

if __name__ == '__main__':
    test_map_description = [
        '...........',
        '.....###.#.',
        '.###.##..#.',
        '..#.#...#..',
        '....#.#....',
        '.##..S####.',
        '.##..#...#.',
        '.......##..',
        '.##.#.####.',
        '.##..##.##.',
        '...........',
    ]
    test_map = Map.from_lines(lines=test_map_description)
    # print(test_map)
    test_map.do_n_steps(n_steps=6)
    # print(test_map)
    test_map.print_graph()
    print(f'Test map after 6 steps provides this number of steps available: {test_map.get_n_possible_steps()}')

    with open('.\map.txt', "r") as fr:
        map = Map.from_lines(lines=[line for line in fr])
    map.do_n_steps(n_steps=64)
    print(f'Map after 64 steps provides this number of steps available: {map.get_n_possible_steps()}')