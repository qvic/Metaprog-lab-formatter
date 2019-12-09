import argparse

from util.util import Properties

parser = argparse.ArgumentParser(description='Code formatter for Java. Properties generation utility.')

parser.add_argument('output', type=str, help='Where to save generated properties.')

parser.add_argument('--schema', help='File with description of properties. "schema.properties" by default.', type=str,
                    default='schema.properties')

args = parser.parse_args()
properties = Properties(args.schema)

new_properties_map = {}
for key, value in properties.map.items():
    print('Option:', key)
    print('Default value:', value)
    converter = Properties.converters.get(type(value).__name__)
    raw_input = input('Your value: ')
    if raw_input is None or raw_input == '':
        entered_value = value
    else:
        entered_value = converter(raw_input)

    new_properties_map[key] = entered_value

Properties.save_map_to_file(new_properties_map, args.output)
