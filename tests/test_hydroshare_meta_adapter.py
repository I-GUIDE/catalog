from datetime import datetime
import pytest
from pydantic import ValidationError

from api.adapters.utils import RepositoryType, get_adapter_by_type
from api.models.catalog import DatasetMetadataDOC


@pytest.mark.parametrize('coverage_type', ["box", "point"])
@pytest.mark.asyncio
async def test_hydroshare_resource_meta_adapter(hydroshare_resource_metadata, coverage_type, dataset_model):
    """Test the HydroshareMetaAdapter for Composite Resource"""

    adapter = get_adapter_by_type(RepositoryType.HYDROSHARE)
    if coverage_type == "point":
        hydroshare_resource_metadata["spatial_coverage"] = {"type": "point", "name": "Logan River",
                                                            "north": 41.74, "east": -111.83,
                                                            "units": "Decimal degrees",
                                                            "projection": "Unknown"}

    dataset = adapter.to_catalog_record(hydroshare_resource_metadata)
    try:
        dataset_model(**dataset.model_dump())
    except ValidationError as err:
        pytest.fail(f"Catalog dataset schema model validation failed: {str(err)}")

    assert isinstance(dataset, DatasetMetadataDOC)
    assert dataset.name == "Testing IGUIDE Metadata Adapter for Hydroshare Resource"
    assert dataset.description == "This is a test resource - abstract"
    assert dataset.url == "http://www.hydroshare.org/resource/1ee81318135c40f587d9a3e5d689daf5"
    assert dataset.identifier == ["http://www.hydroshare.org/resource/1ee81318135c40f587d9a3e5d689daf5"]
    assert len(dataset.creator) == 3
    for cr in dataset.creator:
        if cr.type == "Person":
            assert cr.name in ["Smith, John", "Tseganeh Z. Gichamo"]
            if cr.name == "Smith, John":
                assert cr.email == "john.smith@usu.edu"
                assert cr.identifier == "https://orcid.org/user/123"
            else:
                assert cr.identifier is None
        else:
            assert cr.type == "Organization"
            assert cr.name == "Utah State University"
            assert cr.address == "101 Logan 1st Ave"
            assert cr.url == "https://www.usu.edu/"

    assert dataset.dateCreated == datetime.fromisoformat("2023-05-31T03:12:34.504216+00:00")
    assert dataset.dateModified == datetime.fromisoformat("2023-06-23T21:43:10.582708+00:00")
    assert dataset.datePublished == datetime.fromisoformat("2023-07-23T21:43:10.582708+00:00")
    assert dataset.keywords == ["Logan River", "Snow water equivalent", "UEB"]
    assert dataset.license.name == "This resource is shared under the Creative Commons Attribution CC BY."
    assert dataset.license.url == "http://creativecommons.org/licenses/by/4.0/"
    assert dataset.provider.name == "HYDROSHARE"
    assert dataset.provider.url == "https://www.hydroshare.org/"
    assert dataset.inLanguage == "eng"
    assert len(dataset.funding) == 1
    assert dataset.funding[0].name == "Modelling Watershed Colorado Riverbasin"
    assert dataset.funding[0].identifier == "100-678-NSF"
    assert dataset.funding[0].funder.name == "NSF"
    assert dataset.funding[0].funder.url == "https://www.nsf.gov/"
    assert dataset.temporalCoverage.startDate == datetime.fromisoformat("2008-10-01T00:00:00")
    assert dataset.temporalCoverage.endDate == datetime.fromisoformat("2009-06-30T21:00:00")
    if coverage_type == "point":
        assert dataset.spatialCoverage.name == "Logan River"
        assert dataset.spatialCoverage.geo.longitude == -111.83
        assert dataset.spatialCoverage.geo.latitude == 41.74
    else:
        assert dataset.spatialCoverage.name == "Colorado River Basin"
        bounding_box = "42.11917118550477 -111.42822713925766 41.70323788190726 -111.79877261430926"
        assert dataset.spatialCoverage.geo.box == bounding_box

    assert len(dataset.isPartOf) == 1
    assert dataset.isPartOf[0].description == "Dash, P. (2023). DSP Collection Resource Registration Test, HydroShare"
    assert dataset.isPartOf[0].url == "http://www.hydroshare.org/resource/35cd83561bd7424c9e28f95a79af7f02"
    assert dataset.hasPart == []
    assert dataset.citation == ["Dash, P., T. Z. Gichamo, Utah State University (2023). Testing IGUIDE Metadata Adapter for Hydroshare Resource, http://www.hydroshare.org/resource/1ee81318135c40f587d9a3e5d689daf5"]

    # test for resource files (MediaObject)
    assert len(dataset.associatedMedia) == 3
    assert dataset.associatedMedia[0].name == "V.dat"
    assert dataset.associatedMedia[1].name == "Qsi.nc"
    assert dataset.associatedMedia[2].name == "README.md"
    media_base_url = "http://www.hydroshare.org/resource/1ee81318135c40f587d9a3e5d689daf5/data/contents"
    for media in dataset.associatedMedia:
        if media.name == "V.dat":
            assert media.contentUrl == f"{media_base_url}/model-program/V.dat"
            assert media.encodingFormat == "None"
            assert media.contentSize == "124.144 KB"
            assert media.sha256 == "a0b00d911d09e69bdbee0033e40414f9"
        elif media.name == "Qsi.nc":
            assert media.contentUrl == f"{media_base_url}/model-program/Qsi.nc"
            assert media.encodingFormat == "application/x-netcdf"
            assert media.contentSize == "20.144 KB"
            assert media.sha256 == "93b546c41fca467496900d0f2415c1de"
        else:
            assert media.name == "README.md"
            assert media.contentUrl == f"{media_base_url}/README.md"
            assert media.encodingFormat == "text/markdown"
            assert media.contentSize == "4.422 KB"
            assert media.sha256 == "7d460cb12903a965d144cddcb2b62eac"


@pytest.mark.asyncio
async def test_hydroshare_collection_meta_adapter(hydroshare_collection_metadata, dataset_model):
    """Test the HydroshareMetaAdapter for Collection Resource"""

    adapter = get_adapter_by_type(RepositoryType.HYDROSHARE)
    dataset = adapter.to_catalog_record(hydroshare_collection_metadata)
    try:
        dataset_model(**dataset.model_dump())
    except ValidationError as err:
        pytest.fail(f"Catalog dataset schema model validation failed: {str(err)}")

    assert isinstance(dataset, DatasetMetadataDOC)
    assert dataset.isPartOf == []
    assert len(dataset.hasPart) == 3
    assert dataset.hasPart[0].description == "Tarboton, D. (2019). Created from iRODS by copy from create resource page, HydroShare"
    assert dataset.hasPart[0].url == "http://www.hydroshare.org/resource/abba182072cc48b691ca61509019e9f8"
    assert dataset.hasPart[1].description == "Dash, P. (2017). Water quality sensor data from the Little Bear River at Mendon Road near Mendon, UT, HydroShare"
    assert dataset.hasPart[1].url == "http://www.hydroshare.org/resource/fd6f39c25ccf492992c79465a2bf0030"
    assert dataset.hasPart[2].description == "Gan, T. (2016). Composite Resource Type Design, HydroShare"
    assert dataset.hasPart[2].url == "http://www.hydroshare.org/resource/e8cd813e376347c5b617deb321227a36"
    assert len(dataset.associatedMedia) == 0


@pytest.mark.asyncio
async def test_get_adapter_by_type():
    """Test the get_adapter_by_type function"""
    for repo_type in RepositoryType.__members__.values():
        adapter = get_adapter_by_type(repo_type)
        assert adapter is not None
