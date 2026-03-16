# graphviz visualization
import graphviz

from src.lexer import tokenize
from src.parser import parse
from src.nfa import ast_to_nfa
from src.dfa import nfa_to_dfa


def visualize_nfa(nfa, filename="nfa", view=True):
    dot = graphviz.Digraph("NFA", format="png")
    dot.attr(rankdir="LR")

    # invisible entry point arrow
    dot.node("start", shape="point")
    dot.edge("start", str(nfa.start))

    # collect all state ids from transitions
    all_states = set()
    all_states.add(nfa.start)
    for (from_state, _), to_states in nfa.transitions.items():
        all_states.add(from_state)
        all_states.update(to_states)

    accept_ids = set(nfa.accept_states)

    for state_id in sorted(all_states):
        if state_id in accept_ids:
            dot.node(str(state_id), shape="doublecircle")
        else:
            dot.node(str(state_id), shape="circle")

    # transitions
    for (from_state, symbol), to_states in nfa.transitions.items():
        label = "ε" if symbol is None else symbol
        for to_state in to_states:
            dot.edge(str(from_state), str(to_state), label=label)

    dot.render(filename, cleanup=True, view=view)
    return filename + ".png"


def visualize_dfa(dfa, filename="dfa", view=True):
    dot = graphviz.Digraph("DFA", format="png")
    dot.attr(rankdir="LR")

    # invisible entry point arrow
    dot.node("start", shape="point")
    dot.edge("start", str(dfa.start.id))

    accept_ids = {s.id for s in dfa.accept_states}

    for state in dfa.states:
        label = f"{state.id}\n{set(state.nfa_states)}"
        if state.id in accept_ids:
            dot.node(str(state.id), label=label, shape="doublecircle")
        else:
            dot.node(str(state.id), label=label, shape="circle")

    # transitions
    for (from_state, symbol), to_state in dfa.transitions.items():
        dot.edge(str(from_state), str(to_state), label=symbol)

    dot.render(filename, cleanup=True, view=view)
    return filename + ".png"


def visualize_regex(pattern, filename=None, view=True):
    # Visualise both NFA and DFA for a regex pattern.
    tokens = tokenize(pattern)
    ast = parse(tokens)
    nfa = ast_to_nfa(ast)
    dfa = nfa_to_dfa(nfa)

    name = filename or pattern.replace("*", "star").replace("|", "or").replace("(", "").replace(")", "")
    nfa_file = visualize_nfa(nfa, filename=f"{name}_nfa", view=view)
    dfa_file = visualize_dfa(dfa, filename=f"{name}_dfa", view=view)
    return nfa_file, dfa_file
