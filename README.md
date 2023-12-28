# Erection project

## Step 1:

Scrape the data from the website https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach/ and save it in a csv file
to minio.


## Step 2:

Read thedata from minio stored csv files and retrieve any interesting transformations from the data.
Saving them back to minio in different files.

TODO: Connecting and communicatiing with minio
TODO: Move Martinez's implementation of methods to subclasses of Apportionment
TODO: Consider using different type for additional data Dict[Any, Any], maybe a List of Dicts.
But keep one standard so we can use the same saving to file method for all of them.

Propositions of methods and their additional info:
* ...

## Step 3:

Inside of a jupyter notebook, read the data from minio and create a dashboard with the data.

TODO: Create some interesting visualizations of results


Propositions of visualizations:
* ...
