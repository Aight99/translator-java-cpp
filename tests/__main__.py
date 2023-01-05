import logging
from unittest import TestCase, main
from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.semantixer.semantixer import SemanticAnalyzer, SemanticError

logger = logging.getLogger(__name__)


class SemantixerTestCase(TestCase):
    def check_correct(self, code):
        filepath = '../example/grammar.txt'
        self.grammar = Grammar.load_grammar(filepath)
        self.lexer = Lexer(Tag, LEXER_RULES, filepath)
        self.semantixer = SemanticAnalyzer()

        self.lexer.buffer = code
        tokens = list(self.lexer.tokens)
        earley = EarleyParse(tokens, self.grammar)
        tree = earley.get_parse_tree()
        is_correct = self.semantixer.is_correct(tree)
        return is_correct

    def check_wrong(self, code, err=SemanticError, msg=None):
        filepath = '../example/grammar.txt'
        self.grammar = Grammar.load_grammar(filepath)
        self.lexer = Lexer(Tag, LEXER_RULES, filepath)
        self.semantixer = SemanticAnalyzer()

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

    def test_multiple_function_declaration(self):
        self.check_correct("""
            public class Main
            {
                public static void plus(int a, int b, int c) {
                    System.out.println(a + b + c);
                }
                
                public static void plus(int a, int b) {
                    System.out.println(a + b);
                }
                
                public static void main(String[] args) {
                   int a;
                   int b;
                   a = 5;
                   int k;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a, int b) {
                    System.out.println(a + b);
                }
                
                public static void plus(int a, int b) {
                    System.out.println(a + b);
                }
                
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

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a, int b) {
                    System.out.println(a);
                }
            
                public static void main(String[] args) {
                    plus(c, e);
                    int c = 10;
                    int e = 5;
                    System.out.println(e);
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

    def test_wrong_type(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    char a = true;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = true;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5.0;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean a = 'a';
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean a = 5;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean a = 5.0;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5;
                    char b = a;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5;
                    boolean b = a;
                }
            }
        """)


# Correct tests
'''
public class Main
{
    public static void main(String[] args) {
       for (int i = 0; 5 > 0; ) {
           System.out.print(i);
       }
    }
}
'''

# Wrong tests
'''

'''

if __name__ == '__main__':
    main()
