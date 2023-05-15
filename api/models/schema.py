import re
from datetime import date, datetime


from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


class CreativeWork(BaseModel):
    type: str = Field(alias="@type", const=True, default="CreativeWork")
    name: str


class PropertyValue(BaseModel):
    id: HttpUrl = Field(alias="@id")
    type: str = Field(alias="@type", const=True, default="PropertyValue")
    name: Optional[str]
    propertyID: Optional[HttpUrl]
    value: str
    url: HttpUrl


Identifier = Union[str, HttpUrl, PropertyValue]


class Person(BaseModel):
    type: str = Field(alias="@type", const=True, default="Person")
    name: str
    email: Optional[EmailStr]
    identifier: Optional[Union[Identifier, List[HttpUrl]]]


class Organization(BaseModel):
    type: str = Field(alias="@type", const=True, default="Organization")
    name: str
    url: Optional[HttpUrl]
    identifier: Optional[Union[Identifier, List[HttpUrl]]]
    address: Optional[str]  # Should address be a string or another constrained type?


class ProviderID(BaseModel):
    id: HttpUrl = Field(alias="@id")


class ProviderOrganization(Organization):
    parentOrganization: Optional[Organization]


class DefinedTerm(BaseModel):
    type: str = Field(alias="@type", const=True, default="DefinedTerm")
    name: str
    description: str


class KeywordTerm(DefinedTerm):
    inDefinedTermSet: HttpUrl


class HasPart(CreativeWork):
    description: str
    identifier: Identifier
    creator: Optional[Union[Person, Organization]]


class IsPartOf(HasPart):
    pass


class SubjectOf(CreativeWork):
    url: HttpUrl
    encodingFormat: str


class License(CreativeWork):
    url: HttpUrl


class LanguageEnum(str, Enum):
    eng = 'eng'
    esp = 'esp'


class Grant(BaseModel):
    type: str = Field(alias="@type", const=True, default="MonetaryGrant")
    name: str
    url: HttpUrl
    funder: Union[Person, Organization]


class TimeInterval(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        pass

    @classmethod
    def validate(cls, v):
        def parse_date(date_string):
            if len(date_string) == 10:
                parse_format = "%Y-%m-%d"
            elif len(date_string) == 7:
                parse_format = "%Y-%m"
            elif len(date_string) == 4:
                parse_format = "%Y"
            else:
                parse_format = "%Y-%m-%dT%H:%M:%SZ"
            try:
                datetime.strptime(date_string, parse_format)
            except ValueError:
                raise ValueError('invalid date format')

        if not isinstance(v, str):
            raise TypeError('string required')

        v = v.strip()
        if not v:
            raise ValueError('empty string')
        try:
            start, end = v.split('/')
        except ValueError:
            raise ValueError('invalid format')

        parse_date(start)
        if end != "..":
            parse_date(end)

        return v

    def __repr__(self):
        return f'TimeInterval({super().__repr__()})'


class GeoCoordinates(BaseModel):
    type: str = Field(alias="@type", const=True, default="GeoCoordinates")
    latitude: float
    longitude: float

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class GeoShape(BaseModel):
    type: str = Field(alias="@type", const=True, default="GeoShape")


class Line(GeoShape):
    line: str

    @validator('line')
    def validate_line(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        v = v.strip()
        if not v:
            raise ValueError('empty string')
        v_parts = v.split(' ')
        if len(v_parts) < 2:
            raise ValueError('Line must have at least 2 points')
        for item in v_parts:
            try:
                item = float(item)
            except ValueError:
                raise ValueError('Line point is not a number')
            item = abs(item)
            if item > 180:
                raise ValueError('Line point must be between -180 and 180')
        return v


class Polygon(GeoShape):
    polygon: str

    @validator('polygon')
    def validate_polygon(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        v = v.strip()
        if not v:
            raise ValueError('empty string')
        v_parts = v.split(' ')
        if len(v_parts) < 3:
            raise ValueError('Polygon must have at least 3 points')
        for item in v_parts:
            try:
                item = float(item)
            except ValueError:
                raise ValueError('Polygon point is not a number')
            item = abs(item)
            if item > 180:
                raise ValueError('Polygon point must be between -180 and 180')
        return v


class Place(BaseModel):
    type: str = Field(alias="@type", const=True, default="Place")
    name: Optional[str]
    address: Optional[str]
    geo: Optional[Union[Line, Polygon, GeoCoordinates]]


class MediaObject(BaseModel):
    type: str = Field(alias="@type", const=False, default="MediaObject")
    contentUrl: HttpUrl
    encodingFormat: str     # TODO enum for encoding formats
    contentSize: str
    name: str

    @validator('contentSize')
    def validate_content_size(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('empty string')

        match = re.match(r"([0-9.]+)([a-zA-Z]+$)", v.replace(" ", ""))
        if not match:
            raise ValueError('invalid format')

        size_unit = match.group(2)
        if size_unit.upper() not in ['KB', 'MB', 'GB', 'TB', 'PB', 'KILOBYTES', 'MEGABYTES',
                                     'GIGABYTES', 'TERABYTES', 'PETABYTES']:
            raise ValueError('invalid unit')

        return v


class CoreMetadata(BaseModel):
    context: HttpUrl = Field(alias='@context', default='https://schema.org')
    type: str = Field(alias="@type", const=True, default="Dataset")
    name: str = Field(description="The name or title of the record.")
    description: str = Field(description="The description or abstract of the record.")
    url: HttpUrl = Field(description="The url of the record.")
    identifier: List[Union[str, HttpUrl, PropertyValue]] = Field(description="Any kind of identifier for the record.")
    creator: List[Union[Person, Organization]] = Field(description="Person or organization that created the work.")
    dateCreated: Union[date, datetime] = Field(description="The date on which the work was created.")
    keywords: List[Union[KeywordTerm, str, HttpUrl]] = Field(min_items=1, description="Keywords or tags used to describe the dataset, delimited by commas.")
    license: Union[License, HttpUrl] = Field(description="A license document that applies to the content, typically indicated by a URL.")
    provider: Union[ProviderOrganization, Person, ProviderID] = Field(description="The service provider, service operator, or service performer.")
    publisher: Optional[Union[ProviderOrganization, Person, ProviderID]] = Field(description="The publisher of the record.")
    datePublished: Optional[Union[date, datetime]] = Field(description="Date of first publication for the record.")
    subjectOf: Optional[List[SubjectOf]] = Field(description="A CreativeWork about the record - e.g., a related metadata document describing the record.")
    version: Optional[Union[float, str]] = Field(description="The version of the record.")  # TODO find something better than float for number
    inLanguage: Optional[Union[LanguageEnum, str]] = Field(description="The language of the content of the record.")
    creativeWorkStatus: Optional[Union[DefinedTerm, str]] = Field(description="The status of a creative work in terms of its stage in a lifecycle. Example terms include Incomplete, Draft, Published, Obsolete. Some organizations define a set of terms for the stages of their publication lifecycle.")
    dateModified: Optional[Union[date, datetime]] = Field(description="The date on which the CreativeWork was most recently modified or updated.")
    funding: Optional[List[Grant]] = Field(description="A Grant that directly or indirectly provide funding or sponsorship for creation of the dataset.")
    temporalCoverage: Optional[TimeInterval] = Field(description="The temporalCoverage of a CreativeWork indicates the period that the content applies to, i.e. that it describes, either as a DateTime or as a textual string indicating a time period in ISO 8601 time interval format.")
    spatialCoverage: Optional[Place] = Field(description="The spatialCoverage of a CreativeWork indicates the place(s) which are the focus of the content. It is a subproperty of contentLocation intended primarily for more technical and detailed materials. For example with a Dataset, it indicates areas that the dataset describes: a dataset of New York weather would have spatialCoverage which was the place: the state of New York.")
    hasPart: Optional[List[HasPart]] = Field(description="Indicates an record or CreativeWork that is part of this record.")
    isPartOf: Optional[List[IsPartOf]] = Field(description="Indicates an record or CreativeWork that this record, or CreativeWork (in some sense), is part of.")
    associatedMedia: Optional[List[MediaObject]] = Field(description="A media object that encodes this CreativeWork. This property is a synonym for encoding.")


class Distribution(BaseModel):
    type: str = Field(alias="@type", const=True, default="DataDownload")
    name: str
    contentUrl: Optional[HttpUrl]
    encodingFormat: Optional[Union[str, list[str]]]
    contentSize: Optional[str]
    comment: Optional[str]


class VariableMeasured(BaseModel):
    type: str = Field(alias="@type", const=True, default="PropertyValue")
    name: str
    unitText: str


class IncludedInDataCatalog(BaseModel):
    type: str = Field(alias="@type", const=True, default="DataCatalog")
    name: str
    description: str
    url: HttpUrl
    identifier: Identifier
    creator: Union[Person, Organization]


class Dataset(BaseModel):
    distribution: Union[Distribution, List[Distribution]] = Field(description="A data distribution in the form of a dataset (see https://schema.org/Dataset for more information).")
    variableMeasured: Optional[Union[str, VariableMeasured, List[VariableMeasured]]] = Field(description="The variableMeasured property can indicate (repeated as necessary) the variables that are measured in some dataset, either described as text or as pairs of identifier and description using PropertyValue.")
    includedInDataCatalog: List[IncludedInDataCatalog] = Field(description="A data catalog which contains this dataset (this property was previously 'catalog', preferred name is now 'includedInDataCatalog').")


class DatasetSchema(Dataset, CoreMetadata):
    # used only for generating the JSON-LD schema for a dataset.
    pass
