from typing import List
from dataclasses import dataclass

VELOCITY_GAIN_MM_ON_MS = 1

@dataclass
class Race:

    time_ms: int
    distance_record_mm: int
    
    def get_from_lines(time_line: str, distance_line: str) -> List['Race']:
        times = [int(t) for t in time_line.rstrip().removeprefix('Time:').split()]
        distance_line = distance_line.rstrip()
        distances = [int(d) for d in distance_line.rstrip().removeprefix('Distance:').split()]
        return [Race(*td) for td in zip(times, distances)]
    
    def get_single_long_race(time_line: str, distance_line: str) -> 'Race':
        time_long_race = int(time_line.rstrip().removeprefix('Time:').replace(' ', ''))
        distance_record_long_race = int(distance_line.rstrip().removeprefix('Distance:').replace(' ', ''))
        return Race(time_ms=time_long_race, distance_record_mm=distance_record_long_race)

    def distance_run_holding_ms_time(self, hold_time_ms) -> int:
        time_left_ms = self.time_ms - hold_time_ms
        velocity_reached = hold_time_ms * VELOCITY_GAIN_MM_ON_MS
        return time_left_ms * velocity_reached
    
    def win_holding_ms_time(self, hold_time_ms) -> bool:
        return self.distance_run_holding_ms_time(hold_time_ms=hold_time_ms) > self.distance_record_mm

    def get_nr_ways_to_win(self) -> bool:
        return len([hold_time for hold_time in range(self.time_ms) if self.win_holding_ms_time(hold_time_ms=hold_time)])

if __name__ == '__main__':
    # test_time_line = 'Time:      7  15   30'
    # test_distance_line = 'Distance:  9  40  200'
    # test_races = Race.get_from_lines(time_line=test_time_line, distance_line=test_distance_line)
    # test_long_race = Race.get_single_long_race(time_line=test_time_line, distance_line=test_distance_line)
    # print(test_long_race)
    # print(test_races)
    # r1 = test_races[0]
    # print(r1.distance_run_holding_ms_time(2))
    # print(r1.win_holding_ms_time(2))
    # print(r1.get_nr_ways_to_win())
    # test_multiply_wins = 1
    # for race in test_races:
    #     test_multiply_wins *= race.get_nr_ways_to_win()
    # print(f'test race multiply wins value is {test_multiply_wins}')
    # print(f'long test race wins value is {test_long_race.get_nr_ways_to_win()}')

    with open("races.txt", "r") as fr:
        for i, line in enumerate(fr):
            if i == 0:
                time_line = line
            if i == 1:
                distance_line = line
    # races = Race.get_from_lines(time_line=time_line, distance_line=distance_line)
    long_race = Race.get_single_long_race(time_line=time_line, distance_line=distance_line)
    
    # print(races)
    # multiply_wins = 1
    # for race in races:
    #     multiply_wins *= race.get_nr_ways_to_win()
    # print(f'race multiply wins value is {multiply_wins}')
    print(f'long race wins value is {long_race.get_nr_ways_to_win()}')