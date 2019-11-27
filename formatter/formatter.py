from typing import List

from lexer.token import *
from util.util import Properties


class TokenUtils:

    @staticmethod
    def has_before(i, type, tokens):
        if not 0 <= i < len(tokens):
            raise ValueError('Token at {0} does not exist'.format(i))

        if i < 1:
            raise ValueError('Nothing before {0}'.format(i))

        if isinstance(tokens[i - 1], type):
            return True

        return False

    @staticmethod
    def has_after(i, type, tokens):
        if not 0 <= i < len(tokens):
            raise ValueError('Token at {0} does not exist'.format(i))

        if i >= len(tokens) - 1:
            raise ValueError('Nothing after {0}'.format(i))

        if isinstance(tokens[i + 1], type):
            return True

        return False

    @staticmethod
    def add_before_if_not_present(tokens, i, *tokens_to_add):
        s = 0
        for token_to_add in reversed(tokens_to_add):
            if i > 0 and type(tokens[i - 1]) is type(token_to_add):
                tokens[i - 1] = token_to_add
                i -= 1
            else:
                tokens.insert(i, token_to_add)
                s += 1
        return s

    @staticmethod
    def add_after_if_not_present(tokens, i, *tokens_to_add):
        for token_to_add in tokens_to_add:
            if i < len(tokens) - 1 and type(tokens[i + 1]) is type(token_to_add):
                tokens[i + 1] = token_to_add
                i += 1
            else:
                tokens.insert(i + 1, token_to_add)

    @staticmethod
    def is_any_line_start(token):
        types = (Literal, Keyword, Identifier)

        return isinstance(token, types)

    @staticmethod
    def format_comment(token, indent) -> Comment:
        result = []
        shift = indent - token.position.column

        split = token.value.split('\n')
        result.append(split[0])
        for line in split[1:]:
            result.append(line.rjust(len(line) + shift))

        return Comment('\n'.join(result))


class Formatter:

    @staticmethod
    def format_tokens(tokens, p: Properties) -> str:
        formatters = (
            Formatter.curly_braces_formatter,
        )

        for f in formatters:
            tokens = f(tokens, p)

        return ''.join(token.value for token in tokens)

    @staticmethod
    def curly_braces_formatter(tokens: List[Token], p: Properties) -> List[Token]:
        indent = 0
        i = 0
        skip_to_line_break = False

        while i < len(tokens):
            token = tokens[i]

            if token.value == '{':
                indent += p.indent
                TokenUtils.add_after_if_not_present(tokens, i, LineBreak('\n'))

            elif token.value == '}':
                indent = max(indent - p.indent, 0)
                i += TokenUtils.add_before_if_not_present(tokens, i, LineBreak('\n'), Whitespace(' ' * indent))

            elif skip_to_line_break:
                if token.value == '\n':
                    skip_to_line_break = False

            elif TokenUtils.is_any_line_start(token):
                skip_to_line_break = True
                i += TokenUtils.add_before_if_not_present(tokens, i, Whitespace(' ' * indent))

            elif not p.preserve_comment_indent and isinstance(token, Comment):
                tokens[i] = TokenUtils.format_comment(token, indent)
                i += TokenUtils.add_before_if_not_present(tokens, i, Whitespace(' ' * indent))

                if p.line_break_after_comment:
                    TokenUtils.add_after_if_not_present(tokens, i, LineBreak('\n'))

            i += 1

        return tokens
