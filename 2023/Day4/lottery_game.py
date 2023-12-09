from typing import Set, List, Dict
from dataclasses import dataclass, field

@dataclass
class GameCard:
    
    card_id: int
    winning_numbers: Set[int]
    played_numbers: Set[int]

    @property
    def winning_played_numbers(self) -> Set[int]:
        return self.played_numbers.intersection(self.winning_numbers)

    @property
    def win_worth_points(self) -> int:
        if not any(self.winning_played_numbers):
            return 0
        return pow(2, len(self.winning_played_numbers) - 1)

    def _parse_card_number(card_id_description: str) -> int:
        """Card   1 -> 1"""
        return int(card_id_description.split()[1])

    @staticmethod
    def from_game_description(game_description: str) -> 'GameCard':
        card_id_description = game_description.split(':')[0]
        card_id = GameCard._parse_card_number(card_id_description)
        number_descriptions = game_description.split(':')[1].split('|')
        winning_numbers = {int(nr) for nr in number_descriptions[0].split()}
        played_numbers = {int(nr) for nr in number_descriptions[1].split()}
        return GameCard(card_id=card_id, winning_numbers=winning_numbers, played_numbers=played_numbers)
    
    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, GameCard):
            return self.card_id > obj.card_id
        raise NotImplemented

@dataclass
class GameCards:
    
    original_cards: List[GameCard]
    copy_cards: List[GameCard] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        self.order_original_cards()

    def order_original_cards(self) -> None:
        self.original_cards.sort()

    def get_card_copies(self, origin_card_id: int) -> List[GameCard]:
        cards_copies = []
        original_card = self.original_cards[origin_card_id - 1]
        for i in range(origin_card_id, origin_card_id + len(original_card.winning_played_numbers)):
            cards_copies.append(self.original_cards[i])
        return cards_copies
    
    def get_card_copies_ancient_to_childs(self, origin_card_id: int) -> List[GameCard]:
        card_copies = self.get_card_copies(origin_card_id=origin_card_id)
        cards_to_process = self.get_card_copies(origin_card_id=origin_card_id)
        while any(cards_to_process):
            new_cards_to_process = []
            for card in cards_to_process:
                card_copies.extend(self.get_card_copies(card.card_id))
                new_cards_to_process.extend(self.get_card_copies(card.card_id))
            cards_to_process = new_cards_to_process.copy()
        return card_copies
    
    def add_copy_cards(self, copy_cards: List[GameCard]) -> None:
        self.copy_cards.extend(copy_cards)

    def generate_copy_cards(self) -> None:
        self.copy_cards = []
        for card in self.original_cards:
            self.add_copy_cards(self.get_card_copies_ancient_to_childs(origin_card_id=card.card_id))

    @property
    def summary_cards(self) -> Dict[int, int]:
        return {f'Card {card.card_id} number instances': len([cc for cc in self.copy_cards if card.card_id == cc.card_id]) + 1 for card in self.original_cards}

if __name__ == '__main__':
    # id = GameCard._parse_card_number('Card   1')
    # print(id)
    # game_description = 'Card   1: 26 36 90  2 75 32  3 21 59 18 | 47 97 83 82 43  7 61 73 57  2 67 31 69 11 44 38 23 52 10 21 45 36 86 49 14'
    # gd = GameCard.from_game_description(game_description)
    # print(gd)
    # print(gd.winning_played_numbers)
    # print(gd.win_worth_points)
    test_game = [
        'Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53',
        'Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19',
        'Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1',
        'Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83',
        'Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36',
        'Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11',
    ]
    test_game_cards = [GameCard.from_game_description(line) for line in test_game]
    print(f'total test worth points is {sum([card.win_worth_points for card in test_game_cards])}')
    test_game_cards = GameCards(original_cards=test_game_cards)
    # print(game_cards.get_card_copies(origin_card_id=1))
    # print(game_cards.get_card_copies_ancient_to_childs(origin_card_id=1))
    test_game_cards.generate_copy_cards()
    # print(f'total card copyed is {len(game_cards.copy_cards)}')
    print(test_game_cards.summary_cards)
    with open("card_games.txt", "r") as fr:
        game_cards = [GameCard.from_game_description(line) for line in fr]
    print(f'total worth points is {sum([card.win_worth_points for card in game_cards])}')
    game_cards = GameCards(original_cards=game_cards)
    game_cards.generate_copy_cards()
    print(f'total number of cards after the generation copy is {len(game_cards.original_cards) + len(game_cards.copy_cards)}')
