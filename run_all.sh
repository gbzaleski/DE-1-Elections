#! /bin/bash

./start_minio.sh

./scrape.py
./transform.py

./stop_minio.sh