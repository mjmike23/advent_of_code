from copy import deepcopy
from itertools import repeat
from typing import List, Tuple

with open("puzzle.txt", "r") as fr:
    i = 0
    for line in fr:
        codec =  line.rstrip()
        i += 1
        # read first line only
        if i > 0:
            break
    id = 0
    is_file_block = True
    # approach id per cell
    files_layout = []
    for c in codec:
        if is_file_block:
            files_layout.extend(repeat(id, int(c)))
            id += 1
        else:
            files_layout.extend('.'*int(c))
        is_file_block = not is_file_block
    # print(''.join(files_layout))
    defragmented = deepcopy(files_layout)
    last_cursor = len(defragmented) - 1
    for i, c in enumerate(defragmented):
        if c == '.':
            while True:
                last_c_memory = defragmented[last_cursor]
                if last_c_memory != '.':
                    # print(f'found {last_c_memory}')
                    break
                last_cursor -= 1
            if i >= last_cursor:
                # print(f'breaking with i as {i} and last_cursor as {last_cursor}')
                break
            defragmented[i] = last_c_memory
            defragmented[last_cursor] = '.'
    # print(''.join([str(x) for x in defragmented]))
    # print(defragmented)
    print(sum([index*int(id) for index, id in enumerate(defragmented) if id != '.']))  # solution a

    # print(''.join([str(x) for x in files_layout]))
    defragmented_compact = deepcopy(files_layout)
    # list files to move: ID, lenght, starting index
    files_to_move: List[Tuple[int, int, int]] = []
    file_component = None
    file_lenght = 0
    file_starting_index = 0
    for i, c in enumerate(defragmented_compact[::-1]):
        # print(f'iteration {i} current scan {c}, file_component {file_component}')
        # caso eravamo nel vuoto e continuiamo a stare nel vuoto -> do nothing
        if file_component is None and str(c) == '.':
            continue
        # caso eravamo nel vuoto e entriamo in nuovo file -> file setting start
        if file_component is None and str(c) != '.':
            file_component = c
            file_lenght = 1
            continue
        # caso siamo nel file (stesso di prima) -> keep on adding length
        if str(c) == str(file_component):
            file_lenght += 1
            continue
        # caso eravamo in un file, e ora andiamo nel vuoto o eravamo in un file, ora andiamo in un altro. Sarebbero i casi rimanenti
        file_starting_index = len(defragmented_compact) - i
        # print(f'We need to search {file_component} long {file_lenght} that start at index {file_starting_index}')
        files_to_move.append((int(file_component), file_lenght, file_starting_index))
        file_lenght = 1
        file_component = c if c != '.' else None
    if file_component is not None:
        # print(f'We need to search {file_component} long {file_lenght} that start at index 0')
        files_to_move.append((int(file_component), file_lenght, file_starting_index))
    # print(len(files_to_move))
    # print(files_to_move)
    for id, len, index in files_to_move:
        i = defragmented_compact.index('.')
        while i < index:
            if defragmented_compact[i: i+len] == list(repeat('.', len)):
                # print(f'Found space for file ({id}, {len}, {index}) in {i}')
                defragmented_compact[i: i+len] = list(repeat(id, len))
                defragmented_compact[index: index+len] = list(repeat('.', len))
                break
            i += 1
        else:
            # print(f'Unable to find enough space for file ({id}, {len}, {index}) in {i}')
            pass
    # print(''.join([str(x) for x in defragmented_compact]))
    print(sum([index*int(id) for index, id in enumerate(defragmented_compact) if id != '.']))  # solution a (wait a min or something)

