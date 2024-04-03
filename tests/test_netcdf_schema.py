import pytest

from tests import utils


@pytest.mark.asyncio
async def test_netcdf_schema(netcdf_metadata, netcdf_metadata_model):
    """Test that a netcdf metadata pydantic model can be created from netcdf  metadata json.
    Purpose of the test is to validate netcdf metadata schema as defined by the pydantic model. Note: This test does nat
    add a record to the database.
    """
    netcdf_metadata = netcdf_metadata
    netcdf_metadata_model = netcdf_metadata_model
    # remove additionalType field
    netcdf_metadata.pop("additionalType")
    # validate the data model
    name = "Snow water equivalent estimation at TWDEF site from Oct 2009 to June 2010"
    description = ("This netCDF data is the simulation output from Utah Energy Balance (UEB) model.It includes "
                   "the simulation result of snow water equivalent during the period Oct. 2009 to June 2010 "
                   "for TWDEF site in Utah.")
    netcdf_model_instance = await utils.validate_data_model(netcdf_metadata, netcdf_metadata_model, name, description)

    assert netcdf_model_instance.name == name
    assert netcdf_model_instance.additionalType == "NetCDF"
