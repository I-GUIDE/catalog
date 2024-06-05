from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from beanie import Document, Link, PydanticObjectId
from pydantic import HttpUrl, BaseModel

if TYPE_CHECKING:
    # this avoids circular imports
    from api.adapters.utils import RepositoryType


class SubmissionType(str, Enum):
    HYDROSHARE = 'HYDROSHARE'
    S3 = 'S3'
    IGUIDE_FORM = 'IGUIDE_FORM'


class S3Path(BaseModel):
    path: str
    bucket: str
    endpoint_url: HttpUrl = 'https://api.minio.cuahsi.io'

    @property
    def identifier(self):
        endpoint_url = self.endpoint_url.rstrip("/")
        identifier = f"{endpoint_url}/{self.bucket}/{self.path}"
        return identifier

    @property
    def fetch_identifier(self):
        # This is the identifier that is used to fetch the file from S3
        return f"{self.endpoint_url}+{self.bucket}+{self.path}"


class Submission(Document):
    title: str = None
    authors: List[str] = []
    identifier: PydanticObjectId
    submitted: datetime = datetime.utcnow()
    url: HttpUrl = None
    repository: Optional[str]
    repository_identifier: Optional[str]
    s3_path: Optional[S3Path]


class User(Document):
    access_token: str
    orcid: str
    preferred_username: Optional[str]
    submissions: List[Link[Submission]] = []

    def submission(self, identifier: PydanticObjectId) -> Submission:
        return next(filter(lambda submission: submission.identifier == identifier, self.submissions), None)

    def submission_by_repository(self, repo_type: 'RepositoryType', identifier: str) -> Submission:
        return next(
            filter(
                lambda submission: submission.repository_identifier == identifier
                and submission.repository == repo_type,
                self.submissions,
            ),
            None,
        )
