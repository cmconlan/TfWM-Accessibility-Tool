# TfWM-Accessibility-Tool ![unit tests](https://github.com/cmconlan/TfWM-Accessibility-Tool/workflows/Python%20unit%20tests/badge.svg)
Development repository for the development of the accessibility tool for Transport for West Midlands.

## Directory Structure
- `config/base` - contains YAML files for configuring the model, and what data files are created in which tables.
- `doc` - contains documentation for modelling, Postgres setup, and the webserver backend.
- `otp` - files required for running [Open Trip Planner](https://www.opentripplanner.org/).
- `reference` - contains the OpenAPI documentation for the RESTful API provided by the backend, created using [stoplight.io studio](https://stoplight.io/studio/).
- `sql` - contains a number of SQL statements within files. The base level queries are Postgres compatible, with MySQL and SQLite compatible queries residing in their respective folders.
- `src` - contains the Python source for the ETL and modelling process, largely adapted from the previous project [repository](https://github.com/alan-turing-institute/DSSG19-WMCA-PUBLIC). Also contains the source code for the RESTful API in `src/www`.