from lexer.token import *


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
    def add_or_replace_before(tokens, i, *tokens_to_add):
        shift = 0
        for token_to_add in reversed(tokens_to_add):
            if i > 0 and type(tokens[i - 1]) is type(token_to_add):
                tokens[i - 1] = token_to_add
                i -= 1
            else:
                tokens.insert(i, token_to_add)
                shift += 1
        return shift

    @staticmethod
    def add_or_replace_after(tokens, i, *tokens_to_add):
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
        shift = indent - token.position.column + 1

        split = token.value.split('\n')
        result.append(split[0])
        for line in split[1:]:
            if shift < 0:
                result.append(line[-shift:])
            else:
                result.append(line.rjust(len(line) + shift))

        return Comment('\n'.join(result))
