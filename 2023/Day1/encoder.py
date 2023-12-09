from dataclasses import dataclass

@dataclass
class DigitFounded:
    
    value: int
    position: int
    
    def __gt__(self, obj: object) -> bool:
        if isinstance(obj, DigitFounded):
            return self.position > obj.position
        raise NotImplemented


WORDS_TO_NUMBERS = {
    # 'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
}

def search_first_digit(input_code: str, reverse: bool = False) -> DigitFounded:
    code_search = input_code if not reverse else input_code[::-1]
    for i, l in enumerate(code_search):
        if l in '0123456789':
            return DigitFounded(value=int(l), position=i if not reverse else len(input_code) - i -1)
    return DigitFounded(value=-1, position=-1)


def get_first_founded_digit(reverse: bool, *digits: DigitFounded) -> DigitFounded:
    valid_digits = [digit for digit in digits if digit.position != -1]
    valid_digits.sort(reverse=reverse)
    return valid_digits[0]


def search_first_letter_digit(input_code: str, reverse: bool = False) -> DigitFounded:
    candidates =  []
    for word_num in WORDS_TO_NUMBERS.keys():
        index_founded = input_code.find(word_num) if not reverse else input_code.rfind(word_num)
        if index_founded!= -1:
            candidates.append(DigitFounded(value=WORDS_TO_NUMBERS[word_num], position=index_founded))
    return get_first_founded_digit(reverse, *candidates) if any(candidates) else DigitFounded(value=-1, position=-1)


def encoder(input_code: str) -> int:
    return int(f'{search_first_digit(input_code, reverse=False).value}{search_first_digit(input_code, reverse=True).value}')


def advanced_encoder(input_code: str) -> int:
    first_digit = get_first_founded_digit(False, search_first_digit(input_code=input_code), search_first_letter_digit(input_code=input_code)).value
    second_digit = get_first_founded_digit(True, search_first_digit(input_code=input_code, reverse=True), search_first_letter_digit(input_code=input_code, reverse=True)).value
    return int(f'{first_digit}{second_digit}')


if __name__ == '__main__':
    # test_code = 'dasks3daslfkj2hnhs'
    # test_code_1 = 'dasks1daslfkjdhnhs'
    # print(encoder(test_code))
    # print(encoder(test_code_1))
    # with open("encoded_coordinates.txt", "r") as fr:
    #     decoded_rows = [encoder(line) for line in fr] # 55002
    # print(f'result is ({sum(decoded_rows)})')
    # d1 = DigitFounded(value=3, position=2)
    # d2 = DigitFounded(value=8, position=5)
    # d3 = DigitFounded(value=7, position=-1)
    # print(get_first_founded_digit(False, d1, d2, d3))
    # print(get_first_founded_digit(True, d1, d2, d3))
    # advanced_test = 'eighteight9dnvcqznjvfpreight'
    # advanced_test = 'ctrv3hmvjphrffktwothree'
    # print(search_first_letter_digit(input_code=advanced_test))
    # print(search_first_letter_digit(input_code=advanced_test, reverse=True))
    # print(search_first_digit(input_code=advanced_test, reverse=True))
    # print(advanced_encoder(advanced_test))
    with open("encoded_coordinates.txt", "r") as fr:
        decoded_rows_adv = [advanced_encoder(line) for line in fr] # 55060
        # for line in fr:
        #     print(f'adv encoding of {line} is {advanced_encoder(line)}') 
    print(f'result is ({sum(decoded_rows_adv)})')
    # for i in decoded_rows_adv:
    #     print(i)
