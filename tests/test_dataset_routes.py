import pytest

from api.adapters.utils import RepositoryType
from api.models.catalog import Submission
from api.models.user import SubmissionType, User

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_dataset(client_test, dataset_data, test_user_access_token):
    """Testing the dataset routes for post and get"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.pop("_id")

    # adjust the temporal coverage dates for comparison
    if dataset_data["temporalCoverage"]["startDate"].endswith("Z"):
        dataset_data["temporalCoverage"]["startDate"] = dataset_data["temporalCoverage"]["startDate"][:-1]
    if dataset_data["temporalCoverage"]["endDate"].endswith("Z"):
        dataset_data["temporalCoverage"]["endDate"] = dataset_data["temporalCoverage"]["endDate"][:-1]
    start_date_length = len(dataset_data["temporalCoverage"]["startDate"])
    end_date_length = len(dataset_data["temporalCoverage"]["endDate"])

    response_data['temporalCoverage']['startDate'] = response_data['temporalCoverage']['startDate'][:start_date_length]
    response_data['temporalCoverage']['endDate'] = response_data['temporalCoverage']['endDate'][:end_date_length]
    # assert that the response contains the expected data
    response_data.pop("repository_identifier")
    response_data["submission_type"] = SubmissionType.IGUIDE_FORM
    response_data.pop("submission_type")
    response_data.pop("s3_path")
    # remove additional property fields from response_data for which the test data does not have values
    for a_property in response_data["additionalProperty"]:
        assert a_property.pop("description") is None
        assert a_property.pop("minValue") is None
        assert a_property.pop("maxValue") is None
        assert a_property.pop("unitCode") is None
        assert a_property.pop("propertyID") is None
        assert a_property.pop("measurementTechnique") is None

    assert response_data == dataset_data
    # there should be one related submission record in the db
    submissions = await Submission.find().to_list()
    assert len(submissions) == 1
    user = await User.find_one(User.access_token == test_user_access_token, fetch_links=True)
    assert len(user.submissions) == 1
    submission_id = submissions[0].identifier
    assert submission_id == user.submissions[0].identifier
    assert user.submission(submission_id) is not None
    assert user.submission(submission_id).repository is None
    assert user.submission(submission_id).repository_identifier is None
    # retrieve the record from the db
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200


@pytest.mark.parametrize('object_store_type', ['s3', 'minio'])
@pytest.mark.asyncio
async def test_create_dataset_s3(client_test, dataset_data, test_user_access_token, object_store_type):
    """Testing the s3 dataset routes for post and get"""

    if object_store_type == "minio":
        # set the path to the generic metadata file on minIO s3
        s3_path = {
            "path": "data/.hs/dataset_metadata.json",
            "bucket": "catalog-api-test",
            "endpoint_url": "https://api.minio.cuahsi.io/",
        }
    else:
        # set the path to the generic metadata file on AWS s3
        s3_path = {
            "path": "data/.hs/dataset_metadata.json",
            "bucket": "iguide-catalog",
            "endpoint_url": "https://iguide-catalog.s3.us-west-2.amazonaws.com/",
        }

    payload = {
        "s3_path": s3_path,
        "document": dataset_data
    }

    # this is the endpoint for creating the s3 metadata record that we are testing
    response = await client_test.post("api/catalog/dataset-s3/", json=payload)
    assert response.status_code == 201
    ds_metadata = response.json()
    if object_store_type == "minio":
        expected_repository_identifier = f"{s3_path['endpoint_url']}{s3_path['bucket']}/{s3_path['path']}"
    else:
        expected_repository_identifier = f"{s3_path['endpoint_url']}{s3_path['path']}"
    assert ds_metadata["repository_identifier"] == expected_repository_identifier
    assert ds_metadata["submission_type"] == SubmissionType.S3
    assert ds_metadata["s3_path"] == s3_path

    # retrieve the record from the db
    record_id = ds_metadata.pop('_id')
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200
    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200
    submission_response_data = submission_response.json()
    assert len(submission_response_data) == 1
    assert submission_response_data[0]['repository'] == RepositoryType.S3
    assert submission_response_data[0]['s3_path'] == s3_path


@pytest.mark.parametrize('object_store_type', ['s3', 'minio'])
@pytest.mark.asyncio
async def test_update_dataset_s3(client_test, dataset_data, test_user_access_token, object_store_type):
    """Testing the s3 dataset route (api/catalog/dataset-s3/) for put for updating s3 metadata record"""

    if object_store_type == "minio":
        # set the path to the generic metadata file on minIO s3
        s3_path = {
            "path": "data/.hs/dataset_metadata.json",
            "bucket": "catalog-api-test",
            "endpoint_url": "https://api.minio.cuahsi.io/",
        }
    else:
        # set the path to the generic metadata file on AWS s3
        s3_path = {
            "path": "data/.hs/dataset_metadata.json",
            "bucket": "iguide-catalog",
            "endpoint_url": "https://iguide-catalog.s3.us-west-2.amazonaws.com/",
        }

    payload = {
        "s3_path": s3_path,
        "document": dataset_data
    }

    response = await client_test.post("api/catalog/dataset-s3/", json=payload)
    assert response.status_code == 201
    ds_metadata = response.json()
    if object_store_type == "minio":
        expected_repository_identifier = f"{s3_path['endpoint_url']}{s3_path['bucket']}/{s3_path['path']}"
    else:
        expected_repository_identifier = f"{s3_path['endpoint_url']}{s3_path['path']}"
    assert ds_metadata["repository_identifier"] == expected_repository_identifier
    assert ds_metadata["submission_type"] == SubmissionType.S3
    # retrieve the record from the db
    record_id = ds_metadata.pop('_id')
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200

    # update the dataset record
    dataset_data['name'] = 'Updated title for S3 metadata record'
    if object_store_type == "minio":
        # set the path to the generic metadata file on minIO s3 - changing the path
        s3_path = {
            "path": "data/.hs/dataset_metadata-updated.json",
            "bucket": "catalog-api-test-updated",
            "endpoint_url": "https://api.minio.cuahsi.io/",
        }
    else:
        # set the path to the generic metadata file on AWS s3 - changing the path and bucket
        s3_path = {
            "path": "data/.hs/dataset_metadata-updated.json",
            "bucket": "iguide-catalog-updated",
            "endpoint_url": "https://iguide-catalog-updated.s3.us-west-2.amazonaws.com/",
        }

    payload = {
        "s3_path": s3_path,
        "document": dataset_data
    }
    # this is the endpoint for updating the s3 metadata record that we are testing
    response = await client_test.put(f"api/catalog/dataset-s3/{record_id}", json=payload)
    assert response.status_code == 200
    ds_metadata = response.json()
    if object_store_type == "minio":
        expected_repository_identifier = f"{s3_path['endpoint_url']}{s3_path['bucket']}/{s3_path['path']}"
    else:
        expected_repository_identifier = f"{s3_path['endpoint_url']}{s3_path['path']}"
    assert ds_metadata["repository_identifier"] == expected_repository_identifier
    assert ds_metadata["submission_type"] == SubmissionType.S3
    assert ds_metadata["s3_path"] == s3_path
    assert ds_metadata["name"] == dataset_data['name']
    # retrieve the record from the db
    record_id = ds_metadata.pop('_id')
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200
    ds_metadata = response.json()
    assert ds_metadata["s3_path"] == s3_path

    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200
    submission_response_data = submission_response.json()
    assert len(submission_response_data) == 1
    assert submission_response_data[0]['repository'] == RepositoryType.S3
    assert submission_response_data[0]['s3_path'] == s3_path


@pytest.mark.asyncio
async def test_create_refresh_dataset_from_hydroshare(
    client_test, test_user_access_token
):
    """Testing catalog registration/refresh of hydroshare metadata record"""

    # create hydroshare resource metadata as a catalog dataset record
    hs_published_res_id = "b5f58460941c49578e311adb9823657a"
    response = await client_test.get(f"api/catalog/repository/hydroshare/{hs_published_res_id}")
    assert response.status_code == 200
    hs_dataset = response.json()
    assert hs_dataset['repository_identifier'] == hs_published_res_id
    assert hs_dataset['submission_type'] == SubmissionType.HYDROSHARE
    await _check_hs_submission(hs_dataset, test_user_access_token, hs_published_res_id)

    # retrieve the record from the db
    record_id = hs_dataset.get('_id')
    response = await client_test.get(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200

    # refresh the hydroshare metadata record
    response = await client_test.put(f"api/catalog/repository/hydroshare/{hs_published_res_id}")
    assert response.status_code == 200
    hs_dataset = response.json()
    assert hs_dataset["repository_identifier"] == hs_published_res_id
    assert hs_dataset["submission_type"] == SubmissionType.HYDROSHARE
    await _check_hs_submission(hs_dataset, test_user_access_token, hs_published_res_id)


@pytest.mark.asyncio
async def test_update_dataset(client_test, dataset_data):
    """Testing the dataset put route for updating dataset record"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.get("_id")
    # update the dataset name
    dataset_data["name"] = "Updated title"
    # remove citation
    dataset_data["citation"] = []
    # remove publisher
    dataset_data["publisher"] = None

    # update the dataset temporal coverage
    dataset_data["temporalCoverage"] = {
        "startDate": "2020-01-01T10:00:20",
        "endDate": "2020-11-29T00:30:00",
    }
    response = await client_test.put(
        f"api/catalog/dataset/{record_id}", json=dataset_data
    )
    assert response.status_code == 200
    response_data = response.json()
    response_data.pop("_id")
    # assert that the response contains the expected data
    response_data.pop("repository_identifier")
    response_data["submission_type"] = SubmissionType.IGUIDE_FORM
    response_data.pop("submission_type")
    response_data.pop("s3_path")
    # remove additional property fields from response_data for which the test data does not have values
    for a_property in response_data["additionalProperty"]:
        assert a_property.pop("description") is None
        assert a_property.pop("minValue") is None
        assert a_property.pop("maxValue") is None
        assert a_property.pop("unitCode") is None
        assert a_property.pop("propertyID") is None
        assert a_property.pop("measurementTechnique") is None
    assert response_data == dataset_data


@pytest.mark.asyncio
async def test_delete_dataset(client_test, dataset_data, test_user_access_token):
    """Testing the dataset delete route for deleting a dataset record"""

    # add a dataset record to the db
    response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert response.status_code == 201
    response_data = response.json()
    record_id = response_data.get("_id")
    # delete the dataset record
    response = await client_test.delete(f"api/catalog/dataset/{record_id}")
    assert response.status_code == 200
    # there should not be any submission records in the db
    assert await Submission.find_many().count() == 0
    user = await User.find_one(User.access_token == test_user_access_token, fetch_links=True)
    assert len(user.submissions) == 0

    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200


@pytest.mark.parametrize("multiple", [True, False])
@pytest.mark.asyncio
async def test_get_datasets(client_test, dataset_data, multiple):
    """Testing the get all datasets for a given user"""

    # add a dataset record to the db
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    if multiple:
        # add another dataset record to the db
        dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
        assert dataset_response.status_code == 201

    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    if multiple:
        assert len(dataset_response_data) == 2
    else:
        assert len(dataset_response_data) == 1

    for ds in dataset_response_data:
        assert ds["submission_type"] == SubmissionType.IGUIDE_FORM


@pytest.mark.asyncio
async def test_get_datasets_2(client_test, dataset_data):
    """Testing the get all datasets for a given user with different submission types"""

    # add a dataset record to the db
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    # set the path to the generic metadata file on minIO s3
    s3_path = {
        "path": "data/.hs/dataset_metadata.json",
        "bucket": "catalog-api-test",
        "endpoint_url": "https://api.minio.cuahsi.io/",
    }
    payload = {
        "s3_path": s3_path,
        "document": dataset_data
    }

    response = await client_test.post("api/catalog/dataset-s3/", json=payload)
    assert response.status_code == 201

    # this is the endpoint we are testing
    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    assert len(dataset_response_data) == 2
    assert dataset_response_data[0]["submission_type"] == SubmissionType.IGUIDE_FORM
    assert dataset_response_data[1]["submission_type"] == SubmissionType.S3
    assert dataset_response_data[1]["s3_path"] == s3_path


@pytest.mark.asyncio
async def test_get_datasets_different_submission_types(client_test, dataset_data):
    """Testing the get all datasets for a given user"""

    # add a dataset record to the db simulation iGuide form submission
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201

    # add a dataset record to the db simulation S3 submission
    s3_path = {
            "path": "data/.hs/dataset_metadata.json",
            "bucket": "iguide-catalog",
            "endpoint_url": "https://iguide-catalog.s3.us-west-2.amazonaws.com/",
        }

    payload = {
        "s3_path": s3_path,
        "document": dataset_data
    }

    dataset_response = await client_test.post("api/catalog/dataset-s3/", json=payload)
    assert dataset_response.status_code == 201

    # add a dataset record to the db simulation HydroShare submission
    hs_published_res_id = "b5f58460941c49578e311adb9823657a"
    response = await client_test.get(f"api/catalog/repository/hydroshare/{hs_published_res_id}")
    assert response.status_code == 200
    hs_dataset = response.json()
    assert hs_dataset['repository_identifier'] == hs_published_res_id
    assert hs_dataset['submission_type'] == SubmissionType.HYDROSHARE

    # retrieve all datasets
    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    assert len(dataset_response_data) == 3
    assert dataset_response_data[0]["submission_type"] == SubmissionType.IGUIDE_FORM
    assert dataset_response_data[1]["submission_type"] == SubmissionType.S3
    assert dataset_response_data[2]["submission_type"] == SubmissionType.HYDROSHARE
    assert dataset_response_data[1]["s3_path"] == s3_path


@pytest.mark.asyncio
async def test_get_datasets_exclude_none(client_test, dataset_data):
    """Testing exclude none is applied to dataset response model"""

    dataset_data["version"] = None
    dataset_data["spatialCoverage"]["name"] = None
    # add a dataset record to the db
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201

    dataset_response = await client_test.get("api/catalog/dataset")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response.json()
    assert "version" not in dataset_response_data[0]
    assert "name" not in dataset_response_data[0]["spatialCoverage"]
    for a_property in dataset_response_data[0]["additionalProperty"]:
        assert "description" not in a_property
        assert "minValue" not in a_property
        assert "maxValue" not in a_property
        assert "unitCode" not in a_property
        assert "propertyID" not in a_property
        assert "measurementTechnique" not in a_property


@pytest.mark.parametrize("multiple", [True, False])
@pytest.mark.asyncio
async def test_get_submissions_1(client_test, dataset_data, multiple):
    """Testing the get submissions route with one submission type only"""

    # add a dataset record to the db - this will also add a submission record
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    dataset_response_data = dataset_response.json()
    if multiple:
        # add another dataset record to the db - this will also add a submission record
        dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
        assert dataset_response.status_code == 201
        dataset_response_data = [dataset_response_data, dataset_response.json()]

    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200
    submission_response_data = submission_response.json()
    if multiple:
        assert len(submission_response_data) == 2
        assert submission_response_data[0]['identifier'] != submission_response_data[1]['identifier']
        assert submission_response_data[0]['title'] == dataset_response_data[0]['name']
        assert submission_response_data[1]['title'] == dataset_response_data[1]['name']
        assert submission_response_data[0]['identifier'] == dataset_response_data[0]['_id']
        assert submission_response_data[1]['identifier'] == dataset_response_data[1]['_id']
        assert submission_response_data[0]['url'] == dataset_response_data[0]['url']
        assert submission_response_data[1]['url'] == dataset_response_data[1]['url']
        assert submission_response_data[0]['repository'] is None
        assert submission_response_data[1]['repository'] is None
    else:
        assert len(submission_response_data) == 1
        assert submission_response_data[0]['title'] == dataset_response_data['name']
        assert submission_response_data[0]['identifier'] == dataset_response_data['_id']
        assert submission_response_data[0]['url'] == dataset_response_data['url']
        assert submission_response_data[0]['repository'] is None


@pytest.mark.asyncio
async def test_get_submissions_2(client_test, dataset_data):
    """Testing the get submissions route with different submission types"""

    # add a dataset record to the db - this will also add a submission record
    dataset_response = await client_test.post("api/catalog/dataset", json=dataset_data)
    assert dataset_response.status_code == 201
    dataset_response_data = dataset_response.json()
    s3_path = {
            "path": "data/.hs/dataset_metadata.json",
            "bucket": "iguide-catalog",
            "endpoint_url": "https://iguide-catalog.s3.us-west-2.amazonaws.com/",
        }

    payload = {
        "s3_path": s3_path,
        "document": dataset_data
    }

    dataset_response = await client_test.post("api/catalog/dataset-s3/", json=payload)
    assert dataset_response.status_code == 201
    dataset_response_data = [dataset_response_data, dataset_response.json()]

    # add a dataset record to the db simulation HydroShare submission
    hs_published_res_id = "b5f58460941c49578e311adb9823657a"
    dataset_response = await client_test.get(f"api/catalog/repository/hydroshare/{hs_published_res_id}")
    assert dataset_response.status_code == 200
    dataset_response_data = dataset_response_data + [dataset_response.json()]
    # retrieve all submissions for the current user from the db
    submission_response = await client_test.get("api/catalog/submission")
    assert submission_response.status_code == 200
    submission_response_data = submission_response.json()
    assert len(submission_response_data) == 3
    assert submission_response_data[0]['identifier'] != submission_response_data[1]['identifier']
    assert submission_response_data[0]['title'] == dataset_response_data[0]['name']
    assert submission_response_data[1]['title'] == dataset_response_data[1]['name']
    assert submission_response_data[0]['identifier'] == dataset_response_data[0]['_id']
    assert submission_response_data[1]['identifier'] == dataset_response_data[1]['_id']
    assert submission_response_data[0]['url'] == dataset_response_data[0]['url']
    assert submission_response_data[1]['url'] == dataset_response_data[1]['url']
    assert submission_response_data[0]['repository'] is None
    assert submission_response_data[1]['repository'] == RepositoryType.S3
    assert submission_response_data[1]['s3_path'] == payload['s3_path']
    assert submission_response_data[2]['repository'] == RepositoryType.HYDROSHARE
    assert submission_response_data[2]['s3_path'] is None


async def _check_hs_submission(hs_dataset, user_access_token, hs_published_res_id):
    assert hs_dataset["provider"]["name"] == "HYDROSHARE"
    assert hs_dataset["provider"]["url"] == "https://www.hydroshare.org/"

    # there should be one related submission record in the db
    submissions = await Submission.find().to_list()
    assert len(submissions) == 1
    user = await User.find_one(User.access_token == user_access_token, fetch_links=True)
    assert len(user.submissions) == 1
    submission_id = submissions[0].identifier
    assert submission_id == user.submissions[0].identifier
    assert user.submission(submission_id) is not None
    assert user.submission(submission_id).repository == "HYDROSHARE"
    assert user.submission(submission_id).repository_identifier == hs_published_res_id
