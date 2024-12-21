from typing import Tuple, Set, Dict
from copy import deepcopy

class Area:

    tag: str
    coordinates_perimeter: Set[Tuple[str, str]]
    coordinates_inside: Set[Tuple[str, str]]

    def __init__(self, tag):
        self.tag = tag
        self.coordinates_perimeter = set()
        self.coordinates_inside = set()
    
    @property
    def area_points(self) -> Set[Tuple[int, int]]:
        return self.coordinates_perimeter.union(self.coordinates_inside)
    
    @property
    def get_area(self) -> int:
        return len((self.coordinates_inside).union(self.coordinates_perimeter))

    @property
    def get_perimeter(self) -> int:
        perimeter = 0
        for perimeter_coord in self.coordinates_perimeter:
            for delta_x, delta_y in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                next_x = perimeter_coord[1] + delta_x
                next_y = perimeter_coord[0] + delta_y
                if (next_y, next_x) in self.area_points:
                    # next is inside so not a perimeter side
                    continue
                perimeter += 1
        return perimeter

    def __repr__(self):
        msg = f'Area tag: {self.tag}'
        msg += '. Perimeter is following: '
        for point in self.coordinates_perimeter:
            msg += f'{point}'
        msg += '. Inside points are following:'
        for point in self.coordinates_inside:
            msg += f'{point}'
        return msg
    
    def print_as_map(self, size_v = None, size_h = None) -> None:
        size_v = size_v if size_v else max([p[0] for p in self.area_points]) + 1
        size_h = size_h if size_h else max([p[1] for p in self.area_points]) + 1
        for i in range(size_v):
            line = ['#' if (i, j) in self.area_points else '.' for j in range(size_h)]
            print(''.join(line))
        

with open("puzzle.txt", "r") as fr:
    map = []
    for line in fr:
        map.append([[tag, 0] for tag in line.rstrip()])
    areas: Dict[int, Area] = {}
    id_area = 0
    open_area = None
    for i, line in enumerate(map):
        for j, tag in enumerate(line):
            if tag[1] == 1:
                # print(f'Tile already assigned')
                continue
            if open_area is None:
                # print(f'Evaluating new area')
                open_area = Area(tag=tag[0])
                points_to_evaluate_if_area_or_perimeter = {(i, j)}
                while len(points_to_evaluate_if_area_or_perimeter) > 0:
                    next_points_to_evaluate_if_area_or_perimeter = set()
                    # print(f'evaluation for {points_to_evaluate_if_area_or_perimeter}')
                    for coord in points_to_evaluate_if_area_or_perimeter:
                        next_points = {(coord[0] + 1, coord[1]), (coord[0] - 1, coord[1]), (coord[0], coord[1]  + 1), (coord[0], coord[1] - 1)}
                        invalid_next_points = set()
                        new_area_perimeter_points = set()
                        near_bound = False
                        for search_point in next_points:
                            if search_point[0] < 0 or search_point[1] < 0:
                                # out of bound
                                near_bound = True
                                invalid_next_points.add(search_point)
                                continue
                            try:
                                search_tag = map[search_point[0]][search_point[1]]
                            except IndexError:
                                # out of bound
                                near_bound = True
                                invalid_next_points.add(search_point)
                                continue
                            if open_area.tag == search_tag[0]:
                                if search_point in open_area.area_points:
                                    # already part of the area
                                    invalid_next_points.add(search_point)
                                    continue
                                new_area_perimeter_points.add(search_point)

                        # near bound automaticamente è perimeter
                        if near_bound:
                            open_area.coordinates_perimeter.add(coord)
                        # tutti adiacenti, area perimeter points
                        elif new_area_perimeter_points == next_points.difference(invalid_next_points):
                            # print(f'{coord} is area point')
                            open_area.coordinates_inside.add(coord)
                        # nessun adiacente area perimeter point
                        # alcuni adiancenti area perimeter point
                        else:
                            # print(f'{coord} is perimeter point')
                            open_area.coordinates_perimeter.add(coord)
                        
                        next_points_to_evaluate_if_area_or_perimeter.update(new_area_perimeter_points)
                        map[coord[0]][coord[1]][1] = 1

                    points_to_evaluate_if_area_or_perimeter = deepcopy(next_points_to_evaluate_if_area_or_perimeter)

                areas[id_area] = open_area
                open_area = None
                id_area += 1
        
    if open_area is not None:
        areas[id_area] = open_area
    
    # print(areas)
    # visual repr
    # for id, area in areas.items():
    #     print(f'area {id} filler {area.tag}')
    #     area.print_as_map()
    #     print(f'area is {area.get_area}')
    #     print(f'perimeter is {area.get_perimeter}')

    print(sum([area.get_area * area.get_perimeter for _, area in areas.items()]))  # solution a
