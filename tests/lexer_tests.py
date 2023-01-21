import logging
import unittest
from transpiler.constants import Tag, LEXER_RULES
from transpiler.lexer.lexer import Lexer
from transpiler.syntaxer.earley import Grammar, EarleyParse
from transpiler.semantixer.semantixer import SemanticAnalyzer
from transpiler.generator.generator import Generator

logger = logging.getLogger(__name__)


class LexerTestCase(unittest.TestCase):

    def test_math_operation(self):
        code = """
        public class Main
        {
            public static void main(String[] args) {
                int c = 10; c += 15; c -= 10; c*= 5;  c %= 2; c /=5; 
                c = 1 + 3 - 4 / 3 * 2;
                c++;
                c--;
                --c;
                ++c;
            }
        }
        """
        lexer = Lexer(Tag, LEXER_RULES)
        lexer.buffer = code
        tokens = list(lexer.tokens)
        self.assertEqual(tokens[0].tag, Tag.PUBLIC)
        self.assertEqual(tokens[1].tag, Tag.CLASS)
        self.assertEqual(tokens[2].tag, Tag.MAIN)
        self.assertEqual(tokens[3].tag, Tag.LBRACKET_CURLY)
        self.assertEqual(tokens[4].tag, Tag.PUBLIC)
        self.assertEqual(tokens[5].tag, Tag.STATIC)
        self.assertEqual(tokens[6].tag, Tag.VOID)
        self.assertEqual(tokens[7].tag, Tag.MAIN)
        self.assertEqual(tokens[8].tag, Tag.LBRACKET)
        self.assertEqual(tokens[9].tag, Tag.STRING)
        self.assertEqual(tokens[10].tag, Tag.RBRACKET)
        self.assertEqual(tokens[11].tag, Tag.LBRACKET_CURLY)
        self.assertEqual(tokens[12].tag, Tag.TYPE_HINT)
        self.assertEqual(tokens[13].tag, Tag.ID)
        self.assertEqual(tokens[14].tag, Tag.ASSIGN)
        self.assertEqual(tokens[15].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[16].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[17].tag, Tag.ID)
        self.assertEqual(tokens[18].tag, Tag.OP_ASSIGN)
        self.assertEqual(tokens[19].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[20].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[21].tag, Tag.ID)
        self.assertEqual(tokens[22].tag, Tag.OP_ASSIGN)
        self.assertEqual(tokens[23].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[24].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[25].tag, Tag.ID)
        self.assertEqual(tokens[26].tag, Tag.OP_ASSIGN)
        self.assertEqual(tokens[27].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[28].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[29].tag, Tag.ID)
        self.assertEqual(tokens[30].tag, Tag.OP_ASSIGN)
        self.assertEqual(tokens[31].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[32].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[33].tag, Tag.ID)
        self.assertEqual(tokens[34].tag, Tag.OP_ASSIGN)
        self.assertEqual(tokens[35].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[36].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[37].tag, Tag.ID)
        self.assertEqual(tokens[38].tag, Tag.ASSIGN)
        self.assertEqual(tokens[39].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[40].tag, Tag.MATH_OPERATOR)
        self.assertEqual(tokens[41].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[42].tag, Tag.MATH_OPERATOR)
        self.assertEqual(tokens[43].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[44].tag, Tag.MATH_OPERATOR)
        self.assertEqual(tokens[45].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[46].tag, Tag.MATH_OPERATOR)
        self.assertEqual(tokens[47].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[48].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[49].tag, Tag.ID)
        self.assertEqual(tokens[50].tag, Tag.INCREMENT)
        self.assertEqual(tokens[51].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[52].tag, Tag.ID)
        self.assertEqual(tokens[53].tag, Tag.INCREMENT)
        self.assertEqual(tokens[54].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[55].tag, Tag.INCREMENT)
        self.assertEqual(tokens[56].tag, Tag.ID)
        self.assertEqual(tokens[57].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[58].tag, Tag.INCREMENT)
        self.assertEqual(tokens[59].tag, Tag.ID)
        self.assertEqual(tokens[60].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[61].tag, Tag.RBRACKET_CURLY)
        self.assertEqual(tokens[62].tag, Tag.RBRACKET_CURLY)

    def test_if_for_statements(self):
        code = """
                public class Main
                {
                    public static void main(String[] args) {
                        for (int i = 0; i < 10; i++) {
                            if (i >= 6) {
                                int a = Math.min(i, 6);
                            }
                            else {
                                int a = Math.max(i, 6);
                            }
                            System.out.println(a);
                        }
                    }
                }
                """

        lexer = Lexer(Tag, LEXER_RULES)
        lexer.buffer = code
        tokens = list(lexer.tokens)

        self.assertEqual(tokens[0].tag, Tag.PUBLIC)
        self.assertEqual(tokens[1].tag, Tag.CLASS)
        self.assertEqual(tokens[2].tag, Tag.MAIN)
        self.assertEqual(tokens[3].tag, Tag.LBRACKET_CURLY)
        self.assertEqual(tokens[4].tag, Tag.PUBLIC)
        self.assertEqual(tokens[5].tag, Tag.STATIC)
        self.assertEqual(tokens[6].tag, Tag.VOID)
        self.assertEqual(tokens[7].tag, Tag.MAIN)
        self.assertEqual(tokens[8].tag, Tag.LBRACKET)
        self.assertEqual(tokens[9].tag, Tag.STRING)
        self.assertEqual(tokens[10].tag, Tag.RBRACKET)
        self.assertEqual(tokens[11].tag, Tag.LBRACKET_CURLY)

        self.assertEqual(tokens[12].tag, Tag.FOR)
        self.assertEqual(tokens[13].tag, Tag.LBRACKET)
        self.assertEqual(tokens[14].tag, Tag.TYPE_HINT)
        self.assertEqual(tokens[15].tag, Tag.ID)
        self.assertEqual(tokens[16].tag, Tag.ASSIGN)
        self.assertEqual(tokens[17].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[18].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[19].tag, Tag.ID)
        self.assertEqual(tokens[20].tag, Tag.COMPARE)
        self.assertEqual(tokens[21].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[22].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[23].tag, Tag.ID)
        self.assertEqual(tokens[24].tag, Tag.INCREMENT)
        self.assertEqual(tokens[25].tag, Tag.RBRACKET)
        self.assertEqual(tokens[26].tag, Tag.LBRACKET_CURLY)

        self.assertEqual(tokens[27].tag, Tag.IF)
        self.assertEqual(tokens[28].tag, Tag.LBRACKET)
        self.assertEqual(tokens[29].tag, Tag.ID)
        self.assertEqual(tokens[30].tag, Tag.COMPARE)
        self.assertEqual(tokens[31].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[32].tag, Tag.RBRACKET)
        self.assertEqual(tokens[33].tag, Tag.LBRACKET_CURLY)

        self.assertEqual(tokens[34].tag, Tag.TYPE_HINT)
        self.assertEqual(tokens[35].tag, Tag.ID)
        self.assertEqual(tokens[36].tag, Tag.ASSIGN)
        self.assertEqual(tokens[37].tag, Tag.MIN)
        self.assertEqual(tokens[38].tag, Tag.LBRACKET)
        self.assertEqual(tokens[39].tag, Tag.ID)
        self.assertEqual(tokens[40].tag, Tag.COMMA)
        self.assertEqual(tokens[41].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[42].tag, Tag.RBRACKET)
        self.assertEqual(tokens[43].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[44].tag, Tag.RBRACKET_CURLY)

        self.assertEqual(tokens[45].tag, Tag.ELSE)
        self.assertEqual(tokens[46].tag, Tag.LBRACKET_CURLY)
        self.assertEqual(tokens[47].tag, Tag.TYPE_HINT)
        self.assertEqual(tokens[48].tag, Tag.ID)
        self.assertEqual(tokens[49].tag, Tag.ASSIGN)
        self.assertEqual(tokens[50].tag, Tag.MAX)
        self.assertEqual(tokens[51].tag, Tag.LBRACKET)
        self.assertEqual(tokens[52].tag, Tag.ID)
        self.assertEqual(tokens[53].tag, Tag.COMMA)
        self.assertEqual(tokens[54].tag, Tag.NUMBER_INT)
        self.assertEqual(tokens[55].tag, Tag.RBRACKET)
        self.assertEqual(tokens[56].tag, Tag.SEMICOLON)
        self.assertEqual(tokens[57].tag, Tag.RBRACKET_CURLY)

        self.assertEqual(tokens[58].tag, Tag.PRINT)
        self.assertEqual(tokens[59].tag, Tag.LBRACKET)
        self.assertEqual(tokens[60].tag, Tag.ID)
        self.assertEqual(tokens[61].tag, Tag.RBRACKET)
        self.assertEqual(tokens[62].tag, Tag.SEMICOLON)

        self.assertEqual(tokens[63].tag, Tag.RBRACKET_CURLY)
        self.assertEqual(tokens[64].tag, Tag.RBRACKET_CURLY)
        self.assertEqual(tokens[65].tag, Tag.RBRACKET_CURLY)


def tests():
    a = LexerTestCase()
    a.test_if_for_statements()
    a.test_math_operation()

