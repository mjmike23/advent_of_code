import numpy as np
from shapely import Polygon, Point
from dataclasses import dataclass
from typing import List, Tuple

GROUND_LEVEL = '.'
DIG_LEVEL = '#'

class Directions:

    right='R'
    left='L'
    up='U'
    down='D'

    direction_decoder = {0: right, 1: down, 2 : left, 3: up}

    @staticmethod
    def h_directions() -> Tuple[str]:
        return (Directions.right, Directions.left)
    
    @staticmethod
    def v_directions() -> Tuple[str]:
        return (Directions.up, Directions.down)

@dataclass(frozen=True)
class Coordinate:

    x: int
    y: int

    @property
    def geo_point(self) -> Point:
        return Point(self.x, self.y)

@dataclass(frozen=True)
class DigStep:

    direction: str
    n_steps: int
    hash_colour: str

    @staticmethod
    def from_description(line: str) -> 'DigStep':
        line_info = line.rstrip().rsplit(' ')
        direction = line_info[0]
        n_steps = int(line_info[1])
        hash_colour = line_info[2].removeprefix('(').removesuffix(')')
        return DigStep(direction=direction, n_steps=n_steps, hash_colour=hash_colour)

    def from_description_as_hex(line: str) -> 'DigStep':
        line_info = line.rstrip().rsplit(' ')
        hash_colour = line_info[2].removeprefix('(').removesuffix(')')
        n_steps = int(hash_colour[1:-1], 16)
        direction = Directions.direction_decoder[int(hash_colour[-1])]
        return DigStep(direction=direction, n_steps=n_steps, hash_colour=hash_colour)

    def get_final_coordinate(self, start_coordinate: Coordinate) -> Coordinate:
        if self.direction == Directions.right:
            return Coordinate(x=start_coordinate.x + self.n_steps, y=start_coordinate.y)
        if self.direction == Directions.left:
            return Coordinate(x=start_coordinate.x - self.n_steps, y=start_coordinate.y)
        if self.direction == Directions.up:
            return Coordinate(x=start_coordinate.x, y=start_coordinate.y - self.n_steps)
        if self.direction == Directions.down:
            return Coordinate(x=start_coordinate.x, y=start_coordinate.y + self.n_steps)

@dataclass
class DigField:

    max_distance_right: int
    max_distance_left: int
    max_distance_up: int
    max_distance_down: int

    @staticmethod
    def from_dig_steps(dig_steps: List[DigStep]) -> 'DigField':
        max_distance_right = 0
        max_distance_left = 0
        max_distance_up = 0
        max_distance_down = 0
        h_distance_current = 0
        v_distance_current = 0
        for ds in dig_steps:
            if ds.direction in Directions.h_directions():
                h_distance_current += ds.n_steps if ds.direction == Directions.right else - ds.n_steps
                max_distance_right = h_distance_current if h_distance_current > max_distance_right else max_distance_right
                max_distance_left = h_distance_current if h_distance_current < max_distance_left else max_distance_left
                continue
            if ds.direction in Directions.v_directions():
                v_distance_current += ds.n_steps if ds.direction == Directions.up else - ds.n_steps
                max_distance_up = v_distance_current if v_distance_current > max_distance_up else max_distance_up
                max_distance_down = v_distance_current if v_distance_current < max_distance_down else max_distance_down
                continue
            raise Exception(f'found strange direction with this dig step: {ds}')
        return DigField(max_distance_right=max_distance_right, max_distance_left=abs(max_distance_left), max_distance_up=max_distance_up, max_distance_down=abs(max_distance_down))

    @property
    def size_h(self) -> int:
        return self.max_distance_right + self.max_distance_left + 1
    
    @property
    def size_v(self) -> int:
        return self.max_distance_up + self.max_distance_down + 1

    @property
    def start_coordinate(self) -> Coordinate:
        return Coordinate(x=self.max_distance_left, y=self.max_distance_up)

class MapDig:

    dig_steps: List[DigStep]
    field: DigField
    map: np.ndarray
    dig_perimeter: Polygon

    def __init__(self, dig_steps: List[DigStep]) -> None:
        self.dig_steps = dig_steps
        self.field = DigField.from_dig_steps(dig_steps=self.dig_steps)
        self.map = np.full(shape=(self.field.size_v, self.field.size_h), fill_value=GROUND_LEVEL)
    
    @property
    def n_dug_cells(self) -> int:
        return len([self.map[i, j] for i in range(self.map.shape[0]) for j in range(self.map.shape[1]) if self.map[i, j] == DIG_LEVEL])

    @property
    def n_dug_cells_advance(self) -> int:
        """I don't need to dig all cells inside dig perimeter to understand how many them are:

        Indeed number is sum of:
        - area inside the perimeter: that is the area in the perimeter
        - out border: since the perimeter is a "thick border" wide 1, then the outside of the border is part of the cells.
        That outside part is the perimeter length itselg/2 (half part is already calculated into the area) + 1 (consider that polygon results in a lot of 90 deg corners. Summing all them up, the end is 4 corners, and out of them, the outside is 1 full tile)
        """
        inside_border = self.dig_perimeter.area
        outside_border = self.dig_perimeter.length/2 + 1
        return inside_border + outside_border

    def dig_a_step(self, start_coordinate: Coordinate, dig_step: DigStep) -> None:
        if dig_step.direction == Directions.right:
            self.map[start_coordinate.y, start_coordinate.x + 1:start_coordinate.x + 1 + dig_step.n_steps] = dig_step.hash_colour
        elif dig_step.direction == Directions.left:
            self.map[start_coordinate.y, start_coordinate.x - dig_step.n_steps:start_coordinate.x] = dig_step.hash_colour
        elif dig_step.direction == Directions.up:
            self.map[start_coordinate.y - dig_step.n_steps:start_coordinate.y, start_coordinate.x] = dig_step.hash_colour
        elif dig_step.direction == Directions.down:
            self.map[start_coordinate.y + 1: start_coordinate.y + 1 + dig_step.n_steps, start_coordinate.x] = dig_step.hash_colour

    def dig(self) -> None:
        current_coordinate = self.field.start_coordinate
        points = [current_coordinate.geo_point]
        for dig_step in self.dig_steps:
            self.dig_a_step(start_coordinate=current_coordinate, dig_step=dig_step)
            current_coordinate = dig_step.get_final_coordinate(start_coordinate=current_coordinate)
            points.append(current_coordinate.geo_point)
        self.dig_perimeter = Polygon(points)

    def dig_inside_area(self) -> None:
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                point_coordinates = Coordinate(x=j, y=i)
                if self.dig_perimeter.contains(point_coordinates.geo_point):
                    self.map[i, j] = DIG_LEVEL

    def print_graphic(self) -> None:
        for ri in range(self.map.shape[0]):
            print(''.join(self.map[ri]))


class MapDigAdv:
    """I need polygon only actually..."""

    dig_steps: List[DigStep]
    dig_perimeter: Polygon

    def __init__(self, dig_steps: List[DigStep]) -> None:
        self.dig_steps = dig_steps
        self.field = DigField.from_dig_steps(dig_steps=self.dig_steps)
        self.dig_perimeter = Polygon()

    @property
    def n_dug_cells_advance(self) -> int:
        """I don't need to dig all cells inside dig perimeter to understand how many them are:

        Indeed number is sum of:
        - area inside the perimeter: that is the area in the perimeter
        - out border: since the perimeter is a "thick border" wide 1, then the outside of the border is part of the cells.
        That outside part is the perimeter length itselg/2 (half part is already calculated into the area) + 1 (consider that polygon results in a lot of 90 deg corners. Summing all them up, the end is 4 corners, and out of them, the outside is 1 full tile)
        """
        inside_border = self.dig_perimeter.area
        outside_border = self.dig_perimeter.length/2 + 1
        return inside_border + outside_border

    def dig(self) -> None:
        current_coordinate = self.field.start_coordinate
        points = [current_coordinate.geo_point]
        for dig_step in self.dig_steps:
            current_coordinate = dig_step.get_final_coordinate(start_coordinate=current_coordinate)
            points.append(current_coordinate.geo_point)
        self.dig_perimeter = Polygon(points)


if __name__ == '__main__':
    test_dig_steps_descriptions = [
		'R 6 (#70c710)',
		'D 5 (#0dc571)',
		'L 2 (#5713f0)',
		'D 2 (#d2c081)',
		'R 2 (#59c680)',
		'D 2 (#411b91)',
		'L 5 (#8ceee2)',
		'U 2 (#caa173)',
		'L 1 (#1b58a2)',
		'U 2 (#caa171)',
		'R 2 (#7807d2)',
		'U 3 (#a77fa3)',
		'L 2 (#015232)',
		'U 2 (#7a21e3)'
    ]
    test_dig_steps = [DigStep.from_description(tdd) for tdd in test_dig_steps_descriptions]
    # print(test_dig_steps)
    test_dig_field = DigField.from_dig_steps(dig_steps=test_dig_steps)
    print(test_dig_field)
    assert test_dig_field.size_h == 7
    assert test_dig_field.size_v  == 10
    test_mp = MapDig(dig_steps=test_dig_steps)
    # print(test_mp.map)
    # test_mp.dig_a_step(start_coordinate=Coordinate(x=0, y=0), dig_step=DigStep.from_description(line='R 6 (#70c710)'))
    # print(DigStep.from_description(line='R 6 (#70c710)').get_final_coordinate(start_coordinate=Coordinate(x=0, y=0)))
    test_mp.dig()
    print('After dig the border')
    print(test_mp.map)
    print('Aafter dig the area')
    test_mp.dig_inside_area()
    print(test_mp.map)
    print(f'Test Number of cells with method digging inside is {test_mp.n_dug_cells}')
    print(f'Test Number of cells dug using advanced method is {test_mp.n_dug_cells_advance}')

    with open('.\dig_steps.txt', "r") as fr:
        dig_steps = [DigStep.from_description(line=line) for line in fr]
    map_lava = MapDig(dig_steps=dig_steps)
    map_lava.dig()
    # map_lava.dig_inside_area()  # sloooooow
    # print(f'Number of cells dug is {map_lava.n_dug_cells}')
    print(f'Number of cells dug using advanced method is {map_lava.n_dug_cells_advance}')

    test_dig_steps_hex = [DigStep.from_description_as_hex(tdd) for tdd in test_dig_steps_descriptions]
    # print(test_dig_steps_hex)
    test_mp_hex = MapDigAdv(dig_steps=test_dig_steps_hex)
    test_mp_hex.dig()
    print(f'Test Number of cells hex map dug is {test_mp_hex.n_dug_cells_advance}')

    with open('.\dig_steps.txt', "r") as fr:
        dig_steps_hex = [DigStep.from_description_as_hex(line=line) for line in fr]
    map_lava_hex = MapDigAdv(dig_steps=dig_steps_hex)
    map_lava_hex.dig()
    print(f'Number of cells hex map dug is {map_lava_hex.n_dug_cells_advance}')