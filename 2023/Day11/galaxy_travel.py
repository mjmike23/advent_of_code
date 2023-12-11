from typing import List, Tuple
from dataclasses import dataclass
import itertools

@dataclass(frozen=True)
class Coordinate:

    x: int
    y: int

    @staticmethod
    def get_min_distance_between_coordinates(coord_a: 'Coordinate', coord_b: 'Coordinate') -> int:
        return abs(coord_b.x - coord_a.x) + abs(coord_b.y - coord_a.y)

@dataclass
class UniverseElement:
    
    type: str

GALAXY = UniverseElement(type='#')
EMPTY_SPACE = UniverseElement(type='.')

@dataclass
class Universe:

    universe_map: List[List[UniverseElement]]
    is_universe_expanded: bool = False

    @property
    def space_size_row(self) -> int:
        return len(self.universe_map[0])

    @property
    def space_size_column(self) -> int:
        return len(self.universe_map)

    @staticmethod
    def from_universe_lines(universe_lines: List[str]) -> 'Universe':
        universe_map = []
        for universe_line in universe_lines:
            universe_row = [UniverseElement(type=universe_element) for universe_element in universe_line.rstrip()]
            universe_map.append(universe_row)
        return Universe(universe_map=universe_map)
    
    def print_visual_repr(self) -> None:
        for universe_row in self.universe_map:
            print(''.join([un_el.type for un_el in universe_row])) 
    
    def is_universe_row_only_empty_space(self, row_id: int) -> bool:
        return not any([universe_row_element for universe_row_element in self.universe_map[row_id] if universe_row_element == GALAXY])

    def is_universe_column_only_empty_space(self, column_id: int) -> bool:
        return not any([universe_row[column_id] for universe_row in self.universe_map if universe_row[column_id] == GALAXY])
    
    def get_empty_space_row(self) -> List[UniverseElement]:
        return list(itertools.repeat(EMPTY_SPACE, self.space_size_row))
    
    def get_empty_space_column(self) -> List[UniverseElement]:
        return list(itertools.repeat(EMPTY_SPACE, self.space_size_column))

    def expand_universe_row(self, row_id: int) -> None:
        self.universe_map.insert(row_id, self.get_empty_space_row())

    def expand_universe_column(self, column_id: int) -> None:
        for universe_row in self.universe_map:
            universe_row.insert(column_id, EMPTY_SPACE)

    def get_row_indexes_to_explode(self) -> List[int]:
        return [row_id for row_id in range(self.space_size_row) if self.is_universe_row_only_empty_space(row_id=row_id)]
    
    def get_column_indexes_to_explode(self) -> List[int]:
        return [column_id for column_id in range(self.space_size_column) if self.is_universe_column_only_empty_space(column_id=column_id)]

    def expand_universe(self) -> None:
        if self.is_universe_expanded:
            print('Universe has been already expanded, hence not expanding again')
            return
        rows_index_to_explode = self.get_row_indexes_to_explode()
        column_index_to_explode = self.get_column_indexes_to_explode()
        # expand rows first
        correction_row_factor = 0  # needed when we will expand: first index will be ok, then next one will be original index + 1 (since exploding the exploded universe by first one) and so on
        for row_id in rows_index_to_explode:
            self.expand_universe_row(row_id=row_id + correction_row_factor)
            correction_row_factor += 1

        # expand_columns_then
        correction_column_factor = 0  # needed when we will expand: first index will be ok, then next one will be original index + 1 (since exploding the exploded universe by first one) and so on
        for column_id in column_index_to_explode:
            self.expand_universe_column(column_id=column_id + correction_column_factor)
            correction_column_factor += 1
        self.is_universe_expanded = True

    def get_galaxies_coordinates(self) -> List[Coordinate]:
        galaxy_coordinates = []
        for row_id, universe_row in enumerate(self.universe_map):
            galaxy_coordinates.extend([Coordinate(x=col_id, y=row_id) for col_id, un_el in enumerate(universe_row) if un_el == GALAXY])
        return galaxy_coordinates
        
    def get_all_galaxies_pairs(self) -> List[Tuple[Coordinate]]:
        return list(itertools.combinations(self.get_galaxies_coordinates(), 2))
    
    def get_min_distance_across_galaxy_from_unexploded_map(self, galaxy_coord_a: Coordinate, galaxy_coord_b: Coordinate, light_jump_explosion_step: int, column_indexes_light_jumps: List[int] = None, row_indexes_light_jumps: List[int] = None) -> int:  # light_jump_explosion_step 2 means 1 jump becomes 2 elements 
        assert not self.is_universe_expanded,  'That method can be used if looking still unexpanded universe'
        column_indexes_light_jumps = column_indexes_light_jumps if column_indexes_light_jumps is not None else self.get_column_indexes_to_explode()
        row_indexes_light_jumps = row_indexes_light_jumps if row_indexes_light_jumps is not None else self.get_row_indexes_to_explode()
        base_unexploded_min_distance = Coordinate.get_min_distance_between_coordinates(galaxy_coord_a, galaxy_coord_b)
        n_horizontal_light_jumps = len([col_index for col_index in column_indexes_light_jumps if (col_index > galaxy_coord_a.x and col_index < galaxy_coord_b.x) or (col_index > galaxy_coord_b.x and col_index < galaxy_coord_a.x)])  # space to explode is between the galaxies
        n_vertical_light_jumps = len([row_index for row_index in row_indexes_light_jumps if (row_index > galaxy_coord_a.y and row_index < galaxy_coord_b.y) or (row_index > galaxy_coord_b.y and row_index < galaxy_coord_a.y)])  # space to explode is between the galaxies
        return base_unexploded_min_distance - (n_horizontal_light_jumps + n_vertical_light_jumps) + (n_horizontal_light_jumps * light_jump_explosion_step + n_vertical_light_jumps * light_jump_explosion_step)

if __name__ == '__main__':
    test_universe_lines = [
        '...#......',
        '.......#..',
        '#.........',
        '..........',
        '......#...',
        '.#........',
        '.........#',
        '..........',
        '.......#..',
        '#...#.....',
    ]
    test_universe = Universe.from_universe_lines(universe_lines=test_universe_lines)
    # print(test_universe)
    # assert test_universe.is_universe_column_only_empty_space(column_id=2)
    # assert not test_universe.is_universe_column_only_empty_space(column_id=1)
    # assert test_universe.is_universe_row_only_empty_space(row_id=3)
    # assert not test_universe.is_universe_row_only_empty_space(row_id=4)
    # assert test_universe.space_size_column == 10
    # assert test_universe.space_size_row == 10
    # print(test_universe.get_empty_space_column())
    # print(test_universe.get_row_indexes_to_explode())
    # print(test_universe.get_column_indexes_to_explode())
    # # test_universe.expand_universe_column(column_id=2)
    # # test_universe.print_visual_repr()
    test_universe.expand_universe()
    # test_universe.print_visual_repr()
    # print(test_universe.get_galaxies_coordinates())
    # assert Coordinate.get_min_distance_between_coordinates(coord_a=Coordinate(x=4, y=0), coord_b=Coordinate(x=9, y=10)) == 15
    # print(test_universe.get_all_galaxies_pairs())
    # print(len(test_universe.get_all_galaxies_pairs()))
    print(f'Test universe sum of min distance across galaxies is {sum([Coordinate.get_min_distance_between_coordinates(pair_gal[0], pair_gal[1])  for pair_gal in test_universe.get_all_galaxies_pairs()])}')

    # approach 2: no explosion
    test_universe = Universe.from_universe_lines(universe_lines=test_universe_lines)
    print(f'Test universe sum of min distance across galaxies is {sum([test_universe.get_min_distance_across_galaxy_from_unexploded_map(galaxy_coord_a=pair_gal[0], galaxy_coord_b=pair_gal[1], light_jump_explosion_step=2)  for pair_gal in test_universe.get_all_galaxies_pairs()])}')
    print(f'Test universe sum of min distance across galaxies far light jump is is {sum([test_universe.get_min_distance_across_galaxy_from_unexploded_map(galaxy_coord_a=pair_gal[0], galaxy_coord_b=pair_gal[1], light_jump_explosion_step=100)  for pair_gal in test_universe.get_all_galaxies_pairs()])}')

    with open(".\space.txt", "r") as fr:
        universe = Universe.from_universe_lines(universe_lines=[line for line in fr])
    universe.expand_universe()
    print(f'Universe sum of min distance across galaxies is {sum([Coordinate.get_min_distance_between_coordinates(pair_gal[0], pair_gal[1])  for pair_gal in universe.get_all_galaxies_pairs()])}')
    
    # approach 2: no explosion -> step 1000000
    with open(".\space.txt", "r") as fr:
        universe = Universe.from_universe_lines(universe_lines=[line for line in fr])
    column_indexes_light_jumps = universe.get_column_indexes_to_explode()
    row_indexes_light_jumps = universe.get_row_indexes_to_explode()
    print(f'Universe sum of min distance across galaxies far light jump is is {sum([universe.get_min_distance_across_galaxy_from_unexploded_map(galaxy_coord_a=pair_gal[0], galaxy_coord_b=pair_gal[1], light_jump_explosion_step=1000000, column_indexes_light_jumps=column_indexes_light_jumps, row_indexes_light_jumps=row_indexes_light_jumps)  for pair_gal in universe.get_all_galaxies_pairs()])}')
