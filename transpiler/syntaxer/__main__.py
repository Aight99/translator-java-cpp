import sys

from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse


def main():
    filepath = sys.argv[1]
    grammar = Grammar.load_grammar(filepath)

    with open('../../example/text.txt') as f:
        document = f.read()
    lexer = Lexer(Tag, LEXER_RULES, filepath)
    lexer.buffer = document
    tokens = list(lexer.tokens)
    print(tokens)

    earley = EarleyParse(tokens, grammar)
    parse = earley.get_parse_tree()

    if parse is None:
        print('Синтакс ерор :c \n')
    else:
        parse.pretty_print()
        # print("Done")


if __name__ == '__main__':
    main()
