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
    DOT = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    END = auto()

@dataclass
class Token:
    type: TokenType
    value: str | None = None


#read each character in string, extract operator type (and value if char), and store in a list
#now uses index-based iteration so escape sequences can skip ahead
def tokenize(regex: str) -> list[Token]:
    tokens = []
    i = 0
    while i < len(regex):
        c = regex[i]
        match c:
            case "\\":
                # escape: next character is always a literal
                if i + 1 >= len(regex):
                    raise SyntaxError("Trailing backslash")
                i += 1
                tokens.append(Token(TokenType.CHAR, regex[i]))
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
            case ".":
                tokens.append(Token(TokenType.DOT))
            case "[":
                tokens.append(Token(TokenType.LBRACKET))
            case "]":
                tokens.append(Token(TokenType.RBRACKET))
            case _:
                tokens.append(Token(TokenType.CHAR, c))
        i += 1

    tokens.append(Token(TokenType.END))
    return tokens
