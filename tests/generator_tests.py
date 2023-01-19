import logging
import unittest
from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.semantixer.semantixer import SemanticAnalyzer
from transpiler.generator.generator import Generator

logger = logging.getLogger(__name__)


class GeneratorTestCase(unittest.TestCase):

    def check_generator(self, code, valid_cpp):
        filepath = '../example/grammar.txt'
        self.grammar = Grammar.load_grammar(filepath)
        self.lexer = Lexer(Tag, LEXER_RULES, filepath)
        self.semantixer = SemanticAnalyzer()
        self.lexer.buffer = code
        tokens = list(self.lexer.tokens)
        earley = EarleyParse(tokens, self.grammar)
        tree = earley.get_parse_tree()
        # semantixer = SemanticAnalyzer()
        # if semantixer.is_correct(tree):
        #     generator = Generator()
        #     generated_code = generator.generate_code(tree)
        #     self.assertEqual(generated_code, valid_cpp)
        generator = Generator()
        generated_code = generator.generate_code(tree)
        self.assertEqual(generated_code, valid_cpp)

    def test_var(self):
        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        char a = 'b';
        a = 'a';
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    char a = 'b';
    a = 'a';
}
""")

        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        int i1 = 5;
        int i2 = (2 + i1) * ((10 - 2) / 5) % 3;
        float f1 = 5;
        float f2 = f1 / 2;
        double d1 = 5.5;
        double d2 = d1 - 2.15;
        char c1 = 'a';
        char c2 = c1 + 'b';
		boolean b1 = true;
		boolean b2 = !((true || false) && (5 == 2) || (2.5 < 5.1) || ('a' <= 'c') && !(i1 > i2) && (f2 >= f1) || (c1 != 'a'));
        System.out.println(i1 + 5);
    }
}""", """#include <iostream>

void main(int argc, char *argv[])
{
    int i1 = 5;
    int i2 = (2 + i1) * ((10 - 2) / 5) % 3;
    float f1 = 5;
    float f2 = f1 / 2;
    double d1 = 5.5;
    double d2 = d1 - 2.15;
    char c1 = 'a';
    char c2 = c1 + 'b';
    bool b1 = true;
    bool b2 = !((true || false) && (5 == 2) || (2.5 < 5.1) || ('a' <= 'c') && !(i1 > i2) && (f2 >= f1) || (c1 != 'a'));
    std::cout << i1 + 5 << "\\n";
}
""")

    def test_for(self):
        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            System.out.println(i);
        }
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    for (int i = 0; i < 5; i++)
    {
        std::cout << i << "\\n";
    }
}
""")

        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        for (int i = 0; i < 5; i = i + 2) {
            System.out.println(i);
        }
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    for (int i = 0; i < 5; i = i + 2)
    {
        std::cout << i << "\\n";
    }
}
""")

        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            for (int j = (5 - i) * 2; j >= 0; j--) {
                System.out.println(i);
                System.out.println(j);
            }
        }
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    for (int i = 0; i < 5; i++)
    {
        for (int j = (5 - i) * 2; j >= 0; j--)
        {
            std::cout << i << "\\n";
            std::cout << j << "\\n";
        }
    }
}
""")

    def test_while(self):
        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        int i = 0;
        while (i < 5) {
            System.out.println(i);
            i++;
        }
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    int i = 0;
    while (i < 5)
    {
        std::cout << i << "\\n";
        i++;
    }
}
""")

        self.check_generator("""
public class Main
{
        public static void main(String[] args) {
            int i = 0;
            while (i < 5) {
                double j = 2.5;
                while (i + j > 0) {
                    System.out.println(i + j);
                    j -= 0.5;
                }
                i++;
            }
        }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    int i = 0;
    while (i < 5)
    {
        double j = 2.5;
        while (i + j > 0)
        {
            std::cout << i + j << "\\n";
            j -= 0.5;
        }
        i++;
    }
}
""")

    def test_do_while(self):
        self.check_generator("""
public class Main
{
        public static void main(String[] args) {
            int i = 0;
            do {
                System.out.println(i);
                i++;
            }
            while (i < 5);
        }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    int i = 0;
    do
    {
        std::cout << i << "\\n";
        i++;
    }
    while (i < 5);
}
""")

    def test_if(self):
        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        if (true) {
            System.out.println(true);
        }
        int a = 5;
        if (a < 10) {
            a *= 2;
        } else {
            a /= 2;
        }
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    if (true)
    {
        std::cout << true << "\\n";
    }
    int a = 5;
    if (a < 10)
    {
        a *= 2;
    }
    else
    {
        a /= 2;
    }
}
""")

        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        if (true) {
            for (int i = 1; i < 7; i *= 2) {
                if (i < 5) {
                    int a = i;
                }
            }
        }
        else {
            int a = 10;
        }
    }
}
""", """#include <iostream>

void main(int argc, char *argv[])
{
    if (true)
    {
        for (int i = 1; i < 7; i *= 2)
        {
            if (i < 5)
            {
                int a = i;
            }
        }
    }
    else
    {
        int a = 10;
    }
}
""")

    def test_user_func(self):
        self.check_generator("""
    public class Main
    {
        public static void plus_print(int a, int b, int c) {
            System.out.println(a + b + c);
        }
        public static float plus_float(float a, float b) {
            return a + b;
        }
        public static double plus_double(double a, double b) {
            float sum = 0;
            for (int i = 0; i < 3; i++) {
                sum += a + b;
            }
            return sum;
        }
        public static int cool_func(int a, double b) {
            if (b == 2.5) {
                a *= 2;
            }
            else {
                a += 15;
            }
            return a;
        }
        public static void main(String[] args) {
            int i1 = 5;
            double d1 = 2.1;
            int i2 = cool_func(i1, d1);
            plus_print(i1, i2, 5);
            d1 = plus_double(4.5, d1);
            System.out.println(plus_float(2, 6));
        }
    }
""", """#include <iostream>

void plus_print(int a, int b, int c)
{
    std::cout << a + b + c << "\\n";
}

float plus_float(float a, float b)
{
    return a + b;
}

double plus_double(double a, double b)
{
    float sum = 0;
    for (int i = 0; i < 3; i++)
    {
        sum += a + b;
    }
    return sum;
}

int cool_func(int a, double b)
{
    if (b == 2.5)
    {
        a *= 2;
    }
    else
    {
        a += 15;
    }
    return a;
}

void main(int argc, char *argv[])
{
    int i1 = 5;
    double d1 = 2.1;
    int i2 = cool_func(i1, d1);
    plus_print(i1, i2, 5);
    d1 = plus_double(4.5, d1);
    std::cout << plus_float(2, 6) << "\\n";
}
""")

    def test_default_func(self):
        self.check_generator("""
public class Main
{
    public static void main(String[] args) {
        boolean b = true;
        int i = 5;
        System.out.println(5);
        System.out.println(b);
        System.out.println(Math.max(i, 5));
        i = Math.min(i, 2);
    }
}
        """, """#include <iostream>

void main(int argc, char *argv[])
{
    bool b = true;
    int i = 5;
    std::cout << 5 << "\\n";
    std::cout << b << "\\n";
    std::cout << std::max(i, 5) << "\\n";
    i = std::min(i, 2);
}
""")

if __name__ == '__main__':
    unittest.main()
