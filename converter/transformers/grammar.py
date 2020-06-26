from lark import lark


_grammar = r"""
?start: expression

?expression: product
           | expression "+" product -> add
           | expression "-" product -> subtract

?product: atom
        | product "*" atom -> multiply
        | product "/" atom -> divide

?atom: lookup
     | FLOAT -> float
     | INTEGER -> integer
     | string
     | BOOL -> boolean
     | "-" number -> negative
     | "(" expression ")"

?number: FLOAT -> float
       | INTEGER -> integer

?lookup: "lookup(" string ")" -> lookup
       | IDENT -> lookup

?string: "'" STRING "'" -> string
       | "''"  -> string

IDENT: /[a-zA-Z][a-zA-Z0-9_]*/
STRING: /((`['`])|([^']))+/
FLOAT: /[0-9]+\.[0-9]*(e[-+]?[0-9]+)?|[0-9]+e[-+]?[0-9]+/
INTEGER: /[0-9]+/
BOOL: /True|False/

%import common.WS
%ignore WS
"""

#: Object for parsing the transformer strings and producing a tree
parser = lark.Lark(_grammar)
