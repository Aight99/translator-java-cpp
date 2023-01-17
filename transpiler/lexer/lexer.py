import re
from sty import fg
import logging
import os

from transpiler.constants import WHITESPACE, LEXER_REGEX_FLAGS, Special
from transpiler.base import Token, Terminal

logging.basicConfig(
    format='%(levelname)s:[%(module)s:%(lineno)d]: %(message)s',
    level=os.getenv('LOG_LEVEL', logging.WARNING),
)

logger = logging.getLogger(__name__)


class TranspilerError(Exception):
    pass


class LexerError(TranspilerError):
    pass


class UnexpectedTokenError(LexerError):
    pass


class Lexer:
    """
    Token parser from code sequence.
    """

    def __init__(
        self,
        terminal_cls: type[Terminal],
        rules: list,
        filepath: str | None = None,
    ):
        self.terminal_cls = terminal_cls
        parts = [f'(?P<{rule.tag.value}>{rule.regex})' for rule in rules]
        self.regex = re.compile('|'.join(parts))
        self.pos: int = 0
        self.line: int = 1
        self.line_pos: int = 1

        self.buffer: str | None = None
        self.buffer_length: int = -1

        self.filepath = filepath

    @property
    def tokens(self):
        assert self.buffer is not None, 'nothing to tokenize'
        self.buffer_length = len(self.buffer)

        while token := self._parse_token():
            yield token
        return

    def _parse_token(self) -> Token | None:
        if self.pos > self.buffer_length:
            return None

        cursor = WHITESPACE.search(self.buffer, self.pos)
        if cursor is None:
            return None

        self.pos = cursor.start()
        cursor = self.regex.match(self.buffer, self.pos)
        if cursor:
            group = cursor.lastgroup
            token = Token(
                self.terminal_cls(group),
                cursor.group(group),
                self.pos + 1,
                self._get_line()
            )
            logger.debug(
                f'parsed token {fg.li_green}{token}{fg.rs} at line '
                f'{token.line} ({group})'
            )
            self.pos = cursor.end()
            return token

        line = self._get_line()
        msg = f"unexpected token '{self.buffer[self.pos]}' at line {line}"
        raise UnexpectedTokenError(msg)

    def _get_line(self):
        return self.buffer.count('\n', 0, self.pos) + 1