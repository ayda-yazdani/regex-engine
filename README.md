# Regex Engine

A regex engine built from scratch that compiles patterns into deterministic finite automata (DFAs) for guaranteed linear-time matching, because I had no idea where I could apply Thompson's construction irl when I learned about it in my lectures :). Immune to ReDoS [[1]](#references) by design, which is an added bonus I learned about through research [[2]](#references).

## How to use this repo

### Install requirements

```
pip install -r requirements.txt
```

Only dependency is pytest. Graphviz is optional if you want to generate automata diagrams (install separately via `brew install graphviz`).

### Create and activate environment

```
python -m venv venv
source venv/bin/activate
```

### Run the matcher

```python
from src.matcher import regex_match

regex_match("(a|b)*c", "aaabbbc")  # True
regex_match("(a|b)*c", "aaabbb")   # False
regex_match("a+b", "aaab")         # True
regex_match("a?", "")              # True
```

### Run tests

```
python -m pytest tests/ -v
```

### Generate automata diagrams

Requires Graphviz installed on your system.

```python
from src.visualizer import visualize_regex

visualize_regex("(a|b)*c")  # generates NFA and DFA PNGs
```

## Supported syntax

| Syntax | Name | Example | Matches |
|---|---|---|---|
| `a` | Literal | `abc` | "abc" |
| `\|` | Union | `a\|b` | "a" or "b" |
| `*` | Kleene star | `a*` | "", "a", "aa", ... |
| `+` | Kleene plus | `a+` | "a", "aa", ... |
| `?` | Optional | `a?` | "" or "a" |
| `()` | Grouping | `(ab)*` | "", "ab", "abab", ... |

## Overview

Takes a regex pattern string and compiles it into a DFA through five stages:

```
"(a|b)*c" → Lexer → Parser → Thompson's → Powerset → Matcher
              tokens   AST      NFA          DFA       O(n)
```

**Lexer** tokenises the string into characters, operators, and parentheses. **Parser** builds an abstract syntax tree (AST) using recursive descent with correct precedence (quantifiers bind tighter than concatenation, concatenation tighter than union). **Thompson's construction** converts the AST into an NFA (non-deterministic finite automaton). **Powerset construction** converts the NFA into a DFA (deterministic finite automaton). **Matcher** walks the DFA one character at a time.

Why did I go through all this work? Well, once you have the DFA, matching is O(n) where n is the string length, so there's no backtracking involved, and no exponential blowup (yay!). The pattern `.*.*=.*` that took down Cloudflare's entire network in 2019 [[3]](#references) is harmless here because the DFA has no mechanism to backtrack through ;)

## Repo structure

```
src/
├── lexer.py        # tokenise regex string
├── ast_nodes.py    # AST node definitions (Char, Concat, Union, Star, Plus, Optional, Epsilon)
├── parser.py       # recursive descent parser
├── nfa.py          # NFA data structure + Thompson's construction
├── dfa.py          # DFA data structure + powerset construction
├── matcher.py      # string matching using DFA
└── visualizer.py   # Graphviz output for NFA/DFA diagrams

tests/
├── test_lexer.py
├── test_parser.py
├── test_nfa.py        # epsilon closure, transitions
├── test_dfa.py        # DFA structure, determinism check
└── test_integration.py # full pipeline tests
```

## Comments on the code

The NFA transition function returns a **set** of states, not a single state, which is the whole difference between NFA and DFA. In the code it's `dict[tuple[int, str | None], set[int]]` where keys are `(state_id, symbol)` pairs and values are sets of destination states. `None` as the symbol means epsilon transition.

Epsilon closure is graph reachability, the same algorithm you'd use for "find all nodes reachable from source" in any graph. Uses a worklist (BFS-style) with a `result` set to track visited states. The `result` set is what prevents infinite loops on cycles, not the worklist, since the worklist shrinks as you process states so checking against it doesn't work. 

(That was a bug I hit early on.)

Thompson's construction creates one NFA object at the outer scope and mutates it through a recursive `build()` function. Each call to `build()` returns `(start_id, accept_id)` for the fragment it just created. I originally tried creating a new NFA inside each recursive call, which doesn't work because you need all the transitions in one place.

Every Thompson fragment has exactly one start and one accept state, and that constraint is what makes composition possible. Concat wires left's accept to right's start with epsilon. Union fans out from a new start to both branches then merges to a new accept. Star adds four epsilon transitions: into the inner NFA, back from accept to start (the loop), from start to the new accept (skip/empty match), and from inner accept to new accept.

Plus and Optional don't need their own NFA patterns. `a+` is just `Concat(a, Star(a))` and `a?` is just `Union(a, Epsilon())`. The `build()` function desugars them into existing constructions and recurses but it took me a while to remember to actually `return build(...)` instead of just creating the AST node.

In `ast_to_nfa`, I used `case Epsilon():` with parentheses. Without them (`case Epsilon:`) it pattern-matches against the class itself rather than an instance, which silently matches everything and was confusing to debug.

The powerset construction uses `frozenset` instead of `set` for the NFA state groups because sets aren't hashable and can't be dictionary keys. Each DFA state's `nfa_states` field is a frozenset representing which NFA states are simultaneously active, essentially a "snapshot" of the NFA. I didn't understand this for a while because I kept thinking `{0, 2, 3}` meant three separate destinations, when really it's one DFA state.

The `visited` dictionary maps frozensets to DFA states and serves two purposes: preventing duplicate DFA state creation and telling the worklist when to stop. Same pattern as epsilon closure, just operating on sets of states instead of individual states.

The alphabet isn't tracked by `ast_to_nfa`, so I extract it from the NFA transition keys after construction: `{symbol for (_, symbol) in nfa.transitions if symbol is not None}`. Not elegant but it works.

DFA transitions map `(state_id, symbol)` to a single `int`, not a set. Deterministic means one destination per symbol per state, which I had to remind myself after I initially wrote `{to_state}` (a set) out of habit from the NFA code.

The matcher is about 10 lines. Walk the DFA, follow one transition per character, reject if no transition exists, accept if you end in an accept state. All the complexity lives in construction, which is the entire argument for this approach over backtracking.

`regex_match()` in `matcher.py` ties the full pipeline together in one call: `tokenize → parse → ast_to_nfa → nfa_to_dfa → match`. Each of the five modules implement one step of the theory.

The parser handles precedence through grammar structure rather than explicit precedence tables. The call hierarchy is `parse_regex → parse_union → parse_concat → parse_unary → parse_primary`, where lower in the call stack means higher precedence. So `ab*` naturally parses as `Concat(a, Star(b))` because `parse_unary` captures the `*` before `parse_concat` ever sees it. The call stack _is_ the precedence hierarchy.

`parse_concat` doesn't check for union, it just stops when it hits a token it can't handle (anything that isn't CHAR or LPAREN). The caller (`parse_union`) picks up from there. Bascially, each grammar level only handles its own operators.

For the visualiser, Graphviz draws left-to-right (`rankdir="LR"`). Accept states get `doublecircle` shape. DFA node labels include the NFA state set so you can trace the powerset construction visually. There's an invisible `point` node with an arrow into the start state, which is the standard automata diagram convention.

I used Python `dataclasses` throughout. `NFAState` and `DFAState` are both dataclasses which auto-generate `__init__`, `__repr__`, and `__eq__`. `NFA` and `DFA` are regular classes because they need methods like `add_transition` and `epsilon_closure`.

The `counter = [0]` pattern in `ast_to_nfa` is a closure workaround. The inner `build()` function needs to increment a counter that persists across calls, but you can't reassign a variable from an enclosing scope in Python without `nonlocal`. Wrapping it in a list lets you mutate `counter[0]` from inside the closure. Same pattern appears in `nfa_to_dfa` with `counter = [1]`.

## Why this exists

I did some reading and most regex engines use backtracking, which has exponential worst-case complexity. Surprisingly, though, the solution has been around for a while: Thompson's NFA construction (1968) [[4]](#references) and the powerset construction (Rabin and Scott, 1959) [[5]](#references) guarantee linear-time matching. I learnt about these algorithms at the start of my Algorithms and Complexity module and wanted to build this to understand the algorithms properly, after covering finite automata.

A cool/motivating (?) example of where this is relevant is the Cloudflare outage of July 2019 [[3]](#references). One regex rule (`.*.*=.*`) in their Web Application Firewall triggered catastrophic backtracking across their entire global network, taking down millions of websites for 27 minutes. The funny thing in hindsight is that a Thompson-based engine would have made it impossible.

I will present this as a poster at the BCSWomen Lovelace Colloquium 2026, University of Bath. Will upload the accompanying poster when it's complete!

## References

1. OWASP Foundation. [Regular expression Denial of Service - ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
2. Cox, R. (2007). [Regular Expression Matching Can Be Simple And Fast](https://swtch.com/~rsc/regexp/regexp1.html)
3. Graham-Cumming, J. (2019). [Details of the Cloudflare outage on July 2, 2019](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/). Cloudflare Blog.
4. Thompson, K. (1968). ["Programming Techniques: Regular expression search algorithm."](https://dl.acm.org/doi/10.1145/363347.363387) *Communications of the ACM*, 11(6), 419-422.
5. Rabin, M. O. and Scott, D. (1959). ["Finite Automata and Their Decision Problems."](https://dl.acm.org/doi/10.1147/rd.32.0114) *IBM Journal of Research and Development*, 3(2), 114-125.
