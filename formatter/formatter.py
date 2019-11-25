from typing import Optional

from lexer.token import *
from util.util import Properties


class Formatter:

    @staticmethod
    def reformat_tokens(tokens, p: Properties):
        indent = 0
        closed_block = False
        ident_last = False

        output = list()

        for token in tokens:
            if closed_block:
                closed_block = False
                indent -= p.indent

                output.append('\n')
                output.append(' ' * indent)
                output.append('}')

                if isinstance(token, (Literal, Keyword, Identifier)):
                    output.append('\n')
                    output.append(' ' * indent)

            if token.value == '{':
                indent += p.indent
                output.append(' {\n')
                output.append(' ' * indent)

            elif token.value == '}':
                closed_block = True

            elif token.value == ',':
                output.append(', ')

            elif isinstance(token, (Literal, Keyword, Identifier)):
                if ident_last:
                    # If the last token was a literla/keyword/identifer put a space in between
                    output.append(' ')
                ident_last = True
                output.append(token.value)

            elif isinstance(token, Operator):
                output.append(' ' + token.value + ' ')

            elif token.value == ';':
                output.append(';\n')
                output.append(' ' * indent)

            else:
                output.append(token.value)

            ident_last = isinstance(token, (Literal, Keyword, Identifier))

        if closed_block:
            output.append('\n}')

        output.append('\n')

        return ''.join(output)
