import re
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


class SchemaBaseModel(BaseModel):
    class Config:
        @staticmethod
        def schema_extra(schema: dict[str, Any], model) -> None:
            # json schema modification for jsonforms
            for prop in schema.get('properties', {}).values():
                if 'const' in prop:
                    # hiding const/readonly fields from the form
                    prop['readonly'] = True
                    prop['option'] = {'hidden': True}
                if 'format' in prop and prop['format'] == 'uri':
                    # using a regex for url matching
                    prop.pop('format')
                    prop[
                        'pattern'
                    ] = "^(http:\\/\\/www\\.|https:\\/\\/www\\.|http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$"
                    prop['errorMessage'] = {"pattern": "must match format \"url\""}


class CreativeWork(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="CreativeWork", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")


class PropertyValue(SchemaBaseModel):
    id: HttpUrl = Field(alias="@id", title="TODO", description="TODO")
    type: str = Field(alias="@type", const=True, default="PropertyValue", title="TODO", description="TODO")
    name: Optional[str] = Field(title="TODO", description="TODO")
    propertyID: Optional[HttpUrl] = Field(title="TODO", description="TODO")
    value: str = Field(title="TODO", description="TODO")
    url: HttpUrl = Field(title="TODO", description="TODO")


Identifier = Union[str, HttpUrl, PropertyValue]


class Person(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="Person", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    email: Optional[EmailStr] = Field(title="TODO", description="TODO")
    identifier: Optional[List[Identifier]] = Field(title="TODO", description="TODO")


class Organization(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="Organization", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    url: Optional[HttpUrl] = Field(title="TODO", description="TODO")
    identifier: Optional[List[Identifier]] = Field(title="TODO", description="TODO")
    address: Optional[str] = Field(
        title="TODO", description="TODO"
    )  # Should address be a string or another constrained type?


class ProviderID(SchemaBaseModel):
    id: HttpUrl = Field(alias="@id", title="TODO", description="TODO")


class ProviderOrganization(Organization):
    parentOrganization: Optional[Organization] = Field(title="TODO", description="TODO")


class DefinedTerm(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DefinedTerm", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    description: str = Field(title="TODO", description="TODO")


class KeywordTerm(DefinedTerm):
    inDefinedTermSet: HttpUrl = Field(title="TODO", description="TODO")


class HasPart(CreativeWork):
    description: str = Field(title="TODO", description="TODO")
    identifier: Identifier = Field(title="TODO", description="TODO")
    creator: Optional[Union[Person, Organization]] = Field(title="TODO", description="TODO")


class IsPartOf(HasPart):
    pass


class SubjectOf(CreativeWork):
    url: HttpUrl = Field(title="TODO", description="TODO")
    encodingFormat: str = Field(title="TODO", description="TODO")


class License(CreativeWork):
    url: HttpUrl = Field(title="TODO", description="TODO")


class LanguageEnum(str, Enum):
    eng = 'eng'
    esp = 'esp'


class Grant(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="MonetaryGrant", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    url: HttpUrl = Field(title="TODO", description="TODO")
    funder: Union[Person, Organization] = Field(title="TODO", description="TODO")


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


class GeoCoordinates(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="GeoCoordinates", title="TODO", description="TODO")
    latitude: float = Field(title="TODO", description="TODO")
    longitude: float = Field(title="TODO", description="TODO")

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


class GeoShape(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="GeoShape", title="TODO", description="TODO")


class Line(GeoShape):
    line: str = Field(title="TODO", description="TODO")

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
    polygon: str = Field(title="TODO", description="TODO")

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


class Place(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="Place", title="TODO", description="TODO")
    name: Optional[str] = Field(title="TODO", description="TODO")
    address: Optional[str] = Field(title="TODO", description="TODO")
    geo: Optional[Union[Line, Polygon, GeoCoordinates]] = Field(title="TODO", description="TODO")


class MediaObject(SchemaBaseModel):
    type: str = Field(alias="@type", const=False, default="MediaObject", title="TODO", description="TODO")
    contentUrl: HttpUrl = Field(title="TODO", description="TODO")
    encodingFormat: str = Field(title="TODO", description="TODO")  # TODO enum for encoding formats
    contentSize: str = Field(title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")

    @validator('contentSize')
    def validate_content_size(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('empty string')

        match = re.match(r"([0-9.]+)([a-zA-Z]+$)", v.replace(" ", ""))
        if not match:
            raise ValueError('invalid format')

        size_unit = match.group(2)
        if size_unit.upper() not in [
            'KB',
            'MB',
            'GB',
            'TB',
            'PB',
            'KILOBYTES',
            'MEGABYTES',
            'GIGABYTES',
            'TERABYTES',
            'PETABYTES',
        ]:
            raise ValueError('invalid unit')

        return v


class CoreMetadata(SchemaBaseModel):
    context: HttpUrl = Field(alias='@context', default='https://schema.org', title="TODO", description="TODO")
    type: str = Field(alias="@type", const=True, default="Dataset", title="TODO", description="TODO")
    name: str = Field(description="The name or title of the record.", title="TODO")
    description: str = Field(description="The description or abstract of the record.", title="TODO")
    url: HttpUrl = Field(description="The url of the record.", title="TODO")
    identifier: List[Union[str, HttpUrl, PropertyValue]] = Field(
        description="Any kind of identifier for the record.", title="TODO"
    )
    creator: List[Union[Person, Organization]] = Field(
        description="Person or organization that created the work.", title="TODO"
    )
    dateCreated: Union[date, datetime] = Field(description="The date on which the work was created.", title="TODO")
    keywords: List[Union[KeywordTerm, str, HttpUrl]] = Field(
        min_items=1, description="Keywords or tags used to describe the dataset, delimited by commas.", title="TODO"
    )
    license: Union[License, HttpUrl] = Field(
        description="A license document that applies to the content, typically indicated by a URL.", title="TODO"
    )
    provider: Union[ProviderOrganization, Person, ProviderID] = Field(
        description="The service provider, service operator, or service performer.", title="TODO"
    )
    publisher: Optional[Union[ProviderOrganization, Person, ProviderID]] = Field(
        description="The publisher of the record.", title="TODO"
    )
    datePublished: Optional[Union[date, datetime]] = Field(
        description="Date of first publication for the record.", title="TODO"
    )
    subjectOf: Optional[List[SubjectOf]] = Field(
        description="A CreativeWork about the record - e.g., a related metadata document describing the record.",
        title="TODO",
    )
    version: Optional[Union[float, str]] = Field(
        description="The version of the record.", title="TODO"
    )  # TODO find something better than float for number
    inLanguage: Optional[Union[LanguageEnum, str]] = Field(
        description="The language of the content of the record.", title="TODO"
    )
    creativeWorkStatus: Optional[Union[DefinedTerm, str]] = Field(
        description="The status of a creative work in terms of its stage in a lifecycle. Example terms include Incomplete, Draft, Published, Obsolete. Some organizations define a set of terms for the stages of their publication lifecycle.",
        title="TODO",
    )
    dateModified: Optional[Union[date, datetime]] = Field(
        description="The date on which the CreativeWork was most recently modified or updated.", title="TODO"
    )
    funding: Optional[List[Grant]] = Field(
        description="A Grant that directly or indirectly provide funding or sponsorship for creation of the dataset.",
        title="TODO",
    )
    temporalCoverage: Optional[TimeInterval] = Field(
        description="The temporalCoverage of a CreativeWork indicates the period that the content applies to, i.e. that it describes, either as a DateTime or as a textual string indicating a time period in ISO 8601 time interval format.",
        title="TODO",
    )
    spatialCoverage: Optional[Place] = Field(
        description="The spatialCoverage of a CreativeWork indicates the place(s) which are the focus of the content. It is a subproperty of contentLocation intended primarily for more technical and detailed materials. For example with a Dataset, it indicates areas that the dataset describes: a dataset of New York weather would have spatialCoverage which was the place: the state of New York.",
        title="TODO",
    )
    hasPart: Optional[List[HasPart]] = Field(
        description="Indicates an record or CreativeWork that is part of this record.", title="TODO"
    )
    isPartOf: Optional[List[IsPartOf]] = Field(
        description="Indicates an record or CreativeWork that this record, or CreativeWork (in some sense), is part of.",
        title="TODO",
    )
    associatedMedia: Optional[List[MediaObject]] = Field(
        description="A media object that encodes this CreativeWork. This property is a synonym for encoding.",
        title="TODO",
    )


class Distribution(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DataDownload", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    contentUrl: Optional[HttpUrl] = Field(title="TODO", description="TODO")
    encodingFormat: Optional[list[str]] = Field(title="TODO", description="TODO")
    contentSize: Optional[str] = Field(title="TODO", description="TODO")
    comment: Optional[str] = Field(title="TODO", description="TODO")


class VariableMeasured(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="PropertyValue", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    unitText: str = Field(title="TODO", description="TODO")


class IncludedInDataCatalog(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DataCatalog", title="TODO", description="TODO")
    name: str = Field(title="TODO", description="TODO")
    description: str = Field(title="TODO", description="TODO")
    url: HttpUrl = Field(title="TODO", description="TODO")
    identifier: Identifier = Field(title="TODO", description="TODO")
    creator: Union[Person, Organization] = Field(title="TODO", description="TODO")


class Dataset(SchemaBaseModel):
    distribution: List[Distribution] = Field(
        description="A data distribution in the form of a dataset (see https://schema.org/Dataset for more information).",
        title="TODO",
    )
    variableMeasured: Optional[List[Union[str, VariableMeasured]]] = Field(
        description="The variableMeasured property can indicate (repeated as necessary) the variables that are measured in some dataset, either described as text or as pairs of identifier and description using PropertyValue.",
        title="TODO",
    )
    includedInDataCatalog: List[IncludedInDataCatalog] = Field(
        description="A data catalog which contains this dataset (this property was previously 'catalog', preferred name is now 'includedInDataCatalog').",
        title="TODO",
    )


class DatasetSchema(Dataset, CoreMetadata):
    # used only for generating the JSON-LD schema for a dataset.
    pass
