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

?comparison: atom
           | atom "is" atom -> eq
           | atom "is not" atom -> not_eq
           | atom "is in" array -> is_in
           | atom "is not in" array -> not_in
           | atom "gt" atom -> gt
           | atom "gte" atom -> gte
           | atom "lt" atom -> lt
           | atom "lte" atom -> lte

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
