from pprint import pprint
from unittest import TestCase

from formatter.formatter import Formatter
from lexer.lexer import  tokenize
from util.util import SourceFile, Properties


class TestFormatter(TestCase):

    def test_reformat_tokens(self):
        tokens = tokenize(SourceFile('test_formatter_input_1.java').read_all())
        # pprint(list(tokens))

        print(Formatter.reformat_tokens(tokens, Properties('default.properties')))