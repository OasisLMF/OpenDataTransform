Configuration
=============

The converter tool is configurable by environment variable, on the
command line and by configuration file.

The configuration is taken from the configuration sources in the
following order (in increasing precedence).

1. Command Line
2. Environment
3. Configuration file

The configuration and file has the following schema::

    extractor:
        path: <str>
        options:
            <str>: <any>
            ...
    runner:
        path: <str>
        options:
            <str>: <any>
            ...
    mapping:
        path: <str>
        options:
            input_format: <str>
            output_format: <str>
            <str>: <any>
            ...
    loader:
        path: <str>
        options:
            <str>: <any>
            ...

The only required configuration options are
:code:`mapping.options.input_format` and
:code:`mapping.options.output_format` although each :code:`extractor`,
:code:`runner`, :code:`mapping` and :code:`loader` may require
specific properties.

For each element the :code:`path` property is a python path to a valid
python class.

Environment Configuration
-------------------------

To set a configuration option on the environment, create a variable
that starts with :code:`CONVERTER_` and add the path to the option
to be set.

For example, to set the path to the extractor as an environment
variable use::

    export CONVERTER_EXTRACTOR_PATH=<path>

In the options configuration for a particular component you can nest
further levels of configuration by adding :code:`_` between nested
levels. For example::

    export CONVERTER_EXTRACTOR_OPTIONS_FOO_BAR=bash

will resolve to the following configuration::

    extractor:
        options:
            foo:
                bar: bash


CLI Configuration
-----------------

To set configuration variables on the command line use the :code:`-o`
option on the command. This option takes 2 values, the option path
and option value.

The option path is specified in a similar way to the environment
variables but each level of nesting is separated by :code:`.`
rather than :code:`_`.

To build the same configuration as in the environment example you
would use::

    converter -o extractor.options.foo.bar bash run

Debugging
=========

To debug you r configuration you can use the `show-config` command.
This will print the fully resolved config to the console.