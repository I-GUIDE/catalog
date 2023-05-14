import datetime

from beanie import Document

from .schema import CoreMetadata, Dataset


class CoreMetadataDOC(Document, CoreMetadata):

    class Settings:
        # name is the collection name in database (iguide) where the Metadata Record documents will be stored
        # for all metadata record types (e.g. dataset, geopackage, software etc.)
        name = "catalog"
        is_root = True
        bson_encoders = {
            datetime.date: lambda dt: datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0,
                                                        second=0)
        }


class DatasetMetadataDOC(Dataset, CoreMetadataDOC):
    pass
