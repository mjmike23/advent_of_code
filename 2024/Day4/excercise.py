with open("puzzle.txt", "r") as fr:
    horiz = [line.rstrip() for line in fr]
    horiz_len = len(horiz[0])
    vert = [''.join([h[i] for h in horiz]) for i in range(horiz_len)]
    vert_len = len(vert[0])
    diag_sup_nw_se = []
    for offset_est in range(horiz_len):
        d = ''
        for i in range(horiz_len):
            try:
                d += horiz[i][i + offset_est]
            except IndexError:
                diag_sup_nw_se.append(d)
                break
        else:
            diag_sup_nw_se.append(d)
    diag_inf_nw_se = []
    # start from 1 to not take twice central diagonal nw_se
    for offset_sud in range(1, vert_len):
        d = ''
        for i in range(vert_len):
            try:
                d += vert[i][i + offset_sud]
            except IndexError:
                diag_inf_nw_se.append(d)
                break
        else:
            diag_inf_nw_se.append(d)
    diag_sup_ne_sw = []
    for offset_west in range(horiz_len):
        d = ''
        i = 0
        while (horiz_len - 1 - i - offset_west) >= 0:
            d += horiz[i][horiz_len - 1 - i - offset_west]
            i += 1
        else:
            diag_sup_ne_sw.append(d)
    diag_inf_ne_sw = []
    # start from 1 to not take twice central diagonal ne_sw
    for j in range(1, vert_len - 1):
        d = ''
        for i in range(len(vert)):
            try:
                d += vert[- 1- i][i + j]
                i += 1
            except IndexError:
                diag_inf_ne_sw.append(d)
                break
        else:
            diag_inf_ne_sw.append(d)
    diag = [*diag_sup_nw_se, *diag_inf_nw_se, *diag_sup_ne_sw, *diag_inf_ne_sw]
    direzioni = [*horiz, *vert, *diag]
    # n_xmas_debug = [(direzione.count('XMAS') + direzione.count('SAMX'), direzione) for direzione in direzioni]
    # for n, di in n_xmas_debug:
    #     print(f'{di} -> {n}')
    n_xmas = [direzione.count('XMAS') + direzione.count('SAMX') for direzione in direzioni]
    print(sum(n_xmas))  # solution a

    # borders excluded searching for the center of the X
    n_x_mas = 0
    for i in range(1, vert_len - 1):
        for j in range(1, horiz_len -1):
            if horiz[i][j] != 'A':
                # not A, not valid x
                continue
            nw = horiz[i - 1][j - 1]
            ne = horiz[i - 1][j + 1]
            sw = horiz[i + 1][j - 1]
            se = horiz[i + 1][j + 1]
            if nw == ne == 'M' and sw == se == 'S':
                n_x_mas += 1
                continue
            if nw == sw == 'M' and ne == se == 'S':
                n_x_mas += 1
                continue
            if sw == se == 'M' and nw == ne == 'S':
                n_x_mas += 1
                continue
            if se == ne == 'M' and nw == sw == 'S':
                n_x_mas += 1
                continue
    print(n_x_mas)  # solution b