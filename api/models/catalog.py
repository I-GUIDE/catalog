import datetime
from typing import TypeVar

from beanie import Document

from api.models.user import Submission
from .schema import (
    CoreMetadata,
    GenericDatasetMetadata,
    HSResourceMetadata,
    HSNetCDFMetadata,
    HSRasterMetadata,
)


class CoreMetadataDOC(Document, CoreMetadata):
    class Settings:
        # name is the collection name in database (iguide) where the Metadata Record documents will be stored
        # for all metadata record types (e.g. dataset, geopackage, software etc.)
        name = "catalog"
        is_root = True
        bson_encoders = {
            datetime.date: lambda dt: datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, second=0
            ),
            datetime.datetime: lambda dt: datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute, second=dt.second
            )
        }

    def as_submission(self) -> Submission:
        return Submission(
            title=self.name,
            authors=[creator.name for creator in self.creator],
            submitted=datetime.datetime.utcnow(),
            identifier=self.id,
            url=self.url,
        )


class HSResourceMetadataDOC(CoreMetadataDOC, HSResourceMetadata):
    repository_identifier: str = None

    def as_submission(self) -> Submission:
        submission = super().as_submission()
        submission.repository = "HydroShare"
        submission.repository_identifier = self.repository_identifier
        return submission


class GenericDatasetMetadataDOC(CoreMetadataDOC, GenericDatasetMetadata):
    repository_identifier: str = None


class NetCDFMetadataDOC(CoreMetadataDOC, HSNetCDFMetadata):
    repository_identifier: str = None


class RasterMetadataDOC(CoreMetadataDOC, HSRasterMetadata):
    repository_identifier: str = None


# T is a type variable that can be used for type hinting for any schema model that inherits from CoreMetadataDOC

T = TypeVar("T", bound=CoreMetadataDOC)
