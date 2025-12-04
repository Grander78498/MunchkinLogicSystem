from enum import Enum
from dataclasses import dataclass
from typing import Any


class LexerException(Exception):
    """Custom exception"""


class TokenType(str, Enum):
    IDENTIFIER = "identifier"
    DOT = "."
    EOL = ""

    OR = "OR"
    AND = "AND"
    NOT = "NOT"
    IMPLIES = "IMPLIES"
    EQUIVALENCE = "EQUALS"


@dataclass
class Token:
    type: TokenType
    value: Any
    position: int


class Lexer:
    def __init__(self):
        pass

    def advance(self, step: int = 1):
        self.current_pos += step
        if self.current_pos < len(self.text):
            self.current_char = self.text[self.current_pos]
        else:
            self.current_char = None

    def tokenize_line(self, text: str):
        self.current_pos = 0
        self.text = text
        self.current_char = self.text[0]
        self.tokens = []

        while self.current_char is not None:
            self.token_pos = self.current_pos
            if self.current_char.isalpha():
                self.parse_identifier()
            elif self.current_char == '"':
                self.advance()
                self.parse_identifier(skip_spaces=True)
                if self.current_char != '"':
                    raise LexerException("Незакрытая строка")
            elif self.current_char == ".":
                self.tokens.append(
                    Token(
                        type=TokenType.DOT,
                        value=self.current_char,
                        position=self.token_pos,
                    )
                )
                self.advance()

        eol_token = Token(type=TokenType.EOL, value=None, position=self.current_pos)
        self.tokens.append(eol_token)
        return self.tokens

    def parse_identifier(self, skip_spaces: bool = False):
        self.current_value = []
        while self.current_char and (
            skip_spaces or self.current_char.isalnum() or self.current_char == "_"
        ):
            self.current_value.append(self.current_char)
            self.advance()

        new_token = Token(
            type=TokenType.IDENTIFIER,
            value="".join(self.current_value),
            position=self.token_pos,
        )
        self.tokens.append(new_token)
