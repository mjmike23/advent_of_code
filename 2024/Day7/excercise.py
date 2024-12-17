from itertools import permutations, repeat

with open("puzzle.txt", "r") as fr:
    calibrations = [line.rstrip() for line in fr]
    r = 0
    for calibration in calibrations:
        result_searched = int(calibration.split(':')[0])
        numbers = [int(n) for n in calibration.split(':')[1].lstrip().split(' ')]
        print(f'searching for {result_searched} using {numbers}')
        n_operations = len(numbers) - 1
        operations = [*repeat('+', n_operations), *repeat('*', n_operations)]
        for combo_operations in permutations(operations, n_operations):
            print(combo_operations)
            expression = ''
            for i, number in enumerate(numbers):
                expression += f'{number}'
                try:
                    expression += combo_operations[i]
                except IndexError:
                    pass
            if eval(expression) == result_searched:
                print(f'ottimo con {expression} -> {result_searched}')
                r += 1
    print(r)