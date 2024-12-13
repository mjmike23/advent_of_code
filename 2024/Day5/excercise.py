from typing import Set, List, Tuple

with open("puzzle.txt", "r") as fr:
    print_sequences: List[str] = []
    rules: Set[str] = set()
    are_rules = True
    for line in fr:
        line = line.rstrip()
        if line == '':
            are_rules = False
            continue
        if are_rules:
            rules.add(line)
            continue
        print_sequences.append(line)

    valid_sequences = []
    invalid_sequences_and_violated_rules: List[Tuple[List, str]] = []
    for sequence in print_sequences:
        seq_tot_rules = set()
        seq_elements = sequence.split(',')
        # print(seq_elements)
        for i, el in enumerate(seq_elements):
            rules_to_verify = [f'{prev_elem}|{el}' for prev_elem in seq_elements[:i]]
            rules_to_verify.extend([f'{el}|{next_elem}' for next_elem in seq_elements[i:]])
            rules_to_verify.remove(f'{el}|{el}')
            # print(el)
            # print(rules_to_verify)
            seq_tot_rules.update(set(rules_to_verify))
        # print(seq_tot_rules.difference(rules))
        if len(seq_tot_rules.difference(rules)) == 0:
            valid_sequences.append(seq_elements)
        else:
            invalid_sequences_and_violated_rules.append((seq_elements, seq_tot_rules.difference(rules)))

    # print(valid_sequences)
    print(sum([int(seq[len(seq) // 2]) for seq in valid_sequences]))  # solution a

    fixed_sequences = []
    for invalid_seq, _ in invalid_sequences_and_violated_rules:
        ranked_elements: List[Tuple[str, int]] = []
        for element_to_order in invalid_seq:
            rank = 0
            for element_to_face in invalid_seq:
                if element_to_order == element_to_face:
                    continue
                if f'{element_to_order}|{element_to_face}' in rules:
                    rank -= 1
                    continue
                if f'{element_to_face}|{element_to_order}' in rules:
                    rank += 1
                    continue
                raise Exception(f'******** unreachable facing {element_to_order} vs {element_to_face}')
            # print(f'Element {element_to_order} position {rank}')
            ranked_elements.append((element_to_order, rank))
        fixed_seq = [x[0] for x in sorted(ranked_elements, key=lambda x: x[1])]
        # print(f'{invalid_seq} fixed to {fixed_seq}')
        fixed_sequences.append(fixed_seq)

    # print(fixed_sequences)
    print(sum([int(seq[len(seq) // 2]) for seq in fixed_sequences]))  # solution b