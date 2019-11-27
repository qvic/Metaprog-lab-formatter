from util.util import Representable


class Token(Representable):
    __slots__ = ('value', 'position')

    def __init__(self, value, position=None):
        self.value = value
        self.position = position

    def __eq__(self, other: object) -> bool:
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class Whitespace(Token):
    pass


class LineBreak(Token):
    pass


class Comment(Token):
    pass


class EndOfInput(Token):
    pass


class Keyword(Token):
    VALUES = ('abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue',
              'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'goto', 'if',
              'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new', 'package', 'private',
              'protected', 'public', 'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this',
              'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while')


class Modifier(Keyword):
    VALUES = ('abstract', 'default', 'final', 'native', 'private', 'protected', 'public', 'static', 'strictfp',
              'synchronized', 'transient', 'volatile')


class BasicType(Keyword):
    VALUES = ('boolean', 'byte', 'char', 'double', 'float', 'int', 'long', 'short')


class Literal(Token):
    pass


class Integer(Literal):
    pass


class DecimalInteger(Literal):
    pass


class OctalInteger(Integer):
    pass


class BinaryInteger(Integer):
    pass


class HexInteger(Integer):
    pass


class FloatingPoint(Literal):
    pass


class DecimalFloatingPoint(FloatingPoint):
    pass


class HexFloatingPoint(FloatingPoint):
    pass


class Boolean(Literal):
    VALUES = ('true', 'false')


class Character(Literal):
    pass


class String(Literal):
    pass


class Null(Literal):
    pass


class Separator(Token):
    VALUES = ('(', ')', '{', '}', '[', ']', ';', ',', '.')


class Operator(Token):
    MAX_LEN = 4
    VALUES = {'>>>=', '>>=', '<<=', '%=', '^=', '|=', '&=', '/=', '*=', '-=', '+=', '<<', '--', '++', '||', '&&', '!=',
              '>=', '<=', '==', '%', '^', '|', '&', '/', '*', '-', '+', ':', '?', '~', '!', '<', '>', '=', '...', '->',
              '::'}

    # '>>>' and '>>' are excluded so that >> becomes two tokens and >>> becomes
    # three. This is done because we can not distinguish the operators >> and
    # >>> from the closing of multipel type parameter/argument lists when
    # lexing. The job of potentially recombining these symbols is left to the
    # parser

    INFIX = ('||', '&&', '|', '^', '&', '==', '!=', '<', '>', '<=', '>=', '<<', '>>', '>>>', '+', '-', '*', '/', '%')

    PREFIX = ('++', '--', '!', '~', '+', '-')

    POSTFIX = ('++', '--')

    ASSIGNMENT = ('=', '+=', '-=', '*=', '/=', '&=', '|=', '^=', '%=', '<<=', '>>=', '>>>=')

    LAMBDA = ('->',)

    METHOD_REFERENCE = ('::',)

    def is_infix(self):
        return self.value in self.INFIX

    def is_prefix(self):
        return self.value in self.PREFIX

    def is_postfix(self):
        return self.value in self.POSTFIX

    def is_assignment(self):
        return self.value in self.ASSIGNMENT


class Annotation(Token):
    pass


class Identifier(Token):
    pass
