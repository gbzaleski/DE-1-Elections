# Elections Data Engineering project

## Step 1:

Scrape the data from the website https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach/ and save it in a csv file
to minio.


## Step 2:

Read thedata from minio stored csv files and retrieve any interesting transformations from the data.
Saving them back to minio in different files.

Methods:
* Constituencial DHondt
* Global DHondt
* Constituencial Sainte-Lague
* Global Sainte-Lague
* Squared DHondt
* Fair Vote Weight DHondt
* Constituencial DHondt without thresholds
* Constituencial Sainte-Lague without thresholds

## Step 3:

Inside of a jupyter notebook, read the data from minio and create a dashboard with the data.

