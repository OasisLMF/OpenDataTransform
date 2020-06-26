.. _transformerlanguage:

Transformer Language
====================

The transformer language allows for complex data transformations to be defined
in the mapping files by looking up values in the row and applying mathematical
operations to them.

Primitive Types
---------------

The transformer language supports the following primitive types:

* integers - Any number without a decimal point, can be positive or negative.
  Valid integers include `123` and `-45`.
* floats - Any number with a decimal point or written in e-notation format, can be
  positive or negative. Valid floats include `12.3`, `-45.6` and `7.8e9`.
* strings - Any characters withing single quotes (`'`). If a single quote character
  is needed in the string it must be escaped using a backtick (`\``) which must
  also be escaped with a backtick is required in a string. For example the string
  `must escape ' and \`` would be represented as `'must escape \`' and \`\`'`.
  Valid strings include `'foo bar'`, `''` and `'baz\`'s bar'`.

Column Lookup
-------------

To act on columns you must lookup their value from the row, this can be done in 2
ways:

1. If the name of the column only contains alphanumeric character and underscores
   (`_`) then simply using the name of the column will get the lookup value. The
   name must start with an upper or lowecase letter. Valid column names include
   `firstCol` and `column_2`. `column 3` would be invalid as it contains a space
   and `4thColumn` would be invalid as it doesn't start with a letter.
2. If your columns name is not a valid name then you can use the `lookup` function
   which allows you to lookup any valid string. Using the `lookup` function
   `lookup('column 3')` and `lookup('4thColumn')` are both valid lookups.

Operations
----------

The transformation language supports combining columns with other columns or
primitive values by using mathematics operators (`+-*/`). Operations are performed
in the expected order, multiplication and division are applied before addition and
subtraction unles operations are surrounded by brackets. For example `1 + foo * 2`
will multiple column `foo` by 2 then add 1 to the result, whereas `(1 + foo) * 2`
will add 1 to column `foo` and then multiply the result by 2.
