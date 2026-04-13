# lexer tests
from src.lexer import tokenize, Token, TokenType


# --- basic tokens ---

def test_single_char():
    tokens = tokenize("a")
    assert tokens == [Token(TokenType.CHAR, "a"), Token(TokenType.END)]

def test_operators():
    tokens = tokenize("a*+?|")
    assert tokens[0] == Token(TokenType.CHAR, "a")
    assert tokens[1] == Token(TokenType.STAR)
    assert tokens[2] == Token(TokenType.PLUS)
    assert tokens[3] == Token(TokenType.OPTIONAL)
    assert tokens[4] == Token(TokenType.UNION)

def test_parens():
    tokens = tokenize("(a)")
    assert tokens[0] == Token(TokenType.LPAREN)
    assert tokens[1] == Token(TokenType.CHAR, "a")
    assert tokens[2] == Token(TokenType.RPAREN)
    assert tokens[3] == Token(TokenType.END)

def test_dot():
    tokens = tokenize("a.b")
    assert tokens[0] == Token(TokenType.CHAR, "a")
    assert tokens[1] == Token(TokenType.DOT)
    assert tokens[2] == Token(TokenType.CHAR, "b")

def test_brackets():
    tokens = tokenize("[abc]")
    assert tokens[0] == Token(TokenType.LBRACKET)
    assert tokens[1] == Token(TokenType.CHAR, "a")
    assert tokens[2] == Token(TokenType.CHAR, "b")
    assert tokens[3] == Token(TokenType.CHAR, "c")
    assert tokens[4] == Token(TokenType.RBRACKET)


# --- escape sequences ---

def test_escape_star():
    tokens = tokenize("\\*")
    assert tokens == [Token(TokenType.CHAR, "*"), Token(TokenType.END)]

def test_escape_dot():
    tokens = tokenize("\\.")
    assert tokens == [Token(TokenType.CHAR, "."), Token(TokenType.END)]

def test_escape_backslash():
    tokens = tokenize("\\\\")
    assert tokens == [Token(TokenType.CHAR, "\\"), Token(TokenType.END)]

def test_escape_pipe():
    tokens = tokenize("\\|")
    assert tokens == [Token(TokenType.CHAR, "|"), Token(TokenType.END)]

def test_escape_paren():
    tokens = tokenize("\\(\\)")
    assert tokens[0] == Token(TokenType.CHAR, "(")
    assert tokens[1] == Token(TokenType.CHAR, ")")

def test_escape_bracket():
    tokens = tokenize("\\[\\]")
    assert tokens[0] == Token(TokenType.CHAR, "[")
    assert tokens[1] == Token(TokenType.CHAR, "]")

def test_escape_in_middle():
    # a\*b should tokenize as CHAR(a), CHAR(*), CHAR(b)
    tokens = tokenize("a\\*b")
    assert tokens[0] == Token(TokenType.CHAR, "a")
    assert tokens[1] == Token(TokenType.CHAR, "*")
    assert tokens[2] == Token(TokenType.CHAR, "b")

def test_trailing_backslash():
    import pytest
    with pytest.raises(SyntaxError):
        tokenize("abc\\")
