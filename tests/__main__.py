import logging
from unittest import TestCase, main
from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.semantixer.semantixer import SemanticAnalyzer, SemanticError

logger = logging.getLogger(__name__)


class SemantixerTestCase(TestCase):
    def setUp(self) -> None:
        filepath = '../example/grammar.txt'
        self.grammar = Grammar.load_grammar(filepath)
        self.lexer = Lexer(Tag, LEXER_RULES, filepath)
        self.semantixer = SemanticAnalyzer()

    def check_correct(self, code):
        self.lexer.buffer = code
        tokens = list(self.lexer.tokens)
        earley = EarleyParse(tokens, self.grammar)
        tree = earley.get_parse_tree()
        is_correct = self.semantixer.is_correct(tree)
        return is_correct

    def check_wrong(self, code, err=SemanticError, msg=None):
        self.lexer.buffer = code
        tokens = list(self.lexer.tokens)
        earley = EarleyParse(tokens, self.grammar)
        tree = earley.get_parse_tree()
        with self.assertRaises(err) as error:
            self.semantixer.is_correct(tree)
        if msg is not None:
            self.assertEqual(str(error.exception), msg)

        logger.info(f"Raised {error.exception}")

    def test_example(self):
        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                   int a;
                   int b;
                   a = 5;
                   int k;
                }
            }
        """)

    def test_multiple_declaration(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 1;
                    int a = 2;
                }
            }
        """)

    def test_no_init(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    a = (a + 1);
                }
            }
        """)


if __name__ == '__main__':
    main()
