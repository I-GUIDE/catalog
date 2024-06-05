import re
import typing
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union, Literal

import pydantic_core
from pydantic_core import CoreSchema
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
    AfterValidator,
    GetJsonSchemaHandler,
)

from pydantic.json_schema import JsonSchemaValue
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated

orcid_pattern = "\\b\\d{4}-\\d{4}-\\d{4}-\\d{3}[0-9X]\\b"
orcid_pattern_placeholder = "e.g. '0000-0001-2345-6789'"
orcid_pattern_error = "must match the ORCID pattern. e.g. '0000-0001-2345-6789'"

url_pattern = "^(http:\\/\\/www\\.|https:\\/\\/www\\.|http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$"
url_pattern_error = 'must match format "url"'


def url_to_string(url: HttpUrl) -> str:
    return str(url)


HttpUrlStr = Annotated[
    HttpUrl,
    AfterValidator(url_to_string),
    PlainSerializer(lambda v: HttpUrl(v), return_type=HttpUrl),
]


class SchemaBaseModel(BaseModel):
    @classmethod
    def update_url_schema(cls, url_schema: dict[str, Any]) -> dict[str, Any]:
        """Update the schema for url fields to use a regex for url matching"""
        if "format" in url_schema and url_schema["format"] == "uri":
            url_schema.pop("format")
            url_schema["pattern"] = url_pattern
            url_schema["errorMessage"] = {"pattern": url_pattern_error}
        return url_schema

    @classmethod
    def remove_any_of(cls, schema: dict[str, Any], field: str) -> dict[str, Any]:
        """Remove the anyOf key from the schema for the given field and set the value of the field to the first
        item in the anyOf list - the 2nd item in the list is always {"type": "null"} which we don't want
        in our schema for the UI to work"""

        field_schema = schema["properties"][field]
        anyOf = field_schema.pop("anyOf")
        field_schema.update(anyOf[0])
        return field_schema

    @classmethod
    def remove_default_null(cls, field_schema: dict[str, Any]) -> dict[str, Any]:
        """Remove the default value of null from the schema for the given field"""
        if "default" in field_schema and field_schema["default"] is None:
            field_schema.pop("default")
        return field_schema

    @classmethod
    def remove_default_empty_list(cls, field_schema: dict[str, Any]) -> dict[str, Any]:
        """Remove the default value of an empty list from the schema for the given field"""
        if "default" in field_schema and field_schema["default"] == []:
            field_schema.pop("default")
        return field_schema

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # adjusting the json schema to make the UI work
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        for field, field_info in cls.model_fields.items():
            if field not in json_schema["properties"]:
                continue
            # check if the field is an optional field
            if (
                type(field_info.annotation) is typing._UnionGenericAlias
                and type(None) in field_info.annotation.__args__
            ):
                # check if the field is also a union type
                if len(field_info.annotation.__args__) > 2:
                    # remove the null type from the union type
                    field_schema = json_schema["properties"][field]
                    field_schema["anyOf"] = [
                        item
                        for item in field_schema["anyOf"]
                        if item != {"type": "null"}
                    ]
                else:
                    # field is not a union type - remove the anyOf key
                    field_schema = cls.remove_any_of(json_schema, field)
                # check if the field is an url type
                if HttpUrlStr in field_info.annotation.__args__:
                    field_schema = cls.update_url_schema(field_schema)
                for data_type in field_info.annotation.__args__:
                    origin_data_type = typing.get_origin(data_type)
                    if origin_data_type is list:
                        field_schema = cls.remove_default_empty_list(field_schema)
                        break
                field_schema = cls.remove_default_null(field_schema)
                json_schema["properties"][field] = field_schema
            else:
                # field is not optional
                if field in json_schema["properties"]:
                    field_schema = json_schema["properties"][field]
                    # check if the field is an url type
                    if field_info.annotation is pydantic_core._pydantic_core.Url:
                        field_schema = cls.update_url_schema(field_schema)
                    field_schema = cls.remove_default_null(field_schema)
                    json_schema["properties"][field] = field_schema

        return json_schema


class CreativeWork(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="CreativeWork",
        description="Submission type can include various forms of content, such as datasets, "
        "software source code, digital documents, etc.",
    )
    name: str = Field(description="Submission's name or title", title="Name or title")


class Person(SchemaBaseModel):
    type: Literal["Person"] = Field(
        alias="@type",
        default="Person",
        frozen=True,
        description="A person.",
        json_schema_extra={"type": "string"},
    )
    name: str = Field(
        description="A string containing the full name of the person. Personal name format: Family Name, Given Name."
    )
    email: Optional[EmailStr] = Field(
        description="A string containing an email address for the person.", default=None
    )
    identifier: Optional[List[str]] = Field(
        description="Unique identifiers for the person. Where identifiers can be encoded as URLs, enter URLs here.",
        default=[],
    )


class Organization(SchemaBaseModel):
    type: Literal["Organization"] = Field(
        alias="@type",
        default="Organization",
        frozen=True,
        json_schema_extra={"type": "string"},
    )
    name: str = Field(description="Name of the provider organization or repository.")
    url: Optional[HttpUrlStr] = Field(
        title="URL",
        description="A URL to the homepage for the organization.",
        default=None,
    )
    address: Optional[str] = Field(
        description="Full address for the organization - e.g., “8200 Old Main Hill, Logan, UT 84322-8200”.",
        default=None,
    )  # Should address be a string or another constrained type?


class Affiliation(Organization):
    name: str = Field(
        description="Name of the organization the creator is affiliated with."
    )


class Provider(Person):
    identifier: Optional[str] = Field(
        description="ORCID identifier for the person.",
        json_schema_extra={
            "pattern": orcid_pattern,
            "errorMessage": {"pattern": orcid_pattern_error},
            "options": {"placeholder": orcid_pattern_placeholder},
        },
        default=None,
    )
    email: Optional[EmailStr] = Field(
        description="A string containing an email address for the provider.",
        default=None,
    )
    affiliation: Optional[Affiliation] = Field(
        description="The affiliation of the creator with the organization.",
        default=None,
    )


class Creator(Person):
    identifier: Optional[str] = Field(
        description="ORCID identifier for creator.",
        json_schema_extra={
            "pattern": orcid_pattern,
            "errorMessage": {"pattern": orcid_pattern_error},
            "options": {"placeholder": orcid_pattern_placeholder},
        },
        default=None,
    )
    email: Optional[EmailStr] = Field(
        description="A string containing an email address for the creator.",
        default=None,
    )
    affiliation: Optional[Affiliation] = Field(
        description="The affiliation of the creator with the organization.",
        default=None,
    )


class FunderOrganization(Organization):
    model_config = ConfigDict(title="Funding Organization")
    name: str = Field(description="Name of the organization.")


class PublisherOrganization(Organization):
    name: str = Field(description="Name of the publishing organization.")
    url: Optional[HttpUrlStr] = Field(
        title="URL",
        description="A URL to the homepage for the publisher organization or repository.",
        default=None,
    )


class SourceOrganization(Organization):
    name: str = Field(
        description="Name of the organization that created the data."
    )


class DefinedTerm(SchemaBaseModel):
    type: str = Field(alias="@type", default="DefinedTerm")
    name: str = Field(description="The name of the term or item being defined.")
    description: str = Field(description="The description of the item being defined.")


class Draft(DefinedTerm):
    name: str = Field(default="Draft")
    description: str = Field(
        default="The resource is in draft state and should not be considered final. Content and metadata may change",
        json_schema_extra={"readOnly": True},
        description="The description of the item being defined.",
    )


class Incomplete(DefinedTerm):
    name: str = Field(default="Incomplete")
    description: str = Field(
        default="Data collection is ongoing or the resource is not completed",
        json_schema_extra={"readOnly": True},
        description="The description of the item being defined.",
    )


class Obsolete(DefinedTerm):
    name: str = Field(default="Obsolete")
    description: str = Field(
        default="The resource has been replaced by a newer version, or the resource is no longer considered applicable",
        json_schema_extra={"readOnly": True},
        description="The description of the item being defined.",
    )


class Published(DefinedTerm):
    name: str = Field(default="Published")
    description: str = Field(
        default="The resource has been permanently published and should be considered final and complete",
        json_schema_extra={"readOnly": True},
        description="The description of the item being defined.",
    )


class HasPart(CreativeWork):
    url: Optional[HttpUrlStr] = Field(
        title="URL", description="The URL address to the data resource.", default=None
    )
    description: Optional[str] = Field(
        description="Information about a related resource that is part of this resource.",
        default=None,
    )


class IsPartOf(CreativeWork):
    url: Optional[HttpUrlStr] = Field(
        title="URL", description="The URL address to the data resource.", default=None
    )
    description: Optional[str] = Field(
        description="Information about a related resource that this resource is a "
        "part of - e.g., a related collection.",
        default=None,
    )


class MediaObjectPartOf(CreativeWork):
    url: Optional[HttpUrlStr] = Field(
        title="URL",
        description="The URL address to the related metadata document.",
        default=None,
    )
    description: Optional[str] = Field(
        description="Information about a related metadata document."
    )


class SubjectOf(CreativeWork):
    url: Optional[HttpUrlStr] = Field(
        title="URL",
        description="The URL address that serves as a reference to access additional details related to the record. "
        "It is important to note that this type of metadata solely pertains to the record itself and "
        "may not necessarily be an integral component of the record, unlike the HasPart metadata.",
        default=None,
    )
    description: Optional[str] = Field(
        description="Information about a related resource that is about or describes this "
        "resource - e.g., a related metadata document describing the resource.",
        default=None,
    )


class License(CreativeWork):
    name: str = Field(
        description="A text string indicating the name of the license under which the resource is shared."
    )
    url: Optional[HttpUrlStr] = Field(
        title="URL",
        description="A URL for a web page that describes the license.",
        default=None,
    )
    description: Optional[str] = Field(
        description="A text string describing the license or containing the text of the license itself.",
        default=None,
    )


class LanguageEnum(str, Enum):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema["type"] = "string"
        json_schema["title"] = "Language"
        json_schema["description"] = ""
        return json_schema

    eng = "eng"
    esp = "esp"


InLanguageStr = Annotated[
    str, Field(title="Other", description="Please specify another language.")
]
IdentifierStr = Annotated[str, Field(title="Identifier")]


class Grant(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="MonetaryGrant",
        description="This metadata represents details about a grant or financial assistance provided to an "
        "individual(s) or organization(s) for supporting the work related to the record.",
    )
    name: str = Field(
        title="Name or title",
        description="A text string indicating the name or title of the grant or financial assistance.",
    )
    description: Optional[str] = Field(
        description="A text string describing the grant or financial assistance.",
        default=None,
    )
    identifier: Optional[str] = Field(
        title="Funding identifier",
        description="Grant award number or other identifier.",
        default=None,
    )
    funder: Optional[FunderOrganization] = Field(
        description="The organization that provided the funding or sponsorship.",
        default=None,
    )


class TemporalCoverage(SchemaBaseModel):
    startDate: datetime = Field(
        title="Start date",
        description="A date/time object containing the instant corresponding to the commencement of the time "
        "interval (ISO8601 formatted date - YYYY-MM-DDTHH:MM).",
        # TODO: these are failing due to a problem with transpiled dependencies inside cznet-vue-core
        json_schema_extra={
            "formatMaximum": {"$data": "1/endDate"},
            "errorMessage": {"formatMaximum": "must be lesser than or equal to End date"}
        },
    )
    endDate: Optional[datetime] = Field(
        title="End date",
        description="A date/time object containing the instant corresponding to the termination of the time "
        "interval (ISO8601 formatted date - YYYY-MM-DDTHH:MM). If the ending date is left off, "
        "that means the temporal coverage is ongoing.",
        json_schema_extra={
            "formatMaximum": {"$data": "1/startDate"},
            "errorMessage": {"formatMaximum": "must be lesser than or equal to Start date"}
        },
        default=None,
    )


class GeoCoordinates(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="GeoCoordinates",
        description="Geographic coordinates that represent a specific location on the Earth's surface. "
        "GeoCoordinates typically consists of two components: latitude and longitude.",
    )
    latitude: float = Field(
        description="Represents the angular distance of a location north or south of the equator, "
        "measured in degrees and ranges from -90 to +90 degrees."
    )
    longitude: float = Field(
        description="Represents the angular distance of a location east or west of the Prime Meridian, "
        "measured in degrees and ranges from -180 to +180 degrees."
    )

    @field_validator("latitude")
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


class GeoShape(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="GeoShape",
        description="A structured representation that describes the coordinates of a geographic feature.",
    )
    box: str = Field(
        description="A box is a rectangular region defined by a pair of coordinates representing the "
        "southwest and northeast corners of the box."
    )

    @field_validator("box")
    def validate_box(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        v = v.strip()
        if not v:
            raise ValueError("empty string")
        v_parts = v.split(" ")
        if len(v_parts) != 4:
            raise ValueError("Bounding box must have 4 coordinate points")
        for index, item in enumerate(v_parts, start=1):
            try:
                item = float(item)
            except ValueError:
                raise ValueError("Bounding box coordinate value is not a number")
            item = abs(item)
            if index % 2 == 0:
                if item > 180:
                    raise ValueError(
                        "Bounding box coordinate east/west must be between -180 and 180"
                    )
            elif item > 90:
                raise ValueError(
                    "Bounding box coordinate north/south must be between -90 and 90"
                )

        return v


class PropertyValueBase(SchemaBaseModel):
    model_config = ConfigDict(title="Property Value")

    type: str = Field(
        alias="@type",
        default="PropertyValue",
        frozen=True,
        description="A property-value pair.",
    )
    propertyID: Optional[str] = Field(
        title="Property ID",
        description="The ID of the property.",
        default=None,
    )
    name: str = Field(description="The name of the property.")
    value: str = Field(description="The value of the property.")
    unitCode: Optional[str] = Field(
        title="Measurement unit",
        description="The unit of measurement for the value.",
        default=None,
    )
    description: Optional[str] = Field(
        description="A description of the property.",
        default=None,
    )
    minValue: Optional[float] = Field(
        title="Minimum value",
        description="The minimum allowed value for the property.",
        default=None,
    )
    maxValue: Optional[float] = Field(
        title="Maximum value",
        description="The maximum allowed value for the property.",
        default=None,
    )
    measurementTechnique: Optional[str] = Field(
        title="Measurement technique", description="A technique or technology used in a measurement.",
        default=None,
    )

    @model_validator(mode="before")
    def validate_min_max_values(cls, values):
        if isinstance(values, dict):
            min_value = values.get("minValue", None)
            max_value = values.get("maxValue", None)
            if min_value is not None and max_value is not None:
                if isinstance(min_value, str):
                    min_value = min_value.strip()
                    min_value = float(min_value)
                if isinstance(max_value, str):
                    max_value = max_value.strip()
                    max_value = float(max_value)
                if min_value > max_value:
                    raise ValueError(
                        "Minimum value must be less than or equal to maximum value"
                    )

        return values


class PropertyValue(PropertyValueBase):
    # using PropertyValueBase model instead of PropertyValue model as one of the types for the value field
    # in order for the schema generation (schema.json) to work. Self referencing nested models leads to
    # infinite loop in our custom schema generation code when trying to replace dict with key '$ref'
    value: Union[str, PropertyValueBase, List[PropertyValueBase]] = Field(
        description="The value of the property."
    )


class Place(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="Place",
        description="Represents the focus area of the record's content.",
    )
    name: Optional[str] = Field(description="Name of the place.", default=None)
    geo: Optional[Union[GeoCoordinates, GeoShape]] = Field(
        description="Specifies the geographic coordinates of the place in the form of a point location, line, "
        "or area coverage extent.",
        default=None,
    )
    additionalProperty: Optional[List[PropertyValue]] = Field(
        title="Additional properties",
        default=[],
        description="Additional properties of the place.",
    )

    @model_validator(mode="before")
    def validate_geo_or_name_required(cls, values):
        name = values.get("name", None)
        geo = values.get("geo", None)
        if not name and not geo:
            raise ValueError(
                "Either place name or geo location of the place must be provided"
            )
        return values


class MediaObject(SchemaBaseModel):
    type: str = Field(
        alias="@type",
        default="MediaObject",
        description="An item that encodes the record.",
    )
    contentUrl: HttpUrlStr = Field(
        title="Content URL",
        description="The direct URL link to access or download the actual content of the media object.",
    )
    encodingFormat: Optional[str] = Field(
        title="Encoding format",
        description="Represents the specific file format in which the media is encoded.",
        default=None,
    )  # TODO enum for encoding formats
    contentSize: str = Field(
        title="Content size",
        description="Represents the file size, expressed in bytes, kilobytes, megabytes, or another "
        "unit of measurement.",
    )
    name: str = Field(description="The name of the media object (file).")
    sha256: Optional[str] = Field(
        title="SHA-256", description="The SHA-256 hash of the media object.",
        default=None,
    )
    isPartOf: Optional[List[MediaObjectPartOf]] = Field(
        title="Is part of",
        description="Link to or citation for a related metadata document that this media object is a part of",
        default=[],
    )

    @field_validator("contentSize")
    def validate_content_size(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("empty string")

        match = re.match(r"([0-9.]+)([a-zA-Z]+$)", v.replace(" ", ""))
        if not match:
            raise ValueError("invalid format")

        size_unit = match.group(2)
        if size_unit.upper() not in [
            "KB",
            "MB",
            "GB",
            "TB",
            "PB",
            "KILOBYTES",
            "MEGABYTES",
            "GIGABYTES",
            "TERABYTES",
            "PETABYTES",
        ]:
            raise ValueError("invalid unit")

        return v

    # TODO: not validating the SHA-256 hash for now as the hydroshare content file hash is in md5 format
    # @validator('sha256')
    # def validate_sha256_string_format(cls, v):
    #     if v:
    #         v = v.strip()
    #         if v and not re.match(r"^[a-fA-F0-9]{64}$", v):
    #             raise ValueError('invalid SHA-256 format')
    #     return v


class CoreMetadata(SchemaBaseModel):
    context: HttpUrlStr = Field(
        alias="@context",
        default="https://schema.org",
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )
    type: str = Field(
        alias="@type",
        title="Submission type",
        default="Dataset",
        description="Submission type can include various forms of content, such as datasets,"
        " software source code, digital documents, etc.",
        json_schema_extra={"enum": ["Dataset", "Notebook", "Software Source Code"]},
    )
    name: str = Field(
        title="Name or title",
        description="A text string with a descriptive name or title for the resource.",
    )
    description: str = Field(
        title="Description or abstract",
        description="A text string containing a description/abstract for the resource.",
    )
    url: HttpUrlStr = Field(
        title="URL",
        description="A URL for the landing page that describes the resource and where the content "
        "of the resource can be accessed. If there is no landing page,"
        " provide the URL of the content.",
    )
    identifier: Optional[List[IdentifierStr]] = Field(
        title="Identifiers",
        description="Any kind of identifier for the resource. Identifiers may be DOIs or unique strings "
        "assigned by a repository. Multiple identifiers can be entered. Where identifiers can be "
        "encoded as URLs, enter URLs here.",
        default=[],
    )
    creator: List[Union[Creator, Organization]] = Field(
        description="Person or Organization that created the resource."
    )
    dateCreated: datetime = Field(
        title="Date created", description="The date on which the resource was created."
    )
    keywords: List[str] = Field(
        min_length=1,
        description="Keywords or tags used to describe the dataset, delimited by commas.",
    )
    license: License = Field(
        description="A license document that applies to the resource."
    )
    provider: Union[Organization, Provider] = Field(
        description="The repository, service provider, organization, person, or service performer that provides"
        " access to the resource."
    )
    publisher: Optional[PublisherOrganization] = Field(
        title="Publisher",
        description="Where the resource is permanently published, indicated the repository, service provider,"
        " or organization that published the resource - e.g., CUAHSI HydroShare."
        " This may be the same as Provider.",
        default=None,
    )
    datePublished: Optional[datetime] = Field(
        title="Date published",
        description="Date of first publication for the resource.",
        default=None,
    )
    subjectOf: Optional[List[SubjectOf]] = Field(
        title="Subject of",
        description="Link to or citation for a related resource that is about or describes this resource"
        " - e.g., a journal paper that describes this resource or a related metadata document "
        "describing the resource.",
        default=[],
    )
    version: Optional[str] = Field(
        description="A text string indicating the version of the resource.",
        default=None,
    )  # TODO find something better than float for number
    inLanguage: Optional[Union[LanguageEnum, InLanguageStr]] = Field(
        title="Language",
        description="The language of the content of the resource.",
        default=None,
    )
    creativeWorkStatus: Optional[Union[Draft, Incomplete, Obsolete, Published]] = Field(
        title="Resource status",
        description="The status of this resource in terms of its stage in a lifecycle. "
        "Example terms include Incomplete, Draft, Published, and Obsolete.",
        default=None,
    )
    dateModified: Optional[datetime] = Field(
        title="Date modified",
        description="The date on which the resource was most recently modified or updated.",
        default=None,
    )
    funding: Optional[List[Grant]] = Field(
        description="A Grant or monetary assistance that directly or indirectly provided funding or sponsorship "
        "for creation of the resource.",
        default=[],
    )
    temporalCoverage: Optional[TemporalCoverage] = Field(
        title="Temporal coverage",
        description="The time period that applies to all of the content within the resource.",
        default=None,
    )
    spatialCoverage: Optional[Place] = Field(
        description="The spatialCoverage of a CreativeWork indicates the place(s) which are the focus of the content. "
        "It is a sub property of contentLocation intended primarily for more technical and "
        "detailed materials. For example with a Dataset, it indicates areas that the dataset "
        "describes: a dataset of New York weather would have spatialCoverage which was the "
        "place: the state of New York.",
        default=None,
    )
    hasPart: Optional[List[HasPart]] = Field(
        title="Has part",
        description="Link to or citation for a related resource that is part of this resource.",
        default=[],
    )
    isPartOf: Optional[List[IsPartOf]] = Field(
        title="Is part of",
        description="Link to or citation for a related resource that this resource is a "
        "part of - e.g., a related collection.",
        default=[],
    )
    associatedMedia: Optional[List[MediaObject]] = Field(
        title="Resource content",
        description="A media object that encodes this CreativeWork. This property is a synonym for encoding.",
        default=[],
    )
    citation: Optional[List[str]] = Field(
        title="Citation",
        description="A bibliographic citation for the resource.",
        default=[],
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        field = "@context"
        field_schema = json_schema["properties"][field]
        field_schema = cls.update_url_schema(field_schema)
        json_schema["properties"][field] = field_schema
        return json_schema


class DatasetMetadata(CoreMetadata):
    variableMeasured: Optional[List[Union[str, PropertyValue]]] = Field(
        title="Variables measured", description="Measured variables.",
        default=[],
    )
    additionalProperty: Optional[List[PropertyValue]] = Field(
        title="Additional properties",
        default=[],
        description="Additional properties of the dataset."
    )
    sourceOrganization: Optional[SourceOrganization] = Field(
        title="Source organization",
        description="The organization that provided the data for this dataset.",
        default=None,
    )
