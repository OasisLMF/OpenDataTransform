from lark import lark


_grammar = r"""
?start: expression

?expression: product
           | comparison
           | "not" comparison -> logical_not
           | expression "or" comparison -> logical_or
           | expression "and" comparison -> logical_and
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
     | NULL -> null
     | SIGNED_NUMBER -> number
     | "(" expression ")"
     | string_manip
     | regex

array: "[" [expression ("," expression)*] "]"

?lookup: "lookup(" string ")" -> lookup
       | IDENT -> lookup

?string_manip: "join(" string [("," expression)*] ")" -> str_join
             | "replace(" expression [("," pattern "," expression)+] ")" -> str_replace
             | "match(" expression "," pattern ")" -> str_match
             | "search(" expression "," pattern ")" -> str_search

?pattern: string
        | regex

?regex: "re" string -> regex
      | "ire" string -> iregex

?string: "'" STRING "'" -> string
       | "''"  -> string

IDENT: /[a-zA-Z][a-zA-Z0-9_]*/
STRING: /((`['`])|([^']))+/
BOOL: /True|False/
NULL: /Null/

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""  # noqa: E501
# ignore line length in this file as its not always possible to break lines
# on the grammar

#: Object for parsing the transformer strings and producing a tree
parser = lark.Lark(_grammar)
