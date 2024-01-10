#! /bin/bash

APPORTIONMENTS=(
    constituencial-dhondt constituencial-sainte-lague 
    global-dhondt global-sainte-lague 
    global-dhondt-no-threshold global-sainte-lague-no-threshold 
    constituencial-dhondt-no-threshold constituencial-sainte-lague-no-threshold 
    squared-dhondt fair-vote-weight-dhondt
)
YEARS=(2019 2023)

echo "Setting up the virtualenv..."
./setup.sh
source venv/bin/activate

echo "Starting Minio..."
./start_minio.sh

echo "Scraping..."
./scrape.py

for year in "${YEARS[@]}"
do
    for apportionment in "${APPORTIONMENTS[@]}"
    do
        echo "Running transform for $year $apportionment"
        ./transform.py --year $year --apportionment $apportionment
    done
done

echo "Stopping Minio..."
./stop_minio.sh

echo "Deactivating the virtualenv..."
deactivate
