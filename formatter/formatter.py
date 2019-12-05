from typing import List

from formatter.util import TokenUtils
from lexer.token import *
from util.util import Properties


class Formatter:

    @staticmethod
    def format_tokens(tokens, p: Properties) -> str:
        formatters = (
            Formatter.line_break_after_semicolon,
            Formatter.split_long_lines,
            Formatter.curly_braces_formatter,
        )

        for f in formatters:
            tokens = f(tokens, p)

        return ''.join(token.value for token in tokens)

    @staticmethod
    def curly_braces_formatter(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.format_curly_braces:
            return tokens

        indent = 0
        i = 0
        skip_to_line_break = False

        while i < len(tokens):
            token = tokens[i]

            if token.value == '{':
                indent += p.indent
                TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))

            elif token.value == '}':
                indent = max(indent - p.indent, 0)
                i += TokenUtils.add_or_replace_before(tokens, i, LineBreak('\n'), Whitespace(' ' * indent))

            elif skip_to_line_break:
                if token.value == '\n':
                    skip_to_line_break = False

            elif TokenUtils.is_any_line_start(token):
                skip_to_line_break = True
                i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' ' * indent))

            elif token.value in ['.', '::']:
                skip_to_line_break = True
                i += TokenUtils.add_or_replace_before(tokens, i,
                                                      Whitespace(' ' * (indent + p.method_chain_split_indent)))

            elif not p.preserve_comment_indent and isinstance(token, Comment):
                tokens[i] = TokenUtils.format_comment(token, indent)
                i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' ' * indent))

                if p.line_break_after_comment:
                    TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))

            i += 1

        return tokens

    @staticmethod
    def spaces_within_keywords(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.spaces_within_keywords:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if isinstance(token, Keyword):
                shift = TokenUtils.add_or_replace_before(tokens, i, Whitespace(' '))
                i += shift

            i += 1

        return tokens

    @staticmethod
    def line_break_after_semicolon(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.line_break_after_semicolon:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value == ';':
                TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))

            i += 1

        return tokens

    @staticmethod
    def split_long_lines(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.split_long_lines:
            return tokens

        i = 0
        split = False
        split_index = None
        current_line_length = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value == '.' or token.value == '::':
                split_index = i
            elif token.value == '\n':
                current_line_length = 0

            if split_index is not None and current_line_length > p.preferred_line_length:
                shift = TokenUtils.add_or_replace_before(tokens, split_index, LineBreak('\n'))
                i += shift
                current_line_length = 0

            # can't use position because of the possible modification
            current_line_length += len(token.value)
            i += 1

        return tokens
