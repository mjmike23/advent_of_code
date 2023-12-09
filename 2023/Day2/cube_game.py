from typing import List
from dataclasses import dataclass

CUBE_COLORS = {'blue', 'green', 'red'}

@dataclass
class GameShow:

    n_blue: int
    n_green: int
    n_red: int

    @staticmethod
    def from_string_description(description: str) -> 'GameShow':
        cube_extractions = description.strip().split(',')
        try:
            dict_extraction = {extraction.strip().split(' ')[1]: extraction.strip().split(' ')[0] for extraction in cube_extractions}
        except:
            raise Exception(f'something strange happened parsing cube_extractions. Here it is {cube_extractions}')
        n_blue = int(dict_extraction.get('blue')) if dict_extraction.get('blue') is not None else 0
        n_green = int(dict_extraction.get('green')) if dict_extraction.get('green') is not None else 0
        n_red = int(dict_extraction.get('red')) if dict_extraction.get('red') is not None else 0
        return GameShow(n_blue=n_blue, n_green=n_green, n_red=n_red)

@dataclass
class GameReveal:
    
    game_id: int
    game_reveals: List[GameShow]

    @staticmethod
    def from_string_description(description: str) -> 'GameReveal':
        description.split(':')[0]
        game_id = int(description.split(':')[0].split(' ')[1])
        game_extraction_descriptions = [GameShow.from_string_description(extraction_description) for extraction_description in description.split(':')[1].split(';') if extraction_description!='']
        return GameReveal(game_id=game_id, game_reveals=game_extraction_descriptions)

    @property
    def n_cubes_blue_needed(self) -> int:
        return max([game_reveal.n_blue for game_reveal in self.game_reveals])

    @property
    def n_cubes_green_needed(self) -> int:
        return max([game_reveal.n_green for game_reveal in self.game_reveals])

    @property
    def n_cubes_red_needed(self) -> int:
        return max([game_reveal.n_red for game_reveal in self.game_reveals])
    
    @property
    def power_game(self) -> int:
        return self.n_cubes_blue_needed * self.n_cubes_green_needed * self.n_cubes_red_needed    

    def is_possible_cube_composition(self, n_blue_allowed, n_green_allowed, n_red_allowed) ->bool:
        return self.n_cubes_blue_needed <= n_blue_allowed and self.n_cubes_green_needed <= n_green_allowed and self.n_cubes_red_needed <= n_red_allowed
    
    def is_possible(self, n_cubes_allowed: int) -> bool:
        return self.n_cubes_blue_needed + self.n_cubes_green_needed + self.n_cubes_red_needed <= n_cubes_allowed



if __name__ == '__main__':
    test_game_show_parse = ' 3 green, 2 red'
    gs = GameShow.from_string_description(test_game_show_parse)
    print(gs)
    test_game_show = 'Game 6: 1 green, 7 red; 1 blue, 3 green, 1 red; 1 blue, 2 red, 2 green; 1 blue, 1 green, 2 red; 3 red; 8 red, 1 green, 1 blue'
    gr = GameReveal.from_string_description(test_game_show)
    print(gr)
    print(gr.n_cubes_blue_needed)
    print(gr.n_cubes_green_needed)
    print(gr.n_cubes_red_needed)
    print(gr.is_possible(n_cubes_allowed=11))
    print(gr.is_possible_cube_composition(n_blue_allowed=2, n_green_allowed=3, n_red_allowed=7))
    test_games = [
        'Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green',
        'Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue',
        'Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red'
        'Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red',
        'Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green',
    ]
    test_games_parsed = [GameReveal.from_string_description(description=desc) for desc in test_games]
    test_possible_12 = [game for game in test_games_parsed if game.is_possible(n_cubes_allowed=12)]
    print(f'test result is {sum([gp.game_id for gp in test_possible_12])}')
    
    with open("puzzle_cube_games.txt", "r") as fr:
        games = [GameReveal.from_string_description(description=line) for line in fr] # 55002
        
    # possible_12 = [game for game in games if game.is_possible(n_cubes_allowed=12)]
    # possible_13 = [game for game in games if game.is_possible(n_cubes_allowed=13)]
    # possible_14 = [game for game in games if game.is_possible(n_cubes_allowed=13)]
    
    # sum_possible_12 = sum([gp.game_id for gp in possible_12])
    # sum_possible_13 = sum([gp.game_id for gp in possible_13])
    # sum_possible_14 = sum([gp.game_id for gp in possible_14])
    possible_12_13_14 = [game for game in games if game.is_possible_cube_composition(n_blue_allowed=14, n_green_allowed=13, n_red_allowed=12)]
    print(f'composition result 12 13 14 is {sum([gp.game_id for gp in possible_12_13_14])}')

    game_powers = [game.power_game for game in games]
    print(f'full power games is {sum(game_powers)}')
