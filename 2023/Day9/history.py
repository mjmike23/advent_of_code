from dataclasses import dataclass
from typing import List, Iterable

@dataclass
class History:

    sequence: List[int]

    @staticmethod
    def from_description(description: str) -> 'History':
        return History(sequence=[int(el) for el in description.rstrip().split(' ')])

    def next_sequence(self) -> 'History':
        return History(sequence=[self.sequence[i + 1] - el  for i, el in enumerate(self.sequence[:-1])])

    @property
    def is_final_sequence(self) -> bool:
        return not any([el for el in self.sequence if el != 0])
    
    def get_full_history_sequence_iterator(self) ->Iterable['History']:
        current_sequence = self
        yield current_sequence
        while not current_sequence.is_final_sequence:
            current_sequence = current_sequence.next_sequence()
            yield current_sequence
            
    def get_list_last_elements_history(self) -> List[int]:
        return [his_sequence.sequence[-1] for his_sequence in self.get_full_history_sequence_iterator()]
    
    def get_list_first_elements_history(self) -> List[int]:
        return [his_sequence.sequence[0] for his_sequence in self.get_full_history_sequence_iterator()]

    def get_history_factor(self) -> int:
        factor = 0
        for element in self.get_list_last_elements_history()[::-1]:
            factor += element
        return factor
    
    def get_history_back_factor(self) -> int:
        factor = 0
        for element in self.get_list_first_elements_history()[::-1]:
            factor = element - factor
        return factor

if __name__ == '__main__':
    # h1_description = '1 3 6 10 15 21'
    # h1 = History(sequence=[1, 3, 6, 10, 15, 21])
    # h1_from_parsing = History.from_description(h1_description)
    # assert h1 == h1_from_parsing
    # print(h1.next_sequence())
    # print(h1.is_final_sequence)
    # for seq in h1.get_full_history_sequence_iterator():
    #     print(seq)
    # print(h1.get_list_last_elements_history())
    # print(h1.get_history_factor())
    # h2 = History(sequence=[10, 13, 16, 21, 30, 45])
    # print(h2.get_history_factor())
    # print(h2.get_list_first_elements_history())
    # print(h2.get_history_back_factor())
    # test_ecol_hist = [
    #     '0 3 6 9 12 15',
    #     '1 3 6 10 15 21',
    #     '10 13 16 21 30 45',
    # ]
    # test_histories = [History.from_description(history_descriptions)for history_descriptions in test_ecol_hist]
    # print(f'Test factor from histories is {sum([h.get_history_factor() for h in test_histories])}')
    # print(f'Test factor backward from histories is {sum([h.get_history_back_factor() for h in test_histories])}')
    
    with open(".\ecological_history.txt", "r") as fr:
        histories = [History.from_description(history_descriptions)for history_descriptions in fr]
    print(f'Factor from histories is {sum([h.get_history_factor() for h in histories])}')
    print(f'Factor from backward histories is {sum([h.get_history_back_factor() for h in histories])}')