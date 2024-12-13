with open("puzzle.txt", "r") as fr:
    l_left = []
    l_right = []
    for line in fr:
        line_numbs = line.split('   ')
        l_left.append(int(line_numbs[0]))
        l_right.append(int(line_numbs[1]))
    l_left.sort()
    l_right.sort()
    distance = [abs(r[0] - r[1]) for r in zip(l_left, l_right)]
    print(sum(distance))  # solution a
    similarity_index = [i * l_right.count(i) for i in l_left]
    print(sum(similarity_index))  # solution b
        