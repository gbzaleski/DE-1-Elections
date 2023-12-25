import dataclasses
import os

import minio



def _get_minio_endpoint_str() -> str:
    minio_server = os.environ.get("MINIO_SERVER_URL", "localhost:9000")
    return minio_server
    # minio_port = os.environ.get("MINIO_ENDPOINT_PORT", "9000")
    # minio_endpoint_host = os.environ.get("MINIO_ENDPOINT_HOST", "localhost")
    # return minio_endpoint_host + ":" + minio_port

def _get_minio_access_key() -> str:
    key = os.environ["MINIO_ACCESS_KEY"]
    return key

def _get_minio_secret_key() -> str:
    secret = os.environ["MINIO_SECRET_KEY"]
    return secret

def create_bucket_if_not_exist(minio_client: minio.Minio, minio_bucket_name: str):
    if not minio_client.bucket_exists(minio_bucket_name):
        minio_client.make_bucket(minio_bucket_name)

async def upload(minio_client: minio.Minio, minio_bucket_name: str, object_name: str, filepath_local: str):
    minio_client.fput_object(minio_bucket_name, object_name, filepath_local)

def get_client() -> minio.Minio:
    return minio.Minio(
        _get_minio_endpoint_str(),
        access_key=_get_minio_access_key(),
        secret_key=_get_minio_access_key(),
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




