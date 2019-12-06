import argparse

from formatter.formatter import Formatter
from util.util import SourceFile, Properties

parser = argparse.ArgumentParser(description='Code formatter for Java.')

parser.add_argument('input', type=str, help='File to format.')
parser.add_argument('template', type=str, help='Properties for formatter.')

parser.add_argument('--print', help='Print to standard output.', action='store_true')
parser.add_argument('--output', type=str,
                    help='Output file. If not specified, formatted file will be written to the input file.')

args = parser.parse_args()

file = SourceFile(args.input)
formatted_file_content = Formatter.format_tokens(file.read_all(), Properties(args.template))

if args.print:
    print(formatted_file_content)
elif args.output is not None:
    SourceFile(args.output).replace_all(formatted_file_content)
else:
    file.replace_all(formatted_file_content)
