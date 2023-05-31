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
    type: str = Field(
        alias="@type",
        const=True,
        default="CreativeWork",
        description="All records in the IGUIDE data catalog are considered creative works. Creative works can encompass various forms of content, such as datasets, software source code, digital documents, etc.",
    )
    name: str = Field(description="Record's title")


class PropertyValue(SchemaBaseModel):
    id: HttpUrl = Field(
        alias="@id",
        description="The unique identifier for the property value. For example, this can be an ORCID identifier for a person who created a creative work.",
    )
    type: str = Field(
        alias="@type",
        const=True,
        default="PropertyValue",
        description="Specifies that the type of the structured data object is a PropertyValue.",
    )
    name: Optional[str] = Field(
        description="The name of the property that is related to a specific creative work. For example, DOI of a person who created the creatiev work or the varibale name that is measured for a research work."
    )
    propertyID: Optional[HttpUrl] = Field(
        description="Specifies the property ID. For example, this can be the ORCID registry identifier."
    )
    value: str = Field(
        description="Represents the actual value assigned to the property. For example,  the ORCID identifier: 0000-0000-0000-0001."
    )
    url: HttpUrl = Field(
        description="Indicates the URL associated with the property value. For example, the ORCID profile URL"
    )


Identifier = Union[str, HttpUrl, PropertyValue]


class Person(SchemaBaseModel):
    type: str = Field(
        alias="@type", const=True, default="Person", description="Describe the author(s) of a creative work"
    )
    name: str = Field(
        description="The name of individual who contributed to this creative work. Contribution can include being an author, editor, publisher, etc."
    )
    email: Optional[EmailStr] = Field(description="The email address of the individual who is listed as a contributor.")
    identifier: Optional[List[Union[HttpUrl, Identifier]]] = Field(description="The unique identifier for the person.")


class Organization(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        const=True,
        default="Organization",
        description="Describe the organization(s) contributed to a creative work",
    )
    name: str = Field(description="The organization name who contributed to this creative work.")
    url: Optional[HttpUrl] = Field(
        description="Indicates the URL associated with the organizatino who contributed to this work."
    )
    identifier: Optional[List[Union[HttpUrl, Identifier]]] = Field(
        description="The unique identifier for the organization."
    )
    address: Optional[str] = Field(
        description="The mailing address for the organization."
    )  # Should address be a string or another constrained type?


class ProviderID(SchemaBaseModel):
    id: HttpUrl = Field(
        alias="@id",
        description="The URL of a provider. For example, the URL to the HydroShare data repository that is considered as a provider for a creatiev work.",
    )


class ProviderOrganization(Organization):
    parentOrganization: Optional[Organization] = Field(
        description="The larger organization that the provider or publisher organization is a subOrganization of."
    )


class DefinedTerm(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DefinedTerm", description="A formal definition of a word, name, acronym, phrase, or similar. Often used in the context of category or subject classification, glossaries or dictionaries, product or creative work types, etc.")
    name: str = Field(description="The name of the term or item being defined.")
    description: str = Field(description="The description of the item being defined.")


class KeywordTerm(DefinedTerm):
    inDefinedTermSet: HttpUrl = Field(description="Keywords or tags with a formal definition used to describe the creative work.")


class HasPart(CreativeWork):
    description: str = Field(description="A creative work that is part of this record. This metadata is used to show specific relationships between a collection record and its member records.")
    identifier: Identifier = Field(description="The unique identifier for the creative work.")
    creator: Optional[Union[Person, Organization]] = Field(description="The creator of this creative work. The creator could be a person, a list of people, or an organization(s).")


class IsPartOf(HasPart):
    pass


class SubjectOf(CreativeWork):
    url: HttpUrl = Field(description="The URL address that serves as a reference to access additional details related to the record. It is important to note that this type of metadata solely pertains to the record itself and may not necessarily be an integral component of the record, unlike the HasPart metadata.")
    encodingFormat: str = Field(description="This metadata indicates the format of the creative work that provides details about the record.")


class License(CreativeWork):
    url: HttpUrl = Field(description="The URL address to the specific license that governs the usage and permissions associated with the record.")


class LanguageEnum(str, Enum):
    eng = 'eng'
    esp = 'esp'


class Grant(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="MonetaryGrant", description="This metadata represents details about a grant or financial assistance provided to an individual(s) or organization(s) for supporting the work related to the record.")
    name: str = Field(description="The project or grant name that funds or sponsors the work presented in the record.")
    url: HttpUrl = Field(description="The URL address to the awarded project.")
    funder: Union[Person, Organization] = Field(description="The funder's name (entity or organization) that provides financial resources for the creation and execution of the work documented in the record.")


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
    type: str = Field(alias="@type", const=True, default="GeoCoordinates", description="Geographic coordinates that represent a specific location on the Earth's surface. GeoCoordinates typically consists of two components: latitude and longitude.")
    latitude: float = Field(description="Represents the angular distance of a location north or south of the equator, measured in degrees and ranges from -90 to +90 degrees.")
    longitude: float = Field(description="Represents the angular distance of a location east or west of the Prime Meridian, measured in degrees and ranges from -180 to +180 degrees.")

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
    type: str = Field(alias="@type", const=True, default="GeoShape", description="A structured representation that describes the coordinates of a geographic feature (line or polygon).")


class Line(GeoShape):
    line: str = Field(description="A line that is expressed as a series of two or more point objects separated by space.")

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
    polygon: str = Field(description="A polygon outlines the boundary of a specific region by a point-to-point path for which the starting and ending points are the same.")

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
    type: str = Field(alias="@type", const=True, default="Place", description="Represents the focus area of the record's content.")
    name: Optional[str] = Field(description="The name of the focus area of the record's content.")
    address: Optional[str] = Field(description="The address of the focus area.")
    geo: Optional[Union[Line, Polygon, GeoCoordinates]] = Field(description="Specifies the geographic coordinates of the place in the form of a point location, line, or area coverage extent.")


class MediaObject(SchemaBaseModel):
    type: str = Field(alias="@type", const=False, default="MediaObject", description="An item that encodes the record.")
    contentUrl: HttpUrl = Field(description="The direct URL link to access or download the actual content of the media object.")
    encodingFormat: str = Field(description="Represents the specific file format in which the media is encoded.")  # TODO enum for encoding formats
    contentSize: str = Field(description="Represents the file size, expressed in bytes, kilobytes, megabytes, or another unit of measurement.")
    name: str = Field(description="The name of the media object (file).")

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
    context: HttpUrl = Field(alias='@context', default='https://schema.org', description="Specifies the vocabulary employed for understanding the structured data markup.")
    type: str = Field(alias="@type", const=True, default="Dataset", description="A specific vocabulary that applies to a specific piece of data.")
    name: str = Field(description="The name or title of the record.")
    description: str = Field(description="The description or abstract of the record.")
    url: HttpUrl = Field(description="The url of the record.")
    identifier: List[Identifier] = Field(description="Any kind of identifier for the record.")
    creator: List[Union[Person, Organization]] = Field(description="Person or organization that created the work.")
    dateCreated: Union[date, datetime] = Field(description="The date on which the work was created.")
    keywords: List[Union[str, HttpUrl, KeywordTerm]] = Field(
        min_items=1, description="Keywords or tags used to describe the dataset, delimited by commas."
    )
    license: Union[License, HttpUrl] = Field(
        description="A license document that applies to the content, typically indicated by a URL."
    )
    provider: Union[ProviderOrganization, Person, ProviderID] = Field(
        description="The service provider, service operator, or service performer."
    )
    publisher: Optional[Union[ProviderOrganization, Person, ProviderID]] = Field(
        description="The publisher of the record."
    )
    datePublished: Optional[Union[date, datetime]] = Field(description="Date of first publication for the record.")
    subjectOf: Optional[List[SubjectOf]] = Field(
        description="A CreativeWork about the record - e.g., a related metadata document describing the record.",
    )
    version: Optional[Union[float, str]] = Field(
        description="The version of the record."
    )  # TODO find something better than float for number
    inLanguage: Optional[Union[LanguageEnum, str]] = Field(description="The language of the content of the record.")
    creativeWorkStatus: Optional[Union[DefinedTerm, str]] = Field(
        description="The status of a creative work in terms of its stage in a lifecycle. Example terms include Incomplete, Draft, Published, Obsolete. Some organizations define a set of terms for the stages of their publication lifecycle.",
    )
    dateModified: Optional[Union[date, datetime]] = Field(
        description="The date on which the CreativeWork was most recently modified or updated."
    )
    funding: Optional[List[Grant]] = Field(
        description="A Grant that directly or indirectly provide funding or sponsorship for creation of the dataset.",
    )
    temporalCoverage: Optional[TimeInterval] = Field(
        description="The temporalCoverage of a CreativeWork indicates the period that the content applies to, i.e. that it describes, either as a DateTime or as a textual string indicating a time period in ISO 8601 time interval format.",
    )
    spatialCoverage: Optional[Place] = Field(
        description="The spatialCoverage of a CreativeWork indicates the place(s) which are the focus of the content. It is a subproperty of contentLocation intended primarily for more technical and detailed materials. For example with a Dataset, it indicates areas that the dataset describes: a dataset of New York weather would have spatialCoverage which was the place: the state of New York.",
    )
    hasPart: Optional[List[HasPart]] = Field(
        description="Indicates an record or CreativeWork that is part of this record."
    )
    isPartOf: Optional[List[IsPartOf]] = Field(
        description="Indicates an record or CreativeWork that this record, or CreativeWork (in some sense), is part of.",
    )
    associatedMedia: Optional[List[MediaObject]] = Field(
        description="A media object that encodes this CreativeWork. This property is a synonym for encoding.",
    )


class Distribution(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DataDownload", description="Represents the general availability of a dataset and describes how the content related to the catalog record may be obtained")
    name: str = Field(description="The name of the downloadable file.")
    contentUrl: Optional[HttpUrl] = Field(description="The direct URL link to download the dataset.")
    encodingFormat: Optional[list[str]] = Field(description="Represents the file format in which the dataset is encoded.")
    contentSize: Optional[str] = Field(description="Represents the file size, expressed in bytes, kilobytes, megabytes, or another unit of measurement.")
    comment: Optional[str] = Field(description="An explanation providing additional information on how the dataset is being accessed or downloaded.")


class VariableMeasured(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="PropertyValue", description="Indicates specific information about the variable being measured in a particular dataset, study, or observation.")
    name: str = Field(description="The name of the variable being measured.")
    unitText: str = Field(description="Indicate the unit of measurement for the variable.")


class IncludedInDataCatalog(SchemaBaseModel):
    type: str = Field(alias="@type", const=True, default="DataCatalog", description="A data catalog which contains this dataset.")
    name: str = Field(description="The name of the data catalog containing this dataset.")
    description: str = Field(description="The description of the data catalog.")
    url: HttpUrl = Field(description="The URL address to the data catalog.")
    identifier: Identifier = Field(description="The unique identifier for the data catalog. This is generated automatically by the system.")
    creator: Union[Person, Organization] = Field(description="The creator, owner, or provider of the data catalog.")


class Dataset(SchemaBaseModel):
    distribution: List[Distribution] = Field(
        description="A data distribution in the form of a dataset (see https://schema.org/Dataset for more information).",
    )
    variableMeasured: Optional[List[Union[str, VariableMeasured]]] = Field(
        description="The variableMeasured property can indicate (repeated as necessary) the variables that are measured in some dataset, either described as text or as pairs of identifier and description using PropertyValue.",
    )
    includedInDataCatalog: List[IncludedInDataCatalog] = Field(
        description="A data catalog which contains this dataset (this property was previously 'catalog', preferred name is now 'includedInDataCatalog').",
    )


class DatasetSchema(Dataset, CoreMetadata):
    # used only for generating the JSON-LD schema for a dataset.
    pass
