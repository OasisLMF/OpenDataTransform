Runners
=======

Each runner handles taking the input data from the extractor, applying each
transformation and passing the transformed data onto the loader. The base runner
handles all dictionary like rows but can be reimplemented to handle running the
transformations in any architecture (such as the :code:`PandasRunner`).

.. note:: The runner expects the extractor to provide data on a row by row basis,
          if multiple sources need to be queried to produce the extracted data
          they must be merged together to produce complete rows (using sql joins
          for example). Similarly, when loading the data connection will receive
          rows containing complete records and it's the job of the connection to
          transform them into multiple queries if multiple tables or databases
          should be updated.

Coercing data types
-------------------

Coercing the rows data types is handled in the runner rather than the extractor.
While it may make sense to handle this in the loader it is handled in the runner
so that efficiencies can be gained from distributing the conversion across the
architecture.

In the base runner this is handles in the :code:`apply_transformation_set` method.
If you override this method you should call :code:`coerce_row_types`.

If you want to change how the type transformation is handled across the architecture,
reimplement :code:`coerce_row_types`.
