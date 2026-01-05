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


#read each character in string, extract operator type (and value if char), and store in a list 
def tokenize(regex: str) -> list[Token]:
    tokens = []
    for c in regex:
        match c:
            case "|":
                tokens.append(Token(TokenType.UNION))
            case "+":
                tokens.append(Token(TokenType.PLUS))
            case "*":
                tokens.append(Token(TokenType.STAR))
            case "(":
                tokens.append(Token(TokenType.LPAREN))
            case ")":
                tokens.append(Token(TokenType.RPAREN))
            case "?":
                tokens.append(Token(TokenType.OPTIONAL))
            case _:
                tokens.append(Token(TokenType.CHAR, c))
    
    tokens.append(Token(TokenType.END))
    return tokens
