from igclib.converters.formats import AIXMFormat

class Converter:
    """
    Converter class to convert between different file formats.
    For the moment, the supported conversions are:
    * aixm -> openair
    """
    formats = {
        'aixm': AIXMFormat
    }
    def __init__(self, from_format, input_file):
        self.file = self.formats[from_format]()
        self.file.read(input_file)
        
    def convert(self, to_format, output_file):
        self.file.write(to_format, output_file)