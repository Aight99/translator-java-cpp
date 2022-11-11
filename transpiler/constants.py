from transpiler.base import Symbol, Terminal, LexerRule
import re

WHITESPACE = re.compile('\S')
LEXER_REGEX_FLAGS = re.IGNORECASE



class Special(Symbol):
    LAMBDA = '__LAMBDA__'
    START = '__START__'
    LIMITER = '__LIMITER__'


class Tag(Terminal):
    ID = 'id'
    NUMBER_INT = 'number_int'
    NUMBER_FLOAT = 'number_float'
    LBRACKET = 'lbracket'
    RBRACKET = 'rbracket'
    LBRACKET_SQUARE = 'lbracket_square'
    RBRACKET_SQUARE = 'rbracket_square'
    RBRACKET_CURLY = 'rbracket_curly'
    LBRACKET_CURLY = 'lbracket_curly'
    SEMICOLON = 'semicolon'
    COMMA = 'comma'
    DOT = 'dot'
    QUOTE = "quote"
    DOUBLE_QUOTE = "double_quote"
    TYPE_HINT = 'type_hint'
    COMPARE = 'compare'
    MATH_OPERATOR = 'math_operator'
    BOOLEAN_OPERATOR = 'boolean_operator'
    BOOLEAN_NOT = 'boolean_not'
    ASSIGN = 'assign'
    OP_ASSIGN = 'op_assign'
    BOOLEAN_VALUE = 'boolean_value'

    IF = 'if'
    ELSE = 'else'
    FOR = 'for'
    WHILE = 'while'
    DO = 'do'
    VOID = 'void'
    MAX = 'max'
    MIN = 'min'
    STATIC = 'static'
    CLASS = 'class'
    PUBLIC = 'public'
    PRINT = 'print'
    MAIN = 'main'


LEXER_RULES = [
    LexerRule(Tag.TYPE_HINT, r'\bint|boolean|float|double|char|void\b'),
    LexerRule(Tag.MATH_OPERATOR, r'\+\+|\-\-|\*|/|\%|\+|\-'),
    LexerRule(Tag.COMPARE, r'==\!=|\<=|\<|\>=|\>'),
    LexerRule(Tag.NUMBER_FLOAT, r'[\-\+]?\d+\.\d+'),
    LexerRule(Tag.BOOLEAN_OPERATOR, r'\&\&|\|\|'),
    LexerRule(Tag.NUMBER_INT, r'[\-\+]?\d+'),

    LexerRule(Tag.OP_ASSIGN, r'\+=|\-=|\*=|/=|\%='),
    LexerRule(Tag.BOOLEAN_NOT, r'\!'),
    LexerRule(Tag.ASSIGN, r'='),
    LexerRule(Tag.BOOLEAN_VALUE, r'\btrue|false\b'),
    LexerRule(Tag.IF, r'\bif\b'),
    LexerRule(Tag.ELSE, r'\belse\b'),
    LexerRule(Tag.FOR, r'\bfor\b'),
    LexerRule(Tag.WHILE, r'\bwhile\b'),
    LexerRule(Tag.DO, r'\bdo\b'),
    LexerRule(Tag.MAX, r'\bMath\.max\b'),
    LexerRule(Tag.MIN, r'\bMath\.min\b'),

    LexerRule(Tag.STATIC, r'\bstatic\b'),
    LexerRule(Tag.CLASS, r'\bclass\b'),
    LexerRule(Tag.PUBLIC, r'\bpublic\b'),
    LexerRule(Tag.PRINT, r'\bSystem\.out\.println\b'),
    LexerRule(Tag.MAIN, r'\bMain|main\b'),

    LexerRule(Tag.LBRACKET, r'\('),
    LexerRule(Tag.RBRACKET, r'\)'),
    LexerRule(Tag.RBRACKET_CURLY, r'\}'),
    LexerRule(Tag.LBRACKET_CURLY, r'\{'),
    LexerRule(Tag.LBRACKET_SQUARE, r'\['),
    LexerRule(Tag.RBRACKET_SQUARE, r'\]'),
    LexerRule(Tag.SEMICOLON, r';'),
    LexerRule(Tag.COMMA, r','),
    LexerRule(Tag.DOT, r'\.'),
    LexerRule(Tag.QUOTE, r"\'"),
    LexerRule(Tag.DOUBLE_QUOTE, r'\"'),

    LexerRule(Tag.ID, r'\b[_a-zA-Z]\w*\b'),
]
