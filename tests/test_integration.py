# integration tests — full pipeline: regex string → tokens → AST → NFA → DFA → match
from src.lexer import tokenize
from src.parser import parse
from src.nfa import ast_to_nfa
from src.dfa import nfa_to_dfa
from src.matcher import match


def regex_match(pattern, string):
    tokens = tokenize(pattern)
    ast = parse(tokens)
    nfa = ast_to_nfa(ast)
    dfa = nfa_to_dfa(nfa)
    return match(dfa, string)


# --- single character ---

def test_single_char_match():
    assert regex_match("a", "a") == True

def test_single_char_no_match():
    assert regex_match("a", "b") == False

def test_single_char_empty():
    assert regex_match("a", "") == False


# --- concatenation ---

def test_concat_match():
    assert regex_match("ab", "ab") == True

def test_concat_no_match():
    assert regex_match("ab", "a") == False

def test_concat_too_long():
    assert regex_match("ab", "abc") == False


# --- union ---

def test_union_left():
    assert regex_match("a|b", "a") == True

def test_union_right():
    assert regex_match("a|b", "b") == True

def test_union_no_match():
    assert regex_match("a|b", "c") == False


# --- kleene star ---

def test_star_empty():
    assert regex_match("a*", "") == True

def test_star_one():
    assert regex_match("a*", "a") == True

def test_star_many():
    assert regex_match("a*", "aaaa") == True

def test_star_wrong_char():
    assert regex_match("a*", "b") == False


# --- plus ---

def test_plus_empty():
    assert regex_match("a+", "") == False

def test_plus_one():
    assert regex_match("a+", "a") == True

def test_plus_many():
    assert regex_match("a+", "aaa") == True


# --- optional ---

def test_optional_empty():
    assert regex_match("a?", "") == True

def test_optional_one():
    assert regex_match("a?", "a") == True

def test_optional_too_many():
    assert regex_match("a?", "aa") == False


# --- combined patterns ---

def test_star_concat():
    assert regex_match("a*b", "b") == True

def test_star_concat_many():
    assert regex_match("a*b", "aaab") == True

def test_grouped_star():
    assert regex_match("(ab)*", "") == True

def test_grouped_star_match():
    assert regex_match("(ab)*", "abab") == True

def test_grouped_star_no_match():
    assert regex_match("(ab)*", "aba") == False

def test_union_star_concat():
    assert regex_match("(a|b)*c", "aaabbbc") == True

def test_union_star_concat_no_match():
    assert regex_match("(a|b)*c", "aaabbb") == False

def test_complex_pattern():
    assert regex_match("a(b|c)*d", "ad") == True

def test_complex_pattern_match():
    assert regex_match("a(b|c)*d", "abcbcd") == True

def test_complex_pattern_no_match():
    assert regex_match("a(b|c)*d", "abcbc") == False
