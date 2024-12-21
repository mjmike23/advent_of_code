from copy import deepcopy

with open("puzzle.txt", "r") as fr:
    for i, line in enumerate(fr):
        if i == 0:
            base_stones = [int(stone) for stone in line.rstrip().split(' ')]
            continue
        print(f'reading line {i}, but excercise takes only row 0')
    steps = {0: deepcopy(base_stones)}
    number_blinks = 25
    for i in range(1, number_blinks + 1):
        stones_init = deepcopy(steps[i - 1])
        stones_end = []
        for stone in stones_init:
            if stone == 0:
                stones_end.append(1)
                continue
            if len(str(stone)) % 2 == 0:
                cut_len = int(len(str(stone))/2)
                left_stone = int(str(stone)[:cut_len])
                right_stone = int(str(stone)[cut_len:])
                stones_end.extend([left_stone, right_stone])
                continue
            stones_end.append(stone * 2024)
        steps[i] = deepcopy(stones_end)
    # for step, stones in steps.items():
    #     print(f'Step {step} has stones {stones}')
    print(len(steps[number_blinks]))  # solution a

    # sol 2
    curr_stones = deepcopy(base_stones)
    map_stones = {}
    number_blinks = 75
    for i in range(1, number_blinks + 1):
        print(f'Doing iteration {i}')
        stones_end = []
        distinct_stones = set(curr_stones)
        # print(f'Distinct stones are {len(set(curr_stones))}')
        for stone in set(curr_stones):
            if stone in map_stones.keys():
                continue
            if stone == 0:
                map_stones[stone] = 1
                continue
            if len(str(stone)) % 2 == 0:
                cut_len = int(len(str(stone))/2)
                left_stone = int(str(stone)[:cut_len])
                right_stone = int(str(stone)[cut_len:])
                map_stones[stone] = [left_stone, right_stone]
                continue
            map_stones[stone] = (stone * 2024)

        print('Doing the replacement')
        # list approach
        for stone in curr_stones:
            new_stones = map_stones[stone]
            if isinstance(new_stones, list):
                stones_end.extend(new_stones)
                continue
            stones_end.append(new_stones)

        curr_stones = deepcopy(stones_end)
        # end list approach

        # # string replace approach
        # # new stones starts from existing. Eacj stone surrounded by double _ to understande needs to be replaced
        # new_stones_as_str = '__'.join([str(s) for s in curr_stones])
        # new_stones_as_str = f'__{new_stones_as_str}__'
        # for stone in distinct_stones:
        #     new_stones = map_stones[stone]
        #     if isinstance(new_stones, list):
        #         stones_replace = ',,'.join([str(s) for s in new_stones])
        #         stones_replace = f',{stones_replace},'
        #     else:
        #         stones_replace = f',{new_stones},'

        #     new_stones_as_str = new_stones_as_str.replace(f'_{stone}_', stones_replace)

        # new_stones_as_str = (
        #     new_stones_as_str
        #     .removeprefix('_')
        #     .removesuffix('_')
        #     .removeprefix(',')
        #     .removesuffix(',')
        # )
        # # print(new_stones_as_str)
        # curr_stones = [int(s) for s in new_stones_as_str.split(',,')]
        # # end string replace approach

        # print(f'Step {i} has stones {curr_stones}')
    print(len(curr_stones))
