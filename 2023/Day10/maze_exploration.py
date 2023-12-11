from typing import List, Set
from dataclasses import dataclass

START_NODE_TYPE = 'S'
END_PATH_DUMMY_TYPE = 'EEE'
TILE_TYPE = '.'

X_MAZE_BOUND = 140
Y_MAZE_BOUND = 140

class NoConnectionException(Exception):

    pass

class NoExistingNodeException(Exception):

    pass

@dataclass(frozen=True)
class Coordinate:

    x: int
    y: int

    @property
    def next_north(self) -> 'Coordinate':
        return Coordinate(self.x, self.y + 1)

    @property
    def next_south(self) -> 'Coordinate':
        return Coordinate(self.x, self.y - 1)

    @property
    def next_east(self) -> 'Coordinate':
        return Coordinate(self.x + 1, self.y)

    @property
    def next_west(self) -> 'Coordinate':
        return Coordinate(self.x - 1, self.y)

    @property
    def is_out_of_bound(self) -> bool:
        return self.x < 1 or self.x > X_MAZE_BOUND or self.y < 1 or self.y > Y_MAZE_BOUND

    @staticmethod
    def exclude_out_of_bound_coordinates(coordinates: Set['Coordinate']) -> Set['Coordinate']:
        return {coordinate for coordinate in coordinates if not coordinate.is_out_of_bound}
    
    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, Coordinate):
            if self.y == obj.y:
                return self.x > obj.x
            return self.y > obj.y
        raise NotImplemented

@dataclass(frozen=True)
class MazeNode:

    type: str
    coordinate: Coordinate

    @property
    def is_tile(self) -> bool:
        return self.type == TILE_TYPE

    def get_connected_coordinates(self) -> Set[Coordinate]:
        if self.type == '|':
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_north, self.coordinate.next_south})
        if self.type == '-':
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_west, self.coordinate.next_east})
        if self.type == 'L':
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_north, self.coordinate.next_east})
        if self.type == 'J':
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_north, self.coordinate.next_west})
        if self.type == '7':
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_south, self.coordinate.next_west})
        if self.type == 'F':
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_south, self.coordinate.next_east})
        if self.type == START_NODE_TYPE:  # starting point, like a jolly
            return Coordinate.exclude_out_of_bound_coordinates({self.coordinate.next_south, self.coordinate.next_north, self.coordinate.next_west, self.coordinate.next_east})
        return set()

    def is_coordinate_connected(self, coordinate: Coordinate) -> bool:
        return coordinate in self.get_connected_coordinates()

    def get_next_node_connected_coordinate(self, previous_coordinate: Coordinate) -> Coordinate:
        """Get coordinate of next node, considering we are in current node, and we came from previous_coordinate"""
        try:
            return [coordinate for coordinate in self.get_connected_coordinates() if coordinate != previous_coordinate][0]
        except IndexError:
            raise NoConnectionException(f'there is no node connected to node {self}')

    @staticmethod
    def get_connector_across_nodes(node_a: 'MazeNode', node_b: 'MazeNode', coordinate_connector: Coordinate) -> 'MazeNode':
        for connector_type in '|-LJ7F':
            candidate_connector = MazeNode(type=connector_type, coordinate=coordinate_connector)
            if candidate_connector.get_connected_coordinates() == {node_a.coordinate, node_b.coordinate}:
                return candidate_connector
        raise Exception(f'Unable to connect nodes {node_a} and {node_b} in coordinates {coordinate_connector}')

    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, MazeNode):
            return self.coordinate > obj.coordinate
        raise NotImplemented

END_DUMMY_NODE = MazeNode(type=END_PATH_DUMMY_TYPE, coordinate=Coordinate(x=-1, y=-1))


class AdjacentCornerNodeCombo:

    CORNER_PIPES = {'L', '7', 'J', 'F'}

    @staticmethod
    def is_horizontal_flex(note_type_west: str, note_type_east: str) -> bool:
        """Flesso tangente orizzontale"""
        if note_type_west == 'L' and note_type_east == '7':
            return True
        if note_type_west == 'F' and note_type_east == 'J':
            return True
        return False
    
    @staticmethod
    def is_vertical_flex(note_type_south: str, note_type_north: str) -> bool:
        """Flesso tangente verticale"""
        if note_type_north == 'F' and note_type_south == 'J':
            return True
        if note_type_north == '7' and note_type_south == 'L':
            return True
        return False
    
    @staticmethod
    def get_number_vertical_flex(column_pipe_types_south_to_north: List[str]) -> List[str]:
        relevant_column_pipe_types = [pt for pt in column_pipe_types_south_to_north if pt in AdjacentCornerNodeCombo.CORNER_PIPES]
        count_flex = 0
        for i, pt in enumerate(relevant_column_pipe_types[:-1]):
            if i%2!=0:
                continue
            if AdjacentCornerNodeCombo.is_vertical_flex(note_type_south=pt, note_type_north=relevant_column_pipe_types[i + 1]):
                count_flex += 1
        return count_flex

    @staticmethod
    def get_number_horizontal_flex(row_pipe_types_west_to_east: List[str]) -> List[str]:
        relevant_column_pipe_types = [pt for pt in row_pipe_types_west_to_east if pt in AdjacentCornerNodeCombo.CORNER_PIPES]
        count_flex = 0
        for i, pt in enumerate(relevant_column_pipe_types[:-1]):
            if i%2!=0:
                continue
            if AdjacentCornerNodeCombo.is_horizontal_flex(note_type_west=pt, note_type_east=relevant_column_pipe_types[i + 1]):
                count_flex += 1
        return count_flex

@dataclass
class Maze:

    nodes: Set[MazeNode]
    loop_pipe_path: List[MazeNode] = None

    @staticmethod
    def from_maze_lines(maze_lines: List[str]) -> 'Maze':
        nodes = []
        for ri, maze_line in enumerate(maze_lines[::-1]):  # reading from top to bottom, the y system is reversed, that's why we need to invert reading lines
            maze_row_elements = [MazeNode(type=node_element, coordinate=Coordinate(x=ci + 1, y=ri + 1)) for ci, node_element in enumerate(maze_line.rstrip())]
            nodes.extend(maze_row_elements)
        return Maze(nodes=set(nodes))

    @property
    def tiles(self) -> Set[MazeNode]:
        assert self.loop_pipe_path is not None,  'evaluate pipe path before using it'
        return {node for node in self.nodes.difference(set(self.loop_pipe_path))}  # at the end all that is not loop can be tile..

    def get_loop_pipe_path_column_nodes_south_to_north(self, x: int) -> Set[MazeNode]:
        assert self.loop_pipe_path is not None,  'evaluate pipe path before using it'
        column_nodes = [pn for pn in self.loop_pipe_path if pn.coordinate.x == x]
        column_nodes.sort()
        return column_nodes

    def get_loop_pipe_path_row_nodes_west_to_east(self, y: int) -> Set[MazeNode]:
        assert self.loop_pipe_path is not None,  'evaluate pipe path before using it'
        row_nodes = [pn for pn in self.loop_pipe_path if pn.coordinate.y == y]
        row_nodes.sort()
        return row_nodes


    def get_node_from_coordinates(self, coordinate: Coordinate) -> MazeNode:
        try:
            return [node for node in self.nodes if node.coordinate == coordinate][0]
        except IndexError:
            raise NoExistingNodeException(f'no existing node for coordinate {coordinate}')

    def get_start_node(self) -> MazeNode:
        return [node for node in self.nodes if node.type == START_NODE_TYPE][0]

    def get_connected_nodes_from_current_one(self, current_node: MazeNode) -> Set[MazeNode]:
        return set(self. get_node_from_coordinates(coordinate=connected_coordinate) for connected_coordinate in current_node.get_connected_coordinates())

    def get_next_node_connected_from_following_path(self, current_node: MazeNode, previous_node: MazeNode) -> MazeNode:
        return self.get_node_from_coordinates(coordinate=current_node.get_next_node_connected_coordinate(previous_coordinate=previous_node.coordinate))

    def are_nodes_connected(self, previous_node: MazeNode, current_node: MazeNode) -> bool:
        return current_node.is_coordinate_connected(coordinate=previous_node.coordinate)

    def follow_path_from_node_to_start(self, previous_node: MazeNode, starting_node: MazeNode) -> List[MazeNode]:
        if not self.are_nodes_connected(previous_node=previous_node, current_node=starting_node):
            raise NoConnectionException(f'nodes {previous_node} and {starting_node} are not connected, hence not possible to give a direction to follow a path')
        current_step_node = starting_node
        previous_step_node = previous_node
        steps = [starting_node]
        while True:
            # print(f'iteration {len(steps)} we are in {current_step_node} coming from {previous_step_node}')
            try:
                next_node = self.get_next_node_connected_from_following_path(current_node=current_step_node, previous_node=previous_step_node)
                # print(f'iteration {len(steps)} move to {next_node}')
            except (NoConnectionException, NoExistingNodeException) as e:
                print(e)
                steps.append(END_DUMMY_NODE)
                break 
            if not self.are_nodes_connected(previous_node=previous_step_node, current_node=current_step_node):  # to understand if the step is legit
                steps.append(END_DUMMY_NODE)
                break
            steps.append(next_node)
            if next_node.type == START_NODE_TYPE:
                # print('we reach start node!')
                break
            previous_step_node = current_step_node
            current_step_node = next_node
        return steps

    @staticmethod
    def does_path_reach_start(node_steps: List[MazeNode]) -> bool:
        return node_steps[-1].type == START_NODE_TYPE

    def get_loop_path_from_start_node(self) -> List[MazeNode]:
        start_node = self.get_start_node()
        for start_adjacent_node in self.get_connected_nodes_from_current_one(current_node=start_node):
            # print(f'Experiment going from {start_adjacent_node}')
            try:
                self.follow_path_from_node_to_start(previous_node=start_node, starting_node=start_adjacent_node)
            except NoConnectionException as e:
                print(e)
                continue
            path = self.follow_path_from_node_to_start(previous_node=start_node, starting_node=start_adjacent_node)
            if self.does_path_reach_start(node_steps=path):
                return path
        raise Exception('there is no path that start and ends from starting point!')

    def set_loop_path_from_start_node(self, loop_path: List[MazeNode] =  None) -> None:
        if self.loop_pipe_path is None:
            loop_path = loop_path if loop_path is not None else self.get_loop_path_from_start_node()
            if loop_path[-1].type == START_NODE_TYPE:
                replace_start_node = MazeNode.get_connector_across_nodes(node_a=loop_path[0], node_b=loop_path[-2], coordinate_connector=loop_path[-1].coordinate)  # last of the path as builded is start, first and one before last are adjacents
                loop_path = loop_path[:-1] + [replace_start_node]
            self.loop_pipe_path = loop_path

    def check_node_for_area_control(self, node: MazeNode) -> None:
        assert self.loop_pipe_path is not None,  'we can execute node check in/out area only after evaluating pipe path'
        assert node in self.tiles,  'we do teh check for tile node only'

    def count_touches_pipe_path_vertical(self, pipe_nodes_column_zone_south_to_north: List[MazeNode]) -> int:
        """Check border crossed vertically
        
        That is the sum of pure horizontal borders and vertical flex
        """
        n_pure_horizontal_borders_crossed = len([node for node in pipe_nodes_column_zone_south_to_north if node.type == '-'])
        n_vertical_flex = AdjacentCornerNodeCombo.get_number_vertical_flex(column_pipe_types_south_to_north=[node.type for node in pipe_nodes_column_zone_south_to_north])
        return n_pure_horizontal_borders_crossed + n_vertical_flex

    def count_touches_pipe_path_horizontal(self, pipe_nodes_row_zone_west_to_east: List[MazeNode]) -> int:
        n_pure_horizontal_borders_crossed = len([node for node in pipe_nodes_row_zone_west_to_east if node.type == '|'])
        n_horizontal_flex = AdjacentCornerNodeCombo.get_number_horizontal_flex(row_pipe_types_west_to_east=[node.type for node in pipe_nodes_row_zone_west_to_east])
        return n_pure_horizontal_borders_crossed + n_horizontal_flex

    def count_touches_pipe_path_north(self, tile_node: MazeNode, pipe_nodes_column_zone_south_to_north: List[MazeNode]) -> int:
        north_pipe_nodes_south_to_north = [node for node in pipe_nodes_column_zone_south_to_north if node.coordinate.y > tile_node.coordinate.y]
        return self.count_touches_pipe_path_vertical(pipe_nodes_column_zone_south_to_north=north_pipe_nodes_south_to_north)

    def count_touches_pipe_path_south(self, tile_node: MazeNode, pipe_nodes_column_zone_south_to_north: List[MazeNode]) -> int:
        south_pipe_nodes_south_to_north = [node for node in pipe_nodes_column_zone_south_to_north if node.coordinate.y < tile_node.coordinate.y]
        return self.count_touches_pipe_path_vertical(pipe_nodes_column_zone_south_to_north=south_pipe_nodes_south_to_north)

    def count_touches_pipe_path_east(self, tile_node: MazeNode, pipe_nodes_row_zone_west_to_east: List[MazeNode]) -> int:
        east_pipe_nodes_west_to_east = [node for node in pipe_nodes_row_zone_west_to_east if node.coordinate.x > tile_node.coordinate.x]
        return self.count_touches_pipe_path_horizontal(pipe_nodes_row_zone_west_to_east=east_pipe_nodes_west_to_east)

    def count_touches_pipe_path_west(self, tile_node: MazeNode, pipe_nodes_row_zone_west_to_east: List[MazeNode]) -> int:
        west_pipe_nodes_west_to_east = [node for node in pipe_nodes_row_zone_west_to_east if node.coordinate.x > tile_node.coordinate.x]
        return self.count_touches_pipe_path_horizontal(pipe_nodes_row_zone_west_to_east=west_pipe_nodes_west_to_east)

    def is_tile_inside_pipe_path_loop(self, tile_node: MazeNode) -> bool:
        self.check_node_for_area_control(node=tile_node)
        tile_column_loop_path_nodes_south_to_north = self.get_loop_pipe_path_column_nodes_south_to_north(x=tile_node.coordinate.x)
        if self.count_touches_pipe_path_north(tile_node=tile_node, pipe_nodes_column_zone_south_to_north=tile_column_loop_path_nodes_south_to_north)%2 == 0:
            return False
        if self.count_touches_pipe_path_south(tile_node=tile_node, pipe_nodes_column_zone_south_to_north=tile_column_loop_path_nodes_south_to_north)%2 == 0:
            return False
        tile_row_loop_path_nodes_west_to_east = self.get_loop_pipe_path_row_nodes_west_to_east(y=tile_node.coordinate.y)
        if self.count_touches_pipe_path_east(tile_node=tile_node, pipe_nodes_row_zone_west_to_east=tile_row_loop_path_nodes_west_to_east)%2 == 0:
            return False
        if self.count_touches_pipe_path_west(tile_node=tile_node, pipe_nodes_row_zone_west_to_east=tile_row_loop_path_nodes_west_to_east)%2 == 0:
            return False
        return True

if __name__ == '__main__':
    # coord_test = Coordinate(x=3, y=5)
    # assert coord_test.next_north == Coordinate(x=3, y=6)
    # assert coord_test.next_south == Coordinate(x=3, y=4)
    # assert coord_test.next_east == Coordinate(x=4, y=5)
    # assert coord_test.next_west == Coordinate(x=2, y=5)
    # md_test = MazeNode(type='F', coordinate=coord_test)
    # print(md_test)
    # print(md_test.get_connected_coordinates())
    # print(md_test.get_next_node_connected_coordinate(previous_coordinate=Coordinate(x=4, y=5)))
    # test_maze_1 = [
    #     '.....',
    #     '.S-7.',
    #     '.|.|.',
    #     '.L-J.',
    #     '.....',
    # ]
    # test_maze_1 = Maze.from_maze_lines(maze_lines=test_maze_1)
    # # print(test_maze_1)
    # # pipe_node = test_maze_1.get_node_from_coordinates(coordinate=Coordinate(x=4, y=4))
    # # print(pipe_node)
    # # print(pipe_node.get_connected_coordinates())
    # # print(pipe_node.get_next_node_connected_coordinate(previous_coordinate=Coordinate(x=2, y=4)))
    # # print(test_maze_1.get_connected_nodes_from_current_one(current_node=pipe_node))
    # # print(test_maze_1.get_next_node_connected_from_following_path(current_node=pipe_node, previous_node=MazeNode(type='-', coordinate=Coordinate(x=3, y=4))))
    
    # # path = test_maze_1.follow_path_from_node_to_start(previous_node=MazeNode(type='S', coordinate=Coordinate(x=2, y=4)), starting_node=MazeNode(type='-', coordinate=Coordinate(x=3, y=4)))
    # # for step in path:
    # #     print(step)
    # path_t1 = test_maze_1.get_loop_path_from_start_node()
    # # print(len(path_t1))
    # print(f' test_maze_1 farthest from the starting position requires {len(path_t1)/2} steps')
    
    # test_maze_2 =[
    #     '..F7.',
    #     '.FJ|.',
    #     'SJ.L7',
    #     '|F--J',
    #     'LJ...',
    # ]
    # test_maze_2 = Maze.from_maze_lines(maze_lines=test_maze_2)
    # path_t2 = test_maze_2.get_loop_path_from_start_node()
    # # print(len(path_t2))
    # print(f'test_maze_2 farthest from the starting position requires {len(path_t2)/2} steps')
    
    with open("./maze.txt", "r") as fr:
        maze = Maze.from_maze_lines(maze_lines=[line for line in fr])
    path = maze.get_loop_path_from_start_node()
    print(f'maze farthest path from the starting position requires {len(path)/2} steps')
    maze.set_loop_path_from_start_node(loop_path=path)
    inside_tiles = [tile for tile in maze.tiles if maze.is_tile_inside_pipe_path_loop(tile_node=tile)]
    print(f'tiles inside maze are {len(inside_tiles)}')

    # test_maze_tiles_description = [
    #     '..........',
    #     '.S------7.',
    #     '.|F----7|.',
    #     '.||....||.',
    #     '.||....||.',
    #     '.|L-7F-J|.',
    #     '.|..||..|.',
    #     '.L--JL--J.',
    #     '..........',
    # ]
    # test_maze_tiles = Maze.from_maze_lines(maze_lines=test_maze_tiles_description)
    # test_maze_tiles.set_loop_path_from_start_node()
    # print(test_maze_tiles.loop_pipe_path)
    # print(test_maze_tiles.tiles)
    # connector = MazeNode.get_connector_across_nodes(
    #     node_a=MazeNode(type='-', coordinate=Coordinate(x=3, y=8)),
    #     node_b=MazeNode(type='|', coordinate=Coordinate(x=2, y=7)),
    #     coordinate_connector=Coordinate(x=2, y=8)
    # )
    # print(connector)

    
    # print(AdjacentCornerNodeCombo.get_number_horizontal_flex(row_pipe_types_west_to_east=['F', 'J', 'L', '7', 'F', '7']))
    # print(AdjacentCornerNodeCombo.get_number_vertical_flex(column_pipe_types_south_to_north=['J', 'F', 'J', '7']))
    # column_5_path_nodes = test_maze_tiles.get_loop_pipe_path_column_nodes_south_to_north(x=5)
    # print(column_5_path_nodes)
    # count_intersections_north = test_maze_tiles.count_touches_pipe_path_north(tile_node=MazeNode(type='.', coordinate=Coordinate(x=5, y=5)), pipe_nodes_column_zone_south_to_north=column_5_path_nodes)
    # count_intersections_south = test_maze_tiles.count_touches_pipe_path_south(tile_node=MazeNode(type='.', coordinate=Coordinate(x=5, y=5)), pipe_nodes_column_zone_south_to_north=column_5_path_nodes)
    # print(count_intersections_north)
    # print(count_intersections_south)
    # print(test_maze_tiles.is_tile_inside_pipe_path_loop(tile_node=MazeNode(type='.', coordinate=Coordinate(x=5, y=5))))
    # print(test_maze_tiles.is_tile_inside_pipe_path_loop(tile_node=MazeNode(type='.', coordinate=Coordinate(x=4, y=3))))
    # test_inside_tiles = [tile for tile in test_maze_tiles.tiles if test_maze_tiles.is_tile_inside_pipe_path_loop(tile_node=tile)]
    # print(f'tiles inside test maze tiles are {len(test_inside_tiles)}')

    # test_maze_tiles_complicated_description = [
    #     '.F----7F7F7F7F-7....',
    #     '.|F--7||||||||FJ....',
    #     '.||.FJ||||||||L7....',
    #     'FJL7L7LJLJ||LJ.L-7..',
    #     'L--J.L7...LJS7F-7L7.',
    #     '....F-J..F7FJ|L7L7L7',
    #     '....L7.F7||L7|.L7L7|',
    #     '.....|FJLJ|FJ|F7|.LJ',
    #     '....FJL-7.||.||||...',
    #     '....L---J.LJ.LJLJ...',
    # ]
    # test_maze_tiles_complicated = Maze.from_maze_lines(maze_lines=test_maze_tiles_complicated_description)
    # test_maze_tiles_complicated.set_loop_path_from_start_node()
    # test_inside_tiles_complicated = [tile for tile in test_maze_tiles_complicated.tiles if test_maze_tiles_complicated.is_tile_inside_pipe_path_loop(tile_node=tile)]
    # print(f'tiles inside test maze complicated tiles are {len(test_inside_tiles_complicated)}')

    # test_maze_tiles_c2_description = [
    #     'FF7FSF7F7F7F7F7F---7',
    #     'L|LJ||||||||||||F--J',
    #     'FL-7LJLJ||||||LJL-77',
    #     'F--JF--7||LJLJ7F7FJ-',
    #     'L---JF-JLJ.||-FJLJJ7',
    #     '|F|F-JF---7F7-L7L|7|',
    #     '|FFJF7L7F-JF7|JL---7',
    #     '7-L-JL7||F7|L7F-7F7|',
    #     'L.L7LFJ|||||FJL7||LJ',
    #     'L7JLJL-JLJLJL--JLJ.L',
    # ]
    # test_maze_tiles_c2 = Maze.from_maze_lines(maze_lines=test_maze_tiles_c2_description)
    # Y_MAZE_BOUND = 10
    # test_maze_tiles_c2.set_loop_path_from_start_node()
    # test_inside_tiles_c2 = [tile for tile in test_maze_tiles_c2.tiles if test_maze_tiles_c2.is_tile_inside_pipe_path_loop(tile_node=tile)]
    # print(f'tiles inside test maze c2 tiles are {len(test_inside_tiles_c2)}')
