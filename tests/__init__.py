import json
import os
import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from api.models.schema import CoreMetadata, Dataset
from api.config import get_settings
from main import app


@pytest.fixture
async def client_test():
    """
    Create an instance of the client.
    :return: yield HTTP client.
    """
    if not get_settings().testing:
        raise Exception("App is not in testing mode")
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
            ac.app = app
            yield ac


@pytest.fixture(scope="function")
async def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


@pytest.fixture
async def core_data(change_test_dir):
    with open("data/core_metadata.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture
async def dataset_data(core_data):
    dataset_data = core_data.copy()
    # add dataset specific metadata
    dataset_data["distribution"] = {
        "@type": "DataDownload",
        "name": "Search",
        "contentUrl": "https://www.my-unique-url.com/get_zip/9d413b9d1/",
        "encodingFormat": "application/zip",
        "contentSize": "102.1 MB"
      }
    dataset_data["variableMeasured"] = "Water Temperature"
    return dataset_data


@pytest.fixture
async def core_model():
    return CoreMetadata


@pytest.fixture
async def dataset_model():
    class _Dataset(Dataset, CoreMetadata):
        pass
    return _Dataset
