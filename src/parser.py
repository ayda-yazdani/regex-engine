# parser - tokens to AST
from src.ast_nodes import *
from src.lexer import Token, TokenType

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        #track current position in token list
        self.pos = 0

    def current(self) -> Token:
        #what token are we looking at?
        return self.tokens[self.pos]
    
    def consume(self) -> Token:
        #return current token and advance position
        token = self.tokens[self.pos]
        self.pos += 1
        return token
    
    def _consume_class_char(self) -> str:
        """Consume a token inside a character class and return its literal character.
        Inside [...], everything is a literal — no special meaning for . * + etc."""
        token = self.consume()
        match token.type:
            case TokenType.CHAR:
                return token.value
            case TokenType.DOT:
                return '.'
            case TokenType.STAR:
                return '*'
            case TokenType.PLUS:
                return '+'
            case TokenType.OPTIONAL:
                return '?'
            case TokenType.UNION:
                return '|'
            case TokenType.LPAREN:
                return '('
            case TokenType.RPAREN:
                return ')'
            case TokenType.LBRACKET:
                return '['
            case _:
                raise SyntaxError(f"Unexpected token in character class: {token}")

    #implements grammar rule: primary --> CHAR | '.' | '[' class ']' | '(' regex ')'
    def parse_primary(self) -> RegexAST:
        if self.current().type == TokenType.CHAR:
            token = self.consume()
            return Char(token.value)
        elif self.current().type == TokenType.DOT:
            self.consume()
            return Dot()
        elif self.current().type == TokenType.LBRACKET:
            self.consume()  # consume [
            chars = []
            while self.current().type != TokenType.RBRACKET:
                if self.current().type == TokenType.END:
                    raise SyntaxError("Unclosed character class")
                char = self._consume_class_char()
                # check for range like a-z
                if (self.current().type == TokenType.CHAR
                        and self.current().value == '-'
                        and self.tokens[self.pos + 1].type != TokenType.RBRACKET):
                    self.consume()  # consume -
                    end_char = self._consume_class_char()
                    chars.extend(chr(c) for c in range(ord(char), ord(end_char) + 1))
                else:
                    chars.append(char)
            self.consume()  # consume ]
            return CharClass(chars)
        elif self.current().type == TokenType.LPAREN:
            self.consume()
            inner = self.parse_regex()
            self.consume()
            return inner
        else:
            raise SyntaxError(f"Unexpected token: {self.current()}")
        
    #implements grammar rule: unary → primary ('*' | '+' | '?')?
    def parse_unary(self) -> RegexAST:
        expr = self.parse_primary()
        if self.current().type == TokenType.STAR:
            #need to consume the quantifier, so pos updates and parse function sees the next token
            self.consume()
            return Star(expr)
        elif self.current().type == TokenType.PLUS:
            self.consume()
            return Plus(expr)
        elif self.current().type == TokenType.OPTIONAL:
            self.consume()
            return Optional(expr)
        
        return expr
    
    #implements grammar rule: concat -> unary+
    def parse_concat(self) -> RegexAST:
        result = self.parse_unary()
        while self.current().type in (TokenType.CHAR, TokenType.LPAREN, TokenType.DOT, TokenType.LBRACKET):
            result = Concat(result, self.parse_unary()) 
        return result

    #implements grammar rule: union → concat ('|' concat)*
    def parse_union(self) -> RegexAST:
        result = self.parse_concat()
        while self.current().type == TokenType.UNION:
            self.consume()
            result = Union(result, self.parse_concat())
        return result
    
    #implements grammar rule: regex -> union
    def parse_regex(self) -> RegexAST:
       return self.parse_union()

def parse(tokens: list[Token]) -> RegexAST:
    parser = Parser(tokens)
    return parser.parse_regex()

    
