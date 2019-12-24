import argparse

from formatter.formatter import Formatter
from util.util import SourceFile, Properties

parser = argparse.ArgumentParser(description='Code formatter for Java.')

parser.add_argument('input', type=str, help='File to format.')
parser.add_argument('properties', type=str, help='Properties for formatter.')

parser.add_argument('--print', help='Print to standard output.', action='store_true')
parser.add_argument('--output', type=str,
                    help='Output file. If not specified, formatted file will be written to the input file.')

args = parser.parse_args()

file = SourceFile(args.input)
result = Formatter.format(file.read_all(), Properties(args.properties))

if args.print:
    print('\n'.join(result.errors))
    print(result.code)
elif args.output is not None:
    print('\n'.join(result.errors))
    SourceFile(args.output).replace_all(result.code)
else:
    file.replace_all(result.code)
