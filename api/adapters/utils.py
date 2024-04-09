from enum import Enum
from typing import Type, Union, Dict

from api.adapters.base import AbstractRepositoryMetadataAdapter


class RepositoryType(str, Enum):
    HYDROSHARE = 'HYDROSHARE'
    S3 = 'S3'


_adapter_registry: Dict[RepositoryType, Type[AbstractRepositoryMetadataAdapter]] = {}


def register_adapter(repository_type: RepositoryType, adapter_class: Type[AbstractRepositoryMetadataAdapter]) -> None:
    _adapter_registry[repository_type] = adapter_class


def get_adapter_by_type(repository_type: RepositoryType) -> Union[AbstractRepositoryMetadataAdapter, None]:
    adapter_cls = _adapter_registry.get(repository_type, None)
    if adapter_cls:
        return adapter_cls()
    return None


def get_s3_object_url_path(endpoint_url: str, file_path: str, bucket: str) -> str:
    endpoint_url = endpoint_url.rstrip("/")
    if endpoint_url.endswith("amazonaws.com"):
        return f"{endpoint_url}/{file_path}"
    return f"{endpoint_url}/{bucket}/{file_path}"
