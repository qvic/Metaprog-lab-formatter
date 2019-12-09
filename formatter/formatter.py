from typing import List

from formatter.util import TokenUtils
from lexer.lexer import Lexer
from lexer.token import *
from util.util import Properties


class Formatter:

    @staticmethod
    def format(file_content: str, p: Properties) -> str:
        tokens = list(Lexer.get_tokens(file_content))

        formatters = (
            Formatter.clean_spaces,
            Formatter.replace_multiple_spaces,
            Formatter.spaces_near_operators,
            Formatter.space_after_comma,
            Formatter.line_break_after_semicolon,
            Formatter.format_block_expressions,
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
                indent = indent - p.indent
                if indent < 0:
                    print('Unexpected closing bracket at {}, set indent to 0.'.format(token.position))
                    indent = 0

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
    def space_after_comma(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.space_after_comma:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value == ',':
                TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))

            i += 1

        return tokens

    @staticmethod
    def replace_multiple_spaces(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.replace_multiple_spaces:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if isinstance(token, Whitespace) and len(token.value) > 1:
                token.value = ' '

            i += 1

        return tokens

    @staticmethod
    def clean_spaces(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.clean_spaces_near_brackets:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value in ['(', '[']:
                TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
            elif token.value in [')', ']']:
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)

            i += 1

        return tokens

    @staticmethod
    def spaces_near_operators(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.spaces_near_operators:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if isinstance(token, Operator):
                if token.is_infix() or token.is_assignment():
                    i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' '))
                    TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                elif token.is_prefix() or token.is_postfix():
                    i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                    TokenUtils.remove_after_if_exists(tokens, i, Whitespace)

            i += 1

        return tokens

    @staticmethod
    def format_block_expressions(tokens: List[Token], p: Properties) -> List[Token]:

        i = 0
        count_braces = 0
        started_block = False
        while i < len(tokens):
            token = tokens[i]

            if token.value in ['if', 'for', 'while']:
                if p.replace_spaces_near_block_expression:
                    TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                started_block = True

            elif started_block and token.value == '(':
                count_braces += 1

            elif started_block and token.value == ')':
                count_braces -= 1
                if count_braces == 0:
                    if p.replace_spaces_near_block_expression:
                        TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                    started_block = False

            elif started_block and count_braces > 0 and token.value == ';':
                TokenUtils.remove_after_if_exists(tokens, i, LineBreak)
                TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))

            i += 1

        return tokens

    @staticmethod
    def split_long_lines(tokens: List[Token], p: Properties) -> List[Token]:

        if not p.split_long_lines:
            return tokens

        i = 0
        split_index = None
        current_line_length = 0

        brackets_split = False
        brackets_start_column = None

        while i < len(tokens):
            token = tokens[i]

            if split_index is not None and current_line_length > p.preferred_line_length:
                shift = 0
                if brackets_split:
                    shift += TokenUtils.add_or_replace_before(tokens, split_index,
                                                              ImportantWhitespace(' ' * (brackets_start_column - 1)))

                shift += TokenUtils.add_or_replace_before(tokens, split_index, LineBreak('\n'))

                i += shift

                if brackets_split:
                    current_line_length = brackets_start_column - 1
                else:
                    current_line_length = 0

            if token.value in ['.', '::']:
                split_index = i
            elif token.value in [',']:
                split_index = i + 1

            elif token.value == '(':
                brackets_split = True
                brackets_start_column = current_line_length
            elif token.value == ')':
                brackets_split = False

            elif token.value == '\n':
                current_line_length = 0
                split_index = None

            # can't use position because of the possible modification
            current_line_length += len(token.value)
            i += 1

        return tokens
