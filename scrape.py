#!/usr/bin/env python
import minio
import os
import shutil
import tempfile
import urllib.request
import zipfile

from typing import List, Tuple


YEARS = [2019, 2023]
BASE_KAND = "http://wybory.gov.pl/sejmsenat{}/data/csv/wyniki_gl_na_kandydatow_po_obwodach_sejm_csv.zip"
BASE_RES = "http://wybory.gov.pl/sejmsenat{}/data/csv/wyniki_gl_na_listy_po_obwodach_sejm_csv.zip"


def temporary_direrctory() -> str:
    """Create temporary directory and return path to it."""
    return tempfile.mkdtemp()

def remove_directory(path: str) -> None:
    """Removes directory."""
    shutil.rmtree(path)

def download_file(url: str, path: str) -> None:
    """Download file from url and save it to path."""
    filename = url.split("/")[-1]
    urllib.request.urlretrieve(url, path + "/" + filename)

def unzip_all_files(path: str) -> None:
    """Unzip all files in directory."""
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".zip"):
                file_path = os.path.join(root, file)
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(root)

def load_csv_files(path: str) -> List[Tuple[str, str]]:
    """Load all csv files in directory and return list of tuples with file name and content."""
    csv_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    csv_files.append((file, f.read()))
    return csv_files

def init_minio() -> minio.Minio:
    key = os.environ["MINIO_ACCESS_KEY"]
    secret = os.environ["MINIO_SECRET_KEY"]
    pass

def upload_csv_files(minio_client: minio.Minio, csv_files: List[Tuple[str, str]]) -> None:
    pass

def main() -> None:
    directory = temporary_direrctory()
    for year in YEARS:
        download_file(BASE_KAND.format(year), directory)
        download_file(BASE_RES.format(year), directory)
    unzip_all_files(directory)
    csv_files = load_csv_files(directory)
    remove_directory(directory)

    print(csv_files)

    minio_client = init_minio()
    upload_csv_files(minio_client, csv_files)


if __name__ == "__main__":
    main()
