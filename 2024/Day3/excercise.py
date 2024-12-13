with open("puzzle.txt", "r") as fr:
    valid_factors = []
    for line in fr:
        split_elegible_mol = [cmd for cmd in line.split(')') if 'mul(' in cmd]
        for cmd in split_elegible_mol:
            operation = cmd[cmd.rfind('mul(') + 4:]
            if operation.replace(' ', '') != operation:
                # print(f'{cmd} -> space in {operation}')
                continue
            try:
                numbers = operation.split(',')
                if len(numbers) != 2:
                    continue
                valid_factors.append(int(numbers[0])*int(numbers[1]))
                # print(f'{cmd} -> valid {numbers[0]} * {numbers[0]} = {str(int(numbers[0])*int(numbers[1]))}')
            except:
                # print(f'{cmd} -> invalid')
                continue
    print(sum(valid_factors))  # solution a


with open("puzzle.txt", "r") as fr:
    valid_factors_doing = []
    do_operation = True
    for line in fr:
        for i, ch in enumerate(line):
            # search mul only if do active
            if do_operation and ch == 'm':
                elegible_mul = line[i: i+len('mul(')+ 8]
                if ('mul(' not in elegible_mul) or (')' not in elegible_mul):
                    continue
                try:
                    operation = elegible_mul.replace('mul(', '').split(')')[0]
                    numbers = operation.split(',')
                    if len(numbers) != 2:
                        continue
                    valid_factors_doing.append(int(numbers[0])*int(numbers[1]))
                    # print(f'{elegible_mul} -> valid {numbers[0]} * {numbers[1]} = {str(int(numbers[0])*int(numbers[1]))}')
                except:
                    # print(f'{elegible_mul} -> invalid')
                    continue
            if ch == 'd':
                elegible_doing = line[i: i+len("don't()")]
                # print(f'{elegible_doing} detected')
                if "don't()" in elegible_doing:
                    do_operation =  False
                    # print(f'{elegible_doing} dont')
                    continue
                if 'do()' in elegible_doing:
                    # print(f'{elegible_doing} do')
                    do_operation =  True
    print(sum(valid_factors_doing))  # solution b