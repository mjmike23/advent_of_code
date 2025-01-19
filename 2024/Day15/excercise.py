from typing import List, Tuple, Set
from copy import deepcopy
from dataclasses import dataclass

def represents_map(map: List[List[str]]):
    for line in map:
        repr_str = ''.join([x for x in line])
        print(repr_str)

with open("puzzle.txt", "r") as fr:
    base_map = []
    robot_movements = []
    read_map =  True
    for line in fr:
        line = line.rstrip()
        if line == '':
            read_map = False
            continue
        if read_map:
            base_map.append(list(line))
        else:
            robot_movements.extend(list(line))
    
    robot_init_pos_y = -1
    robot_init_pos_x = -1
    robot_found = False
    for i, line in enumerate(base_map):
        for j, item in enumerate(line):
            if item == '@':
                robot_init_pos_y = i
                robot_init_pos_x = j
                robot_found = True
                break
        if robot_found:
            break
    else:
        raise Exception('robot not found!')
    
    # print(f'initial position robot {robot_init_pos_y}, {robot_init_pos_x}')
    # print('Initial state')
    # represents_map(map=base_map)
    
    movement_map = deepcopy(base_map)
    current_robot_pos = (robot_init_pos_y, robot_init_pos_x)
    for movement in robot_movements:
        rocks_shifted = 0
        robot_moves = False
        investigating_position = None
        space_position = None
        if movement == 'v':
            strafe_down = 1
        elif movement == '^':
            strafe_down = -1
        else:
            strafe_down = 0
        if movement == '>':
            strafe_right = 1
        elif movement == '<':
            strafe_right = -1
        else:
            strafe_right = 0
        
        while True:
            investigating_position = (investigating_position[0] + strafe_down, investigating_position[1] + strafe_right) if investigating_position is not None else (current_robot_pos[0] + strafe_down, current_robot_pos[1] + strafe_right)
            item = movement_map[investigating_position[0]][investigating_position[1]]
            if item == '#':
                break
            if item == '.':
                robot_moves = True
                space_position = investigating_position
                break
            if item == 'O':
                rocks_shifted += 1
                continue
            raise Exception(f'Unreachable, unable to work item {item}')
        
        if robot_moves:
            # do the shift
            if rocks_shifted > 0:
                # shift of rocks means space is filled by rock
                movement_map[space_position[0]][space_position[1]] = 'O'
            next_robot_pos = (current_robot_pos[0] + strafe_down, current_robot_pos[1] + strafe_right)
            # current robot position becomes space, while next becomes robot position
            movement_map[current_robot_pos[0]][current_robot_pos[1]] = '.'
            movement_map[next_robot_pos[0]][next_robot_pos[1]] = '@'

            current_robot_pos = next_robot_pos
        
        # print('')
        # print(f'Move {movement}')
        # represents_map(map=movement_map)

    # print('')
    # print('Final stage')
    # represents_map(map=movement_map)

    sum_coord = 0
    for i, line in enumerate(movement_map):
        for j, item in enumerate(line):
            if item == 'O':
                sum_coord += 100 * i + j
    print(sum_coord)  # solution a

    extended_base_map: List[List[str]] = []
    for line in base_map:
        expanded_line = []
        for item in line:
            if item in ('#', '.'):
                new_items = [item] * 2
            elif item == '@':
                new_items = ['@', '.']
            elif item == 'O':
                new_items = ['[', ']']
            else:
                raise Exception(f'unexpeceted item {item}')
            expanded_line.extend(new_items)
        extended_base_map.append(expanded_line)


    # print('Initial state expanded map')
    # represents_map(map=extended_base_map)

    robot_init_pos_y = -1
    robot_init_pos_x = -1
    robot_found = False
    for i, line in enumerate(extended_base_map):
        for j, item in enumerate(line):
            if item == '@':
                robot_init_pos_y = i
                robot_init_pos_x = j
                robot_found = True
                break
        if robot_found:
            break
    else:
        raise Exception('robot not found!')
    
    @dataclass(frozen=True)
    class ItemPosition:

        item: str
        pos_y: int
        pos_x: int

    @dataclass(frozen=True)
    class Element:

        item_positions: Tuple[ItemPosition]

        @property
        def positions(self) -> Tuple[Tuple[int, int]]:
            return tuple([(ip.pos_y, ip.pos_x) for ip in self.item_positions])

    movement_extended_map = deepcopy(extended_base_map)
    current_robot_pos = (robot_init_pos_y, robot_init_pos_x)
    for movement in robot_movements:
        robot_moves = None
        items_chain_to_move: List[Element] = []
        elements_investigate_if_can_move = {Element(item_positions=(ItemPosition(item='@', pos_y=current_robot_pos[0], pos_x=current_robot_pos[1]),))}
        if movement == 'v':
            strafe_down = 1
        elif movement == '^':
            strafe_down = -1
        else:
            strafe_down = 0
        if movement == '>':
            strafe_right = 1
        elif movement == '<':
            strafe_right = -1
        else:
            strafe_right = 0
        
        while True:
            current_elements_investigate_can_move = deepcopy(elements_investigate_if_can_move)
            next_elements_items: List[ItemPosition] = []
            for element in current_elements_investigate_can_move:
                for item_pos in element.item_positions:
                    next_position = (item_pos.pos_y + strafe_down, item_pos.pos_x + strafe_right)
                    if next_position in element.positions:
                        # print(f'next from here is alredy in the element')
                        continue
                    next_item = movement_extended_map[next_position[0]][next_position[1]]
                    if next_item == '#':
                        robot_moves = False
                        break
                    if next_item != '.':
                        # se è spazio, non fa parte di nessun elemento attiguo
                        next_elements_items.append(ItemPosition(item=next_item, pos_y=next_position[0], pos_x=next_position[1]))
                items_chain_to_move.append(element)
                
                if robot_moves == False:
                    break
            if robot_moves == False:
                # we know robot can't move, hence stop the investigation
                break

            if len(next_elements_items) == 0:
                # we do not get adjacent elements, hence space, hence we can move and stop the investigation
                robot_moves = True
                break

            # parse elements from next_elements_items into set of elements
            elements_investigate_if_can_move: Set[Element] = set()
            for ipos in next_elements_items:
                if ipos.item == '@':
                    elements_investigate_if_can_move.add(Element(item_positions=(ipos,)))
                elif ipos.item == '[':
                    box_element = Element(item_positions=(ipos, ItemPosition(item=']', pos_y=ipos.pos_y, pos_x=ipos.pos_x + 1)))
                    elements_investigate_if_can_move.add(box_element)
                elif ipos.item == ']':
                    box_element = Element(item_positions=(ipos, ItemPosition(item='[', pos_y=ipos.pos_y, pos_x=ipos.pos_x - 1)))
                    elements_investigate_if_can_move.add(box_element)
                else:
                    raise Exception(f'unexpeceted item position {ipos}')
  
        if robot_moves:
            next_items_to_move_positions: Set[Tuple[int, int]] = set()
            current_items_to_move_positions: Set[Tuple[int, int]] = set()
            for element in items_chain_to_move:
                current_items_to_move_positions.update([(item_pos.pos_y, item_pos.pos_x) for item_pos in element.item_positions])
            for element in items_chain_to_move:
                # need to move the element
                for item_pos in element.item_positions:
                    next_position = (item_pos.pos_y + strafe_down, item_pos.pos_x + strafe_right)
                    next_items_to_move_positions.add(next_position)
                    movement_extended_map[next_position[0]][next_position[1]] = item_pos.item
                    if item_pos.item == '@':
                        current_robot_pos = next_position
            spaces_positions = current_items_to_move_positions.difference(next_items_to_move_positions)
            for position in spaces_positions:
                movement_extended_map[position[0]][position[1]] = '.'

        # print('')
        # print(f'Move {movement}')
        # represents_map(map=movement_extended_map)

    # print('')
    # print('Final stage')
    # represents_map(map=movement_extended_map)
    
    sum_coord_extended = 0
    for i, line in enumerate(movement_extended_map):
        for j, item in enumerate(line):
            if item == '[':
                sum_coord_extended += 100 * i + j
    print(sum_coord_extended)  # solution b
                

            