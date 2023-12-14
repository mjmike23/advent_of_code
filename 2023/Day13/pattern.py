from typing import List, Tuple, Set
from dataclasses import dataclass

VERTICAL = 'V'
HORIZONTAL = 'H'

@dataclass(frozen=True)
class SymmetricDescription:
    
    type: str
    index: int

    @staticmethod
    def get_new_symmetry(base_symmetry: List['SymmetricDescription'], new_symmetries: List['SymmetricDescription']) -> Set['SymmetricDescription']:
        return set(new_symmetries).difference(set(base_symmetry))

@dataclass(frozen=True)
class PatternMirror:
    
    reflection_row_elements: List[str]

    @staticmethod
    def from_line_descriptions(line_descriptions: List[str]) -> 'PatternMirror':
        return PatternMirror(reflection_row_elements=[line for line in line_descriptions])

    @property
    def columnar_size(self) -> int:
        return len(self.reflection_row_elements[0])
    
    @property
    def row_size(self) -> int:
        return len(self.reflection_row_elements)
    
    def get_column_mirror(self, col_index: int) -> str:
        return ''.join([row_mirror[col_index] for row_mirror in self.reflection_row_elements])
    
    def get_row_mirror(self, row_index: int) -> str:
        return self.reflection_row_elements[row_index]
    
    def are_col_index_out_of_border(self, index_left: int, index_right: int) -> bool:
        return index_left < 0 or index_right >= self.columnar_size
    
    def is_vertical_index_symmetric(self, col_index_verify: int) -> bool:
        if col_index_verify == self.columnar_size - 1:
            return False
        for i in range(col_index_verify + 1):
            left_index_check = col_index_verify - i
            right_index_check = col_index_verify + i + 1
            # print(f'verify {left_index_check} with {right_index_check}')
            if self.are_col_index_out_of_border(index_left=left_index_check, index_right=right_index_check):
                return True
            col_left = self.get_column_mirror(col_index=left_index_check)
            col_right = self.get_column_mirror(col_index=right_index_check)
            if col_left == col_right:
                continue
            return False
        return True

    def are_row_index_out_of_border(self, index_up: int, index_down: int) -> bool:
        return index_up < 0 or index_down >= self.row_size
    
    def is_horizontal_index_symmetric(self, row_index_verify: int) -> bool:
        if row_index_verify == self.row_size - 1:
            return False
        for i in range(self.row_size + 1):
            up_index_check = row_index_verify - i
            down_index_check = row_index_verify + i + 1
            # print(f'check index {up_index_check} vs {down_index_check}')
            if self.are_row_index_out_of_border(index_up=up_index_check, index_down=down_index_check):
                return True
            row_up = self.get_row_mirror(row_index=up_index_check)
            row_down = self.get_row_mirror(row_index=down_index_check)
            if row_up == row_down:
                continue
            return False
        return True

    def get_vertical_mirror_position(self) -> int:
        for col_index in range(self.columnar_size):
            if self.is_vertical_index_symmetric(col_index_verify=col_index):
                return col_index
        return -1
    
    def get_vertical_mirror_all_possibilities_position(self) -> List[SymmetricDescription]:
        positions: List[SymmetricDescription] = []
        for col_index in range(self.columnar_size):
            if self.is_vertical_index_symmetric(col_index_verify=col_index):
                positions.append(SymmetricDescription(type=VERTICAL, index=col_index))
        return positions
    
    def get_horizontal_mirror_position(self) -> int:
        for row_index in range(self.row_size):
            if self.is_horizontal_index_symmetric(row_index_verify=row_index):
                return row_index
        return -1
    
    def get_horizontal_mirror_all_possibilities_position(self) -> List[SymmetricDescription]:
        positions: List[SymmetricDescription] = []
        for row_index in range(self.row_size):
            if self.is_horizontal_index_symmetric(row_index_verify=row_index):
                positions.append(SymmetricDescription(type=HORIZONTAL, index=row_index))
        return positions

    def get_number_columns_to_the_left_of_vertical_mirror_index(self, vertical_mirror_index: int) -> int:
        return vertical_mirror_index + 1

    def get_number_rows_up_on_horizontal_mirror_index(self, horizontal_mirror_index: int) -> int:
        return horizontal_mirror_index + 1

    def get_all_possible_symmetric_positions(self) -> List[SymmetricDescription]:
        return self.get_horizontal_mirror_all_possibilities_position() + self.get_vertical_mirror_all_possibilities_position()

    def get_factor(self) -> int:
        vertical_index = self.get_vertical_mirror_position()
        if vertical_index != -1:
            return self.get_number_columns_to_the_left_of_vertical_mirror_index(vertical_mirror_index=vertical_index)
        horizontal_index = self.get_horizontal_mirror_position()
        if horizontal_index != -1:
            return self.get_number_rows_up_on_horizontal_mirror_index(horizontal_mirror_index=horizontal_index) * 100
        print(self)
        raise Exception('Not allowed')

    def get_factor_for_symmetry(self, symmetry_point: SymmetricDescription) -> int:
        if symmetry_point.type == VERTICAL:
            return self.get_number_columns_to_the_left_of_vertical_mirror_index(vertical_mirror_index=symmetry_point.index)
        if symmetry_point.type == HORIZONTAL:
            return self.get_number_rows_up_on_horizontal_mirror_index(horizontal_mirror_index=symmetry_point.index) * 100

    def get_mirror_and_new_symmetry_with_smudge(self) -> Tuple['PatternMirror', SymmetricDescription]:
        base_symmetric_points = self.get_all_possible_symmetric_positions()
        for ri, row_element in enumerate(self.reflection_row_elements):
            for ci, element in enumerate(row_element):
                candidate_mirror = self.get_mirror_refactored(col_index=ci, row_index=ri)
                candidate_symmetric_points = candidate_mirror.get_all_possible_symmetric_positions()
                candidate_new_symmetries = SymmetricDescription.get_new_symmetry(base_symmetry=base_symmetric_points, new_symmetries=candidate_symmetric_points)
                if len(candidate_new_symmetries) == 1:
                    return (candidate_mirror, candidate_new_symmetries.pop())

    def get_mirror_refactored(self, col_index: int, row_index: int) -> 'PatternMirror':
        element = self.reflection_row_elements[row_index][col_index]
        opposite = '#' if element == '.' else '.'
        new_elements = [[element if not (ci == col_index and ri == row_index) else opposite for ci, element in enumerate(el_row)] for ri, el_row in enumerate(self.reflection_row_elements)]
        return PatternMirror(reflection_row_elements=new_elements)

if __name__ == '__main__':
    test_pattern_description = [
        '#.##..##.',
        '..#.##.#.',
        '##......#',
        '##......#',
        '..#.##.#.',
        '..##..##.',
        '#.#.##.#.',
    ]
    test_pattern = PatternMirror.from_line_descriptions(test_pattern_description)
    # print(test_pattern)
    assert not test_pattern.is_horizontal_index_symmetric(row_index_verify=3)
    assert test_pattern.is_vertical_index_symmetric(col_index_verify=4)
    assert test_pattern.get_vertical_mirror_position() == 4
    # assert test_pattern.get_column_specular_index(col_index=2, vertical_mirror_index=4) == 7
    # assert test_pattern.get_column_specular_index(col_index=7, vertical_mirror_index=4) == 2
    # # print(test_pattern.get_column_specular_index(col_index=4, vertical_mirror_index=4))
    # # print(test_pattern.get_column_indexes_to_check_for_specular_one(vertical_mirror_index=4))
    # # print(test_pattern.get_couple_columns_specular())
    assert test_pattern.get_number_columns_to_the_left_of_vertical_mirror_index(vertical_mirror_index=4) == 5
    assert test_pattern.get_factor() == 5
    test_pattern_s = test_pattern.get_mirror_refactored(col_index=0, row_index=0)
    # for l in test_pattern_s.reflection_row_elements:
    #     print(l)
    assert set(test_pattern_s.get_horizontal_mirror_all_possibilities_position()) == {SymmetricDescription(type=HORIZONTAL, index=2)}
    assert set(test_pattern_s.get_all_possible_symmetric_positions()) == {SymmetricDescription(type=HORIZONTAL, index=2), SymmetricDescription(type='V', index=4)}
    new_symmetry = SymmetricDescription.get_new_symmetry(base_symmetry=test_pattern.get_all_possible_symmetric_positions(), new_symmetries=test_pattern_s.get_all_possible_symmetric_positions())
    assert test_pattern_s.get_factor_for_symmetry(symmetry_point=list(new_symmetry)[0]) == 300
    new_mirror, new_symmetry = test_pattern.get_mirror_and_new_symmetry_with_smudge()
    # for l in new_mirror.reflection_row_elements:
    #     print(l)
    assert new_mirror.get_factor_for_symmetry(symmetry_point=new_symmetry) == 300
    
    test_pattern_h_description = [
        '#...##..#',
        '#....#..#',
        '..##..###',
        '#####.##.',
        '#####.##.',
        '..##..###',
        '#....#..#',
    ]
    test_pattern_h  = PatternMirror.from_line_descriptions(test_pattern_h_description)
    # # # print(test_pattern_h)
    # assert test_pattern_h.get_horizontal_mirror_position() == 3
    # # assert test_pattern_h.get_row_specular_index(row_index=2, horizontal_mirror_index=3) == 5
    # # assert test_pattern_h.get_row_specular_index(row_index=5, horizontal_mirror_index=3) == 2
    # # # print(test_pattern_h.get_row_indexes_to_check_for_specular_one(horizontal_mirror_index=3))
    # # # print(test_pattern_h.get_couple_rows_specular())
    # # print(test_pattern_h.get_number_rows_up_on_horizontal_mirror_index(horizontal_mirror_index=3))
    # assert test_pattern_h.get_factor() == 400
    new_mirror_h_test, new_symmetry_test = test_pattern_h.get_mirror_and_new_symmetry_with_smudge()
    # for l in new_mirror_h_test.reflection_row_elements:
    #     print(l)
    assert new_mirror_h_test.get_factor_for_symmetry(symmetry_point=new_symmetry_test) == 100
    


    with open(".\mirror.txt", "r") as fr:
        pattern_mirrors: List[PatternMirror] = []
        current_mirror_description_elements = []
        for line in fr:
            line = line.rstrip()
            if line == '':
                pm = PatternMirror.from_line_descriptions(line_descriptions=current_mirror_description_elements)
                pattern_mirrors.append(pm)
                current_mirror_description_elements = []
                continue
            current_mirror_description_elements.append(line)
        pm = PatternMirror.from_line_descriptions(line_descriptions=current_mirror_description_elements)
        pattern_mirrors.append(pm)

    print(f'Sum of pattern factors is {sum([pm.get_factor() for pm in pattern_mirrors])}')

    tot_factor_smudge = 0
    for pm in pattern_mirrors:
        smudge_mirror, new_symmetry = pm.get_mirror_and_new_symmetry_with_smudge()
        tot_factor_smudge += smudge_mirror.get_factor_for_symmetry(symmetry_point=new_symmetry)
    print(f'Sum of pattern factors considering smudge is {tot_factor_smudge}')