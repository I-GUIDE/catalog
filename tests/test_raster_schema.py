import pytest

from tests import utils


@pytest.mark.asyncio
async def test_raster_schema(raster_metadata, raster_metadata_model):
    """Test that a raster metadata pydantic model can be created from netcdf  metadata json.
    Purpose of the test is to validate raster metadata schema as defined by the pydantic model. Note: This test does nat
    add a record to the database.
    """
    raster_metadata = raster_metadata
    raster_metadata_model = raster_metadata_model
    # remove additionalType field
    raster_metadata.pop("additionalType")
    # validate the data model
    name = "Logan"
    description = None
    raster_model_instance = await utils.validate_data_model(raster_metadata, raster_metadata_model, name, description)

    assert raster_model_instance.name == name
    assert raster_model_instance.additionalType == "Geo Raster"
