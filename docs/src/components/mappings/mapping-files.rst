Mapping Files
=============

Mapping files describe how to convert between 2 formats, they are yaml files that
take the following form::

    bases:
      - ...
    inputFormat: ...
    outputFormat: ...
    forwardTransform:
      <target>:
        - transformer: ...
          when: ...
        - ...
      ...
    reverseTransform: ...
      <target>:
        - transformer: ...
          when: ...
        - ...

Each file is designed to allow moving from the input format to the output format
and back again. In the mapping files the concept of 'forward' is moving from the
`inputFormat` to the `outputFormat` and 'reverse' is transforming from the
`outputFormat` to the `inputFormat`.

Each of the fields in the mapping file is described below.

`bases`
-------

This is an optional field that allows for existing mappings to be extended in the
case that there are similarities between the 2 formats.

If it is present each of the bases are merged taking fields from the later files
if present. The merging of each field is described in further detail below.

The value of bases (if present) should be a list of strings that are either names
of existing mappings in the standard mapping library or in one of the provided
mapping directories. If there is any ambiguity in which mapping file to use the
file provided in the last provided mapping directory will be used with custom
mapping paths being used over the standard library.

`inputFormat`/`outputFormat`
----------------------------

These fields are required if no `bases` are set or if no bases provide a value.
The input and output format are strings that tell the system which formats are
handled by the conversion.

`forwardTransform`/`reverseTransform`
-------------------------------------

.. note:: The `when` property is currently not implemented and the docs are
          here as a placeholder for how it has been proposed it will work.

These are optional but should be provided by the bases or in the mapping file for
the converter to have any effect. When `bases` are provided the entries for each
target field will be used and will be overwritten by a matching field in later
bases or the mapping file.

The `forwardTransform` and `reverseTransform` entries are both mappings that map
the output field name to a list of possible transformations.

For each field each transformation has a required `transformer` property and an
optional `when` parameter both of which are written in the
:ref:`transformer language <transformerlanguage>`. The `transformer` property
describes the result of the transformation which will be stored in the `<target>`
property in the output. If provided the `when` property describes when the
particular transformer should be applied, if it is not provided this is assumed to
be always. If multiple transforms should be applied because all of their `when`
properties resolve to `True` then the first transform that appears for the target
will be applied.
