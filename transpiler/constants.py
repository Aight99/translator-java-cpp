import string

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
    CHAR = 'char'
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
    MAX = 'max'
    MIN = 'min'
    STATIC = 'static'
    CLASS = 'class'
    PUBLIC = 'public'
    PRINT = 'print'
    MAIN = 'main'
    VOID = 'void'
    STRING = 'string_args'
    INCREMENT = 'increment'
    RETURN = 'return'


LEXER_RULES = [
    LexerRule(Tag.TYPE_HINT, r'\bint|boolean|float|double|char\b'),
    LexerRule(Tag.OP_ASSIGN, r'\+=|\-=|\*=|/=|\%='),
    LexerRule(Tag.INCREMENT, r'\+\+|\-\-'),
    LexerRule(Tag.MATH_OPERATOR, r'\*|/|\%|\+|\-'),
    LexerRule(Tag.COMPARE, r'==|\!=|\<=|\<|\>=|\>'),
    LexerRule(Tag.NUMBER_FLOAT, r'[\-\+]?\d+\.\d+'),
    LexerRule(Tag.BOOLEAN_OPERATOR, r'\&\&|\|\|'),
    LexerRule(Tag.NUMBER_INT, r'[\-\+]?\d+'),

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
    LexerRule(Tag.VOID, r'\bvoid\b'),
    LexerRule(Tag.RETURN, r'\breturn\b'),
    LexerRule(Tag.STRING, r'\bString\[\]\sargs\b'),

    LexerRule(Tag.LBRACKET, r'\('),
    LexerRule(Tag.RBRACKET, r'\)'),
    LexerRule(Tag.RBRACKET_CURLY, r'\}'),
    LexerRule(Tag.LBRACKET_CURLY, r'\{'),
    LexerRule(Tag.LBRACKET_SQUARE, r'\['),
    LexerRule(Tag.RBRACKET_SQUARE, r'\]'),
    LexerRule(Tag.SEMICOLON, r';'),
    LexerRule(Tag.COMMA, r','),
    LexerRule(Tag.DOT, r'\.'),
    LexerRule(Tag.CHAR, r"\'.\'"),

    LexerRule(Tag.ID, r'\b[_a-zA-Z]\w*\b'),
]

VARIABLE_TYPES = ['int', 'byte', 'short', 'long', 'float', 'char', 'boolean', 'double', 'String']
LETTERS = list(string.ascii_letters) + ['_']
KEYWORDS = VARIABLE_TYPES + 'class do else for if public return static while'.split(' ')


class Label(Symbol):
    def __eq__(self, other) -> bool:
        if str(self.value) == other:
            return True
        return False

    FUNC_DECL = '<func_declaration>'
    ID = '<id>'
    FUNC_TYPE = '<func_return_type>'
    FUNC_PARAMS = '<function_params>'
    MAIN_FUNC = '<main_func>'
    CODE_BLOCK = '<code_block>'
    FUNC_CALL_PARAMS = '<func_call_params>'
    LBRACKET_CURLY = '<lbracket_curly>'
    RBRACKET_CURLY = '<rbracket_curly>'
    FOR = '<for>'
    ASSIGN = '<assign>'
    INSTRUCTION = '<instruction>'

    MATH_EXPR = '<math_expression>'
    LOGICAL_EXPR = '<logical_expression>'
    CHAR = '<char>'
    NUMBER = '<number>'
    NUMBER_INT = '<number_int>'
    NUMBER_FLOAT = '<number_float>'

    PRINT = '<print>'
    MAX = '<max>'
    MIN = '<min>'

    # Виды инструкций
    ASSIGNMENT = '<assignment>'
    VAR_DECL = '<variable_declaration>'
    FUNC_CALL = '<func_call>'
    EXPR = '<expression>'
    LOOP = '<loop>'
    CONDITION = '<condition>'
    FUNC_RETURN = '<func_return>'
