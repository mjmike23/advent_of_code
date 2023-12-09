from typing import List, Set
from dataclasses import dataclass
import itertools

SYMBOLS = '+*#*/@$&+=-%'

GEAR_SYMBOL = '*'

@dataclass
class EngineElement:

    initial_position: int
    element: str
    
    @property
    def is_symbol(self) -> bool:
        return self.element in SYMBOLS

    @property
    def final_position(self) -> bool:
        return self.initial_position + len(self.element) - 1

    @staticmethod
    def gear_ratio(*elements: 'EngineElement') -> int:
        assert not any([el for el in elements if el.is_symbol])
        ratio = 1
        for el in elements:
            ratio *= int(el.element)
        return ratio


@dataclass
class EngineElementInMotor(EngineElement):

    row_id: int
    initial_position: int
    element: str

    @staticmethod
    def from_element_mounted(row_id: int, engine_element: EngineElement) -> 'EngineElementInMotor':
        return EngineElementInMotor(row_id=row_id, initial_position=engine_element.initial_position, element=engine_element.element)

    def __hash__(self) -> int:
        return hash(str(self))

@dataclass
class CompositeEngineElement:

    initial_position: int
    composite_element: str
    
    @property
    def is_composite(self) -> bool:
        return len(self.composite_element) > 1 and not self.composite_element.isnumeric()
    
    def get_engine_elements(self) -> List[EngineElement]:
        if not self.is_composite:
            return [EngineElement(initial_position=self.initial_position, element=self.composite_element)]
        element_values = []
        element_search_value = ''
        last_found_number_relative_index = 0
        for i, ch in enumerate(self.composite_element):
            if ch in SYMBOLS:
                if element_search_value != '':
                    element_values.append(EngineElement(initial_position=self.initial_position + last_found_number_relative_index, element= element_search_value))
                element_values.append(EngineElement(initial_position=self.initial_position + i, element= ch))
                element_search_value = ''
                last_found_number_relative_index = i + 1
                continue
            element_search_value += ch
        if element_search_value != '':
            element_values.append(EngineElement(initial_position=self.initial_position + last_found_number_relative_index, element= element_search_value))
        return element_values


@dataclass
class EngineRow:
    
    row_id: int
    components: List[EngineElement]

    @property
    def mounted_elements(self) -> List[EngineElementInMotor]:
        return [EngineElementInMotor(row_id=self.row_id, initial_position=component.initial_position, element=component.element) for component in self.components]
    
    @staticmethod
    def from_engine_line(row_id: int, engine_line: str) -> 'EngineRow':
        comp_elements_index_base = [CompositeEngineElement(initial_position=i, composite_element=el_value)  for i, el_value in enumerate(engine_line.split('.')) if el_value != '']
        comp_elements_corrected = EngineRow._apply_index_correction(comp_elements_index_base)
        return EngineRow(row_id=row_id, components=list(itertools.chain.from_iterable([comp_element.get_engine_elements() for comp_element in comp_elements_corrected])))

    @staticmethod
    def _apply_index_correction(base_c_engine_elements: List[CompositeEngineElement]) -> List[CompositeEngineElement]:
        """Correct index normalizing index to the base description line

        we have such case: ..12..#..345...567
        after string split for . and excluding it, we have: (i=2, val=12), (i=4, val=#), (i=6, val=345), (i=9, val=567)
        That is not correct, since do not consider length of each element.
        That methods bring result desired: (i=2, val=12), (i=6, val=#), (i=9, val=345), (i=15, val=567)
        """
        correction_index = 0
        result_fixed = []
        for c_engine_element in base_c_engine_elements:
            result_fixed.append(CompositeEngineElement(initial_position=c_engine_element.initial_position + correction_index, composite_element=c_engine_element.composite_element))
            correction_index += len(c_engine_element.composite_element)
        return result_fixed

    @property
    def symbol_components(self) -> List[EngineElement]:
        return [el for el in self.components if el.is_symbol]

    @property
    def numeric_components(self) -> List[EngineElement]:
        return [el for el in self.components if not el.is_symbol]

    @property
    def gear_symbols(self) -> List[EngineElement]:
        return [el for el in self.components if el.element == GEAR_SYMBOL]

    def search_symbol_id_range(self, id_start: int, id_end: int = None) -> bool:
        id_end = id_end if id_end is not None else id_start
        assert id_start <= id_end
        for i in range(id_start, id_end + 1):
            if any([el for el in self.symbol_components if el.initial_position == i]):
                return True
        return False

    def get_result_search_numeric_id_range(self, id_start: int, id_end: int = None) -> Set[EngineElementInMotor]:
        id_end = id_end if id_end is not None else id_start
        assert id_start <= id_end
        adjacent_numeric_elements = []
        for i in range(id_start, id_end + 1):
            adjacent_numeric_elements.extend([EngineElementInMotor.from_element_mounted(row_id=self.row_id, engine_element=el) for el in self.numeric_components if el.initial_position <= i and el.final_position >= i])
        return set(adjacent_numeric_elements)

    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, EngineRow):
            return self.row_id > obj.row_id
        raise NotImplemented

@dataclass
class FullEngine:
    
    engine_rows: List[EngineRow]
    
    def __post_init__(self) -> None:
        self.sort_rows()

    @property
    def gear_symbols_mounted(self) -> Set[EngineElementInMotor]:
        gear_symbols_mounted = set()
        for er in self.engine_rows:
            gear_symbols_mounted.update({EngineElementInMotor.from_element_mounted(row_id=er.row_id, engine_element=gsy) for gsy in er.gear_symbols})
        return gear_symbols_mounted

    def sort_rows(self) -> None:
        self.engine_rows.sort()

    def get_gear_adjacent_numeric_elements(self, engine_gear_element_mounted: EngineElementInMotor) -> Set[EngineElementInMotor]:
        self_row = self.engine_rows[engine_gear_element_mounted.row_id]
        row_above = self.engine_rows[engine_gear_element_mounted.row_id - 1] if engine_gear_element_mounted.row_id != 0 else None
        row_below = self.engine_rows[engine_gear_element_mounted.row_id + 1] if engine_gear_element_mounted.row_id != len(self.engine_rows) - 1 else None
        adj_elements = set()
        adj_elements.update(self_row.get_result_search_numeric_id_range(id_start=engine_gear_element_mounted.initial_position - 1)) # search right
        adj_elements.update(self_row.get_result_search_numeric_id_range(id_start=engine_gear_element_mounted.initial_position + 1)) # search left
        if row_above is not None:
            adj_elements.update(row_above.get_result_search_numeric_id_range(id_start=engine_gear_element_mounted.initial_position - 1, id_end=engine_gear_element_mounted.initial_position + 1)) # search above considering diagonals
        if row_below is not None:
            adj_elements.update(row_below.get_result_search_numeric_id_range(id_start=engine_gear_element_mounted.initial_position - 1, id_end=engine_gear_element_mounted.initial_position + 1)) # search below considering diagonals
        return adj_elements
    
    def get_valid_gears(self) -> Set[EngineElementInMotor]:
        return {possible_gear for possible_gear in self.gear_symbols_mounted if len(self.get_gear_adjacent_numeric_elements(engine_gear_element_mounted=possible_gear)) == 2}

    def get_valid_gear_ratios(self) -> List[int]:
        return [EngineElement.gear_ratio(*self.get_gear_adjacent_numeric_elements(engine_gear_element_mounted=valid_gear)) for valid_gear in self.get_valid_gears()]

    def get_valid_elements(self) -> List[EngineElement]:
        valid_elements = []
        for i, engine_row in enumerate(self.engine_rows):
            row_above = self.engine_rows[i - 1] if i != 0 else None
            row_below = self.engine_rows[i + 1] if i != len(self.engine_rows) - 1 else None
            for engine_element in engine_row.numeric_components:
                if engine_row.search_symbol_id_range(id_start=engine_element.initial_position - 1):
                    valid_elements.append(engine_element)
                    continue
                if engine_row.search_symbol_id_range(id_start=engine_element.final_position + 1):
                    valid_elements.append(engine_element)
                    continue
                if row_above is not None and row_above.search_symbol_id_range(id_start=engine_element.initial_position - 1, id_end= engine_element.final_position + 1):
                    valid_elements.append(engine_element)
                    continue
                if row_below is not None and row_below.search_symbol_id_range(id_start=engine_element.initial_position - 1, id_end= engine_element.final_position + 1):
                    valid_elements.append(engine_element)
                    continue
        return valid_elements

if __name__ == '__main__':
    # test_composite = '#854##'
    # ce = CompositeEngineElement(initial_position=5, composite_element=test_composite)
    # print(ce.is_composite)
    # print(ce.get_engine_elements())
    # test_row_engine = '.854...........................................................................362...........271...732........838.........24................'
    # er = EngineRow.from_engine_line(row_id=5, engine_line=test_row_engine)
    # print(er)
    # print(er.search_symbol_id_range(id_start=80))
    # fe = FullEngine(engine_rows=[er])
    # print(fe.get_valid_elements())
    # test_engine = [
    #     '467..114..',
    #     '...*......',
    #     '..35..633.',
    #     '......#...',
    #     '617*......',
    #     '.....+.58.',
    #     '..592.....',
    #     '......755.',
    #     '...$.*....',
    #     '.664.598..',
    # ]
    # test_engine_components = [EngineRow.from_engine_line(row_id=i, engine_line=line) for i, line in enumerate(test_engine)]
    # test_motor_map = FullEngine(engine_rows=test_engine_components)
    # print(test_motor_map.get_valid_elements())
    # print(f'test sum of all valid as result is {sum([int(el.element) for el in test_motor_map.get_valid_elements()])}')
    # print(test_motor_map.gear_symbols_mounted)
    # print(test_motor_map.get_valid_gears())
    # print(test_motor_map.gear_symbols_mounted)
    # print(f'test sum of all valid as result is {sum(test_motor_map.get_valid_gear_ratios())}')
    
    with open("engine_schema.txt", "r") as fr:
        engine_components = [EngineRow.from_engine_line(row_id=i, engine_line=line) for i, line in enumerate(fr)]
        motor_map = FullEngine(engine_rows=engine_components)
    # print(motor_map)
    valid_elements = motor_map.get_valid_elements()
    # print(valid_elements)
    print(f'sum of all valid as result is {sum([int(el.element) for el in valid_elements])}')  # 553825
    print(f'test sum of all valid as result is {sum(motor_map.get_valid_gear_ratios())}')  # 93994191

    # test_row_search_num = '.854*......35..#..6654....'
    # er = EngineRow.from_engine_line(row_id=5, engine_line=test_row_search_num)
    # print(er)
    # print(er.get_result_search_numeric_id_range(id_start=3, id_end=10))    