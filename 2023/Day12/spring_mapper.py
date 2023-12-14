from typing import List, Set
from dataclasses import dataclass

@dataclass(frozen=True)
class SpringElement:
    
    type: str

DAMAGED_SPRING = SpringElement(type='#')
OPERATIONAL_SPRING = SpringElement(type='.')
UNKNOWN_SPRING = SpringElement(type='?')

@dataclass
class IntervalPart:

    n_elements: int
    start: int
    end: int # non compreso

    def get_parts_from_element_sequence(row_length: int, parts_elements: List[int]) -> List['IntervalPart']:
        interval_parts = []
        for i, n_elements in enumerate(parts_elements):
            start = sum(parts_elements[: i])
            end = row_length - sum(parts_elements[i + 1:]) + 1
            interval_parts.append(IntervalPart(n_elements=n_elements, start=start, end=end))
        return interval_parts

@dataclass
class SpringRow:
    
    elements: List[SpringElement]

    @staticmethod
    def from_elements_string(elements_description: str) -> 'SpringRow':
        elements = [SpringElement(type=el) for el in elements_description.rstrip()]
        return SpringRow(elements=elements)

    @property
    def is_final_version(self) -> bool:
        return not any([elem for elem in self.elements if elem == UNKNOWN_SPRING])

    @property
    def string_representation(self) -> str:
        return''.join([el.type for el in self.elements])

    def print_as_single_string(self) -> None:
        print(self.string_representation)

    def fits_borders_contiguous_damaged_springs_elements_at_start_index(self, n_elements: int, start_index: int) -> bool:
        # check left element is not operational
        if start_index > len(self.elements) - 1:
            # print(f'start index {start_index} is over the row, that is length {len(self.elements)}')
            return False
        if start_index != 0:
            if self.elements[start_index - 1] == DAMAGED_SPRING:
                return False
        # check number elements can enter in the rest of the row
        if n_elements > len(self.elements[start_index:]):
            # print(f'elements cannot fit since are {n_elements}, but left space after {start_index} is only {len(self.elements[start_index:])}')
            return False
        if start_index + n_elements < len(self.elements):
            if self.elements[start_index +  n_elements] == DAMAGED_SPRING:
                return False
        return True

    def fits_contiguous_damaged_springs_elements_at_start_index(self, n_elements: int, start_index: int) -> bool:
        if not self.fits_borders_contiguous_damaged_springs_elements_at_start_index(n_elements=n_elements, start_index=start_index):
            return False
        for iteration_check in range(n_elements):
            element = self.elements[start_index + iteration_check]
            if element == OPERATIONAL_SPRING:
                return False
        return True

    def get_spring_row_with_replacement(self, replacement_index: int, new_spring_element: SpringElement) -> 'SpringRow':
        new_elements = self.elements.copy()
        new_elements[replacement_index] = new_spring_element
        return SpringRow(elements=new_elements)
    
    def get_spring_row_with_damaged_springs_elements_at_start_index(self, n_elements: int, start_index: int) -> 'SpringRow':
        current_spring_row = self
        for i in range(n_elements):
            new_spring_row = current_spring_row.get_spring_row_with_replacement(replacement_index=start_index + i, new_spring_element=DAMAGED_SPRING)
            current_spring_row = new_spring_row
        return current_spring_row

    def fill_unknown_with_working_element(self) -> None:
        for i, el in enumerate(self.elements):
            if el == UNKNOWN_SPRING:
                self.elements[i] = OPERATIONAL_SPRING

    def get_spring_rows_that_fits_new_element(self, n_elements: int, start_interval_search: int = None, end_interval_search: int = None) -> List['SpringRow']:
        start_interval_search = start_interval_search if start_interval_search is not None else 0
        end_interval_search = end_interval_search if end_interval_search is not None else len(self.elements)
        spring_rows_that_fits_new_element = []
        for i in range(start_interval_search, end_interval_search - n_elements):
            if self.fits_contiguous_damaged_springs_elements_at_start_index(n_elements=n_elements, start_index=i):
                candidate_spring_row = self.get_spring_row_with_damaged_springs_elements_at_start_index(n_elements=n_elements, start_index=i)
                # candidate_spring_row.fill_unknown_with_working_element()
                spring_rows_that_fits_new_element.append(candidate_spring_row)
        return spring_rows_that_fits_new_element

    def get_spring_rows_that_fits_new_part_sequence(self, parts: List[IntervalPart]) -> List['SpringRow']:
        # after this we have a good selection, even if still invalid scenarios (overlap of parts, and rows that do not consider that other elements can bring to incongruence to desired parts)
        current_candidate_rows = [self]
        for interval_part in parts:
            new_candidate_rows = []
            for current_candidate_row in current_candidate_rows:
                new_candidate_rows.extend(current_candidate_row.get_spring_rows_that_fits_new_element(n_elements=interval_part.n_elements, start_interval_search=interval_part.start, end_interval_search=interval_part.end))
            current_candidate_rows = new_candidate_rows.copy()
        return current_candidate_rows

    def is_valid_row_for_sequence(self, sequence: List[int]) -> bool:
        # assert self.is_final_version,  'replace all unknown element before doing the check'
        return [len(part) for part in self.string_representation.split(OPERATIONAL_SPRING.type) if part != ''] == sequence
    
    def get_spring_rows_that_fits_sequence(self, sequence: List[int]) -> Set['SpringRow']:
        search_interval_parts = IntervalPart.get_parts_from_element_sequence(row_length=len(self.elements), parts_elements=sequence)
        candidate_rows = self.get_spring_rows_that_fits_new_part_sequence(parts=search_interval_parts)
        for candidate_row in candidate_rows:
            candidate_row.fill_unknown_with_working_element()
        return set(candidate_row for candidate_row in candidate_rows if candidate_row.is_valid_row_for_sequence(sequence=sequence))

    def get_number_spring_rows_that_fits_sequence(self, sequence: List[int]) -> int:
        return len(self.get_spring_rows_that_fits_sequence(sequence))

    @property
    def is_allowed_consider_period_adding_unknown_spring_at_the_end(self) -> bool:
        return self.elements[0] != DAMAGED_SPRING

    @property
    def is_allowed_consider_period_adding_unknown_spring_at_the_begin(self) -> bool:
        return self.elements[-1] != DAMAGED_SPRING

    def get_spring_row_extended(self, new_element: SpringElement, put_as_first: bool = False) -> 'SpringRow':
        if put_as_first:
            return SpringRow(elements=[new_element] + self.elements)
        return SpringRow(elements=self.elements+[new_element])

    def __hash__(self) -> int:
        return hash(self.string_representation)

if __name__ == '__main__':
    test_sr_description = '#??????#??.'
    test_sr = SpringRow.from_elements_string(elements_description=test_sr_description)
    # print(len(test_sr.elements))
    # print(test_sr.fits_borders_contiguous_damaged_springs_elements_at_start_index(n_elements=2, start_index=9))  # can enter since next is operational (.), previous is unknown (?)
    # print(test_sr.fits_borders_contiguous_damaged_springs_elements_at_start_index(n_elements=2, start_index=8))  # cannot enter since next is unknown (?), but previous is damaged (#)
    # print(test_sr.fits_borders_contiguous_damaged_springs_elements_at_start_index(n_elements=2, start_index=1)) # cannot enter since previous is damaged (#), even if next is unknown (?)
    # print(test_sr.fits_contiguous_damaged_springs_elements_at_start_index(n_elements=2, start_index=9))  # even if enters, not fits since there is operational (.) in the range
    # print(test_sr.fits_contiguous_damaged_springs_elements_at_start_index(n_elements=5, start_index=2))
    # print(test_sr.fits_contiguous_damaged_springs_elements_at_start_index(n_elements=4, start_index=2))
    # replace_test = test_sr.get_spring_row_with_replacement(replacement_index=2, new_spring_element=SpringElement('X'))
    # print(replace_test)
    # replace_part_test = test_sr.get_spring_row_with_damaged_springs_elements_at_start_index(n_elements=4, start_index=2)
    # print(replace_part_test)
    # replace_part_test.fill_unknown_with_working_element()
    # print(replace_part_test)
    
    # combos = test_sr.get_spring_rows_that_fits_new_element(n_elements=2)
    # for combo in combos:
    #     combo.fill_unknown_with_working_element()
    #     combo.print_as_single_string()

    # combo_parts = test_sr.get_spring_rows_that_fits_new_part_sequence(parts=[IntervalPart(n_elements=2, start=0, end=7), IntervalPart(n_elements=3, start=2, end=11)])
    # for combo in combo_parts:
    #     combo.fill_unknown_with_working_element()
    #     combo.print_as_single_string()
    
    # intervals_parts_test = IntervalPart.get_parts_from_element_sequence(row_length=11, parts_elements=[2, 3])
    # # print(intervals_parts_test)
    # combo_parts = test_sr.get_spring_rows_that_fits_new_part_sequence(parts=intervals_parts_test)
    # for combo in combo_parts:
    #     combo.fill_unknown_with_working_element()
    #     combo.print_as_single_string()

    # test_sr_validate_description = '##..###..#'
    # test_sr_validate = SpringRow.from_elements_string(elements_description=test_sr_validate_description)
    # print(test_sr_validate.is_valid_row_for_sequence(sequence=[2, 3, 1]))
    
    # test_sr_get_combo_description = '.??..??...?##.'
    # test_sequence = [1, 1, 3]
    # test_sr_get_combo = SpringRow.from_elements_string(elements_description=test_sr_get_combo_description)
    # test_match_combos = test_sr_get_combo.get_spring_rows_that_fits_sequence(sequence=test_sequence)
    # print(len(test_match_combos))
    # for combo in test_match_combos:
    #     combo.print_as_single_string()

    # explosion considering question mark as separator, 5 times
    
    def count_combine_result_right(base_combo: List[SpringRow], right_combo: List[SpringRow], sequence_period: List[int]) -> int:
        full_sequence = sequence_period*5
        count = 0
        for combo in base_combo:
            for cr1 in right_combo:
                for cr2 in right_combo:
                    for cr3 in right_combo:
                        for cr4 in right_combo:
                            full_combo = SpringRow(elements=combo.elements + cr1.elements + cr2.elements + cr3.elements + cr4.elements)
                            if full_combo.is_valid_row_for_sequence(sequence=full_sequence):
                                count += 1
        return count
    
    def count_combine_result_left(base_combo: List[SpringRow], left_combo: List[SpringRow], sequence_period: List[int]) -> int:
        full_sequence = sequence_period*5
        count = 0
        for cl1 in left_combo:
            for cl2 in left_combo:
                for cl3 in left_combo:
                    for cl4 in left_combo:
                        for combo in base_combo:
                            full_combo = SpringRow(elements=combo.elements + cl1.elements + cl2.elements + cl3.elements + cl4.elements)
                            if full_combo.is_valid_row_for_sequence(sequence=full_sequence):
                                count += 1
        return count
    
    #    ???#.????#?? 1,1,1,1
    # results are 1002252 and 663552
    
    
    test_expl_description = '???#.????#??'
    test_sequence_expl = [1,1,1,1]
    test_expl = SpringRow.from_elements_string(elements_description=test_expl_description)
    test_match_combos_5_expl_base = test_expl.get_spring_rows_that_fits_sequence(sequence=test_sequence_expl)
    n_test_match_combos_5_expl_base = len(test_match_combos_5_expl_base)
    # test put before
    if test_expl.is_allowed_consider_period_adding_unknown_spring_at_the_begin:
        test_expl_middle_add_before = test_expl.get_spring_row_extended(new_element=UNKNOWN_SPRING, put_as_first=True)
        test_match_combos_5_expl_before = test_expl_middle_add_before.get_spring_rows_that_fits_sequence(sequence=test_sequence_expl)
        n_test_match_combos_5_expl_before = len(test_match_combos_5_expl_before)
        cnt_left_try = count_combine_result_left(base_combo=test_match_combos_5_expl_base, left_combo=test_match_combos_5_expl_before, sequence_period=test_sequence_expl)
    else:
        cnt_left_try = 0
        n_test_match_combos_5_expl_before = 0
    # test put after
    if test_expl.is_allowed_consider_period_adding_unknown_spring_at_the_end:
        test_expl_middle_add_after = test_expl.get_spring_row_extended(new_element=UNKNOWN_SPRING, put_as_first=False)
        test_match_combos_5_expl_after= test_expl_middle_add_after.get_spring_rows_that_fits_sequence(sequence=test_sequence_expl)
        n_test_match_combos_5_expl_after = len(test_match_combos_5_expl_after)
        cnt_right_try = count_combine_result_right(base_combo=test_match_combos_5_expl_base, right_combo=test_match_combos_5_expl_after, sequence_period=test_sequence_expl)
    else:
        cnt_left_try = 0
        n_test_match_combos_5_expl_after = 0
    n_test_match_combos_5_expl_middle = max(n_test_match_combos_5_expl_base, n_test_match_combos_5_expl_before, n_test_match_combos_5_expl_after)
    # print(n_test_match_combos_5_expl_base)
    # print(n_test_match_combos_5_expl_middle)
    print(cnt_left_try)
    print(cnt_right_try)
    print(f'result explosion 5 periodic is {n_test_match_combos_5_expl_base*(n_test_match_combos_5_expl_middle**4)}')
    print(f'result explosion 5 periodic for experiment is {max(cnt_left_try, cnt_right_try, n_test_match_combos_5_expl_base**5)}')

    print('*************')
    # test sample
    test_springs = [
        '???.### 1,1,3',
        '.??..??...?##. 1,1,3',
        '?#?#?#?#?#?#?#? 1,3,1,6',
        '????.#...#... 4,1,1',
        '????.######..#####. 1,6,5',
        '?###???????? 3,2,1',
    ]
    # test part 1
    # tot_test_arrangements = 0
    # for spring_seq_description in test_springs:
    #     spring_seq =spring_seq_description.rstrip().split(' ')
    #     spring_row = SpringRow.from_elements_string(elements_description=spring_seq[0])
    #     sequence = [int(element) for element in spring_seq[1].split(',')]

    #     tot_test_arrangements += len(spring_row.get_spring_rows_that_fits_sequence(sequence))
    # print(f'Test tot arrangements is {tot_test_arrangements}')
    # test part 2
    tot_test_arrangements_unfolded5 = 0
    for spring_seq_description in test_springs:
        # print(spring_seq_description)
        spring_seq =spring_seq_description.rstrip().split(' ')
        base_spring_row = SpringRow.from_elements_string(elements_description=spring_seq[0])
        sequence = [int(element) for element in spring_seq[1].split(',')]
        # test before
        if base_spring_row.is_allowed_consider_period_adding_unknown_spring_at_the_begin:
            spring_row_middle_before = base_spring_row.get_spring_row_extended(new_element=UNKNOWN_SPRING, put_as_first=True)
            match_combos_middle_before = spring_row_middle_before.get_spring_rows_that_fits_sequence(sequence=sequence)
        else:
            match_combos_middle_before = []
        # test after
        if base_spring_row.is_allowed_consider_period_adding_unknown_spring_at_the_end:
            spring_row_middle_after = base_spring_row.get_spring_row_extended(new_element=UNKNOWN_SPRING, put_as_first=False)
            match_combos_middle_after = spring_row_middle_after.get_spring_rows_that_fits_sequence(sequence=sequence)
        else:
            match_combos_middle_after = []

        match_combos_base = base_spring_row.get_spring_rows_that_fits_sequence(sequence=sequence)
        n_combo_base = len(match_combos_base)
        n_combo_middle = max(n_combo_base, len(match_combos_middle_before), len(match_combos_middle_after))
        # print(n_combo_base*(n_combo_middle**4))
        tot_test_arrangements_unfolded5 += n_combo_base*(n_combo_middle**4)
    print(f'Test tot unfolded arrangements is {tot_test_arrangements_unfolded5}')

    # # part 1
    # tot_arrangements = 0
    # with open(".\springs.txt", "r") as fr:
    #     for line in fr:
    #         spring_seq =line.rstrip().split(' ')
    #         spring_row = SpringRow.from_elements_string(elements_description=spring_seq[0])
    #         sequence = [int(element) for element in spring_seq[1].split(',')]

    #         tot_arrangements += len(spring_row.get_spring_rows_that_fits_sequence(sequence))
    # print(f'Tot arrangements is {tot_arrangements}')
    # part 2
    # exploded5_arrangements = 0
    # exploded5_arrangements_experiment = 0
    # with open(".\springs.txt", "r") as fr:
    #     for line in fr:
    #         print(line)
    #         spring_seq =line.rstrip().split(' ')
    #         base_spring_row = SpringRow.from_elements_string(elements_description=spring_seq[0])
    #         sequence = [int(element) for element in spring_seq[1].split(',')]
    #         # test before
    #         if base_spring_row.is_allowed_consider_period_adding_unknown_spring_at_the_begin:
    #             spring_row_middle_before = base_spring_row.get_spring_row_extended(new_element=UNKNOWN_SPRING, put_as_first=True)
    #             match_combos_middle_before = spring_row_middle_before.get_spring_rows_that_fits_sequence(sequence=sequence)
    #         else:
    #             match_combos_middle_before = []
    #         # test after
    #         if base_spring_row.is_allowed_consider_period_adding_unknown_spring_at_the_end:
    #             spring_row_middle_after = base_spring_row.get_spring_row_extended(new_element=UNKNOWN_SPRING, put_as_first=False)
    #             match_combos_middle_after = spring_row_middle_after.get_spring_rows_that_fits_sequence(sequence=sequence)
    #         else:
    #             match_combos_middle_after = []

    #         match_combos_base = base_spring_row.get_spring_rows_that_fits_sequence(sequence=sequence)
    #         n_combo_base = len(match_combos_base)
    #         n_combo_middle = max(n_combo_base, len(match_combos_middle_before), len(match_combos_middle_after))

    #         element_exploded_res = n_combo_base*(n_combo_middle**4)
    #         exploded5_arrangements += element_exploded_res

    #         # cnt_right = count_combine_result_right(base_combo=match_combos_base, right_combo=match_combos_middle_after, sequence_period=sequence)
    #         # cnt_left = count_combine_result_left(base_combo=match_combos_base, left_combo=match_combos_middle_before, sequence_period=sequence)
    #         # element_exploded_res_experiment = max(cnt_right, cnt_left, n_combo_base**5)

    #         # exploded5_arrangements_experiment += element_exploded_res_experiment
    #         # print(f'results are {element_exploded_res} and {element_exploded_res_experiment}')
    # print(f'Test tot unfolded arrangements is {exploded5_arrangements}')
    # print(f'Test tot unfolded arrangements experiment is {exploded5_arrangements_experiment}')