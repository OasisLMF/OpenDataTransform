Creating Data Connections
=========================

Each data connection should implement 3 methods, a constructor, `extract` and
`load`.

A `BaseConnector` exists at `converter.connector.BaseConnector` which should be
used as a base class for all data connections. This implements a constructor for
the connector that takes the provided options and stores them in the `options`
property but this method should be overridden for handling specific options and
providing default values.

The `extract` accepts no arguments. It takes data from the source and passes it
into the system. It should return an iterable where each entry is a row of data
represented as a dictionary of key value pairs. To allow for large data sets this
should be a python generator object rather than returning a list containing all
elements.

The `load` method takes one argument which is an iterable of data rows represented
by dictionaries of key value pairs. It should take each row and add them to the
target. The input data may be a list or any other iterable and you should not
assume the inbound can be iterated over multiple times.
