from lark import lark


_grammar = r"""
?start: expression

?expression: product
           | comparison
           | "not" comparison -> logical_not
           | comparison "or" comparison -> logical_or
           | comparison "and" comparison -> logical_and
           | expression "+" product -> add
           | expression "-" product -> subtract

?product: atom
        | product "*" atom -> multiply
        | product "/" atom -> divide

?comparison: comparison_lhs
           | comparison_lhs "is" atom -> eq
           | comparison_lhs "is not" atom -> not_eq
           | comparison_lhs "is in" array -> is_in
           | comparison_lhs "is not in" array -> not_in
           | comparison_lhs "gt" atom -> gt
           | comparison_lhs "gte" atom -> gte
           | comparison_lhs "lt" atom -> lt
           | comparison_lhs "lte" atom -> lte

?comparison_lhs: group
               | atom

?group: "any" array -> any
      | "all" array -> all

?atom: lookup
     | string
     | array
     | BOOL -> boolean
     | SIGNED_NUMBER -> number
     | "(" expression ")"

array: "[" [expression ("," expression)*] "]"

?lookup: "lookup(" string ")" -> lookup
       | IDENT -> lookup

?string: "'" STRING "'" -> string
       | "''"  -> string

IDENT: /[a-zA-Z][a-zA-Z0-9_]*/
STRING: /((`['`])|([^']))+/
BOOL: /True|False/

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

#: Object for parsing the transformer strings and producing a tree
parser = lark.Lark(_grammar)
