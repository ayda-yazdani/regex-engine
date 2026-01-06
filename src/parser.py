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
    
    #implements grammar rule: primary --> CHAR | '(' regex ')'
    def parse_primary(self) -> RegexAST:
        if self.current().type == TokenType.CHAR:
            token = self.consume()
            return Char(token.value)
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
        while self.current().type in (TokenType.CHAR, TokenType.LPAREN):
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

    
