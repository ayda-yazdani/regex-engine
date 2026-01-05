# lexer - tokenize regex strings

from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    CHAR = auto()
    STAR = auto()
    LPAREN = auto()
    RPAREN = auto()
    UNION = auto()
    PLUS = auto()
    OPTIONAL = auto()
    END = auto()

@dataclass
class Token:
    type: TokenType
    value: str | None = None
