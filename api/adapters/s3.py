import json
from http import HTTPStatus
from typing import Type

import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError as S3ClientError

from api.adapters.base import (
    AbstractRepositoryMetadataAdapter,
    AbstractRepositoryRequestHandler,
)
from api.adapters.utils import RepositoryType, register_adapter
from api.exceptions import RepositoryException
from api.models.catalog import T
from api.models.user import Submission


class _S3RequestHandler(AbstractRepositoryRequestHandler):
    def get_metadata(self, record_id: str) -> dict:
        endpoint_url = record_id.split("+")[0]
        bucket_name = record_id.split("+")[1]
        file_key = record_id.split("+")[2]

        # TODO: Should we be expecting the path for the data file and then compute the metadata file path from that?
        #  Or should we be expecting the metadata file path directly? May be we should get path for both
        #  data file and metadata file. If have the path for the data file we can check that the data file
        #  exists and then retrieve the metadata file and catalog the metadata.

        # check if the endpoint URL is an AWS S3 URL
        if endpoint_url.endswith("amazonaws.com"):
            endpoint_url = None
        s3 = boto3.client(
            "s3", config=Config(signature_version=UNSIGNED), endpoint_url=endpoint_url
        )
        try:
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
        except S3ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey":
                raise RepositoryException(
                    detail=f"Specified metadata file was not found in S3: {bucket_name}/{file_key}",
                    status_code=HTTPStatus.NOT_FOUND
                )
            else:
                err_msg = f"Error accessing S3 file({bucket_name}/{file_key}): {str(ex)}"
                raise RepositoryException(detail=err_msg, status_code=HTTPStatus.BAD_REQUEST)

        json_content = response["Body"].read().decode("utf-8")
        # parse the JSON content
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as ex:
            err_msg = f"Invalid JSON content in S3 file ({file_key}). Error: {str(ex)}"
            raise RepositoryException(detail=err_msg, status_code=HTTPStatus.BAD_REQUEST)

        # remove additionalType field - this will be set by the schema model
        data.pop("additionalType", None)
        return data


class S3MetadataAdapter(AbstractRepositoryMetadataAdapter):
    repo_api_handler = _S3RequestHandler()

    @staticmethod
    def to_catalog_record(metadata: dict, meta_model_type: Type[T]) -> T:
        return meta_model_type(**metadata)

    @staticmethod
    def to_repository_record(catalog_record: T):
        """Converts dataset catalog record to repository resource/dataset metadata"""
        raise NotImplementedError

    @staticmethod
    def update_submission(submission: Submission, repo_record_id: str) -> Submission:
        """Sets additional hydroshare specific metadata to submission record"""

        submission.repository_identifier = repo_record_id
        submission.repository = RepositoryType.S3
        return submission


register_adapter(RepositoryType.S3, S3MetadataAdapter)
