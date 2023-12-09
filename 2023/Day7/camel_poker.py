from typing import List
from dataclasses import dataclass
from collections import Counter

# parsing game, J can be joker, that is %
CARD_VALUE_ORDER = 'AKQJT98765432%'

@dataclass(frozen=True)
class Card:

    card_id: str

    @property
    def card_value(self) -> int:
        return len(CARD_VALUE_ORDER) - CARD_VALUE_ORDER.find(self.card_id)

    @property
    def is_joker(self) -> bool:
        return self.card_id == '%'

    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, Card):
            return self.card_value > obj.card_value
        raise NotImplemented

class HandValue:

    VALUE_TO_LIT = {1: 'high_card', 2: 'pair', 3: 'two_pair', 4: 'three_of_a_kind', 5: 'full_house', 6: 'four_of_a_kind', 7: 'five_of_a_kind'}

    high_card: int = 1
    pair: int = 2
    two_pair: int = 3
    three_of_a_kind: int = 4
    full_house: int = 5
    four_of_a_kind: int = 6
    five_of_a_kind: int = 7


@dataclass
class CardHand:

    cards: List[Card]
    bid: int

    @staticmethod
    def from_line_description(description: str, joker_game: bool = False) -> 'CardHand':
        cards_bid = [el for el in description.rstrip().split(' ')]
        cards = [Card('%' if joker_game and c == 'J' else c) for c in cards_bid[0]]
        bid = int(cards_bid[1])
        return CardHand(cards=cards, bid=bid)

    def to_repr(self) -> str:
        return f"{''.join([c.card_id for c in self.cards])} {self.bid}"

    @property
    def cards_joker_excluded(self) -> List[Card]:
        return [card for card in self.cards if not card.is_joker]

    @property
    def hand_counter_of_each_kind_joker_excluded(self) -> Counter:
        return Counter(self.cards_joker_excluded)

    @property
    def number_of_jokers(self) -> int:
        return len([card for card in self.cards if card.is_joker])

    @property
    def has_joker(self) -> bool:
        return self.number_of_jokers > 0

    @property
    def has_jokers_only(self) -> Counter:
        return self.number_of_jokers == len(self.cards)

    def get_best_replace_jolly_card(self) -> Card:
        if self.has_jokers_only:
            return Card(card_id=CARD_VALUE_ORDER[0])
        max_counter = max(self.hand_counter_of_each_kind_joker_excluded.values())
        return [card for card, n_times in self.hand_counter_of_each_kind_joker_excluded.items() if n_times == max_counter][0]

    def get_card_n_time_repeated(self, n_instances: int) -> Card:
        return [card for card, n_times in self.hand_counter_of_each_kind_joker_excluded.items() if n_times == n_instances][0]

    def get_hand_with_replaced_card(self, card_replace: Card) -> 'CardHand':
        return CardHand(cards=[card_replace if c.is_joker else c for c in self.cards], bid=self.bid)

    def get_best_card_hand_replacing_jokers(self) -> 'CardHand':
        return self.get_hand_with_replaced_card(card_replace=self.get_best_replace_jolly_card())

    def get_hand_combo_value(self, replace_jokers: bool = True) -> int:
        hand_to_evaluate_for_combo = self.get_best_card_hand_replacing_jokers() if replace_jokers else self
        if self.has_jokers_only:
            return HandValue.five_of_a_kind
        max_counter = max(hand_to_evaluate_for_combo.hand_counter_of_each_kind_joker_excluded.values())
        if max_counter == 5:
            return HandValue.five_of_a_kind
        if max_counter == 4:
            return HandValue.four_of_a_kind
        if max_counter == 3:
            if any([v for v in hand_to_evaluate_for_combo.hand_counter_of_each_kind_joker_excluded.values() if v != max_counter]):
                second_max_counter = max([v for v in hand_to_evaluate_for_combo.hand_counter_of_each_kind_joker_excluded.values() if v != max_counter])
                if second_max_counter == 2:
                    return HandValue.full_house
            return HandValue.three_of_a_kind
        if max_counter == 2:
            if len([v for v in hand_to_evaluate_for_combo.hand_counter_of_each_kind_joker_excluded.values() if v == max_counter]) == 2:
                return HandValue.two_pair
            return HandValue.pair
        return HandValue.high_card

    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, CardHand):
            if self.get_hand_combo_value() != obj.get_hand_combo_value():
                return self.get_hand_combo_value() > obj.get_hand_combo_value()
            for i, card in enumerate(self.cards):
                if card != obj.cards[i]:
                    return card > obj.cards[i]
            return Exception('the two hands are same!')
        raise NotImplemented

@dataclass
class FullGame:

    hands: List[CardHand]
    _is_sorted: bool =  False
    
    def sort_hands(self) -> None:
        if self._is_sorted:
            print('Already sorted, no need to sort again')
            return
        self.hands.sort()
        self._is_sorted = True

    def get_total_winnings(self) -> int:
        self.sort_hands()
        return sum([(rk + 1) * card_hand.bid for rk, card_hand in enumerate(self.hands)])

if __name__ == '__main__':
    # c3 = Card('3')
    # c3b = Card('3')
    # c5 = Card('5')
    # ck = Card('K')
    # cq = Card('Q')
    # assert c5 > c3 and c3 < c5
    # assert ck > cq and cq < ck
    # assert ck > c5 and c5 < ck
    # assert c3 == c3b
    # hand_description = 'T55J5 684'
    # h2_desc = 'QQQJA 483'
    # cha = CardHand.from_line_description(description=hand_description)
    # cha2 = CardHand.from_line_description(description=h2_desc)
    # cha2_joker_game = CardHand.from_line_description(description=h2_desc, joker_game=True)
    # print(cha)
    # print(cha2)
    # print(cha2_joker_game)
    # print(cha2_joker_game.has_joker)
    # print(cha2_joker_game.hand_counter_of_each_kind_joker_excluded)
    # print(cha2_joker_game.get_card_n_time_repeated(n_instances=3))
    # print(cha2_joker_game.get_hand_with_replaced_card(card_replace=Card('K')))
    # print(cha2_joker_game.get_best_card_hand_replacing_jokers())
    # print(cha.hand_counter_of_each_kind_joker_excluded)
    # print(cha.get_hand_combo_value())
    # print(HandValue.VALUE_TO_LIT[cha.get_hand_combo_value()])
    # print(HandValue.VALUE_TO_LIT[cha2.get_hand_combo_value()])
    # print(HandValue.VALUE_TO_LIT[cha2_joker_game.get_hand_combo_value()])
    # print(cha > cha2)

    # edge_casej_desc = 'J2QK3 483'
    # edge_casej = CardHand.from_line_description(description=edge_casej_desc, joker_game=True)
    # print(edge_casej.get_best_card_hand_replacing_jokers())
    # print(HandValue.VALUE_TO_LIT[edge_casej.get_hand_combo_value()])

    # test_hands = [
    #     '32T3K 765',
    #     'T55J5 684',
    #     'KK677 28',
    #     'KTJJT 220',
    #     'QQQJA 483',
    # ]
    # test_game = FullGame(hands=[CardHand.from_line_description(hand_description) for hand_description in test_hands])
    # test_game.sort_hands()
    # print(test_game)
    # print(f'test total winnigs are {test_game.get_total_winnings()}')
    # test_game_jokers = FullGame(hands=[CardHand.from_line_description(hand_description, joker_game=True) for hand_description in test_hands])
    # print(f'test total winnigs considering joker rule are {test_game_jokers.get_total_winnings()}')

    with open(".\hands.txt", "r") as fr:
        game = FullGame(hands=[CardHand.from_line_description(hand_description) for hand_description in fr])
    print(f'total winnigs are {game.get_total_winnings()}')

    with open(".\hands.txt", "r") as fr:
        game_joker = FullGame(hands=[CardHand.from_line_description(hand_description, joker_game=True) for hand_description in fr])
    print(f'total winnigs considering joker rule are {game_joker.get_total_winnings()}')
