# dfa and powerset construction
from dataclasses import dataclass

@dataclass
class DFAState:
    id: int
    nfa_states: frozenset[int] #which NFA states this DFA state represents
    is_accept: bool

class DFA:
    def __init__(self, states, alphabet, transitions, start, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start = start
        self.accept_states = accept_states

    def add_transition(self, from_state, symbol, to_state):
        self.transitions[(from_state, symbol)] = to_state

def nfa_to_dfa(nfa):
    # compute the dfa start state (aka snapshot of all the states the nfa can be in at once)
    start_set = frozenset(nfa.epsilon_closure({nfa.start}))

    is_accept = False
    # check if this dfa state is accepting (contains any nfa accept state)
    for s in start_set:
        if s in nfa.accept_states:
            is_accept = True

    start_state = DFAState(id=0, nfa_states=start_set, is_accept=is_accept)

    dfa = DFA(
        states = [start_state],
        alphabet = nfa.alphabet,
        transitions = {},
        start = start_state,
        accept_states = []
    )

    if start_state.is_accept:
        dfa.accept_states.append(start_state)

    # track visited sets and worklist
    counter = [1]

    # dictionary mapping frozenset of nfa states to the dfa state i create for it
    visited = {start_set: start_state}

    # list of dfa states we still need to process (i.e. haven't yet checked their transition on every symbol)
    worklist = [start_set]
    
    alphabet = {symbol for (_, symbol) in nfa.transitions if symbol is not None}

    # process each unvisited dfa state
    while worklist:
        current_set = worklist.pop()
        current_dfa_state = visited[current_set]

        for symbol in alphabet:
            # find all nfa states reachable on this symbol
            move_set = set()
            for nfa_state in current_set:
                if (nfa_state, symbol) in nfa.transitions:
                    for s in nfa.transitions[(nfa_state, symbol)]:
                        move_set.add(s)
            
            next_set = frozenset(nfa.epsilon_closure(move_set))

            # no transition on this symbol, dead end
            if not next_set:
                continue

            # create new dfa state if we haven't seen this set of nfa states before
            if next_set not in visited:
                is_accept = False
                for s in next_set:
                    if s in nfa.accept_states:
                        is_accept = True
                
                new_state = DFAState(id=counter[0], nfa_states=next_set, is_accept=is_accept)
                counter[0] += 1
                visited[next_set] = new_state
                worklist.append(next_set)
                dfa.states.append(new_state)
                if is_accept:
                    dfa.accept_states.append(new_state)

            # add the dfa transition
            dfa.add_transition(current_dfa_state.id, symbol, visited[next_set].id)

    return dfa


