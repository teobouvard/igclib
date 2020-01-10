from lxml import etree

class AIXMFormat:
    def __init__(self):
        self.airspaces = []

    def read(self, input_file):
        tree = etree.parse(input_file)
        for a in tree.findall('Ase'):
            airspace = {}
            airspace['name'] = a.find('txtName').text
            self.airspaces.append(airspace)

    def write(self, to_format, output_file):
        with open(output_file, 'w') as f:
            for a in self.airspaces:
                f.write(f'{a["name"]}\n')
