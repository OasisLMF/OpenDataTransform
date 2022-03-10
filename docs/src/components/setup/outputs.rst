Outputs
=========

The transformation will produce:

Output data
-------------

Data is transformed to the destination format defined in the configuration and mapping files, and saved as .csv files. One file is saved for each account, location, and reinsurance as required by the destination format. The destination file name and path are defined by the user in configuration. 



Log file
----------

A log file, named *<date>-<time>--converter.log*, is produced, containing the configuration information and confirmation of of successful transformation, or a record of errors encountered.


.. image:: ../../docs_img/example_logfile.png
  :width: 600
  :alt: En example log file



Data validation files
-----------------------

A data validation file, containing a comparison of various metrics in both the input file and output file. For example, the sum of Total Insured Value grouped by Occupancy Type and Currency. The fields and operations are defined by the user in the validation definition files. 

After running the transformation there will be a validation log in the log directory (named like 
`<run-timestamp>-validation.yaml`). 

* `Example of validation without grouping <https://github.com/OasisLMF/OpenDataTransform/tree/master/examples/demonstration/validation>`_
* `Example of validation with grouping <https://github.com/OasisLMF/OpenDataTransform/tree/master/examples/demonstration/validation-groups>`_


Portfolio metadata
---------------------

Data describing the portfolio, entered in the user interface, is reported out to the log file. This is useful for keeping a record of transformations performed, especially summary or high-level contextual information.






