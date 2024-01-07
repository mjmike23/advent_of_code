from typing import Tuple, List, Dict, Iterable
from dataclasses import dataclass, field

BROADCASTER = 'broadcaster'
FLIP_FLOP = '%'
CONJUNCTION = '&'

STATE_ON = 'on'
STATE_OFF = 'off'


@dataclass(frozen=True)
class Pulse:

    type: str

PULSE_LOW = Pulse('LOW')
PULSE_HIGH = Pulse('HIGH')


@dataclass(frozen=True)
class PulseSrcTgt:

    id_module_src: str
    pulse: Pulse
    id_module_tgt: str

    def single_string_repr(self) -> str:
        return f'{self.id_module_src} - {self.pulse.type} -> {self.id_module_tgt}'

@dataclass
class Module:

    id: str
    out_ids_connected: Tuple[str]

    @property
    def type(self) -> str:
        raise NotImplemented
    
    def sent_pulses(self, pulse: Pulse) -> List[PulseSrcTgt]:
        return [PulseSrcTgt(id_module_src=self.id, pulse=pulse, id_module_tgt=out_id) for out_id in self.out_ids_connected]

    def _receive_pulse(self, pulse_source: PulseSrcTgt) -> None:
        raise NotImplemented
    
    def get_sented_pulses(self, pulse_source: PulseSrcTgt) -> List[PulseSrcTgt]:
        raise NotImplemented
    
    def reset_status(self) -> None:
        pass

@dataclass
class ModuleFlipFlop(Module):

    id: str
    out_ids_connected: Tuple[str]
    state: str = STATE_OFF

    @property
    def type(self) -> str:
        return CONJUNCTION
    
    def _receive_pulse(self, pulse_source: PulseSrcTgt) -> None:
        if pulse_source.pulse == PULSE_LOW:
            self.state = STATE_OFF if self.state == STATE_ON else STATE_ON

    def get_sented_pulses(self, pulse_source: PulseSrcTgt) -> List[PulseSrcTgt]:
        self._receive_pulse(pulse_source=pulse_source)
        if pulse_source.pulse == PULSE_LOW:
            if self.state == STATE_ON:
                return self.sent_pulses(pulse=PULSE_HIGH)
            return self.sent_pulses(pulse=PULSE_LOW)
        return []
    
    def reset_status(self) -> None:
        self.state = STATE_OFF

@dataclass
class ModuleConjunction(Module):

    id: str
    out_ids_connected: Tuple[str]
    in_last_pulse_received: Dict[str, Pulse] = field(default_factory=dict)

    @property
    def type(self) -> str:
        return FLIP_FLOP

    def add_in_id_modules(self, in_id_modules: List[str]) -> None:
        for in_id_module in in_id_modules:
            self.in_last_pulse_received[in_id_module] = PULSE_LOW

    @property
    def are_all_high_pulses(self) -> bool:
        return not any([pulse for pulse in self.in_last_pulse_received.values() if pulse == PULSE_LOW])
    
    def _receive_pulse(self, pulse_source: PulseSrcTgt) -> None:
        self.in_last_pulse_received[pulse_source.id_module_src] = pulse_source.pulse

    def get_sented_pulses(self, pulse_source: PulseSrcTgt) -> List[PulseSrcTgt]:
        self._receive_pulse(pulse_source=pulse_source)
        if self.are_all_high_pulses:
            return self.sent_pulses(pulse=PULSE_LOW)
        return self.sent_pulses(pulse=PULSE_HIGH)
    
    def reset_status(self) -> None:
        for id in self.in_last_pulse_received.keys():
            self.in_last_pulse_received[id] = PULSE_LOW


@dataclass
class ModuleBroadcaster(Module):

    id: str
    out_ids_connected: Tuple[str]

    @property
    def type(self) -> str:
        return BROADCASTER

    def get_sented_pulses(self, pulse_source: PulseSrcTgt) -> List[PulseSrcTgt]:
        return self.sent_pulses(pulse=pulse_source.pulse)


def get_module_from_description(description: str) -> Module:
    description = description.rstrip().replace(' ', '')
    mod_info = description.split('->')
    id_info = mod_info[0]
    out_ids_connected = tuple(mod_info[1].split(','))
    if id_info[0] == FLIP_FLOP:
        id = id_info.removeprefix(FLIP_FLOP)
        return ModuleFlipFlop(id=id, out_ids_connected=out_ids_connected)
    if id_info[0] == CONJUNCTION:
        id = id_info.removeprefix(CONJUNCTION)
        return ModuleConjunction(id=id, out_ids_connected=out_ids_connected)
    if id_info[:11] == BROADCASTER:
        id = id_info.removeprefix(BROADCASTER)
        return ModuleBroadcaster(id=BROADCASTER, out_ids_connected=out_ids_connected)
    raise Exception(f'Unreachable, module descriprion unable to parse: {description}')


@dataclass
class PulseMachine:

    modules: List[Module]
    n_pulses_high: int = 0
    n_pulses_low: int = 0
    low_pulse_reached_rx_module: bool = False

    @staticmethod
    def from_mod_descriptions(mod_descriptions: List[str]) -> 'PulseMachine':
        modules = [get_module_from_description(description=mod_description) for mod_description in mod_descriptions]
        pulse_machine = PulseMachine(modules=modules)
        for module in pulse_machine.modules:
            if isinstance(module, ModuleConjunction):
                module.add_in_id_modules(in_id_modules=[mod.id for mod in pulse_machine.modules if module.id in mod.out_ids_connected])
        return pulse_machine
    
    @property
    def broadcaster_module(self) -> ModuleBroadcaster:
        return [module for module in self.modules if isinstance(module, ModuleBroadcaster)][0]
    
    def get_module_by_id(self, id: str) -> Module:
        return [module for module in self.modules if module.id == id][0]

    def increment_pulse_counter(self, pulses_src_tgt: Iterable[PulseSrcTgt]) -> None:
        for pulse_src_tgt in pulses_src_tgt:
            if pulse_src_tgt.pulse == PULSE_HIGH:
                self.n_pulses_high += 1
            elif pulse_src_tgt.pulse == PULSE_LOW:
                self.n_pulses_low += 1
            else:
                raise Exception(f'unacceptable pulse {pulse_src_tgt}')

    def update_low_pulse_reached_rx_module(self, pulses_src_tgt: Iterable[PulseSrcTgt]) -> None:
        for pulse_src_tgt in pulses_src_tgt:
            if pulse_src_tgt.id_module_tgt == 'rx' and pulse_src_tgt.pulse == PULSE_LOW:
                self.low_pulse_reached_rx_module = True
                break

    def push_button(self, start_pulse: Pulse, verbose: bool =  False) -> None:
        self.n_pulses_high += 1 if start_pulse == PULSE_HIGH else 0
        self.n_pulses_low += 1 if start_pulse == PULSE_LOW else 0
        current_pulses = self.broadcaster_module.get_sented_pulses(pulse_source=PulseSrcTgt(id_module_src='', pulse=start_pulse, id_module_tgt=BROADCASTER))
        while len(current_pulses) != 0:
            if verbose:
                print([pulse.single_string_repr() for pulse in current_pulses])
            self.increment_pulse_counter(pulses_src_tgt=current_pulses)
            self.update_low_pulse_reached_rx_module(pulses_src_tgt=current_pulses)
            new_pulses: List[PulseSrcTgt] = []
            for pulse in current_pulses:
                try:
                    module = self.get_module_by_id(id=pulse.id_module_tgt)
                except IndexError:
                    if verbose:
                        print(f'module id {pulse.id_module_tgt} is not part of the machine, hence end pulse path here')
                    continue
                new_module_pulses = module.get_sented_pulses(pulse_source=pulse)
                new_pulses.extend(new_module_pulses)
            current_pulses = new_pulses.copy()

    def push_button_n_times(self, start_pulse: Pulse, n_push: int, verbose: bool =  False) -> None:
        for i in range(n_push):
            self.push_button(start_pulse=start_pulse, verbose=verbose)
            if verbose:
                print(f'after iteration {i}, n_pulse high is {self.n_pulses_high}, n_pulse low is {self.n_pulses_low}')

    def reset(self) -> None:
        self.n_pulses_high = 0
        self.n_pulses_low = 0
        self.low_pulse_reached_rx_module = False
        for module in self.modules:
            module.reset_status()

if __name__  == '__main__':
    print(get_module_from_description(description='broadcaster -> a, b, c'))
    print(get_module_from_description(description='%a -> b'))
    print(get_module_from_description(description='&inv -> b'))
    test_pm1_descr = [
        'broadcaster -> a, b, c',
        '%a -> b',
        '%b -> c',
        '%c -> inv',
        '&inv -> a',
    ]
    test_pm1 = PulseMachine.from_mod_descriptions(mod_descriptions=test_pm1_descr)
    # print(test_pm1)
    test_pm1.push_button(start_pulse=PULSE_LOW, verbose=True)
    print(f'test pm1 n pulses low are {test_pm1.n_pulses_low}, n pulses high are {test_pm1.n_pulses_high}')
    test_pm2_descr = [
        'broadcaster -> a',
        '%a -> inv, con',
        '&inv -> b',
        '%b -> con',
        '&con -> output',
    ]
    test_pm2 = PulseMachine.from_mod_descriptions(mod_descriptions=test_pm2_descr)
    # print(test_pm2)
    test_pm2.push_button(start_pulse=PULSE_LOW, verbose=True)
    test_pm2.reset()
    test_pm2.push_button_n_times(start_pulse=PULSE_LOW, n_push=1000)
    print(f'test pm2 after 1000 push n pulses low are {test_pm2.n_pulses_low}, n pulses high are {test_pm2.n_pulses_high}, hence product result is {test_pm2.n_pulses_low * test_pm2.n_pulses_high}')

    with open('.\modules.txt', "r") as fr:
        pm = PulseMachine.from_mod_descriptions(mod_descriptions=[line for line in fr])
    pm.push_button_n_times(start_pulse=PULSE_LOW, n_push=1000)
    print(f'Pm after 1000 push n pulses low are {pm.n_pulses_low}, n pulses high are {pm.n_pulses_high}, hence product result is {pm.n_pulses_low * pm.n_pulses_high}')
    # slow, doesn't reach end
    pm.reset()
    button_press_count = 0
    while not pm.low_pulse_reached_rx_module:
        button_press_count += 1
        pm.push_button(start_pulse=PULSE_LOW)
    print(f'At least a low pulse reached rx module after {button_press_count} button pushes')