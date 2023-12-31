from dataclasses import dataclass
from typing import List

ROCK_STANDING = '#'
ROCK_ROLLING = 'O'
SPACE = '.'
OUT_OF_BORDER = '*'

@dataclass
class RockMap:
    
    elements: List[List[str]]
    
    @property
    def column_size(self) -> int:
        return len(self.elements[0])

    @property
    def row_size(self) -> int:
        return len(self.elements)

    def print_visualization(self) -> None:
        for row_el in self.elements:
            row_el_list = ''.join(row_el)
            print(row_el_list)

    @staticmethod
    def from_lines(lines: List[str]) -> 'RockMap':
        elements = []
        for row_el in lines:
            row_el_list = [el for el in row_el]
            elements.append(row_el_list)
        return RockMap(elements = elements)

    def get_element(self, col_index: int, row_index: int) -> str:
        if col_index < 0 or row_index < 0:
            return '*'
        try:
            return self.elements[row_index][col_index]
        except IndexError:
            return '*'

    def get_column_elements(self, col_index: int) -> List[str]:
        return [row_el[col_index] for row_el in self.elements]

    def get_row_elements(self, row_index: int) -> List[str]:
        return self.elements[row_index]

    @staticmethod
    def get_index_element(elements: List[str], index: int) -> str:
        if index < 0:
            return OUT_OF_BORDER
        try:
            return elements[index]
        except IndexError:
            return OUT_OF_BORDER

    def replace_element(self, new_element: str, col_index: int, row_index: int) -> int:
        self.elements[row_index][col_index] = new_element

    def roll_rock_vertical(self, start_col_index: int, start_row_index: int, south_to_north: bool = True, col_elements: List[str] =  None) -> None:
        # rock_to_roll = self.get_element(col_index=start_col_index, row_index=start_row_index)
        # if rock_to_roll != ROCK_ROLLING:
        #     print(f'this is not a rock that can roll, this is {rock_to_roll}')
        #     return
        rock_row_index = start_row_index
        next_row_index = start_row_index - 1 if south_to_north else start_row_index + 1
        col_elements = col_elements if col_elements is not None else self.get_column_elements(col_index=start_col_index)
        while RockMap.get_index_element(elements=col_elements, index=next_row_index) not in [ROCK_ROLLING, ROCK_STANDING, OUT_OF_BORDER]:
            rock_row_index = next_row_index
            next_row_index = next_row_index - 1 if south_to_north else next_row_index + 1

        if rock_row_index == start_row_index:
            return
        self.replace_element(new_element=SPACE, col_index=start_col_index, row_index=start_row_index)
        self.replace_element(new_element=ROCK_ROLLING, col_index=start_col_index, row_index=rock_row_index)

    def roll_rock_horizontal(self, start_col_index: int, start_row_index: int, east_to_west: bool = True, row_elements: List[str] = None) -> None:
        # rock_to_roll = self.get_element(col_index=start_col_index, row_index=start_row_index)
        # if rock_to_roll != ROCK_ROLLING:
        #     print(f'this is not a rock that can roll, this is {rock_to_roll}')
        #     return
        rock_col_index = start_col_index
        next_col_index = start_col_index - 1 if east_to_west else start_col_index + 1
        row_elements = row_elements if row_elements is not None else self.get_row_elements(row_index=start_row_index)
        while RockMap.get_index_element(elements=row_elements, index=next_col_index) not in [ROCK_ROLLING, ROCK_STANDING, OUT_OF_BORDER]:
            rock_col_index = next_col_index
            next_col_index = next_col_index - 1 if east_to_west else next_col_index + 1

        if rock_col_index == start_col_index:
            return
        self.replace_element(new_element=SPACE, col_index=start_col_index, row_index=start_row_index)
        self.replace_element(new_element=ROCK_ROLLING, col_index=rock_col_index, row_index=start_row_index)

    def roll_rock_to_north(self, start_col_index: int, start_row_index: int, col_elements: List[str] = None) -> None:
        self.roll_rock_vertical(start_col_index=start_col_index, start_row_index=start_row_index, south_to_north=True, col_elements=col_elements)

    def roll_rock_to_south(self, start_col_index: int, start_row_index: int, col_elements: List[str] = None) -> None:
        self.roll_rock_vertical(start_col_index=start_col_index, start_row_index=start_row_index, south_to_north=False, col_elements=col_elements)

    def roll_rock_to_west(self, start_col_index: int, start_row_index: int, row_elements: List[str] = None) -> None:
        self.roll_rock_horizontal(start_col_index=start_col_index, start_row_index=start_row_index, east_to_west=True, row_elements=row_elements)

    def roll_rock_to_east(self, start_col_index: int, start_row_index: int, row_elements: List[str] = None) -> None:
        self.roll_rock_horizontal(start_col_index=start_col_index, start_row_index=start_row_index, east_to_west=False, row_elements=row_elements)

    def tilt_north(self) -> None:
        for ri, raw_elements in enumerate(self.elements):
            for ci, el in enumerate(raw_elements):
                if el == ROCK_ROLLING:
                    self.roll_rock_to_north(start_col_index=ci, start_row_index=ri)

    def tilt_south(self) -> None:
        for ri, raw_elements in enumerate(self.elements[::-1]):
            for ci, el in enumerate(raw_elements):
                if el == ROCK_ROLLING:
                    self.roll_rock_to_south(start_col_index=ci, start_row_index=self.row_size - 1 - ri)

    def tilt_west(self) -> None:
        for ri, raw_elements in enumerate(self.elements):
            for ci, el in enumerate(raw_elements):
                if el == ROCK_ROLLING:
                    self.roll_rock_to_west(start_col_index=ci, start_row_index=ri, row_elements=raw_elements)

    def tilt_east(self) -> None:
        for ri, raw_elements in enumerate(self.elements):
            for ci, el in enumerate(raw_elements[::-1]):
                if el == ROCK_ROLLING:
                    self.roll_rock_to_east(start_col_index=self.column_size -1 - ci, start_row_index=ri)

    def tilt_spin(self) -> None:
        self.tilt_north()
        self.tilt_west()
        self.tilt_south()
        self.tilt_east()

    def get_rock_weight(self, row_index: int) -> int:
        return self.row_size - row_index
    
    def get_full_rock_weight(self) -> int:
        full_rock_weight = 0
        for ri, raw_elements in enumerate(self.elements):
            for el in raw_elements:
                if el == ROCK_ROLLING:
                    rock_weight = self.get_rock_weight(row_index=ri)
                    full_rock_weight += rock_weight
        return full_rock_weight

if __name__ == '__main__':
    test_rock_map_d = [
        'O....#....',
        'O.OO#....#',
        '.....##...',
        'OO.#O....O',
        '.O.....O#.',
        'O.#..O.#.#',
        '..O..#O..O',
        '.......O..',
        '#....###..',
        '#OO..#....',
    ]
    test_rock_map = RockMap.from_lines(lines=test_rock_map_d)
    test_rock_map.print_visualization()
    print('')
    # print(test_rock_map)
    assert test_rock_map.get_element(col_index=3, row_index=1) == ROCK_ROLLING
    # test_rock_map.roll_rock_to_north(start_col_index=5, start_row_index=5)
    # test_rock_map.print_visualization()
    # print('')
    # test_rock_map.roll_rock_to_north(start_col_index=3, start_row_index=1)
    # test_rock_map.print_visualization()
    # print('')
    test_rock_map.tilt_north()
    # test_rock_map.print_visualization()
    # print('')
    print(f'Test rock map full weight after tilt north is {test_rock_map.get_full_rock_weight()}')
    # test_rock_map.tilt_west()
    # test_rock_map.print_visualization()
    # print('')
    # test_rock_map.tilt_south()
    # test_rock_map.print_visualization()
    # print('')
    # test_rock_map.tilt_east()
    # test_rock_map.print_visualization()
    # print('')
    
    # print('reinitialize original map test')
    # test_rock_map_for_spin = RockMap.from_lines(lines=test_rock_map_d)
    # for i in range(1000000000):
    #     if i%100000== 0:
    #         print(i)
    #     test_rock_map_for_spin.tilt_spin()
    # print(f'Test rock map full weight after 1000000000 spins is {test_rock_map_for_spin.get_full_rock_weight()}')

    with open(".\mrocks.txt", "r") as fr:
        rock_map = RockMap.from_lines(lines=[line.rstrip() for line in fr])
    rock_map.tilt_north()
    print(f'Rock map full weight after tilt north is {rock_map.get_full_rock_weight()}')