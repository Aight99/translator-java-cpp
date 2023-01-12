from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.generator.generator import Generator

import os


def compiler(app):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], 'grammar.txt')
    grammar = Grammar.load_grammar(filepath)

    with open(os.path.join(app.config["UPLOAD_FOLDER"], 'text.txt')) as f:
        document = f.read()
    lexer = Lexer(Tag, LEXER_RULES, filepath)
    lexer.buffer = document
    tokens = list(lexer.tokens)

    earley = EarleyParse(tokens, grammar)
    parse = earley.get_parse_tree()

    generator = Generator()
    code = generator.generate_code(parse)
    return code
