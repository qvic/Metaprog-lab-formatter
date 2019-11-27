from unittest import TestCase

from formatter.formatter import TokenUtils
from lexer.token import *


class TestTokenUtils(TestCase):
    def test_has_before_and_after(self):
        tokens = [Separator(''), Modifier(''), Keyword('')]

        self.assertTrue(TokenUtils.has_before(1, Separator, tokens))
        self.assertTrue(TokenUtils.has_after(1, Keyword, tokens))
        self.assertTrue(TokenUtils.has_after(0, Modifier, tokens))
        self.assertTrue(TokenUtils.has_before(2, Modifier, tokens))

        self.assertFalse(TokenUtils.has_after(0, Separator, tokens))
        self.assertFalse(TokenUtils.has_before(1, Modifier, tokens))

        self.assertRaises(ValueError, lambda: TokenUtils.has_before(0, Separator, tokens))
        self.assertRaises(ValueError, lambda: TokenUtils.has_after(2, Keyword, tokens))

        self.assertRaises(ValueError, lambda: TokenUtils.has_before(3, Keyword, tokens))
        self.assertRaises(ValueError, lambda: TokenUtils.has_after(-1, Separator, tokens))

    def test_add_before_if_not_present(self):
        tokens = [LineBreak('\n'), Whitespace(' '), Keyword('a')]

        s = TokenUtils.add_before_if_not_present(tokens, 2, Whitespace(''), LineBreak('\n'))
        self.assertListEqual(tokens, [LineBreak('\n'), Whitespace(''), LineBreak('\n'), Keyword('a')])

    def test_add_after_if_not_present(self):
        tokens = [LineBreak('\n'), Whitespace(' '), Keyword('a')]

        TokenUtils.add_after_if_not_present(tokens, 2, LineBreak('\n'))
        self.assertListEqual(tokens, [LineBreak('\n'), Whitespace(' '), Keyword('a'), LineBreak('\n')])
