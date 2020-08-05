Welcome to Oasis Data Converter's documentation!
================================================

The Oasis Data converter is designed to be able to convert from one data format
to another as long as both formats can be expressed as an iterable of dictionaries.

The convert is broken down into several swappable components:

* Data Connections for specifying how the input and output data should be
  processed by the system.
* Mapping describing how the fields should be transformed to between formats.
* The Runner which takes the  the input connection, transforms the data using the
  mapping and passed the transformed data onto the output connection.

Each of these components are configurable and even swappable to some new
implementation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   config.rst
   components/data-connections/index.rst
   components/mappings/index.rst
   components/runners/index.rst
   components/cli/index.rst
   package/index.rst
