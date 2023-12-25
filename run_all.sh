#! /bin/bash

./setup.sh
source venv/bin/activate

./start_minio.sh

./scrape.py
# ./transform.py

./stop_minio.sh

deactivate