from lark import lark


grammar = r"""
?start: expression

?expression: product
           | expression "+" product -> add
           | expression "-" product -> subtract

// product has priority 2 to fire before sum
?product: atom
        | product "*" atom -> multiply
        | product "/" atom -> divide

?atom: lookup
     | FLOAT -> float
     | INTEGER -> integer
     | string
     | "-" number -> negative
     | "(" expression ")"

?number: FLOAT -> float
       | INTEGER -> integer

?lookup: "lookup(" string ")" -> lookup
       | IDENT -> lookup

?string: "'" STRING "'" -> string
       | "''"  -> string

IDENT: /[a-zA-Z][a-zA-Z0-9]*/
STRING: /((`['`])|([^']))+/
FLOAT: /[0-9]+\.[0-9]*(e[-+]?[0-9]+)?|[0-9]+e[-+]?[0-9]+/
INTEGER: /[0-9]+/

%import common.WS
%ignore WS
"""

parser = lark.Lark(grammar)
