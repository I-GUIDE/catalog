import abc
from typing import Type
from api.config import Settings, get_settings
from api.models.catalog import T
from api.models.user import Submission


class AbstractRepositoryRequestHandler(abc.ABC):
    settings: Settings = get_settings()

    @abc.abstractmethod
    def get_metadata(self, record_id: str) -> dict:
        """Returns the metadata for the specified record from a repository"""
        ...


class AbstractRepositoryMetadataAdapter(abc.ABC):
    repo_api_handler: AbstractRepositoryRequestHandler

    @staticmethod
    @abc.abstractmethod
    def to_catalog_record(metadata: dict, meta_model_type: Type[T]) -> T:
        """Converts repository metadata to a catalog dataset record"""
        ...

    @staticmethod
    @abc.abstractmethod
    def to_repository_record(catalog_record: T):
        """Converts dataset catalog dataset record to repository metadata"""
        ...

    @staticmethod
    @abc.abstractmethod
    def update_submission(submission: Submission, repo_record_id: str) -> Submission:
        """Sets additional repository specific metadata to submission record"""
        ...

    async def get_metadata(self, record_id: str) -> dict:
        """Returns the metadata for the specified record from a repository"""

        return self.repo_api_handler.get_metadata(record_id)
