# nfa tests
from src.nfa import NFA, NFAState


def test_nfa_state_creation():
    state = NFAState(id=0, is_accept=False)
    assert state.id == 0
    assert state.is_accept == False


def test_nfa_state_accept():
    state = NFAState(id=5, is_accept=True)
    assert state.id == 5
    assert state.is_accept == True


def test_add_transition_single():
    nfa = NFA(
        states=[],
        alphabet=['a'],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, 'a', 1)
    assert (0, 'a') in nfa.transitions
    assert nfa.transitions[(0, 'a')] == {1}


def test_add_transition_multiple_destinations():
    # NFA can have multiple destinations from same (state, symbol)
    nfa = NFA(
        states=[],
        alphabet=['a'],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, 'a', 1)
    nfa.add_transition(0, 'a', 2)
    assert nfa.transitions[(0, 'a')] == {1, 2}


def test_add_epsilon_transition():
    nfa = NFA(
        states=[],
        alphabet=[],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, None, 1)  # epsilon transition
    assert (0, None) in nfa.transitions
    assert nfa.transitions[(0, None)] == {1}


def test_epsilon_closure_single_state_no_transitions():
    # State with no epsilon transitions - closure is just itself
    nfa = NFA(
        states=[],
        alphabet=['a'],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, 'a', 1)  # not an epsilon transition

    result = nfa.epsilon_closure({0})
    assert result == {0}


def test_epsilon_closure_chain():
    # 0 --ε--> 1 --ε--> 2
    # epsilon_closure({0}) should be {0, 1, 2}
    nfa = NFA(
        states=[],
        alphabet=[],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, None, 1)
    nfa.add_transition(1, None, 2)

    result = nfa.epsilon_closure({0})
    assert result == {0, 1, 2}


def test_epsilon_closure_branch():
    # 0 --ε--> 1
    # 0 --ε--> 2
    # epsilon_closure({0}) should be {0, 1, 2}
    nfa = NFA(
        states=[],
        alphabet=[],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, None, 1)
    nfa.add_transition(0, None, 2)

    result = nfa.epsilon_closure({0})
    assert result == {0, 1, 2}


def test_epsilon_closure_cycle():
    # 0 --ε--> 1 --ε--> 0 (cycle!)
    # Should not infinite loop, should return {0, 1}
    nfa = NFA(
        states=[],
        alphabet=[],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, None, 1)
    nfa.add_transition(1, None, 0)

    result = nfa.epsilon_closure({0})
    assert result == {0, 1}


def test_epsilon_closure_multiple_start_states():
    # 0 --ε--> 1
    # 2 --ε--> 3
    # epsilon_closure({0, 2}) should be {0, 1, 2, 3}
    nfa = NFA(
        states=[],
        alphabet=[],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, None, 1)
    nfa.add_transition(2, None, 3)

    result = nfa.epsilon_closure({0, 2})
    assert result == {0, 1, 2, 3}


def test_epsilon_closure_mixed_transitions():
    # 0 --ε--> 1 --a--> 2 --ε--> 3
    # epsilon_closure({0}) should be {0, 1} (stops at non-epsilon)
    nfa = NFA(
        states=[],
        alphabet=['a'],
        transitions={},
        start=0,
        accept_states=[]
    )
    nfa.add_transition(0, None, 1)
    nfa.add_transition(1, 'a', 2)
    nfa.add_transition(2, None, 3)

    result = nfa.epsilon_closure({0})
    assert result == {0, 1}  # doesn't cross the 'a' transition
