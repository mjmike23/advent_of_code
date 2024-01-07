from typing import List, Dict, Tuple, Set, Iterable
from dataclasses import dataclass
import itertools as it

MAJOR = '>'
MINOR = '<'
START_WORKFLOW_ID = 'in'
PART_ACCEPTED = 'A'
PART_REJECTED = 'R'

ELEMENT_X = 'x'
ELEMENT_M = 'm'
ELEMENT_A = 'a'
ELEMENT_S = 's'


@dataclass(frozen=True)
class Part:

    x: int
    m: int
    a: int
    s: int

    @property
    def tot_rating(self) -> int:
        return self.x + self.m + self.a + self.s

    @property
    def full_dict(self) -> Dict[str, int]:
        return {ELEMENT_X: self.x, ELEMENT_M: self.m, ELEMENT_A: self.a,ELEMENT_S: self.s}

    @property
    def tot_rating(self) -> int:
        return self.x + self.m + self.a + self.s

    @staticmethod
    def from_dictionary(part_dictionary: Dict[str, int]) -> 'Part':
        return Part(
            x=part_dictionary[ELEMENT_X],
            m=part_dictionary[ELEMENT_M],
            a=part_dictionary[ELEMENT_A],
            s=part_dictionary[ELEMENT_S],
        ) 

    @staticmethod
    def from_string(description: str) -> 'Part':
        part_dictionary = {}
        for element in description.rstrip().removeprefix('{').removesuffix('}').split(','):
            element_info = element.split('=')
            part_dictionary[element_info[0]] = int(element_info[1])
        return Part.from_dictionary(part_dictionary=part_dictionary)

@dataclass(frozen=True)
class PartSet:

    x_interval: Tuple[int, int]
    m_interval: Tuple[int, int]
    a_interval: Tuple[int, int]
    s_interval: Tuple[int, int]

    @property
    def part_delegate(self) -> Part:
        return Part(x=self.x_interval[0], m=self.m_interval[0], a=self.a_interval[0], s=self.s_interval[0])
   
    def get_delta_interval(self, element: str) -> int:
        if element == ELEMENT_X:
            return (self.x_interval[1] - self.x_interval[0]) + 1
        if element == ELEMENT_M:
            return (self.m_interval[1] - self.m_interval[0]) + 1
        if element == ELEMENT_A:
            return (self.a_interval[1] - self.a_interval[0]) + 1
        if element == ELEMENT_S:
            return (self.s_interval[1] - self.s_interval[0]) + 1
        raise Exception(f'Unreachable element tpe {element}')

    @property
    def n_set_parts(self) -> int:
        n = 1
        for element in [ELEMENT_X, ELEMENT_M, ELEMENT_A, ELEMENT_S]:
            n *= self.get_delta_interval(element=element)
        return n


@dataclass(frozen=True)
class Rule:

    parameter: str
    comparer: str
    value: int
    id_rule_output: str

    @staticmethod
    def from_string(description: str) -> 'Rule':
        rule_info = description.rstrip().split(':')
        condition = rule_info[0]
        id_rule_output = rule_info[1]
        for comparer_candidate in (MAJOR, MINOR):
            ch_index_comparer = condition.find(comparer_candidate)
            if ch_index_comparer != -1:
                comparer = comparer_candidate
                break
        else:
            raise Exception(f'Unable to find comparere into condition {description}')
        parameter = condition[:ch_index_comparer]
        value = int(condition[ch_index_comparer + 1:])
        return Rule(parameter=parameter, comparer=comparer, value=value, id_rule_output=id_rule_output)

    def do_part_pass(self, part: Part) -> bool:
        if self.comparer == MAJOR:
            return part.full_dict[self.parameter] > self.value
        if self.comparer == MINOR:
            return part.full_dict[self.parameter] < self.value


@dataclass(frozen=True)
class Workflow:

    id: str
    rules: Tuple[Rule]
    id_wf_otherwise_output: str

    @staticmethod
    def from_string(description: str) -> 'Workflow':
        wf_info = description.rstrip().removesuffix('}').split('{')
        id = wf_info[0]
        all_rules = wf_info[1].split(',')
        rules = [Rule.from_string(rule_description) for rule_description in all_rules[:-1]]
        id_wf_otherwise_output = all_rules[-1]
        return Workflow(id=id, rules=tuple(rules), id_wf_otherwise_output=id_wf_otherwise_output)

    def get_part_destination_wf_id(self, part: Part) -> str:
        for rule in self. rules:
            if rule.do_part_pass(part=part):
                return rule.id_rule_output
        return self.id_wf_otherwise_output

    def get_element_boundary_values(self, element: str) -> Set[int]:
        assert element in [ELEMENT_X, ELEMENT_M, ELEMENT_A, ELEMENT_S], f'unable to extract boundary info for element {element}'
        boundary_values = []
        for rule in self.rules:
            if rule.parameter == element:
                boundary_values.append(rule.value)  # sure thing boundary is the value
                boundary_values.append(rule.value + 1 if rule.comparer == MAJOR else rule.value - 1)  # next boundary depends on comparer: value +1 for major, value -1 for minor
        return boundary_values

@dataclass(frozen=True)
class WorkMachine:

    workflows: Tuple[Workflow]

    def get_workflow_by_id(self, workflow_id) -> Workflow:
        return [workflow for workflow in self.workflows if workflow.id == workflow_id][0]

    def is_part_accepted(self, part: Part) -> bool:
        current_wf_id = START_WORKFLOW_ID
        while True:
            current_workflow = self.get_workflow_by_id(workflow_id=current_wf_id)
            current_wf_id = current_workflow.get_part_destination_wf_id(part=part)
            if current_wf_id == PART_ACCEPTED:
                return True
            if current_wf_id == PART_REJECTED:
                return False
    
    def get_rules_element_boundary_values(self, element: str) -> Set[int]:
        return set(it.chain.from_iterable([rule.get_element_boundary_values(element=element) for rule in self.workflows]))
    
    def get_rules_element_boundary_intervals(self, element: str, max_value: int=4000) -> List[Tuple[int, int]]:
        boundary_values = self.get_rules_element_boundary_values(element=element)
        boundary_values.add(1)
        boundary_values.add(max_value)
        boundary_values = list(boundary_values)
        boundary_values.sort()
        # print(f'relevant boundary values for element {element} are {boundary_elements}')
        return [(b_el, boundary_values[i + 1]) for i, b_el in enumerate(boundary_values[:-1]) if i%2 == 0]
    
    def get_part_representative_sets(self, max_value: int=4000) -> Iterable[PartSet]:
        x_intervals = self.get_rules_element_boundary_intervals(element=ELEMENT_X, max_value=max_value)
        m_intervals = self.get_rules_element_boundary_intervals(element=ELEMENT_M, max_value=max_value)
        a_intervals = self.get_rules_element_boundary_intervals(element=ELEMENT_A, max_value=max_value)
        s_intervals = self.get_rules_element_boundary_intervals(element=ELEMENT_S, max_value=max_value)
        print(f'n sets to obtain is {len(x_intervals) * len(m_intervals) * len(a_intervals) * len(s_intervals)}')
        for x_interval in x_intervals:
            for m_interval in m_intervals:
                for a_interval in a_intervals:
                    for s_interval in s_intervals:
                        yield PartSet(x_interval=x_interval, m_interval=m_interval, a_interval=a_interval, s_interval=s_interval)
        # return {PartSet(x_interval=interval_combo[0], m_interval=interval_combo[1], a_interval=interval_combo[2], s_interval=interval_combo[3]) for interval_combo in it.product(x_intervals, m_intervals, a_intervals, s_intervals)}  # is a generator but still slow as hell!
            

if __name__ == '__main__':
    # ut part 1
    test_rule_description = 'a<2006:qkq'
    test_rule = Rule.from_string(description=test_rule_description)
    print(test_rule)
    test_part_description = '{x=787,m=2655,a=1222,s=2876}'
    test_part = Part.from_string(description=test_part_description)
    print(test_part)
    assert test_rule.do_part_pass(part=test_part)
    test_wf_description = 'px{a<2006:qkq,m>2090:A,rfg}'
    test_wf = Workflow.from_string(description=test_wf_description)
    print(test_wf)
    assert test_wf.get_part_destination_wf_id(part=test_part) == 'qkq'
    # test part 1
    test_workflow_descriptions = [
        'px{a<2006:qkq,m>2090:A,rfg}',
        'pv{a>1716:R,A}',
        'lnx{m>1548:A,A}',
        'rfg{s<537:gd,x>2440:R,A}',
        'qs{s>3448:A,lnx}',
        'qkq{x<1416:A,crn}',
        'crn{x>2662:A,R}',
        'in{s<1351:px,qqz}',
        'qqz{s>2770:qs,m<1801:hdj,R}',
        'gd{a>3333:R,R}',
        'hdj{m>838:A,pv}',
    ]
    test_part_descriptions = [
        '{x=787,m=2655,a=1222,s=2876}',
        '{x=1679,m=44,a=2067,s=496}',
        '{x=2036,m=264,a=79,s=2244}',
        '{x=2461,m=1339,a=466,s=291}',
        '{x=2127,m=1623,a=2188,s=1013}',
    ]
    test_workflows = [Workflow.from_string(description=wf_desc) for wf_desc in test_workflow_descriptions]
    test_parts = [Part.from_string(part_description) for part_description in test_part_descriptions]
    test_wf_machine = WorkMachine(workflows=tuple(test_workflows))
    # print(test_wf_machine)
    for part in test_parts:
        print(f'part {part} accepted: {test_wf_machine.is_part_accepted(part=part)}')
    print(f'Test workflow tot rating is {sum([part.tot_rating for part in test_parts if test_wf_machine.is_part_accepted(part=part)])}')
    # real part 1
    workflow_machine_collect = True
    workflows = []
    parts: List[Part] = []
    with open('.\\flow_chain.txt', "r") as fr:
        for line in fr:
            if len(line) <= 1:
                workflow_machine_collect = False
                continue
            if workflow_machine_collect:
                workflows.append(Workflow.from_string(description=line))
            else:
                parts.append(Part.from_string(description=line))
    wf_machine = WorkMachine(workflows=tuple(workflows))
    print(f'Workflow tot rating is {sum([part.tot_rating for part in parts if wf_machine.is_part_accepted(part=part)])}')
    # ut part 2
    r = test_wf_machine.get_rules_element_boundary_values(element=ELEMENT_A)
    print(r)
    print(test_wf_machine.get_rules_element_boundary_intervals(element=ELEMENT_A))
    print(list(test_wf_machine.get_part_representative_sets())[0])
    # test part 2
    test_n_accepted_parts = 0
    test_repr_set_parts = test_wf_machine.get_part_representative_sets()
    for set_part in test_repr_set_parts:
        if test_wf_machine.is_part_accepted(part=set_part.part_delegate):
            test_n_accepted_parts += set_part.n_set_parts
    print(f'Test workflow distinct combo accepted are {test_n_accepted_parts}')
    # real part 2
    n_accepted_parts = 0
    repr_set_parts = wf_machine.get_part_representative_sets()
    for i, set_part in enumerate(repr_set_parts):
        # print(i)
        if wf_machine.is_part_accepted(part=set_part.part_delegate):
            n_accepted_parts += set_part.n_set_parts
    print(f'Workflow distinct combo accepted are {n_accepted_parts}')