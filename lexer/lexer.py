import re
from collections import namedtuple

from .token import *

Position = namedtuple('Position', ['line', 'column'])


class LexerError(Exception):

    def __init__(self, message: str):
        super().__init__(message)


class Lexer:
    whitespace_pattern = re.compile(r'[^\n\S]+')

    def __init__(self, source: str):
        self.source = source
        self.errors = []

        self.current_line = 1
        self.start_of_line = -1

        self.operators = [set() for i in range(0, Operator.MAX_LEN)]

        for v in Operator.VALUES:
            self.operators[len(v) - 1].add(v)

        self.length = len(self.source)
        self.i = 0
        self.j = 0

    def reset(self):
        self.i = 0
        self.j = 0

    @property
    def tokens(self):
        self.reset()

        length = len(self.source)
        while self.i < length:

            current_character = self.source[self.i]
            lookahead = None
            startswith = current_character

            if self.i + 1 < length:
                lookahead = self.source[self.i + 1]
                startswith = current_character + lookahead

            if current_character == '\n':
                self.i += 1
                self.start_of_line = self.i
                self.current_line += 1
                continue

            elif current_character.isspace():
                token_type = Whitespace
                self.read_whitespace()

            elif startswith in ("//", "/*"):
                token_type = Comment
                comment = self.read_comment()

            elif startswith == '..' and self.try_operator():
                token_type = Operator

            elif current_character == '@':
                token_type = Annotation
                self.j = self.i + 1

            elif current_character == '.' and lookahead and lookahead.isdigit():
                token_type = self.read_decimal_float_or_integer()

            elif self.try_separator():
                token_type = Separator

            elif current_character in ("'", '"'):
                token_type = String
                self.read_string()

            elif current_character in '0123456789':
                token_type = self.read_integer_or_float(current_character, lookahead)

            elif self.is_java_identifier_start(current_character):
                token_type = self.read_identifier()

            elif self.try_operator():
                token_type = Operator

            else:
                self.error('Could not process token', current_character)
                self.i = self.i + 1
                continue

            position = Position(self.current_line, self.i - self.start_of_line)
            self.current_line += self.source.count('\n', self.i, self.j)

            token = token_type(self.source[self.i:self.j], position)
            yield token

            self.i = self.j

    def error(self, message, char=None):
        # Provide additional information in the errors message
        line_start = self.source.rfind('\n', 0, self.i) + 1
        line_end = self.source.find('\n', self.i)
        line = self.source[line_start:line_end].strip()

        line_number = self.current_line

        if not char:
            char = self.source[self.j]

        message = '{0} at "{1}", line {2}: {3}'.format(message, char, line_number, line)
        error = LexerError(message)
        self.errors.append(error)

    def read_whitespace(self):
        match = self.whitespace_pattern.search(self.source, self.i)

        if not match:
            return

        i = match.end()

        start_of_line = self.source.rfind('\n', self.i, i)

        if start_of_line != -1:
            self.start_of_line = start_of_line
            self.current_line += self.source.count('\n', self.i, i)

        self.j = i

    def read_string(self):
        delim = self.source[self.i]

        state = 0
        j = self.i + 1
        length = self.length

        while True:
            if j >= length:
                self.error('Unterminated character/string literal')
                break

            if state == 0:
                if self.source[j] == '\\':
                    state = 1
                elif self.source[j] == delim:
                    break

            elif state == 1:
                if self.source[j] in 'btnfru"\'\\':
                    state = 0
                elif self.source[j] in '0123':
                    state = 2
                elif self.source[j] in '01234567':
                    state = 3
                else:
                    self.error('Illegal escape character', self.source[j])

            elif state == 2:
                # Possibly long octal
                if self.source[j] in '01234567':
                    state = 3
                elif self.source[j] == '\\':
                    state = 1
                elif self.source[j] == delim:
                    break

            elif state == 3:
                state = 0

                if self.source[j] == '\\':
                    state = 1
                elif self.source[j] == delim:
                    break

            j += 1

        self.j = j + 1

    def try_operator(self):
        for l in range(min(self.length - self.i, Operator.MAX_LEN), 0, -1):
            if self.source[self.i:self.i + l] in self.operators[l - 1]:
                self.j = self.i + l
                return True
        return False

    def read_comment(self):
        if self.source[self.i + 1] == '/':
            terminator, accept_eof = '\n', True
        else:
            terminator, accept_eof = '*/', False

        i = self.source.find(terminator, self.i + 2)

        if i != -1:
            i += len(terminator)
        elif accept_eof:
            i = self.length
        else:
            self.error('Unterminated block comment')
            partial_comment = self.source[self.i:]
            self.i = self.length
            return partial_comment

        comment = self.source[self.i:i]

        self.start_of_line = self.i
        self.j = i

        return comment

    def read_decimal_float_or_integer(self):
        orig_i = self.i
        self.j = self.i

        self.read_decimal_integer()

        if self.j >= len(self.source) or self.source[self.j] not in '.eEfFdD':
            return DecimalInteger

        if self.source[self.j] == '.':
            self.i = self.j + 1
            self.read_decimal_integer()

        if self.j < len(self.source) and self.source[self.j] in 'eE':
            self.j = self.j + 1

            if self.j < len(self.source) and self.source[self.j] in '-+':
                self.j = self.j + 1

            self.i = self.j
            self.read_decimal_integer()

        if self.j < len(self.source) and self.source[self.j] in 'fFdD':
            self.j = self.j + 1

        self.i = orig_i
        return DecimalFloatingPoint

    def read_hex_integer_or_float(self):
        orig_i = self.i
        self.j = self.i + 2

        self.read_hex_integer()

        if self.j >= len(self.source) or self.source[self.j] not in '.pP':
            return HexInteger

        if self.source[self.j] == '.':
            self.j = self.j + 1
            self.read_digits('0123456789abcdefABCDEF')

        if self.j < len(self.source) and self.source[self.j] in 'pP':
            self.j = self.j + 1
        else:
            self.error('Invalid hex float literal')

        if self.j < len(self.source) and self.source[self.j] in '-+':
            self.j = self.j + 1

        self.i = self.j
        self.read_decimal_integer()

        if self.j < len(self.source) and self.source[self.j] in 'fFdD':
            self.j = self.j + 1

        self.i = orig_i
        return HexFloatingPoint

    def read_digits(self, digits):
        tmp_i = 0
        c = None

        while self.j + tmp_i < len(self.source):
            c = self.source[self.j + tmp_i]

            if c in digits:
                self.j += 1 + tmp_i
                tmp_i = 0
            elif c == '_':
                tmp_i += 1
            else:
                break

        if c in 'lL':
            self.j += 1

    def read_decimal_integer(self):
        self.j = self.i
        self.read_digits('0123456789')

    def read_hex_integer(self):
        self.j = self.i + 2
        self.read_digits('0123456789abcdefABCDEF')

    def read_bin_integer(self):
        self.j = self.i + 2
        self.read_digits('01')

    def read_octal_integer(self):
        self.j = self.i + 1
        self.read_digits('01234567')

    def read_integer_or_float(self, c, c_next):
        if c == '0' and c_next in 'xX':
            return self.read_hex_integer_or_float()
        elif c == '0' and c_next in 'bB':
            self.read_bin_integer()
            return BinaryInteger
        elif c == '0' and c_next in '01234567':
            self.read_octal_integer()
            return OctalInteger
        else:
            return self.read_decimal_float_or_integer()

    def try_separator(self):
        if self.source[self.i] in Separator.VALUES:
            self.j = self.i + 1
            return True
        return False

    def is_java_identifier_start(self, c: str):
        return c.isalpha()

    def read_identifier(self):
        self.j = self.i + 1

        while self.j < len(self.source) and self.source[self.j].isalnum():
            self.j += 1

        ident = self.source[self.i:self.j]
        if ident in Keyword.VALUES:
            token_type = Keyword

            if ident in BasicType.VALUES:
                token_type = BasicType
            elif ident in Modifier.VALUES:
                token_type = Modifier

        elif ident in Boolean.VALUES:
            token_type = Boolean
        elif ident == 'null':
            token_type = Null
        else:
            token_type = Identifier

        return token_type
