import logging
import unittest
from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.semantixer.semantixer import SemanticAnalyzer, SemanticError, ErrorMessage, Type

logger = logging.getLogger(__name__)


class SemantixerTestCase(unittest.TestCase):
    def check_correct(self, code):
        filepath = '../example/grammar.txt'
        self.grammar = Grammar.load_grammar(filepath)
        self.lexer = Lexer(Tag, LEXER_RULES, filepath)
        self.semantixer = SemanticAnalyzer()
        self.lexer.buffer = code
        tokens = list(self.lexer.tokens)
        earley = EarleyParse(tokens, self.grammar)
        tree = earley.get_parse_tree()

        self.assertTrue(self.semantixer.is_correct(tree))

    def check_wrong(self, code, msg=None, err=SemanticError):
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
            self.assertEqual(str(error.exception.description), msg)

        logger.info(f"Raised {error.exception}")

    def test_func_multiple_decl(self):
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
        """, ErrorMessage.func_multiple_decl('plus'))

    def test_return_not_exists(self):
        self.check_correct("""
            public class Main
            {
                public static void plus(int a) {
                    int b = a;
                }

                public static void main(String[] args) {
                    int a = 1;
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static int plus(int a) {
                    int b = a;
                }

                public static void main(String[] args) {
                    int a = 1;
                }
            }
        """, ErrorMessage.return_not_exists('plus'))

        self.check_wrong("""
            public class Main
            {
                public static int plus(int a) {
                    if (5 > 0) {
                        return a;
                    }
                }

                public static void main(String[] args) {
                    int a = 1;
                }
            }
        """, ErrorMessage.return_not_exists('plus'))

    def test_unreachable_code(self):
        self.check_wrong("""
            public class Main
            {
                public static int plus(int a) {
                    return a;
                    return 5;
                }

                public static void main(String[] args) {
                    int a = 1;
                }
            }
        """, ErrorMessage.unreachable_code())

        self.check_wrong("""
            public class Main
            {
                public static int plus(int a) {
                    if (5 > 0) {
                        return 5;
                        a = 6;
                    }
                    return 5;
                }

                public static void main(String[] args) {
                    int a = 1;
                }
            }
        """, ErrorMessage.unreachable_code())

    def test_var_no_decl(self):
        self.check_correct("""
            public class Main
            {
                public static void plus(int a) {
                    a = 5;
                }

                public static void main(String[] args) {
                    int a;
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    for (int i = 0; i < 5; i++) {
                        System.out.println(i);
                    } 
                }
            }
        """)

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    a = (a + 1);
                }
            }
        """, ErrorMessage.var_no_decl('a'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    while (5 > 0) {
                        int a;
                    }
                    a = 5;
                }
            }
        """, ErrorMessage.var_no_decl('a'))

        self.check_wrong("""
            public class Main
            {
                public static int plus(int a) {
                    return b;
                }
            
                public static void main(String[] args) {
                }
            }
        """, ErrorMessage.var_no_decl('b'))

        self.check_wrong("""
            public class Main
            {
                public static int plus(int a) {
                    return a + b;
                }

                public static void main(String[] args) {
                }
            }
        """, ErrorMessage.var_no_decl('b'))

        self.check_wrong("""
            public class Main
            {
                public static boolean plus(boolean a) {
                    return a && b;
                }

                public static void main(String[] args) {
                }
            }
        """, ErrorMessage.var_no_decl('b'))

    def test_boolean_op_assign(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean b = true;
                    b += true;
                }
            }
        """, ErrorMessage.boolean_op_assign())

    def test_boolean_increment(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean b = true;
                    b++;
                }
            }
        """, ErrorMessage.boolean_increment())

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean b = true;
                    --b;
                }
            }
        """, ErrorMessage.boolean_increment())

    def test_var_no_init(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a;
                    a++;
                }
            }
        """, ErrorMessage.var_no_init('a'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a;
                    a = a + 5;
                }
            }
        """, ErrorMessage.var_no_init('a'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a;
                    a += 5;
                }
            }
        """, ErrorMessage.var_no_init('a'))

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a) {
                    a = 6;
                }
                public static void main(String[] args) {
                    int a;
                    plus(a);
                }
            }
        """, ErrorMessage.var_no_init('a'))

    def test_func_void_return(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    return a;
                }
            }
        """, ErrorMessage.func_void_return('main'))

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a) {
                    return a;
                }

                public static void main(String[] args) {
                    int a;
                }
            }
        """, ErrorMessage.func_void_return('plus'))

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a) {
                    if (5 > 0) {
                        return a;
                    }
                }

                public static void main(String[] args) {
                    int a;
                }
            }
        """, ErrorMessage.func_void_return('plus'))

    def test_var_multiple_decl(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int i = 0;
                    for (int i = 0; i < 5; i++) {
                        System.out.println(i);
                    } 
                }
            }
        """, ErrorMessage.var_multiple_decl('i'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a;
                    if (5 > 0) {
                        int a = 5;
                    }
                }
            }
        """, ErrorMessage.var_multiple_decl('a'))

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a) {
                    int a = 5;
                }

                public static void main(String[] args) {
                    int a;
                }
            }
        """, ErrorMessage.var_multiple_decl('a'))

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a) {
                    a = 5;
                }

                public static void main(String[] args) {
                    int a;
                    a = 0;
                    int a;
                }
            }
        """, ErrorMessage.var_multiple_decl('a'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    for (int i = 0; i < 5; i++) {
                        int i = i;
                    }
                }
            }
        """, ErrorMessage.var_multiple_decl('i'))

        self.check_correct("""
        public class Main
        {
            public static void main(String[] args) {
                if (5 == 5) {
                    int a = 5;
                }
                if (6 == 6) {
                    int a = 5;
                }
            }
        }
        """)

    def test_boolean_var_math_expr(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    boolean b = true;
                    int a = b + 5;
                }
            }
        """, ErrorMessage.boolean_var_math_expr('b'))

    def test_types_not_fit(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int b = 5;
                    char a = b;
                }
            }
        """, ErrorMessage.types_not_fit(Type.INT.name, Type.CHAR.name))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    char a = 65600;
                }
            }
        """, ErrorMessage.types_not_fit(Type.INT.name, Type.CHAR.name))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    double b = 5;
                    float a = b;
                }
            }
        """, ErrorMessage.types_not_fit(Type.DOUBLE.name, Type.FLOAT.name))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    float b = 5;
                    int a = b;
                }
            }
        """, ErrorMessage.types_not_fit(Type.FLOAT.name, Type.INT.name))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5.0;
                }
            }
        """, ErrorMessage.types_not_fit(Type.DOUBLE.name, Type.INT.name))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    int a = 5f;
                }
            }
        """, ErrorMessage.types_not_fit(Type.FLOAT.name, Type.INT.name))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    float a = 5.0;
                }
            }
        """, ErrorMessage.types_not_fit(Type.DOUBLE.name, Type.FLOAT.name))

        self.check_wrong("""
            public class Main
            {
                public static int plus(int a, double b) {
                    return a + b;
                }
                
                public static void main(String[] args) {
                    plus(2, 2.0);
                }
            }
        """, ErrorMessage.types_not_fit(Type.DOUBLE.name, Type.INT.name))

    def test_func_no_decl(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    plus(5, 6);
                }
            }
        """, ErrorMessage.func_no_decl('plus'))

        self.check_wrong("""
            public class Main
            {
                public static void plus(int a) {
                    a = 5;
                }

                public static void main(String[] args) {
                    plus(5, 6);
                }
            }
        """, ErrorMessage.func_no_decl('plus'))

    def test_func_params_mismatch(self):
        self.check_wrong("""
            public class Main
            {
                public static void plus(int a, boolean b) {
                }
                
                public static void main(String[] args) {
                    plus(5, 5);
                }
            }
        """, ErrorMessage.func_params_mismatch('plus'))

    def test_func_ambiguous(self):
        self.check_wrong("""
            public class Main
            {
                public static int plus(int a, double b) {
                    return 5;
                }
                public static int plus(double a, int b) {
                    return 6;
                }
                public static void main(String[] args) {
                    System.out.println(plus('a', 'a'));
                }
            }
        """, ErrorMessage.func_ambiguous('plus'))

        self.check_correct("""
            public class Main
            {
                public static int plus(int a, double b) {
                    return 5;
                }
                public static int plus(double a, int b) {
                    return 6;
                }
                public static void main(String[] args) {
                    System.out.println(plus('a', 5.0));
                }
            }
        """)

    def test_inbuilt_func(self):
        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    System.out.println('a', 5);
                }
            }
        """, ErrorMessage.func_params_mismatch('System.out.println'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    Math.max(true, 5);
                }
            }
        """, ErrorMessage.types_not_fit(Type.BOOLEAN.name, 'NUMBER'))

        self.check_wrong("""
            public class Main
            {
                public static void main(String[] args) {
                    Math.min(1, 2, 3);
                }
            }
        """, ErrorMessage.func_params_mismatch('Math.min'))

        self.check_correct("""
            public class Main
            {
                public static void main(String[] args) {
                    System.out.println();
                    System.out.println('a');
                    System.out.println(5);
                    System.out.println(5.0);
                    System.out.println(true);
                    System.out.println('a' + 'a');
                    System.out.println('a' == 'a');
            
                    char var_char;
                    int var_int;
                    double var_double;
            
                    var_char = Math.max('a', 'a');
                    var_int = Math.max('a', 5);
                    var_double = Math.max('a', 5.0);
                    var_int = Math.max(5, 5);
                    var_double = Math.max(5, 5.0);
                    var_double = Math.max(5.0, 5.0);
            
                    var_char = Math.min('a', 'a');
                    var_int = Math.min('a', 5);
                    var_double = Math.min('a', 5.0);
                    var_int = Math.min(5, 5);
                    var_double = Math.min(5, 5.0);
                    var_double = Math.min(5.0, 5.0);
                }
            }
        """)

    def test_correct_mega_test(self):
        self.check_correct("""
            public class Main
            {
                public static int plus(int a, int b) {
                    return a + b;
                }

                public static void main(String[] args) {
                    int a = 5;
                    char b = 'a';
                    double c = plus(a, b);
                    main();
                    
                    for (int i = 0; i < 5; i++) {
                        int d = 4;
                    }
                    
                    for (int i = 0; i < 5; i++) {
                        int d = 3;
                    }
                }
                
                public static void main() {
                    System.out.println(1 + 2 + 3);
                }
            }
        """)

        self.check_correct("""
            public class Main
            {
                public static void printHello() {
                    System.out.println('h');
                    System.out.println('e');
                    System.out.println('l');
                    System.out.println('o');
                }
            
                public static int plus(int a, int b) {
                    return a + b;
                }
            
                public static boolean isLegit() {
                    boolean a = true;
                    boolean b = true;
                    boolean c = false;
                    boolean d = true;
                    boolean result = (!a && b) && !(c || d);
                    return result;
                }
            
                public static void main(String[] args) {
                    printHello();
                    if (true) {
                        System.out.println('#');
                        doRecursion(5);
                    }
                    {
                        char c = 'a';
                        for (float i = doMath(4, 3, 5f, true); i < doMath(4, 3, 5f, false); ++i) {
                            float j = i;
                            while (j < i + 6) {
                                j++;
                                System.out.println(c);
                                c += 1;
                            }
                        }
                    }
                    char c = '$';
                    System.out.println(c);
            
                    if (isLegit() || 10 <= 11 && 5 >= 14 || 10 == 10 && 10 != 10) {
                        System.out.println(1);
                    } else {
                        System.out.println(0);
                    }
                }
            
                public static float doMath(int a, int b, float c, boolean d) {
                    if (d) {
                        return Math.min(a, b) / c;
                    }
                    c *= 2;
                    c /= 2;
                    c %= 10000000;
                    return c * Math.max(b, a);
                }
            
                public static int doRecursion(int a) {
                    if (a > 0) {
                        printHello();
                        doRecursion(a - 1);
                    }
                    return 0;
                }
            }
        """)


if __name__ == '__main__':
    unittest.main()
