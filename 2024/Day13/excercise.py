from dataclasses import dataclass
from typing import List

# Button A: X+a, Y+b
# Button B: X+c, Y+d
# Prize: X=e, Y=f

# n_push_a * a + n_push_b * c = e
# n_push_a * b + n_push_b * d = f
@dataclass(frozen=True)
class ButtonConfiguration:

    a: int
    b: int
    c: int
    d: int
    e: int
    f: int

    @property
    def n_push_b(self) -> float:
        "soluzione sistena due equazioni due incognite sopra."
        return ((self.a * self.f) - (self.e * self.b)) / ((self.a * self.d) - (self.c * self.b))
    
    @property
    def n_push_a(self) -> float:
        return ((self.e - (self.n_push_b * self.c)) / self.a)

with open("puzzle.txt", "r") as fr:
    button_configs: List[ButtonConfiguration] = []
    a = b = c = d = e = f = None
    for line in fr:
        line = line.rstrip()
        if line == '':
            button_config = ButtonConfiguration(a=a, b=b, c=c, d=d, e=e, f=f)
            button_configs.append(button_config)
            a = b = c = d = e = f = None
            continue
        if 'Button A' in line:
            search_str = line.removeprefix('Button A:').replace(' ', '')
            search_str = search_str.replace('X', '').replace('Y', '').replace('+', '')
            search_li = search_str.split(',')
            a = int(search_li[0])
            b = int(search_li[1])
            continue
        if 'Button B' in line:
            search_str = line.removeprefix('Button B:').replace(' ', '')
            search_str = search_str.replace('X', '').replace('Y', '').replace('+', '')
            search_li = search_str.split(',')
            c = int(search_li[0])
            d = int(search_li[1])
            continue
        if 'Prize' in line:
            search_str = line.removeprefix('Prize:').replace(' ', '')
            search_str = search_str.replace('X', '').replace('Y', '').replace('=', '')
            search_li = search_str.split(',')
            e = int(search_li[0])
            f = int(search_li[1])
            continue
        print(f'line unknown: {line}')
    if (a, b, c, d, e, f) != (None, None, None, None, None, None):
        button_config = ButtonConfiguration(a=a, b=b, c=c, d=d, e=e, f=f)
        button_configs.append(button_config)
    
    token_cost = 0
    for bc in button_configs:
        # print(bc)
        if bc.n_push_a != int(bc.n_push_a) or bc.n_push_b != int(bc.n_push_b):
            # print('no solution!')
            continue
        # print(f'n push A {int(bc.n_push_a)}, n push B {int(bc.n_push_b)}')
        token_cost += 3 * int(bc.n_push_a)
        token_cost += 1 * int(bc.n_push_b)
    
    print(token_cost)  # solution a

    button_configs_amplied = [ButtonConfiguration(a=bc.a, b=bc.b, c=bc.c, d=bc.d, e=bc.e + 10000000000000, f=bc.f + 10000000000000) for bc in button_configs]

    token_cost_amplied = 0
    for bc in button_configs_amplied:
        # print(bc)
        if bc.n_push_a != int(bc.n_push_a) or bc.n_push_b != int(bc.n_push_b):
            # print('no solution!')
            continue
        # print(f'n push A {int(bc.n_push_a)}, n push B {int(bc.n_push_b)}')
        token_cost_amplied += 3 * int(bc.n_push_a)
        token_cost_amplied += 1 * int(bc.n_push_b)
    
    print(token_cost_amplied)  # solution b