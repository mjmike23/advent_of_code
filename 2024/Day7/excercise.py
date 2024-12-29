from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from copy import deepcopy


@dataclass
class Combo:

    current_value: int
    numbers: List[int]
    operations: List[str]

    def __init__(self, current_value: int, numbers: Optional[List[int]] = None, operations: Optional[List[str]]=None):
        self.current_value = current_value
        self.numbers = numbers if numbers else [current_value]
        self.operations = operations if operations else []


with open("puzzle.txt", "r") as fr:
    calibrations = [line.rstrip() for line in fr]
    # tuple key of dict is calibration (result_searched, numbers)
    calibration_matches: Dict[Tuple[int, Tuple[int]], List[Combo]] = {}
    for calibration in calibrations:
        result_searched = int(calibration.split(':')[0])
        numbers = tuple([int(n) for n in calibration.split(':')[1].lstrip().split(' ')])
        # print(f'searching for {result_searched} using {numbers}')

        base_combo = Combo(current_value=numbers[0])
        stage_combos: List[Combo] = [base_combo]
        for number in numbers[1:]:
            new_stage_combos = []

            for combo in stage_combos:
                new_value_plus = combo.current_value + number
                new_value_mult = combo.current_value * number
                new_numbers = deepcopy(combo.numbers)
                new_numbers.append(number)
                # valid if not overflows required result
                if new_value_plus <= result_searched:
                    new_combo_plus_ops = deepcopy(combo.operations)
                    new_combo_plus_ops.append('+')
                    new_combo_plus = Combo(current_value=new_value_plus, numbers=new_numbers, operations=new_combo_plus_ops)
                    new_stage_combos.append(new_combo_plus)
                if new_value_mult <= result_searched:
                    new_combo_mult_ops = deepcopy(combo.operations)
                    new_combo_mult_ops.append('*')
                    new_combo_mult = Combo(current_value=new_value_mult, numbers=new_numbers, operations=new_combo_mult_ops)
                    new_stage_combos.append(new_combo_mult)

            stage_combos = deepcopy(new_stage_combos)

        match_combos = []
        for final_combo in stage_combos:
            if final_combo.current_value == result_searched:
                # print(f'following combo fits: {final_combo}')
                match_combos.append(final_combo)
    
        calibration_matches[(result_searched, numbers)] = match_combos
    
    print(sum([calibrations[0] for calibrations, matches in calibration_matches.items() if len(matches) > 0]))  # solution a