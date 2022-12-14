from enum import Enum


class LexerRule:
    def __init__(self, tag: Enum, regex: str) -> None:
        self.tag = tag
        self.regex = regex


class Symbol(Enum):
    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class Terminal(Symbol):
    pass


class Token:
    def __init__(
        self,
        tag: Symbol,
        value: str,
        pos: int | None = None,
        line: int | None = None,
    ):
        self.tag = tag
        self.value = value
        self.pos = pos
        self.line = line

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value) + ' ' + str(self.tag)
