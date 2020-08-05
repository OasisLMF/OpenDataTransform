Runners
=======

Each runner handles taking the input data from the extractor, applying each
transformation and passing the transformed data onto the loader. The base runner
handles all dictionary like rows but can be reimplemented to handle running the
transformations in any architecture (such as the :code:`PandasRunner`).

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
