Reporting
================================

Reporting on transformations being conducted for testing or operationally is valuable to trace any issues in analyses, and to assist the ongoing testing development of this open data transformation framework.

No data is reported centrally or automatically by the framework - all outputs are only stored locally, by default. Users are encouraged to report via the GitHub repo any issues that cause errors in their transformations.


Portfolio metadata
----------------------

Portfolio metadata allows users to record the transformations being conducted. It includes data, analyst, and context about the nature of the portfolio - region(s), peril(s), line(s) of business, complexity of the data in terms of limit and deductible types included. This information also 

**[show image/content of metadata]**

Data validation
----------------------

Data validation has been included in the framework to provide a transparent check on how the output data relates to input data - for example, has all TIV been transformed and has it been assigned to the correct accounts, modifiers, regions, perils, and currencies as expected by the analyst.

A data validation file defines the fields to include in validation, the operators (e.g., sum, max, count, etc) and any grouping to apply. For example, a user may want to compare the input and output file total TIV grouped by occupancy, the sum of buildings TIV by currency and region, or the number (count) of accounts per peril.

**[show image/content of a validation file]**

Data validation file templates are provided in GitHub, for direct use or adaptation by the user.
