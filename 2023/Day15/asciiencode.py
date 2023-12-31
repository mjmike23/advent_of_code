from dataclasses import dataclass
from typing import List, Set

LENS_REMOVE_MARKER = '-'
LENS_ADD_MARKER = '='

def compute_current_value_adding_char(current_value: int, c: str) -> int:
    ascii_c = ord(c)
    current_value += ascii_c
    current_value *= 17
    return current_value%256

@dataclass(frozen=True)
class SourceCode:

    code: str

    def get_hash_value(self) -> int:
        current_value = 0
        for c in self.code:
            current_value = compute_current_value_adding_char(current_value=current_value, c=c)
        return current_value

@dataclass
class Codes:

    codes: List[SourceCode]

    @staticmethod
    def from_puzzle_input(line: str) -> 'Codes':
        return Codes(codes=[SourceCode(code=code) for code in line.rstrip().split(',')])

    def get_sum_hashes(self) -> int:
        return sum([code.get_hash_value() for code in self.codes])

@dataclass(frozen=True)
class Lens:

    label: str
    focal_length: int

    @staticmethod
    def from_code(code: str) -> 'Lens':
        if LENS_REMOVE_MARKER in code:
            lm = code.index(LENS_REMOVE_MARKER)
            return Lens(label=code[:lm], focal_length=-1)
        if LENS_ADD_MARKER in code:
            lm = code.index(LENS_ADD_MARKER)
            return Lens(label=code[:lm], focal_length=int(code[-1]))
        raise Exception(f'not possible to have lens  from code {code}')

    @staticmethod
    def get_lenses_from_description(description: str) -> List['Lens']:
        return [Lens.from_code(code=l_description) for l_description in description.rstrip().split(',')]

    @property
    def relevant_box(self) -> int:
        return SourceCode(code=self.label).get_hash_value()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Lens):
            return self.label == other.label
        return NotImplemented
    
    def __hash__(self) -> int:
        return hash(self.label)

@dataclass
class Box:

    lenses: List[Lens]

    def remove_lens(self, lens: Lens) -> None:
        if self.get_lens_box_index(lens=lens) != -1:
            self.lenses.remove(lens)

    def add_lens(self, lens: Lens) -> None:
        l_index = self.get_lens_box_index(lens=lens) 
        if l_index != -1:
            self.lenses.pop(l_index)
            self.lenses.insert(l_index, lens)
        else:
            self.lenses.append(lens)

    def get_lens_box_index(self, lens: Lens) -> int:
        try:
            return self.lenses.index(lens)
        except ValueError:
            return -1

    def get_focusing_power(self, box_index: int) -> int:
        return sum([box_index * (i + 1) * lens.focal_length for i, lens in enumerate(self.lenses)])

class LensMagazine:

    boxes: List[Box]

    def __init__(self) -> None:
        boxes = []
        for i in range(256):
            boxes.append(Box(lenses=[]))
        self.boxes = boxes

    def __str__(self) -> str:
        result = 'Magazine summarize: '
        empty_boxes = 0
        for i, box in enumerate(self.boxes):
            if len(box.lenses) > 0:
                result += f'box {i} contains {box}, '
                continue
            else:
                empty_boxes += 1
        return result + f'empty boxes are {empty_boxes}'

    def apply_lens(self, lens: Lens) -> None:
        if lens.focal_length == -1:
            self.boxes[lens.relevant_box].remove_lens(lens=lens)
        else :
            self.boxes[lens.relevant_box].add_lens(lens=lens)

    def apply_lenses(self, lenses: List[Lens]) -> None:
        for lens in lenses:
            self.apply_lens(lens=lens)

    def get_focusing_power(self) -> int:
        return sum([box.get_focusing_power(box_index=bi + 1) for bi, box in enumerate(self.boxes)])


if __name__ == '__main__':
    test_code = 'HASH'
    test_sc = SourceCode(code=test_code)
    print(test_sc.get_hash_value())
    test_codes_description = 'rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7'
    test_codes = Codes.from_puzzle_input(test_codes_description)
    print(f'Test sum of hashes in {test_codes.get_sum_hashes()}')

    with open(".\codes.txt", "r") as fr:
        codes = Codes.from_puzzle_input(line=[line.rstrip() for line in fr][0])
    print(f'Sum of hashes in {codes.get_sum_hashes()}')

    test_lens_add = 'rn=1'
    test_la = Lens.from_code(code=test_lens_add)
    assert test_la.label == 'rn'
    assert test_la.relevant_box == 0
    assert test_la.focal_length == 1

    test_lens_remove = 'cm-'
    test_lr = Lens.from_code(code=test_lens_remove)
    assert test_lr.label == 'cm'
    assert test_lr.relevant_box == 0
    assert test_lr.focal_length == -1

    test_magazine = LensMagazine()
    print(test_magazine)
    test_lenses = Lens.get_lenses_from_description(description=test_codes_description)
    # print(test_lenses)
    test_magazine.apply_lenses(lenses=test_lenses)
    print(test_magazine)
    print(f'Test lenses focusing power is {test_magazine.get_focusing_power()}')

    magazine = LensMagazine()
    print(magazine)
    with open(".\codes.txt", "r") as fr:
        lenses = Lens.get_lenses_from_description(description=[line.rstrip() for line in fr][0])
    magazine.apply_lenses(lenses=lenses)
    print(f'Lenses focusing power is {magazine.get_focusing_power()}')