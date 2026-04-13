# ast node definitions
''' these are needed because when we parse a regex, 
we don't want a flat list of tokens, we want a tree that shows 
the structure (AST nodes are structured because they're recursive)
'''

from dataclasses import dataclass

@dataclass
class Char:
    value: str 
@dataclass
class Concat:
    left: 'RegexAST'
    right: 'RegexAST'

@dataclass
class Union:
    left: 'RegexAST'
    right: 'RegexAST'

@dataclass
class Star:
    expr: 'RegexAST'

@dataclass
class Plus:
    expr: 'RegexAST'

@dataclass
class Optional:
    expr: 'RegexAST'
    
@dataclass
class Dot:
    """Matches any single character"""
    pass

@dataclass
class CharClass:
    """Matches any one character in the set"""
    chars: list[str]

@dataclass
class Epsilon:
    pass

RegexAST = Char | Concat | Union | Star | Plus | Optional | Dot | CharClass | Epsilon