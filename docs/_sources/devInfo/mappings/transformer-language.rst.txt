.. _transformerlanguage:

Transformer Language
====================

The transformer language allows for complex data transformations to be defined
in the mapping files by looking up values in the row and applying mathematical
operations to them.

Primitive Types
---------------

The transformer language supports the following primitive types:

* booleans - Either :code:`True` or :code:`False` to resolve to a true or false result
  respectively.
* null - :code:`Null` is used to specify that a result has no value but has been set by
  the transformation (this is treated as :code:`None` by the python code in the
  background).
* integers - Any number without a decimal point, can be positive or negative.
  Valid integers include :code:`123` and :code:`-45`.
* floats - Any number with a decimal point or written in e-notation format, can be
  positive or negative. Valid floats include :code:`12.3`, :code:`-45.6` and
  :code:`7.8e9`.
* strings - Any characters withing single quotes (:code:`'`). If a single quote
  character is needed in the string it must be escaped using a backtick (`````)
  which must also be escaped with a backtick is required in a string. For example
  the string :code:`must escape ' and `` would be represented as
  ``'must escape `' and ``'``. Valid strings include :code:`'foo bar'`,
  :code:`''` and ``'baz`'s bar'``.
* regular expressions - Regular expressions are strings that are preceded by :code:`re`
  (or `ire` for case insensitive regular expressions). For example :code:`re'.*'` will
  create a regular expression that matches all characters. The regex rules follow the
  same rules as the python regex rules which can be found
  `here <https://docs.python.org/3/howto/regex.html>`_.

Column Lookup
-------------

To act on columns you must lookup their value from the row, this can be done in 2
ways:

1. If the name of the column only contains alphanumeric character and underscores
   (:code:`_`) then simply using the name of the column will get the lookup value. The
   name must start with an upper or lowecase letter. Valid column names include
   :code:`firstCol` and :code:`column_2`. :code:`column 3` would be invalid as it
   contains a space and :code:`4thColumn` would be invalid as it doesn't start with a
   letter.
2. If your columns name is not a valid name then you can use the :code:`lookup` function
   which allows you to lookup any valid string. Using the :code:`lookup` function
   :code:`lookup('column 3')` and :code:`lookup('4thColumn')` are both valid lookups.

Operations
----------

The transformation language supports combining columns with other columns or
primitive values by using mathematics operators (:code:`+-*/`). Operations are performed
in the expected order, multiplication and division are applied before addition and
subtraction unless operations are surrounded by brackets. For example
:code:`1 + foo * 2` will multiple column :code:`foo` by 2 then add 1 to the result,
whereas :code:`(1 + foo) * 2` will add 1 to column `foo` and then multiply the result
by 2.

Groupings
---------

Takes a group of values to perform checks against them. Each expression is made from
the grouping type, a list and a boolean check eg. :code:`<group> [1, 2, 3] is 4`.

* all - Allows to check if all values pass the check. For example
  :code:`all [a, b, c] is 4` will return :code:`True` if columns :code:`a`, :code:`b`
  and :code:`c` are **all** :code:`4`.
* any - Allows to check if any values pass the check. For example
  :code:`any [a, b, c] is 4` will return :code:`True` if columns :code:`a`, :code:`b`
  or :code:`c` is :code:`4`.

String Manipulations
--------------------

A set of functions are supplied for manipulating string:

* :code:`join(separator, string1, string2, strings...)` - joins all the provided
  strings with separated by the :code:`separator` string. If any non strings are passed
  into the the function they will be converted into strings first.
* :code:`replace(target, pattern, repl, [pattern, repl]...)` - replaces :code:`pattern`
  in :code:`target` with :code:`repl`. Multiple :code:`pattern` and :code:`repl`
  pairs can be supplied and each will be applied in the order they are given.
  :code:`pattern` can be either a regular expression or string. If it's a regular
  expression groups can be used and they will be available for use in :code:`repl`.
* :code:`match(target, pattern)` - checks if the :code:`target` string matches the
  :code:`pattern`, if they match the result is :code:`True` otherwise :code:`False`.
  :code:`pattern` may be either a string or regular expression. If a regular expression
  is used it must match the full string, if a string is used it is the same as
  :code:`value is <pattern>`.
* :code:`search(target, pattern)` - checks if the :code:`pattern` string is in the
  :code:`target`, if they it is the result is :code:`True` otherwise :code:`False`.
  :code:`pattern` may be either a string or regular expression.
