from unittest import TestCase

from formatter.formatter import Formatter
from util.util import SourceFile, Properties


class TestFormatter(TestCase):

    def test_reformat_tokens(self):
        # result = Formatter.format(SourceFile('testdata/ModelAndView.java').read_all(), Properties('test.properties'))
        result = Formatter.format(SourceFile('testdata/test2.java').read_all(), Properties('test.properties'))
        print('\n'.join(result.errors))
        print(result.code)
