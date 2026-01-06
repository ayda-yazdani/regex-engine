# parser tests
import pytest
from src.lexer import tokenize
from src.parser import parse
from src.ast_nodes import Char, Concat, Union, Star, Plus, Optional

# === Basic atoms ===

def test_single_char():
    assert parse(tokenize("a")) == Char("a")

def test_single_digit():
    assert parse(tokenize("1")) == Char("1")

# === Concatenation ===

def test_two_chars():
    assert parse(tokenize("ab")) == Concat(Char("a"), Char("b"))

def test_three_chars():
    # Should be left-associative: (ab)c
    assert parse(tokenize("abc")) == Concat(Concat(Char("a"), Char("b")), Char("c"))

# === Quantifiers ===

def test_star():
    assert parse(tokenize("a*")) == Star(Char("a"))

def test_plus():
    assert parse(tokenize("a+")) == Plus(Char("a"))

def test_optional():
    assert parse(tokenize("a?")) == Optional(Char("a"))

# === Union ===

def test_simple_union():
    assert parse(tokenize("a|b")) == Union(Char("a"), Char("b"))

def test_triple_union():
    # Should be left-associative: (a|b)|c
    assert parse(tokenize("a|b|c")) == Union(Union(Char("a"), Char("b")), Char("c"))

# === Precedence tests ===

def test_star_binds_tighter_than_concat():
    # ab* should be a followed by (b*), not (ab)*
    assert parse(tokenize("ab*")) == Concat(Char("a"), Star(Char("b")))

def test_concat_binds_tighter_than_union():
    # a|bc should be a OR (bc), not (a|b) followed by c
    assert parse(tokenize("a|bc")) == Union(Char("a"), Concat(Char("b"), Char("c")))

def test_complex_precedence():
    # ab*|c should be (a followed by b*) OR c
    expected = Union(Concat(Char("a"), Star(Char("b"))), Char("c"))
    assert parse(tokenize("ab*|c")) == expected

# === Grouping with parentheses ===

def test_grouped_concat_with_star():
    # (ab)* should be Star of the whole Concat
    assert parse(tokenize("(ab)*")) == Star(Concat(Char("a"), Char("b")))

def test_grouped_union():
    # (a|b)c should be (a OR b) followed by c
    expected = Concat(Union(Char("a"), Char("b")), Char("c"))
    assert parse(tokenize("(a|b)c")) == expected

def test_nested_groups():
    # ((a)) should just be Char("a")
    assert parse(tokenize("((a))")) == Char("a")

def test_group_with_quantifier():
    # (a|b)+ should be Plus of the Union
    assert parse(tokenize("(a|b)+")) == Plus(Union(Char("a"), Char("b")))

# === Combined complex cases ===

def test_complex_regex():
    # (a|b)*c should match strings of a's and b's followed by c
    expected = Concat(Star(Union(Char("a"), Char("b"))), Char("c"))
    assert parse(tokenize("(a|b)*c")) == expected

def test_email_like_pattern():
    # a+b represents something like "one or more a's followed by b"
    expected = Concat(Plus(Char("a")), Char("b"))
    assert parse(tokenize("a+b")) == expected
