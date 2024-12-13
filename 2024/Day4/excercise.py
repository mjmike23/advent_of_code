test = [
    'MMMSXXMASM',
    'MSAMXMSMSA',
    'AMXSXMAAMM',
    'MSAMASMSMX',
    'XMASAMXAMM',
    'XXAMMXXAMA',
    'SMSMSASXSS',
    'SAXAMASAAA',
    'MAMMMXMMMM',
    'MXMXAXMASX',
]


# with open("puzzle.txt", "r") as fr:
with open("puzzle.txt", "r") as a:
    fr = test.copy()
    horiz = [line.rstrip() for line in fr]
    horiz_len = len(horiz[0])
    vert = [''.join([h[i] for h in horiz]) for i in range(horiz_len)]
    vert_len = len(vert[0])
    diag_centrale_nw_se = ''
    for i in range(horiz_len - 1):
        try:
            diag_centrale_nw_se += horiz[i][i]
        except IndexError:
            break
    diag_sup_nw_se = []
    for j in range(horiz_len- 1):
        d = ''
        for i in range(horiz_len - 1):
            try:
                d += horiz[i][i + j]
            except IndexError:
                diag_sup_nw_se.append(d)
                break
        else:
            diag_sup_nw_se.append(d)
    diag_inf_nw_se = []
    for j in range(vert_len - 1):
        d = ''
        for i in range(vert_len - 1):
            try:
                d += vert[i][i + j]
            except IndexError:
                diag_inf_nw_se.append(d)
                break
        else:
            diag_inf_nw_se.append(d)
    diag_centrale_ne_sw = ''
    for i in range(horiz_len - 1):
        try:
            diag_centrale_ne_sw += horiz[i][horiz_len - 1 - i]
        except IndexError:
            break
    diag_sup_ne_sw = []
    for j in range(1, horiz_len - 1):
        d = ''
        i = 0
        while (horiz_len - 1 - i - j) >= 0:
            d += horiz[i][horiz_len - 1 - i - j]
            i += 1
        else:
            diag_sup_ne_sw.append(d)
    diag_inf_ne_sw = []
    for j in range(1, vert_len - 1):
        d = ''
        for i in range(len(vert) - 1):
            try:
                d += vert[- 1- i][i + j]
                i += 1
            except IndexError:
                diag_inf_ne_sw.append(d)
                break
        else:
            diag_inf_ne_sw.append(d)
    diag = [diag_centrale_nw_se, *diag_sup_nw_se, * diag_inf_nw_se, diag_centrale_ne_sw, *diag_sup_ne_sw, *diag_inf_ne_sw]
    direzioni = [*horiz, *vert, *diag]
    n_xmas_debug = [(direzione.count('XMAS') + direzione.count('SAMX'), direzione) for direzione in direzioni]
    for n, di in n_xmas_debug:
        print(f'{di} -> {n}')
    n_xmas = [direzione.count('XMAS') + direzione.count('SAMX') for direzione in direzioni]
    print(sum(n_xmas))

