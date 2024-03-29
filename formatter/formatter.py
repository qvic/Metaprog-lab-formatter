from typing import List

from formatter.util import TokenUtils
from lexer.lexer import Lexer
from lexer.token import *
from util.util import Properties, FormattingResult


class Formatter:

    @staticmethod
    def format(file_content: str, p: Properties) -> FormattingResult:
        tokens = list(Lexer.get_tokens(file_content))
        errors = []

        formatters = (
            Formatter.clear_spaces,
            Formatter.replace_multiple_spaces,
            Formatter.spaces_near_operators,
            Formatter.space_after_comma,
            Formatter.clear_line_breaks,
            Formatter.line_break_after_semicolon,
            Formatter.format_block_expressions,
            Formatter.curly_braces_formatter,
            Formatter.split_long_lines,
            Formatter.remove_redundant_line_breaks,
        )

        for f in formatters:
            tokens = f(tokens, p, errors)

        return FormattingResult(''.join(token.value for token in tokens), errors)

    @staticmethod
    def curly_braces_formatter(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.format_curly_braces:
            return tokens

        indent = 0
        i = 0
        skip_to_line_break = False

        while i < len(tokens):
            token = tokens[i]

            if token.value == '{':
                if (i > 2 and TokenUtils.has_before(tokens, i, Whitespace) and TokenUtils.has_before(tokens, i - 1,
                                                                                                     LineBreak)) or \
                        (i > 1 and TokenUtils.has_before(tokens, i, LineBreak)) or \
                        i == 0:
                    i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' ' * indent))
                else:
                    i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' '))

                indent += p.indent
                TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))

            elif token.value == '}':
                indent = indent - p.indent
                if indent < 0:
                    errors.append('Unexpected closing bracket at {}, set indent to 0.'.format(token.position))
                    indent = 0

                i += TokenUtils.add_or_replace_before(tokens, i, LineBreak('\n'), Whitespace(' ' * indent))

            elif skip_to_line_break:
                if token.value == '\n':
                    skip_to_line_break = False

            elif TokenUtils.is_any_line_start(token) or (isinstance(token, Comment) and token.value.startswith('//')):
                skip_to_line_break = True
                if token.value in ['else', 'catch', 'finally']:
                    i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                    i += TokenUtils.remove_before_if_exists(tokens, i, LineBreak)
                    i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' '))
                else:
                    i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' ' * indent))

            elif token.value in ['.', '::']:
                skip_to_line_break = True
                i += TokenUtils.add_or_replace_before(tokens, i,
                                                      Whitespace(' ' * (indent + p.split_indent)))

            elif not p.preserve_comment_indent and isinstance(token, Comment) and token.value.startswith('/*'):
                tokens[i] = TokenUtils.format_comment(token, indent)
                i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' ' * indent))

                if p.line_break_after_comment:
                    TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))

            i += 1

        if indent > 0:
            errors.append('Expected closing bracket at the end.')

        return tokens

    @staticmethod
    def spaces_within_keywords(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

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
    def remove_redundant_line_breaks(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.remove_redundant_line_breaks:
            return tokens

        i = 0
        line_break_count = 0
        while i < len(tokens):
            token = tokens[i]

            if isinstance(token, LineBreak):
                line_break_count += 1
            elif not isinstance(token, Whitespace):
                line_break_count = 0

            while line_break_count > 2:
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                i += TokenUtils.remove_before_if_exists(tokens, i, LineBreak)
                line_break_count -= 1

            i += 1

        return tokens

    @staticmethod
    def line_break_after_semicolon(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.line_break_after_semicolon:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value == ';':
                if TokenUtils.has_after(tokens, i, value=';'):
                    errors.append('Double semicolon at {}.'.format(token.position))
                elif not (i < len(tokens) - 2 and TokenUtils.has_after(tokens, i, Whitespace) and
                          TokenUtils.has_after(tokens, i + 1, Comment)):
                    TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))

            i += 1

        return tokens

    @staticmethod
    def space_after_comma(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.space_after_comma:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value == ',':
                TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)

            i += 1

        return tokens

    @staticmethod
    def replace_multiple_spaces(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

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
    def clear_spaces(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.clear_spaces_near_brackets:
            return tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.value in ['(', '[']:
                TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
            elif token.value in [')', ']']:
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
            elif token.value in ['.']:
                TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)

            i += 1

        return tokens

    @staticmethod
    def clear_line_breaks(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.clear_line_breaks_in_signatures:
            return tokens

        i = 0

        after_modifier = False
        after_return_type = False
        after_name = False
        parameter_brackets = 0

        generic_brackets = 0
        generic_state = False

        while i < len(tokens):
            token = tokens[i]

            if generic_state and token.value == '<':
                generic_brackets += 1
                TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)

            elif (after_return_type or after_modifier or parameter_brackets > 0) and token.value == '<':
                generic_brackets += 1
                TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                if after_return_type or parameter_brackets > 0:
                    i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                generic_state = True

            elif generic_state and token.value == '>':
                generic_brackets -= 1
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                if generic_brackets == 0:
                    TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                    if i < len(tokens) - 1:
                        TokenUtils.remove_after_if_exists(tokens, i + 1, LineBreak)
                    generic_state = False

            elif token.value in [';', '{', '}']:
                if token.value == ';':
                    TokenUtils.remove_before_if_exists(tokens, i, Whitespace)

                after_modifier = False
                after_return_type = False
                after_name = False
                parameter_brackets = 0
                generic_brackets = 0

            elif (after_name or after_return_type) and token.value == '(':
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                i += TokenUtils.remove_before_if_exists(tokens, i, LineBreak)
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                parameter_brackets += 1
                after_name = False
                after_return_type = False

            elif token.value == ')':
                parameter_brackets -= 1
                if parameter_brackets == 0:
                    TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                    TokenUtils.remove_after_if_exists(tokens, i, LineBreak)
                    after_name = False
                elif parameter_brackets < 0:
                    parameter_brackets = 0

            elif isinstance(token, Modifier) or token.value in ['class', 'enum', 'interface']:
                TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                TokenUtils.remove_after_if_exists(tokens, i, LineBreak)
                TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                after_modifier = True

            elif isinstance(token, (BasicType, Identifier)):
                if not generic_state and after_modifier:
                    after_modifier = False
                    TokenUtils.remove_after_if_exists(tokens, i, LineBreak)
                    TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                    after_return_type = True
                elif after_return_type and isinstance(token, Identifier):
                    after_return_type = False
                    after_name = True

            i += 1

        return tokens

    @staticmethod
    def spaces_near_operators(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

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
    def format_block_expressions(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        i = 0
        count_braces = 0
        started_block = False
        switch_block = False
        case_block = False

        while i < len(tokens):
            token = tokens[i]

            if token.value in ['if', 'for', 'while', 'switch']:
                if p.put_spaces_near_block_expression:
                    TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                else:
                    TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                started_block = True

                if token.value == 'switch':
                    switch_block = True

            elif token.value in ['else']:
                TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                if p.put_spaces_near_block_expression:
                    i += TokenUtils.add_or_replace_before(tokens, i, Whitespace(' '))
                else:
                    i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)

            elif switch_block and token.value in ['case', 'default']:
                case_block = False

            elif switch_block and token.value == ':':
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                TokenUtils.add_or_replace_after(tokens, i, LineBreak('\n'))
                case_block = True

            elif started_block and token.value == '(':
                count_braces += 1

            elif started_block and token.value == ')':
                count_braces -= 1
                if count_braces == 0:
                    if p.put_spaces_near_block_expression:
                        TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))
                    else:
                        TokenUtils.remove_after_if_exists(tokens, i, Whitespace)
                    started_block = False

            elif started_block and count_braces > 0 and token.value == ';':
                TokenUtils.remove_after_if_exists(tokens, i, LineBreak)
                TokenUtils.add_or_replace_after(tokens, i, Whitespace(' '))

            elif case_block and TokenUtils.is_any_line_start(token):
                i += TokenUtils.remove_before_if_exists(tokens, i, Whitespace)
                i += TokenUtils.add_or_replace_before(tokens, i, ImportantWhitespace(' ' * p.switch_case_indent))

            elif switch_block and token.value == '}':
                switch_block = False
                case_block = False

            i += 1

        return tokens

    @staticmethod
    def split_long_lines(tokens: List[Token], p: Properties, errors: List) -> List[Token]:

        if not p.split_long_lines:
            return tokens

        i = 0
        split_index = None
        current_line_length = 0
        line_start_column = 0

        brackets_split = False
        brackets_start_column = None

        while i < len(tokens):
            token = tokens[i]

            if split_index is not None and current_line_length > p.preferred_line_length:
                if brackets_split:
                    current_line_length = brackets_start_column
                    i += TokenUtils.add_or_replace_before(tokens, split_index,
                                                          Whitespace(' ' * brackets_start_column))
                else:
                    current_line_length = line_start_column + p.split_indent
                    i += TokenUtils.add_or_replace_before(tokens, split_index,
                                                          Whitespace(' ' * (line_start_column + p.split_indent)))

                i += TokenUtils.add_or_replace_before(tokens, split_index, LineBreak('\n'))
                current_line_length -= 1
                split_index = None

            if token.value in ['.', '::']:
                split_index = i
            elif token.value in [',']:
                split_index = i + 1

            elif not brackets_split and token.value == '(':
                brackets_split = True
                brackets_start_column = current_line_length
            elif token.value == ')':
                brackets_split = False

            elif current_line_length == 0 and isinstance(token, Whitespace):
                line_start_column = len(token.value)

            elif isinstance(token, LineBreak):
                if brackets_split:
                    TokenUtils.add_or_replace_after(tokens, i, Whitespace(' ' * (brackets_start_column + 1)))
                current_line_length = -len(token.value)
                split_index = None

            current_line_length += len(token.value)
            i += 1

        return tokens
