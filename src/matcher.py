# string matching
from src.lexer import tokenize
from src.parser import parse
from src.nfa import ast_to_nfa
from src.dfa import nfa_to_dfa


def regex_match(pattern, string):
    tokens = tokenize(pattern)
    ast = parse(tokens)
    nfa = ast_to_nfa(ast)
    dfa = nfa_to_dfa(nfa)
    return match(dfa, string)


def match(dfa, string):
    current = dfa.start

    for char in string:
        # for each character, follow the one transition
        if (current.id, char) in dfa.transitions:
            next_id = dfa.transitions[(current.id, char)]

            # find the DFAState object with this id
            current = next(s for s in dfa.states if s.id == next_id)
        else:
            # no transition means string is rejected
            return False
    
    # after all characters consumed, accept if we're in an accept state
    return current.is_accept
        