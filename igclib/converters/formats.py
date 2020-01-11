import logging

from lxml import etree
from tqdm import tqdm


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
                print(low[0])

            if high[0] == 'ALT':
                airspace['high'] = f'{high[2]}{high[1]} AMSL'
            elif high[0] == 'HEI':
                airspace['high'] = f'{high[2]}{high[1]} AGL'
            elif high[0] == 'STD':
                airspace['high'] = f'{high[1]}{high[2]}'
            else:
                print(high[0])
            
            # remarks
            if a.find('txtRmk') is not None:
                airspace['text'] = a.find('txtRmk').text.replace('#', '\n')
            else:
                airspace['text'] = 'No information'
            
            # geometry
            geometry = tree.xpath(f'Abd[AbdUid/AseUid[@mid="{airspace_id}"]]')
            if len(geometry) != 1: 
                continue
            airspace['parts'] = []
            for part in geometry[0].iterfind('Avx'):
                part_type = part.find('codeType').text
                if part_type == 'GRC':
                    lat = part.find('geoLat').text
                    lon = part.find('geoLong').text
                    airspace['parts'].append(f'DP {lat} {lon}')
            if airspace['parts']:
                self.airspaces.append(airspace)

    def write(self, to_format, output_file):
        with open(output_file, 'w') as f:
            if to_format == 'openair':
                for a in self.airspaces:
                    f.write('*\n')
                    a['text'] = a['text'].replace('\n', '\n*')
                    f.write(f'** {a["text"]} **\n')
                    f.write(f'AC {a["class"]}\n')
                    f.write(f'AN {a["class"]} {a["name"]}\n')
                    f.write(f'AL {a["low"]}\n')
                    f.write(f'AH {a["high"]}\n')
                    for p in a['parts']:
                        f.write(f'{p}\n')
