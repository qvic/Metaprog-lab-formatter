import os
from collections import namedtuple


class Helpers:

    @staticmethod
    def get_file_extension(file_path):
        return os.path.splitext(file_path)[1]


class Representable:

    def __repr__(self) -> str:
        return '{}[{}]'.format(type(self).__name__, ', '.join('%s=%s' % item for item in vars(self).items()))


class SourceFile(Representable):

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_all(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, SourceFile):
            return self.file_path == o.file_path
        return False

    def __hash__(self) -> int:
        return hash(self.file_path)


class Properties(Representable):

    def __init__(self, file_path: str, separator='=', comment_char='#'):
        with open(file_path, 'r') as file:
            self.map = Properties._load_properties(file, separator, comment_char)

    def __getattr__(self, item: str):
        return self.map.get(item)

    @staticmethod
    def _load_properties(file, separator: str, comment_char: str, type_separator=':'):
        convertors = {
            'int': int,
            'float': float,
            'bool': lambda s: s.lower() == 'true',
        }

        properties = {}
        for line in file:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(separator)
                key = key_value[0].strip()
                splitted_key = key.split(type_separator)

                value_convertor = str
                if len(splitted_key) > 1:
                    value_convertor = convertors[splitted_key[-1]]

                value = value_convertor(separator.join(key_value[1:]).strip().strip('"'))
                properties[type_separator.join(splitted_key[:-1])] = value

        return properties
