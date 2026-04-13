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


# --- wildcard ---

def test_dot_matches_any_char():
    assert regex_match(".", "x") == True

def test_dot_matches_digit():
    assert regex_match(".", "5") == True

def test_dot_no_match_empty():
    assert regex_match(".", "") == False

def test_dot_no_match_two_chars():
    assert regex_match(".", "ab") == False

def test_dot_in_concat():
    assert regex_match("a.b", "axb") == True

def test_dot_in_concat_wrong():
    assert regex_match("a.b", "ab") == False

def test_dot_star():
    assert regex_match(".*", "") == True

def test_dot_star_anything():
    assert regex_match(".*", "anything") == True

def test_dot_plus():
    assert regex_match(".+", "") == False

def test_dot_plus_one():
    assert regex_match(".+", "a") == True

def test_dot_plus_many():
    assert regex_match(".+", "hello") == True

def test_dot_with_concrete():
    # a.*b should match anything starting with a and ending with b
    assert regex_match("a.*b", "ab") == True

def test_dot_with_concrete_long():
    assert regex_match("a.*b", "axxxb") == True

def test_dot_with_concrete_no_match():
    assert regex_match("a.*b", "axxxx") == False


# --- escape sequences ---

def test_escape_star_literal():
    assert regex_match("\\*", "*") == True

def test_escape_star_not_quantifier():
    assert regex_match("\\*", "") == False

def test_escape_dot_literal():
    assert regex_match("\\.", ".") == True

def test_escape_dot_not_wildcard():
    assert regex_match("\\.", "a") == False

def test_escape_pipe_literal():
    assert regex_match("a\\|b", "a|b") == True

def test_escape_pipe_not_union():
    assert regex_match("a\\|b", "a") == False

def test_escape_parens():
    assert regex_match("\\(a\\)", "(a)") == True

def test_escape_backslash():
    assert regex_match("\\\\", "\\") == True


# --- character classes ---

def test_class_basic():
    assert regex_match("[abc]", "a") == True

def test_class_basic_b():
    assert regex_match("[abc]", "b") == True

def test_class_no_match():
    assert regex_match("[abc]", "d") == False

def test_class_empty_string():
    assert regex_match("[abc]", "") == False

def test_class_too_long():
    assert regex_match("[abc]", "ab") == False

def test_class_with_star():
    assert regex_match("[abc]*", "abcabc") == True

def test_class_with_star_empty():
    assert regex_match("[abc]*", "") == True

def test_class_with_plus():
    assert regex_match("[abc]+", "abc") == True

def test_class_with_plus_empty():
    assert regex_match("[abc]+", "") == False

def test_class_range():
    assert regex_match("[a-z]", "m") == True

def test_class_range_no_match():
    assert regex_match("[a-z]", "5") == False

def test_class_digit_range():
    assert regex_match("[0-9]+", "12345") == True

def test_class_digit_range_no_match():
    assert regex_match("[0-9]+", "abc") == False

def test_class_in_concat():
    assert regex_match("[ab]c", "ac") == True

def test_class_in_concat_b():
    assert regex_match("[ab]c", "bc") == True

def test_class_in_concat_no_match():
    assert regex_match("[ab]c", "cc") == False

def test_class_combined_with_dot():
    # [a-c]+ followed by any character
    assert regex_match("[a-c]+.", "abx") == True

def test_class_combined_no_match():
    # [a-c]+. needs at least 2 chars (one for the class, one for the dot)
    assert regex_match("[a-c]+.", "a") == False
