from pprint import pprint
from unittest import TestCase

from formatter.formatter import Formatter
from lexer.lexer import Lexer
from util.util import SourceFile, Properties


class TestFormatter(TestCase):

    def test_reformat_tokens(self):
        lexer = Lexer((SourceFile('testdata/test_formatter_split.java').read_all()))
        tokens = list(lexer.tokens)

        # pprint(tokens)
        # print()
        print(Formatter.format_tokens(tokens, Properties('test.properties')))
