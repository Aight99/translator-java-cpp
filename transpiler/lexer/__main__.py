import sys
from pathlib import Path
from transpiler.lexer.lexer import Lexer
from transpiler.constants import Tag, LEXER_RULES


filepath = sys.argv[1]
code = Path(filepath).read_text()

lexer = Lexer(Tag, LEXER_RULES, filepath)
lexer.buffer = code

print(list(lexer.tokens))
