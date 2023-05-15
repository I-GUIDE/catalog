import pytest

from tests import client_test, dataset_data, core_data, change_test_dir

pytestmark = pytest.mark.asyncio

# TODO: add tests for the routes put and delete


async def test_dataset(client_test, dataset_data):
    """Testing the dataset routes for post and get"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.pop('_id')

    # prepare the expected dataset data
    dataset_data['funding'] = None
    dataset_data['publisher'] = None
    dataset_data['distribution']['comment'] = None
    dataset_data['creator'][0]['identifier']['name'] = None
    dataset_data['provider']['identifier'] = None
    dataset_data['provider']['address'] = None
    dataset_data['provider']['parentOrganization']['identifier'] = None
    dataset_data['spatialCoverage']['geo'] = None

    # assert that the response contains the expected data
    assert response_data == dataset_data

    # retrieve the record from the db
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200
