from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.semantixer.semantixer import SemanticAnalyzer


def main():
    filepath = '../../example/grammar.txt'
    grammar = Grammar.load_grammar(filepath)
    # print(grammar)

    with open('../../example/semantic.txt') as f:
        document = f.read()
    lexer = Lexer(Tag, LEXER_RULES, filepath)
    lexer.buffer = document
    tokens = list(lexer.tokens)

    earley = EarleyParse(tokens, grammar)
    parse = earley.get_parse_tree()

    semantixer = SemanticAnalyzer()
    print(semantixer.get_tree_labels(parse))
    print(semantixer.is_correct(parse))


if __name__ == '__main__':
    main()
