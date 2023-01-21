import unittest
from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse, SyntaxAnalyzerError


class SyntaxerExceptionsTestCase(unittest.TestCase):
    def init_test(self, text):
        filepath = '../example/grammar.txt'
        self.grammar = Grammar.load_grammar(filepath)
        self.lexer = Lexer(Tag, LEXER_RULES, filepath)
        self.lexer.buffer = text
        self.tokens = list(self.lexer.tokens)

    def check_correct(self, text):
        self.init_test(text)
        earley = EarleyParse(self.tokens, self.grammar)

        self.assertTrue(earley.get_parse_tree())

    def check_wrong(self, text, msg=None, err=SyntaxAnalyzerError):
        self.init_test(text)
        earley = EarleyParse(self.tokens, self.grammar)

        with self.assertRaises(err) as error:
            earley.get_parse_tree()

        if msg is not None:
            self.assertEqual(str(error.exception.message), msg)

    def test_math_expr(self):
        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                   int a = 5;
                   a = (a + 10) * 2 / 16 + 'a';
                }
            }
        """)

    def test_cycle(self):
        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    int n = 5;
                    int i = 0;
                    while (i < n) {
                        i += 1;
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    int n = 5;
                    int i = 0;
                    do {
                        i++;
                    } while (i < n);
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (int i = 1; i <= 2; i++) {
                        int j = 1;
                        for (j = 1; j <= 3; j++) {
                        }
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (int i = 1; i <= 2;) {
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (; i <= 2;) {
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (;;) {
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (;;i++) {
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (int i = 5;;) {
                    }
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    for (;;;) {
                    }
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    while (;) {
                    }
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    while () {
                    }
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    do {
                    } while ();
                }
            }
        """)

    def test_statements(self):
        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5;
                    fun(a, a);
                    for (int i = 0; i < a; i++) {
                        i++;
                    }
                    if (true) {
                        return 0;
                    }
                    return 1;
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    ;;;;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                   a + b;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                   5 * 3;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                   a && b;
                }
            }
        """)

    def test_bool_expr(self):
        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5; int b = 6;
                    if (5 != 5) {
                        a += b;
                    } else {
                        return b;
                    }
                    return a;
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5;
                    if (a == 5) {
                        System.out.println(a);
                    }
                    int b = 6;
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean a = true;
                    boolean b = false;
                    System.out.println(a && b);
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    if (isLegit() || 10 <= 11 && 5 >= 14 && isLegit() || 10 == 10 && 10 != 10) {
                        System.out.println(1);
                    } else {
                        System.out.println(0);
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    if (a) {
                        System.out.println(1);
                    }
                }
            }
        """)

    def test_user_functions_declaration(self):
        # Несколько функций
        self.check_correct("""
            public class Main
            {
                public static int plus(int a, int b, int c) {
                    return a + b + c;
                }

                public static int plus(int a, int b) {
                    return a + b;
                }

                public static void main(String[] args) {
                   int a;
                }
            }
        """)

        # Функции по обе стороны от main
        self.check_correct("""
            public class Main
            {
                public static int plus(int a, int b, int c) {
                    return a + b + c;
                }

                public static void main(String[] args) {
                   int a;
                }

                public static int plus(int a, int b) {
                    return a + b;
                }
            }
        """)

        # Объявлен main с другой сигнатурой
        self.check_correct("""
            public class Main
            {
                public static int main(int a, int b) {
                    return a + b + c;
                }

                public static void main(String[] args) {
                   main(5, 6);
                }
            }
        """)

    def test_brackets(self):
        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5;
                    {
                    }
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    {
                    }
                    int a = 1;
                }
            }
        """)

    def test_structure(self):
        self.check_wrong("""
            public class Class
            {
                public static void main(String[] args) {
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void mainFunc(String[] args) {
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main() {
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(int args) {
                }
            }
        """)

        self.check_wrong("""
            public static void main(String[] args) {
            }
        """)


if __name__ == '__main__':
    unittest.main()
