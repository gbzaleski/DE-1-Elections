import dataclasses
import os

import minio

from consts import *


def _get_minio_endpoint_str() -> str:
    minio_server = os.environ.get("MINIO_SERVER_URL", MINIO_DEFAULT_SERVER_URL)
    return minio_server

def _get_minio_access_key() -> str:
    key = os.environ.get("MINIO_ACCESS_KEY", MINIO_DEFAULT_USER)
    return key

def _get_minio_secret_key() -> str:
    secret = os.environ.get("MINIO_SECRET_KEY", MINIO_DEFAULT_PASSWORD)
    return secret

def create_bucket_if_not_exist(minio_client: minio.Minio, minio_bucket_name: str):
    if not minio_client.bucket_exists(minio_bucket_name):
        minio_client.make_bucket(minio_bucket_name)

def upload_file(minio_client: minio.Minio, minio_bucket_name: str, object_name: str, filepath_local: str):
    minio_client.fput_object(minio_bucket_name, object_name, filepath_local)

def get_client() -> minio.Minio:
    return minio.Minio(
        _get_minio_endpoint_str(),
        access_key=_get_minio_access_key(),
        secret_key=_get_minio_secret_key(),
        secure=False,
    )


@dataclasses.dataclass(frozen=True)
class MinioBucketConfigurationForYear:
    raw_data_bucket: str
    transformed_data_bucket: str

def get_minio_bucket_configuration(year: int) -> MinioBucketConfigurationForYear:
    return MinioBucketConfigurationForYear(
        raw_data_bucket="raw-data-{}".format(year),
        transformed_data_bucket="transformed-data-{}".format(year)
    )
