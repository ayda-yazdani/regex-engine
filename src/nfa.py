# nfa construction

from dataclasses import dataclass

from src.ast_nodes import *

# sentinel value for wildcard (.) transitions — can't collide with single-char symbols
DOT_SYMBOL = "__DOT__"


@dataclass
class NFAState:
    id: int
    is_accept: bool

class NFA:
    def __init__(self, states: list[NFAState], alphabet: list[str], transitions: dict[tuple[int, str | None], set[int]], start: int, accept_states: list[NFAState]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start = start
        self.accept_states = accept_states
    
    def add_transition(self, from_state, symbol, to_state):
        if (from_state, symbol) in self.transitions:
            self.transitions[(from_state, symbol)].add(to_state)
        else:
            self.transitions[(from_state, symbol)] = {to_state}
            

    def epsilon_closure(self, states: set[int]) -> set[int]:
        #already visited states + the closure we're building
        result = set(states)

        #states we still need to explore
        worklist = list(states)

        while worklist:
            #visit a new state
            state = worklist.pop()
            result.add(state)

            #if the state has an epsilon-transition, 
            # add the states you can visit via the epsilon-transition to result
            # ONLY if they haven't been visited yet
            if (state, None) in self.transitions:
                for s in self.transitions.get((state, None)):
                    if s not in result:
                        worklist.append(s)
            
        return result


def ast_to_nfa(ast: RegexAST) -> NFA:
    counter = [0]
    nfa = NFA(
        states = [],
        alphabet=[],
        transitions={},
        start = 0,
        accept_states=[]
    )

    def new_state_id():
        id = counter[0]
        counter[0] += 1
        return id
    
    
    #returns (start_id, accept_id)
    def build(node) -> tuple[int,int]: 
        match node:
            case Char(c):
                s1 = new_state_id()
                s2 = new_state_id()
                nfa.add_transition(s1,c,s2)
                return (s1,s2)
            case Concat(left, right):
                left_start, left_accept = build(left)
                right_start, right_accept = build(right)
                nfa.add_transition(left_accept, None, right_start)
                return (left_start, right_accept)
            case Union(left, right):
                left_start, left_accept = build(left)
                right_start, right_accept = build(right)
                new_start_state = new_state_id()
                new_accept_state = new_state_id()
                nfa.add_transition(new_start_state, None, left_start)
                nfa.add_transition(new_start_state, None, right_start)
                nfa.add_transition(right_accept, None, new_accept_state)
                nfa.add_transition(left_accept, None, new_accept_state)
                return (new_start_state, new_accept_state)
            case Star(inner):
                inner_start, inner_accept = build(inner)
                new_start_state = new_state_id()
                new_accept_state = new_state_id()
                nfa.add_transition(new_start_state, None, inner_start)
                nfa.add_transition(inner_accept, None, inner_start)
                nfa.add_transition(new_start_state, None, new_accept_state)
                nfa.add_transition(inner_accept, None, new_accept_state)
                return (new_start_state, new_accept_state)
            case Plus(x):
                return build(Concat(x, Star(x)))
            case Optional(x):
                return build(Union(x, Epsilon()))
            case Dot():
                s1 = new_state_id()
                s2 = new_state_id()
                nfa.add_transition(s1, DOT_SYMBOL, s2)
                return (s1, s2)
            case CharClass(chars):
                # one transition per character, all from same start to same accept
                s1 = new_state_id()
                s2 = new_state_id()
                for c in chars:
                    nfa.add_transition(s1, c, s2)
                return (s1, s2)
            case Epsilon():
                s1 = new_state_id()
                s2 = new_state_id()
                nfa.add_transition(s1, None, s2)
                return (s1, s2)

    start, accept = build(ast)
    nfa.start = start
    nfa.accept_states = [accept]
    return nfa



