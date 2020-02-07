import json
import logging
import os
import pickle

from igclib.serialization.json_encoder import ComplexEncoder


class BaseObject:

    def save(self, output):
        """
        Saves the object instance to each file specified by output.
            * If output is a list, this method calls itself with each element of the list.
            * If output is a JSON file (.json), a human-readable, serialized version of the object is written.
            * If output is a pickle file (.pkl), a binary version of the object is written, allowing for faster loading times in the subsequent uses.
            * If output is -, the JSON serialization is written to the standard output.

        Classes inheriting from this base object must redefine the serialize method.

        Arguments:
            output (str) : File to which the output is written.
        """
        if isinstance(output, list):
            for out in output:
                self.save(out)
        elif output.endswith('.pkl'):
            with open(output, 'wb') as f:
                pickle.dump(self.dump(), f)
        elif output.endswith('.json'):
            with open(output, 'w', encoding='utf8') as f:
                json.dump(self.serialize(), f, cls=ComplexEncoder, ensure_ascii=False, indent=2)
        elif output == '-':
            print(json.dumps(self.serialize(), cls=ComplexEncoder, ensure_ascii=False))
        else:
            raise ValueError(f'Output must be in [*.json, *.pkl, -] but is {output}')

    def load(self, input_file):
        """
        Loads the object instance from a binary file created with the save method.

        Arguments:
            input_file (str) : File to load
        """
        if input_file.endswith('.pkl'):
            with open(input_file, 'rb') as f:
                self.__dict__.update(pickle.load(f))
        else:
            raise ValueError(
                f'Object should be loaded from a .pkl file but input file is {os.path.splitext(input_file)[-1]}')

    def serialize(self):
        """
        Implements a default recursive serialization on the object. All attributes not starting with '_' are dumped.
        """
        serialized = {}
        for x, y in self.__dict__.items():
            if not x.startswith('_'):
                if isinstance(y, BaseObject):
                    serialized[x] = y.serialize()
                serialized[x] = y
        return serialized

    def dump(self):
        """
        Implements a default dumping strategy. All attributes not starting with '_' are dumped.
        """
        return {x: y for x, y in self.__dict__.items() if not x.startswith('_')}
