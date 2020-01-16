import logging

from lxml import etree
from tqdm import tqdm
from igclib.geography.converters import geo2deg, km2nm
from igclib.constants import FILE_HEADERS


class AIXMFormat:

    def __init__(self):
        self.airspaces = []

    def read(self, input_file):
        tree = etree.parse(input_file)
        for a in tqdm(tree.findall('Ase')):
            airspace = {}
            airspace_id = a.find('AseUid').attrib['mid']
            airspace['class'] = a.find('AseUid').find('codeType').text
            airspace['name'] = a.find('txtName').text

            # altitude limits : (type, unit, val) tuple
            try:
                low = (a.find('codeDistVerLower').text, a.find('uomDistVerLower').text, a.find('valDistVerLower').text)
                high = (a.find('codeDistVerUpper').text, a.find('uomDistVerUpper').text, a.find('valDistVerUpper').text)
            except AttributeError:
                logging.warning('Complex airspaces are not yet supported.')
                continue

            if low[0] == 'ALT':
                airspace['low'] = f'{low[2]}{low[1]} AMSL'
            elif low[0] == 'HEI':
                airspace['low'] = f'{low[2]}{low[1]} AGL'
            elif low[0] == 'STD':
                airspace['low'] = f'{low[1]}{low[2]}'
            else:
                logging.error(f'Altitude code unknown : {low[0]}')

            if high[0] == 'ALT':
                airspace['high'] = f'{high[2]}{high[1]} AMSL'
            elif high[0] == 'HEI':
                airspace['high'] = f'{high[2]}{high[1]} AGL'
            elif high[0] == 'STD':
                airspace['high'] = f'{high[1]}{high[2]}'
            else:
                logging.error(f'Altitude code unknown : {high[0]}')

            # remarks
            if a.find('txtRmk') is not None:
                airspace['text'] = a.find('txtRmk').text.replace('#', '\n')
            else:
                airspace['text'] = 'No information'

            # geometry
            geometry = tree.xpath(f'Abd[AbdUid/AseUid[@mid="{airspace_id}"]]')
            if len(geometry) != 1:
                # TODO investigate corner cases
                continue
            # parts are now stored as openair format
            # this may need to change when converting to other formats
            airspace['parts'] = []
            avx = geometry[0].findall('Avx')
            for part in avx:
                part_type = part.find('codeType').text
                if part_type == 'GRC':
                    lat = part.find('geoLat').text
                    lon = part.find('geoLong').text
                    lat, lon = geo2deg(lat, lon)
                    airspace['parts'].append(f'DP {lat} {lon}')
                elif part_type == 'FNT':
                    logging.warning('Country borders not yet supported.')
                    continue
                elif part_type == 'RHL':
                    logging.warning('Rhumb lines not yet supported.')
                    continue
                elif part_type in ['CWA', 'CCA']:
                    center_lat = part.find('geoLatArc').text
                    center_lon = part.find('geoLongArc').text
                    start_lat = part.find('geoLat').text
                    start_lon = part.find('geoLong').text
                    center_lat, center_lon = geo2deg(center_lat, center_lon)
                    start_lat, start_lon = geo2deg(start_lat, start_lon)
                    radius = part.find('valRadiusArc').text
                    unit = part.find('uomRadiusArc').text
                    if unit.upper() == 'NM':
                        pass
                    elif unit.upper() == 'KM':
                        radius = km2nm(radius)
                    elif unit.upper() == 'M':
                        radius = km2nm(1000 * radius)
                    else:
                        logging.error(f'Unknown radius unit : {unit}')
                    if len(avx) == 1:
                        # circle case
                        airspace['parts'].append(f'V X={center_lat} {center_lon}\nDC {radius}')
                    else:
                        # arc case
                        stop_point = avx[(avx.index(part) + 1) % len(avx)]
                        stop_lat = stop_point.find('geoLat').text
                        stop_lon = stop_point.find('geoLong').text
                        stop_lat, stop_lon = geo2deg(stop_lat, stop_lon)
                        airspace['parts'].append(f'V X={center_lat} {center_lon}\nDB {start_lat} {start_lon}, {stop_lat} {stop_lon}')
                else:
                    logging.warning(f'Unknown geometry bound : {part_type}.')
            if len(airspace['parts']) > 2 or (len(airspace['parts']) == 1 and ('DC' in airspace['parts'][0])):
                self.airspaces.append(airspace)
            else:
                logging.warning(f'Airspace {airspace_id} will not be converted.')

    def write(self, to_format, output_file):
        with open(output_file, 'w') as f:
            if to_format == 'openair':
                f.write(FILE_HEADERS['openair'])
                for a in self.airspaces:
                    a['text'] = a['text'].replace('\n', '\n*')
                    f.write('*****\n')
                    f.write(f'*{a["text"]}\n')
                    f.write(f'AC {a["class"]}\n')
                    f.write(f'AN {a["class"]} {a["name"]}\n')
                    f.write(f'AL {a["low"]}\n')
                    f.write(f'AH {a["high"]}\n')
                    for p in a['parts']:
                        f.write(f'{p}\n')
