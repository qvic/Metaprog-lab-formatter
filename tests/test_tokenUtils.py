from unittest import TestCase

from formatter.util import TokenUtils
from lexer.token import *


class TestTokenUtils(TestCase):
    def test_has_before_and_after(self):
        tokens = [Separator(''), Modifier(''), Keyword('')]

        self.assertTrue(TokenUtils.has_before(tokens, 1, Separator))
        self.assertTrue(TokenUtils.has_after(tokens, 1, Keyword))
        self.assertTrue(TokenUtils.has_after(tokens, 0, Modifier))
        self.assertTrue(TokenUtils.has_before(tokens, 2, Modifier))

        self.assertFalse(TokenUtils.has_after(tokens, 0, Separator))
        self.assertFalse(TokenUtils.has_before(tokens, 1, Modifier))

        self.assertRaises(ValueError, lambda: TokenUtils.has_before(tokens, 0, Separator))
        self.assertRaises(ValueError, lambda: TokenUtils.has_after(tokens, 2, Keyword))

        self.assertRaises(ValueError, lambda: TokenUtils.has_before(tokens, 3, Keyword))
        self.assertRaises(ValueError, lambda: TokenUtils.has_after(tokens, -1, Separator))

    def test_add_before_if_not_present(self):
        tokens = [LineBreak('\n'), Whitespace(' '), Keyword('a')]

        s = TokenUtils.add_or_replace_before(tokens, 2, Whitespace(''), LineBreak('\n'))
        self.assertListEqual(tokens, [LineBreak('\n'), Whitespace(''), LineBreak('\n'), Keyword('a')])

    def test_add_after_if_not_present(self):
        tokens = [LineBreak('\n'), Whitespace(' '), Keyword('a')]

        TokenUtils.add_or_replace_after(tokens, 2, LineBreak('\n'))
        self.assertListEqual(tokens, [LineBreak('\n'), Whitespace(' '), Keyword('a'), LineBreak('\n')])
