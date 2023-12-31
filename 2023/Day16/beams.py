from typing import List, Tuple
from dataclasses import dataclass

# puzzle mocked \ as $, to read correctly, not the escapes

SPACE = '.'
MIRROR_NW_SE = '/'
MIRROR_SW_NE = '\\'
SPLITTER_H = '-'
SPLITTER_V = '|'


@dataclass(frozen=True)
class Position:

    x: int
    y: int


@dataclass(frozen=True)
class Vector:

    north: bool
    south: bool
    west: bool
    east: bool

V_N = Vector(north=True, south=False, west=False, east=False)
V_NW = Vector(north=True, south=False, west=True, east=False)
V_W = Vector(north=False, south=False, west=True, east=False)
V_SW = Vector(north=False, south=True, west=True, east=False)
V_S = Vector(north=False, south=True, west=False, east=False)
V_SE = Vector(north=False, south=True, west=False, east=True)
V_E = Vector(north=False, south=False, west=False, east=True)
V_NE = Vector(north=True, south=False, west=False, east=True)
VEXTOR_GRAPHIC_REPR = {V_N: '^', V_S: 'v', V_W: '<', V_E: '>'}

def get_vectors_through_mirror_element(vector: Vector, mirror_element: str) -> List[Vector]:
    if mirror_element == SPACE:
        return [vector]
    if mirror_element == MIRROR_NW_SE:
        # reflect back
        if vector in [V_NW, V_SE]:
            return []
        # cross with no change
        if vector in [V_NE, V_SW]:
            return [vector]
        # 90 degree tilt
        if vector == V_N:
            return [V_E]
        if vector == V_E:
            return [V_N]
        if vector == V_S:
            return [V_W]
        if vector == V_W:
            return [V_S]
    if mirror_element == MIRROR_SW_NE:
        if vector in [V_SW, V_NE]:
            return []
        if vector in [V_NW, V_SE]:
            return [vector]
        if vector == V_N:
            return [V_W]
        if vector == V_W:
            return [V_N]
        if vector == V_S:
            return [V_E]
        if vector == V_E:
            return [V_S]
    if mirror_element == SPLITTER_H:
        if vector in [V_W, V_E]:
            return [vector]
        if vector in [V_N, V_S, V_NW, V_SW, V_SE, V_NE]:
            return [V_W, V_E]
    if mirror_element == SPLITTER_V:
        if vector in [V_N, V_S]:
            return [vector]
        if vector in [V_W, V_E, V_NW, V_SW, V_SE, V_NE]:
            return [V_N, V_S]
    raise Exception(f'Unreachable: case vector {vector} and mirror element {mirror_element}')

@dataclass(frozen=True)
class Beam:

    position: Position
    direction: Vector

    def get_next_position(self) -> Position:
        # x
        if self.direction in [V_N, V_S]:
            next_x = self.position.x
        elif self.direction in [V_E, V_NE, V_SE]:
            next_x = self.position.x  + 1
        elif self.direction in [V_W, V_NW, V_SW]:
            next_x = self.position.x  - 1
        # y
        if self.direction in [V_W, V_E]:
            next_y = self.position.y
        elif self.direction in [V_S, V_SE, V_SW]:
            next_y = self.position.y  + 1
        elif self.direction in [V_N, V_NW, V_NE]:
            next_y = self.position.y  - 1
        return Position(x=next_x, y=next_y)


@dataclass
class Tile:

    element: str
    is_energized: bool
    vector_energizers: List[Vector]

    @property
    def element_energized(self) -> str:
        return '#' if self.is_energized else self.element
    
    @property
    def element_beam_invested(self) -> str:
        if self.element != SPACE:
            return self.element
        if len(self.vector_energizers) > 1:
            return str(len(self.vector_energizers))
        if len(self.vector_energizers) == 1:
            return VEXTOR_GRAPHIC_REPR[self.vector_energizers[0]]
        return self.element

class OutOfMap(Exception):

    pass

@dataclass
class MirrorMap:

    tiles: List[List[Tile]]

    @property
    def n_energized_tiles(self) -> int:
        return sum([len([tile for tile in tr if tile.is_energized]) for tr in self.tiles])

    def from_description(map_line_descriptions: str) -> 'MirrorMap':
        tiles = []
        for line in map_line_descriptions:
            tiles.append([Tile(element=el, is_energized=False, vector_energizers=[]) for el in line.replace('$', MIRROR_SW_NE)])  # thanks python for the escapes...
        return MirrorMap(tiles=tiles)

    def get_tile(self, position: Position) -> Tile:
        if position.y < 0 or position.x < 0:
            raise OutOfMap(f'position {position} is out of border')
        try:
            return self.tiles[position.y][position.x]
        except IndexError:
            raise OutOfMap(f'position {position} is out of border')
    
    def energize_by_beam(self, beam: Beam) -> None:
        t = self.get_tile(position=beam.position)
        t.is_energized = True
        t.vector_energizers.append(beam.direction)

    def reset_energy(self) -> None:
        for tr in self.tiles:
            for tile in tr:
                tile.is_energized = False
                tile.vector_energizers = []

    def spread_beam(self, start_beams: List[Beam], max_beam_steps: int = None) -> None:
        current_beams = start_beams
        next_step_beams = []
        i = 0
        while len(current_beams) != 0:
            i += 1
            # print(f'{i}: {current_beams}')
            next_step_beams = []
            for beam in current_beams:
                self.energize_by_beam(beam=beam)
                next_position = beam.get_next_position()
                try:
                    next_tile = self.get_tile(position=next_position)
                except OutOfMap:
                    # beam going out of map, so no next
                    continue
                next_vectors = get_vectors_through_mirror_element(vector=beam.direction, mirror_element=next_tile.element)
                next_step_beams.extend([Beam(position=next_position, direction=vector) for vector in next_vectors if vector not in next_tile.vector_energizers])  # check on vector_energizers for already passed a beam with same direction here, so no next (circular reflection)
            current_beams = next_step_beams.copy()
            if max_beam_steps is not None and  i > max_beam_steps:
                # print('reached end of steps')
                return
            
    def get_beams_from_edge_tile(self, edge_position: Position, vector: Vector) -> List[Beam]:
        assert edge_position.x == 0 or edge_position.y == 0 or edge_position.x == len(self.tiles[0]) - 1 or edge_position.y == len(self.tiles) - 1,  'position not on the edge'
        return [Beam(position=edge_position, direction=vector) for vector in get_vectors_through_mirror_element(vector=vector, mirror_element=self.get_tile(position=edge_position).element)]

    def get_edge_positions_and_vectors(self) -> List[Tuple[Position, Vector]]:
        edge_position_and_vectors = []
        len_tile_raw = len(self.tiles[0])
        len_tile_col = len(self.tiles)
        for i in range(len_tile_raw):
            edge_position_and_vectors.append((Position(x=i, y=0), V_S))
            edge_position_and_vectors.append((Position(x=i, y=len_tile_raw - 1), V_N))
        for i in range(len_tile_col):
            edge_position_and_vectors.append((Position(x=0, y=i), V_E))
            edge_position_and_vectors.append((Position(x=len_tile_col - 1, y=i), V_W))          
        return edge_position_and_vectors

    def print_as_energized(self) -> None:
        for tr in self.tiles:
            print(''.join([tile.element_energized for tile in tr]))

    def print_beam_flow(self) -> None:
        for tr in self.tiles:
            print(''.join([tile.element_beam_invested for tile in tr]))

if __name__ == '__main__':
    test_mirror_map_lines = [
        '.|...$....',
        '|.-.$.....',
        '.....|-...',
        '........|.',
        '..........',
        '.........$',
        '..../.$$..',
        '.-.-/..|..',
        '.|....-|.$',
        '..$$.|....',
    ]
    test_mirror_map = MirrorMap.from_description(map_line_descriptions=test_mirror_map_lines)
    # print(test_mirror_map)
    print('Test map before beam flow')
    test_mirror_map.print_beam_flow()
    print('')
    tile_a = test_mirror_map.get_tile(position=Position(x=4, y=1))
    assert tile_a.element == MIRROR_SW_NE
    tile_b = test_mirror_map.get_tile(position=Position(x=9, y=5))
    assert tile_b.element ==  MIRROR_SW_NE
    # print(test_mirror_map.n_energized_tiles)
    t_iteration_start_beams = test_mirror_map.get_beams_from_edge_tile(edge_position=Position(x=0, y=0), vector=V_E)
    test_mirror_map.spread_beam(start_beams=t_iteration_start_beams)
    print(f'Test map energized tiles are {test_mirror_map.n_energized_tiles}')
    print('')
    test_mirror_map.print_as_energized()
    print('')
    test_mirror_map.print_beam_flow()
    print('')

    with open('.\mirror_map.txt', "r") as fr:
        mirror_map = MirrorMap.from_description(map_line_descriptions=[line.rstrip() for line in fr])
    start_beams = mirror_map.get_beams_from_edge_tile(edge_position=Position(x=0, y=0), vector=V_E)
    # print(start_beams)
    mirror_map.spread_beam(start_beams=start_beams, max_beam_steps=None)
    print(f'Map energized tiles are {mirror_map.n_energized_tiles}')
    # print('')
    # mirror_map.print_beam_flow()
    # print('')
    # mirror_map.print_as_energized()
    # print('')

    start_point_max_energy = None
    max_energied_tiles = 0
    for edge_pos_vector in test_mirror_map.get_edge_positions_and_vectors():
        # print(edge_pos_vector)
        test_mirror_map.reset_energy()
        t_iteration_start_beams = test_mirror_map.get_beams_from_edge_tile(edge_position=edge_pos_vector[0], vector=edge_pos_vector[1])
        # print(f'start beams {t_iteration_start_beams}')
        test_mirror_map.spread_beam(start_beams=t_iteration_start_beams)
        n_energy_try = test_mirror_map.n_energized_tiles
        # print(n_energy_try)
        if n_energy_try > max_energied_tiles:
            max_energied_tiles = n_energy_try
            start_point_max_energy = edge_pos_vector
    print(f'Test map energized tiles max is {max_energied_tiles}, starting from edge point {start_point_max_energy}')

    start_point_max_energy = None
    max_energied_tiles = 0
    for edge_pos_vector in mirror_map.get_edge_positions_and_vectors():
        mirror_map.reset_energy()
        iteration_start_beams = mirror_map.get_beams_from_edge_tile(edge_position=edge_pos_vector[0], vector=edge_pos_vector[1])
        mirror_map.spread_beam(start_beams=iteration_start_beams)
        n_energy_try = mirror_map.n_energized_tiles
        if n_energy_try > max_energied_tiles:
            max_energied_tiles = n_energy_try
            start_point_max_energy = edge_pos_vector
    print(f'Map energized tiles max is {max_energied_tiles}, starting from edge point {start_point_max_energy}')
