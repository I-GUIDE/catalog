import json

import boto3
from botocore.exceptions import ClientError as S3ClientError
from botocore.client import Config
from botocore import UNSIGNED

from api.adapters.base import AbstractRepositoryMetadataAdapter, AbstractRepositoryRequestHandler
from api.adapters.utils import RepositoryType, register_adapter
from api.models.catalog import NetCDFMetadataDOC
from api.models.user import Submission


class _S3RequestHandler(AbstractRepositoryRequestHandler):

    def get_metadata(self, record_id: str):
        endpoint_url = record_id.split("+")[0]
        bucket_name = record_id.split("+")[1]
        file_key = record_id.split("+")[2]
        # TODO: Should we be expecting the path for the data file and then compute the metadata file path from that?
        #  Or should we be expecting the metadata file path directly? May be we should get path for both
        #  data file and metadata file. If have the path for the data file we can check that the file
        #  exists and then retrieve the metadata file and catalog the metadata.

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), endpoint_url=endpoint_url)
        try:
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
        except S3ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Expected metadata file not found in S3 bucket: {bucket_name}/{file_key}")
            else:
                raise ex

        json_content = response['Body'].read().decode('utf-8')
        # parse the JSON content
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as ex:
            raise ValueError(f"Invalid JSON content in S3 file ({file_key}). Error: {str(ex)}")

        # remove additionalType field - this will be set by the schema model
        data.pop('additionalType', None)

        return data


class S3MetadataAdapter(AbstractRepositoryMetadataAdapter):
    repo_api_handler = _S3RequestHandler()

    # TODO: Need to support multiple metadata types - NetCDF, Raster, GenericDataset
    @staticmethod
    def to_catalog_record(metadata: dict) -> NetCDFMetadataDOC:
        return NetCDFMetadataDOC(**metadata)

    @staticmethod
    def to_repository_record(catalog_record: NetCDFMetadataDOC):
        """Converts dataset catalog record to hydroshare resource metadata"""
        raise NotImplementedError

    @staticmethod
    def update_submission(submission: Submission, repo_record_id: str) -> Submission:
        """Sets additional hydroshare specific metadata to submission record"""

        submission.repository_identifier = repo_record_id
        submission.repository = RepositoryType.S3
        return submission


register_adapter(RepositoryType.S3, S3MetadataAdapter)
