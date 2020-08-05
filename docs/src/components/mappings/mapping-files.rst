Mapping Files
=============

Mapping files describe how to convert between 2 formats, they are yaml files that
take the following form::

    bases:
      - ...
    input_format: ...
    output_format: ...
    forward:
      types:
        <input>:
          type: <int|float|string>
          nullable: <true|false>
          null_values:
            - ...
        ...
      null_values:
        - ...
      transform:
        <target>:
          - transformation: ...
            when: ...
          - ...
        ...
    reverse:
      types:
        <input>:
          type: <int|float|string>
          nullable: <true|false>
          null_values:
            - ...
        ...
      null_values:
        - ...
      transform: ...
        <target>:
          - transformation: ...
            when: ...
          - ...
        ...

Each file is designed to allow moving from the input format to the output format
and back again. In the mapping files the concept of 'forward' is moving from the
:code:`input_format` to the :code:`output_format` and 'reverse' is transforming from
the :code:`output_format` to the :code:`input_format`.

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

`input_format`/`output_format`
------------------------------

These fields are required if no :code:`bases` are set or if no bases provide a value.
The input and output format are strings that tell the system which formats are
handled by the conversion.

`forward`/`reverse`
-------------------

The forward and reverse sections describe how the converter should handle converting
data in both directions. These are optional but should be provided by the bases or
in the mapping file for the converter to have any effect. Each section has a set of
properties:

* **null_values**: A list of values to be considered as null when processing input
  types. If no type is specified for the input field this will be ignored. If a
  :code:`null_types` is set for a specific field that will be used over this.

  If :code:`null_types` is set on any bases, they are all merged with the ones
  specified here.

* **types**: Describes the types of values for each column in the input data. This
  is a mapping of input field name to a set of properties, these are **type** which
  should be one of :code:`'int'`, :code:`'float'` or :code:`'string'`, **nullable**
  which is a boolean flag that states whether a value should be checked against the
  :code:`null_values` and **null_values** which overrides the :code:`null_values`
  in the parent section.

  If :code:`types` are present in any of the bases they are all merged together
  preferring the later parents and this mapping file.

* **transform**: Mappings that map the output field name to a list of possible
  transformations. For each field there is a required :code:`transformation`
  property and an optional :code:`when` parameter both of which are written in the
  :ref:`transformer language <transformerlanguage>`. The :code:`transformation`
  property describes the result of the transformation which will be stored in the
  :code:`<target>` property in the output. If provided the `when` property describes
  when the particular transformer should be applied, if it is not provided this is
  assumed to be always. If multiple transforms should be applied because all of
  their :code:`when` properties resolve to :code:`True` then the first transform
  that appears for the target will be applied.

  If :code:`transform` are present in any of the bases they are all merged together
  preferring the later parents and this mapping file.

  To add a default fallback value add a transformation to the end of the transform
  list that has a :code:`transformation` and no :code:`when` clause. This will
  always resolve and only after all other transformations have been skipped due to
  their :code:`when` clause failing.
