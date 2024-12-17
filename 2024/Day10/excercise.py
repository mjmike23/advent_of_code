from copy import deepcopy

with open("puzzle.txt", "r") as fr:
    map = []
    for line in fr:
        map.append([int(x) for x in line.rstrip()])
    trailheads = []
    for i, line in enumerate(map):
        for j, h in enumerate(line):
            if h== 0:
                trailheads.append((h, i, j))
    # print(trailheads)
    map_trails = {}
    for head in trailheads:
        new_trail = [head]
        trails_from_head = [new_trail]
        next_step_value = 1
        while next_step_value <= 9:
            # print(f'Here we go searching to {next_step_value}')
            for trail in trails_from_head:
                base_trail = deepcopy(trail)
                last_knot = base_trail[-1]
                # trails_from_head mutable object, hence whenever found new biforcation actually go here again, we don't want to iterate on same step biforcations
                # also, if trail was dead end (stopped steps above) we do not want to search next step
                if last_knot[0] != next_step_value - 1:
                    continue
                # print(f'Searching for {next_step_value} starting from {last_knot}')
                last_knot_value = last_knot[0]
                last_knot_y = last_knot[1]
                last_knot_x = last_knot[2]
                near_points = ((last_knot_y + 1, last_knot_x), (last_knot_y - 1, last_knot_x), (last_knot_y, last_knot_x + 1), (last_knot_y, last_knot_x - 1))
                find_biforcation = False
                for point in near_points:
                    if point[0] < 0 or point[1] < 0:
                        # out of bound
                        continue
                    try:
                        value = map[point[0]][point[1]]
                        # print(f'value of point {point} is {value}')
                    except IndexError:
                        # out of bound
                        continue
                    if value == next_step_value:
                        find_next_step = True
                        if not find_biforcation:
                            trail.append((value, point[0], point[1]))
                            find_biforcation = True
                            # print(f'Found: {trail}')
                            continue
                        new_biforcation_trail = deepcopy(base_trail)
                        trails_from_head.append(new_biforcation_trail)
                        new_biforcation_trail.append((value, point[0], point[1]))
                        # print(f'Found in new biforcation: {new_biforcation_trail}')
            # print(trails_from_head)
            next_step_value += 1
        map_trails[head] = trails_from_head
    score_map = 0
    for head in map_trails.keys():
        heighs_reached = {trail[-1] for trail in map_trails[head] if trail[-1][0] == 9}
        # print(f'head {head} score is {len(heighs_reached)}')
        score_map += len(heighs_reached)
    print(score_map)  # solution a

    score_map_n_trails = 0
    for head in map_trails.keys():
        trails_reaching_heighs = [trail[-1] for trail in map_trails[head] if trail[-1][0] == 9]
        # print(f'head {head} score n trails is {len(trails_reaching_heighs)}')
        score_map_n_trails += len(trails_reaching_heighs)
    print(score_map_n_trails)  # solution b