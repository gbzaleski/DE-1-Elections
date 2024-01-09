#!/usr/bin/env python
import minio
import os
import shutil
import tempfile
import urllib.request
import zipfile

from typing import List, Tuple

import minio_communication

from consts import LINKS_BY_YEAR


def temporary_direrctory() -> str:
    """Create temporary directory and return path to it."""
    return tempfile.mkdtemp()


def remove_directory(path: str) -> None:
    """Removes directory."""
    shutil.rmtree(path)


def download_file(url: str, path: str) -> None:
    """Download file from url and save it to path."""
    filename = url.split("/")[-1]
    print(f"Downloading {filename} to {path}")
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
                    csv_files.append((file_path, f.read()))
    return csv_files


def upload_csv_files(minio_client: minio.Minio, year: int, csv_files: List[Tuple[str, str]]) -> None:
    bucket_name = minio_communication.get_minio_bucket_configuration(year).raw_data_bucket
    minio_communication.create_bucket_if_not_exist(minio_client, bucket_name)
    obj_names = set()
    for (csv_file_path, _) in csv_files:
        obj_name = os.path.basename(csv_file_path)
        if obj_name in obj_names:
            raise ValueError(f"Multiple files with same basename {obj_name}")
        obj_names.add(obj_name)
        minio_communication.upload_file(minio_client, bucket_name, obj_name, csv_file_path)


def main() -> None:
    directory = temporary_direrctory()
    minio_client = minio_communication.get_client()

    for year in LINKS_BY_YEAR:
        year_dirname = os.path.join(directory, str(year))
        os.makedirs(year_dirname)

        for link in LINKS_BY_YEAR[year]:
            download_file(link, year_dirname)

        unzip_all_files(year_dirname)
        csv_files = load_csv_files(year_dirname)

        upload_csv_files(minio_client, year, csv_files)

    remove_directory(directory)


if __name__ == "__main__":
    main()
