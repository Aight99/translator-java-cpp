import sys

from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.generator.generator import Generator


def main():
    filepath = '../../example/grammar.txt'
    grammar = Grammar.load_grammar(filepath)

    with open('../../example/text.txt') as f:
        document = f.read()
    lexer = Lexer(Tag, LEXER_RULES, filepath)
    lexer.buffer = document
    tokens = list(lexer.tokens)

    earley = EarleyParse(tokens, grammar)
    parse = earley.get_parse_tree()

    generator = Generator()
    code = generator.generate_code(parse)
    print(code)


if __name__ == '__main__':
    main()
