# dfa tests
from src.lexer import tokenize
from src.parser import parse
from src.nfa import ast_to_nfa
from src.dfa import nfa_to_dfa


def build_dfa(pattern):
    tokens = tokenize(pattern)
    ast = parse(tokens)
    nfa = ast_to_nfa(ast)
    return nfa_to_dfa(nfa)


# --- DFA structure tests ---

def test_single_char_dfa():
    dfa = build_dfa("a")
    # should have a start state and at least one other state
    assert len(dfa.states) >= 2
    assert len(dfa.accept_states) >= 1

def test_single_char_transitions():
    dfa = build_dfa("a")
    # from start, reading 'a' should lead to an accept state
    next_id = dfa.transitions[(dfa.start.id, 'a')]
    accept_ids = [s.id for s in dfa.accept_states]
    assert next_id in accept_ids

def test_union_dfa():
    dfa = build_dfa("a|b")
    # start state should have transitions on both 'a' and 'b'
    assert (dfa.start.id, 'a') in dfa.transitions
    assert (dfa.start.id, 'b') in dfa.transitions

def test_star_start_is_accepting():
    dfa = build_dfa("a*")
    # a* matches empty string, so start state should be accepting
    assert dfa.start.is_accept == True

def test_star_self_loop():
    dfa = build_dfa("a*")
    # reading 'a' from any accepting state should lead to an accepting state
    next_id = dfa.transitions[(dfa.start.id, 'a')]
    accept_ids = [s.id for s in dfa.accept_states]
    assert next_id in accept_ids

def test_concat_dfa():
    dfa = build_dfa("ab")
    # start state should not be accepting
    assert dfa.start.is_accept == False
    # should have transition on 'a' from start
    assert (dfa.start.id, 'a') in dfa.transitions

def test_deterministic():
    """Every (state, symbol) pair should map to exactly one state"""
    dfa = build_dfa("(a|b)*c")
    for key, value in dfa.transitions.items():
        assert isinstance(value, int)
