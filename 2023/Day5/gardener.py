from typing import List, Dict, Tuple, Iterable
from dataclasses import dataclass
import itertools

@dataclass
class GardenElement:

    layer: str
    position: int

    @staticmethod
    def get_elements_from_line(elements_line: str) -> List['GardenElement']:
        # assuming seeds, KISS
        return [GardenElement(layer='seed', position=int(pos)) for pos in elements_line.removeprefix('seeds:').split()]
    
    @staticmethod
    def get_exploded_elements_from_line(elements_line: str) -> List['GardenElement']:
        # assuming seeds, KISS
        starting_positions = [int(pos) for pos in elements_line.removeprefix('seeds:').split()]
        exploded_elements = []
        for i, starting_position in enumerate(starting_positions):
            if i%2 != 0:
                continue
            exploded_elements.extend([GardenElement(layer='seed', position=starting_position + repl) for repl in range(starting_positions[i+1])])
        return exploded_elements

    def get_exploded_elements(self, number_explosions: int) -> Iterable['GardenElement']:
        for explosion in range(number_explosions):
            yield GardenElement(layer='seed', position=self.position+explosion)

    def get_exploded_seed_positions(self, number_explosions: int) -> Iterable[int]:
        for explosion in range(number_explosions):
            yield self.position + explosion

@dataclass
class InOutMapper:

    destination_range_start: int
    source_range_start: int
    range_length: int

    @staticmethod
    def from_description(description: str) -> 'InOutMapper':
        mappers_numbers = [int(num) for num in description.split()]
        return InOutMapper(destination_range_start=mappers_numbers[0], source_range_start=mappers_numbers[1], range_length=mappers_numbers[2])

    @property
    def source_range_end(self) -> int:
        return self.source_range_start + self.range_length

    @property
    def destination_range_end(self) -> int:
        return self.destination_range_start + self.range_length

    @property
    def mapping_source_to_destination(self) -> Dict[int, int]:
        return {self.source_range_start + i: destination_end for i, destination_end in enumerate(range(self.destination_range_start, self.destination_range_end))}

    def source_falls_into_mapper(self, source_position: int) -> bool:
        return source_position >= self.source_range_start and source_position <= self.source_range_end
    
    def get_destination_position(self, source_position: int) -> int:
        return self.destination_range_start + (source_position - self.source_range_start)

    @property
    def source_border_points(self) -> List[int]:
        return [self.source_range_start, self.source_range_end - 1]

@dataclass
class SourceDestinationMapper:
    
    identifier_source: str
    identifier_destination: str
    mappers: List[InOutMapper]

    @staticmethod
    def from_lines_descriptions(identifiers_description: str, mapper_descriptions: List[str]) -> 'SourceDestinationMapper':
        source_to_des = SourceDestinationMapper._parse_identifiers(identifiers_description)
        return SourceDestinationMapper(
            identifier_source=source_to_des[0],
            identifier_destination = source_to_des[1],
            mappers = [InOutMapper.from_description(mapper_desc) for mapper_desc in mapper_descriptions]
        )

    def _parse_identifiers(identifiers_description: str) -> Tuple[str]:
        """seed-to-soil map: -> (seed, soil)"""
        return tuple(identifiers_description.rstrip().removesuffix(' map:').split('-to-'))
    
    def map_source_to_destination(self, source_position: int) -> int:
        for in_out in self.mappers:
            if in_out.source_falls_into_mapper(source_position=source_position):
                return in_out.get_destination_position(source_position=source_position)  # waaaaaay too fucking fast
                # return in_out.mapping_source_to_destination[source_position]
        return source_position

    @property
    def layer_source_border_points(self) -> List[int]:
        return list(itertools.chain.from_iterable([mapper.source_border_points for mapper in self.mappers]))

@dataclass
class SeedAlmanac:

    layer_mappers: List[SourceDestinationMapper]

    def map_layer_source_to_destination(self, garden_element: GardenElement) -> GardenElement:
        catch_sd_mapper = [sd_mapper for sd_mapper in self.layer_mappers if sd_mapper.identifier_source == garden_element.layer]
        position = garden_element.position
        while any(catch_sd_mapper):
            sd_mapper_step = catch_sd_mapper[0]
            reached_layer = sd_mapper_step.identifier_destination
            reached_position_step = sd_mapper_step.map_source_to_destination(position)
            # print(f'Layer: {sd_mapper_step.identifier_source} to {reached_layer}. Element from position {position} go to {reached_position_step}')
            position = reached_position_step
            catch_sd_mapper = [sd_mapper for sd_mapper in self.layer_mappers if sd_mapper.identifier_source == reached_layer]
        # print(f'Element starting {garden_element.layer} position {garden_element.position} reach final position {reached_position_step}, in layer {reached_layer}')
        return GardenElement(layer=reached_layer, position=reached_position_step)

    def map_seed_to_location_position(self, seed_starting_position: int) -> int:
        position = seed_starting_position
        for layer_mapper in self.layer_mappers:
            reached_position_step = layer_mapper.map_source_to_destination(position)
            position = reached_position_step
        return reached_position_step

    @property
    def almanac_source_border_points(self) -> List[int]:
        return list(itertools.chain.from_iterable([mapper.layer_source_border_points for mapper in self.layer_mappers]))

    def get_seed_falling_possibility_intervals(self, end_border: int) -> List[tuple]:
        border_elements = set(self.almanac_source_border_points)
        if 0 not in border_elements:
            border_elements.add(0)
        assert end_border > max(border_elements), f'too low end border chosen: {end_border}. You have to overcome {max(border_elements)}'
        border_elements.add(end_border)
        border_elements_ordered = list(border_elements)
        border_elements_ordered.sort()
        return [(border_element, border_elements_ordered[i + 1]) for i, border_element in enumerate(border_elements_ordered[:-1]) if i%2==0]

    def get_overall_source_destination_mapper(self, end_border: int) -> List[InOutMapper]:
        return [
            InOutMapper(
                destination_range_start=self.map_seed_to_location_position(seed_starting_position=border_interval[0]),
                source_range_start=border_interval[0],
                range_length=border_interval[1] - border_interval[0] + 1
            ) for border_interval in self.get_seed_falling_possibility_intervals(end_border=end_border)
        ]

if __name__ == '__main__':
    # el =  GardenElement(layer='seed', position=39)
    # for el in el.get_exploded_elements(number_explosions=10):
    #     print(el)
    # test_in_out_description = '50 98 2'
    # test_in_out = InOutMapper(destination_range_start=50, source_range_start=98, range_length=2)
    # test_in_out = InOutMapper.from_description(description=test_in_out_description)
    # print(test_in_out)
    # print(test_in_out.mapping_source_to_destination)
    # print(test_in_out.get_destination_position(source_position=99))
    # print(test_in_out.source_border_points)
    # sd_mapper = SourceDestinationMapper(identifier_source='seed', identifier_destination='soil', mappers=[InOutMapper(destination_range_start=50, source_range_start=98, range_length=2), InOutMapper(destination_range_start=52, source_range_start=50, range_length=48)])
    # print(sd_mapper.map_source_to_destination(source_position=79))
    # print(sd_mapper.map_source_to_destination(source_position=14))
    # print(sd_mapper.map_source_to_destination(source_position=55))
    # print(sd_mapper.map_source_to_destination(source_position=13))
    sd_mapper_parsed = SourceDestinationMapper.from_lines_descriptions(identifiers_description='soil-to-fertilizer map:', mapper_descriptions=['0 15 37', '37 52 2', '39 0 15'])
    print(sd_mapper_parsed.layer_source_border_points)
    # print(sd_mapper_parsed)
    test_almanac = [
        'seeds: 79 14 55 13',
        'seed-to-soil map:',
        '50 98 2',
        '52 50 48',
        '',
        'soil-to-fertilizer map:',
        '0 15 37',
        '37 52 2',
        '39 0 15',
        '',
        'fertilizer-to-water map:',
        '49 53 8',
        '0 11 42',
        '42 0 7',
        '57 7 4',
        '',
        'water-to-light map:',
        '88 18 7',
        '18 25 70',
        '',
        'light-to-temperature map:',
        '45 77 23',
        '81 45 19',
        '68 64 13',
        '',
        'temperature-to-humidity map:',
        '0 69 1',
        '1 0 69',
        '',
        'humidity-to-location map:',
        '60 56 37',
        '56 93 4',
    ]
    test_sd_identifiers_description = None
    test_sd_mappers_descriptions = []
    test_layer_mappers = []
    for i, line in enumerate(test_almanac):
        if i == 0:
            test_elements = GardenElement.get_elements_from_line(elements_line=line)
            test_elements_exploded = GardenElement.get_exploded_elements_from_line(elements_line=line)
            continue
        if len(line) <= 1:
            if test_sd_identifiers_description is not None:
                test_layer_mappers.append(SourceDestinationMapper.from_lines_descriptions(identifiers_description=test_sd_identifiers_description, mapper_descriptions=test_sd_mappers_descriptions))
            test_sd_identifiers_description = None
            test_sd_mappers_descriptions = []
            continue
        if test_sd_identifiers_description is None:
            test_sd_identifiers_description = line
            continue
        test_sd_mappers_descriptions.append(line)

    if test_sd_identifiers_description is not None:
        test_layer_mappers.append(SourceDestinationMapper.from_lines_descriptions(identifiers_description=test_sd_identifiers_description, mapper_descriptions=test_sd_mappers_descriptions))
        
    # print(test_elements)
    # print(test_elements_exploded)
    test_almanac = SeedAlmanac(layer_mappers=test_layer_mappers)
    # print(test_almanac.almanac_source_border_points)
    # print(test_almanac.get_seed_falling_possibility_intervals(end_border=101))
    # print(test_almanac.map_seed_to_location_position(14))
    # for in_out in test_almanac.get_overall_source_destination_mapper(end_border=101):
    #     print(in_out)
    # print(test_almanac)
    # locations = [test_almanac.map_layer_source_to_destination(garden_element=el).position for el in test_elements]
    # print(f'test result lowest location number is {min(locations)}')
    # locations_el_exploded = [test_almanac.map_layer_source_to_destination(garden_element=el).position for el in test_elements_exploded]
    # locations_el_exploded_generator = []
    # for i, el_base in enumerate(test_elements):
    #     if i%2 != 0:
    #         continue
    #     for el in el_base.get_exploded_elements(number_explosions=test_elements[i + 1].position):
    #         locations_el_exploded_generator.append(test_almanac.map_layer_source_to_destination(garden_element=el).position)
    # print(f'test result lowest location number after seed explosion is {min(locations_el_exploded)}')
    # print(f'test result lowest location number after seed explosion generator is {min(locations_el_exploded_generator)}')

    # sd_identifiers_description = None
    # sd_mappers_descriptions = []
    # layer_mappers = []
    # with open("seed_mapping.txt", "r") as fr:
    #     for i, line in enumerate(fr):
    #         if i == 0:
    #             elements = GardenElement.get_elements_from_line(elements_line=line)
    #             # elements_exploded = GardenElement.get_exploded_elements_from_line(elements_line=line)
    #             continue
    #         if len(line) <= 1:
    #             if sd_identifiers_description is not None:
    #                 layer_mappers.append(SourceDestinationMapper.from_lines_descriptions(identifiers_description=sd_identifiers_description, mapper_descriptions=sd_mappers_descriptions))
    #             sd_identifiers_description = None
    #             sd_mappers_descriptions = []
    #             continue
    #         if sd_identifiers_description is None:
    #             sd_identifiers_description = line
    #             continue
    #         sd_mappers_descriptions.append(line)

    #     if sd_identifiers_description is not None:
    #         layer_mappers.append(SourceDestinationMapper.from_lines_descriptions(identifiers_description=sd_identifiers_description, mapper_descriptions=sd_mappers_descriptions))

    # # print(elements)
    # # print(elements_exploded)
    # almanac = SeedAlmanac(layer_mappers=layer_mappers)
    # # print(len(almanac.layer_mappers))
    # # print(almanac.layer_mappers[0])
    # # for mapp in almanac.layer_mappers:
    # #     print(f'{mapp.identifier_source} {mapp.identifier_destination} elements {len(mapp.mappers)}')
    # locations = [almanac.map_layer_source_to_destination(garden_element=el).position for el in elements]
    # print(f'result lowest location number is {min(locations)}')

    # tot_exploding_seeds = sum([x.position for x in elements if x.position %2!=0])
    # tot_base_seeds = len([x for x in elements if x.position %2==0])
    # tot_seeds = tot_exploding_seeds + tot_base_seeds
    # print(f'number of seeds to process is {tot_exploding_seeds} cloned plus {tot_base_seeds}: {tot_seeds}')
    
    # import datetime as dt
    # import time
    # print(f'start process at {dt.datetime.now()}')
    # start_window_time = time.time()
    # time_interval_log_s = 120
    # base_seed_processed = 0
    # tot_seed_processed = 0
    # locations_el_exploded_generator = []
    # min_location_exploded = 0
    # for i, el_base in enumerate(elements):
    #     if i%2 != 0:
    #         continue
    #     for el_pos in el_base.get_exploded_seed_positions(number_explosions=elements[i + 1].position):
    #         # location_seed = almanac.map_layer_source_to_destination(garden_element=el).position
    #         location_seed = almanac.map_seed_to_location_position(seed_starting_position=el_pos)
    #         if location_seed < min_location_exploded:
    #             min_location_exploded = location_seed
    #         tot_seed_processed += 1
    #         if time.time() > start_window_time + time_interval_log_s:
    #             print(f'[{dt.datetime.now()}] Processed {base_seed_processed}/{tot_base_seeds} base seeds, {tot_seed_processed}/{tot_seeds} overall')
    #             start_window_time = time.time()
            
    #     base_seed_processed += 1
        
    # print(f'result lowest location number after seed explosion is {min_location_exploded}')
