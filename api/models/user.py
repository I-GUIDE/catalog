from datetime import datetime
from typing import List, Optional

from beanie import Document, Link, PydanticObjectId
from pydantic import HttpUrl


class Submission(Document):
    title: str = None
    authors: List[str] = []
    identifier: PydanticObjectId
    submitted: datetime = datetime.utcnow()
    url: HttpUrl = None
    repository: Optional[str]
    repository_identifier: Optional[str]


class User(Document):
    access_token: str
    orcid: str
    preferred_username: Optional[str]
    submissions: List[Link[Submission]] = []

    def submission(self, identifier: PydanticObjectId) -> Submission:
        return next(filter(lambda submission: submission.identifier == identifier, self.submissions), None)
