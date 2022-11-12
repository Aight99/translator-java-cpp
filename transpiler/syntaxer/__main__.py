import sys

from transpiler.syntaxer.earley import Grammar, EarleyParse


def main():
    filepath = sys.argv[1]
    grammar = Grammar.load_grammar(filepath)
    # print(grammar)

    with open('../../example/text.txt') as f:
        sentence = f.read()

    earley = EarleyParse(sentence, grammar)
    earley.parse()
    parse = earley.get_parse()
    print(earley.chart)

    if parse is None:
        print(sentence + ' is None :c \n')
    else:
        parse.pretty_print()


if __name__ == '__main__':
    main()
