# nfa construction

from dataclasses import dataclass


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




