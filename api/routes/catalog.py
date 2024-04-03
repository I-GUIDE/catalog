from typing import Annotated, List, Type

from beanie import PydanticObjectId, WriteRules
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.adapters.utils import get_adapter_by_type, RepositoryType
from api.authentication.user import get_current_user
from api.models.catalog import (
    CoreMetadataDOC,
    GenericDatasetMetadataDOC,
    HSResourceMetadataDOC,
    NetCDFMetadataDOC,
)
from api.models.user import Submission, User


router = APIRouter()

# TODO: create endpoints to register netcdf and raster datasets - these endpoints will take a path to the
#  metadata json file and will create a new metadata record in the catalog. Use S3 (minIO) as the metadata file path


class S3Path(BaseModel):
    # this model is used to parse the request body for registering a dataset from S3
    path: str
    bucket: str
    endpoint_url: str = 'https://api.minio.cuahsi.io'


def inject_repository_identifier(
    submission: Submission,
    document: Type[CoreMetadataDOC],
):
    if submission.repository_identifier:
        document.repository_identifier = submission.repository_identifier
    return document


@router.post(
    "/dataset/generic",
    response_model=GenericDatasetMetadataDOC,
    summary="Create a new dataset metadata record in catalog with user provided metadata",
    description="Validates the user provided metadata and creates a new dataset metadata record in catalog",
    status_code=status.HTTP_201_CREATED,
)
async def create_generic_dataset(
    document: GenericDatasetMetadataDOC,
    user: Annotated[User, Depends(get_current_user)],
):
    await document.insert()
    submission = document.as_submission()
    user.submissions.append(submission)
    await user.save(link_rule=WriteRules.WRITE)
    return document


@router.get(
    "/dataset/generic/{submission_id}",
    response_model=GenericDatasetMetadataDOC,
    summary="Get a generic dataset metadata record",
    description="Retrieves a generic dataset metadata record by submission identifier",
    response_model_exclude_none=True,
)
async def get_generic_dataset(submission_id: PydanticObjectId):
    submission: Submission = await Submission.find_one(
        Submission.identifier == submission_id
    )
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata record was not found",
        )

    document: GenericDatasetMetadataDOC = await GenericDatasetMetadataDOC.get(submission.identifier)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata record was not found",
        )

    document = inject_repository_identifier(submission, document)
    return document


@router.get(
    "/dataset/hs-resource/{submission_id}",
    response_model=HSResourceMetadataDOC,
    response_model_exclude_none=True,
    summary="Get a HydroShare resource metadata record",
    description="Retrieves a HydroShare resource metadata record by submission identifier",
)
async def get_hydroshare_dataset(submission_id: PydanticObjectId):
    submission: Submission = await Submission.find_one(
        Submission.identifier == submission_id
    )
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata record was not found",
        )

    document: HSResourceMetadataDOC = await HSResourceMetadataDOC.get(submission.identifier)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata record was not found",
        )

    document = inject_repository_identifier(submission, document)
    return document


@router.put("/dataset/generic/{submission_id}",
            response_model=GenericDatasetMetadataDOC,
            summary="Update an existing generic dataset metadata record in catalog with user provided metadata",
            description="Validates the user provided metadata and updates an existing dataset metadata "
                        "record in catalog",
            )
async def update_dataset(
    submission_id: PydanticObjectId,
    updated_document: GenericDatasetMetadataDOC,
    user: Annotated[User, Depends(get_current_user)],
):
    submission: Submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )

    dataset: GenericDatasetMetadataDOC = await GenericDatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )

    updated_document.id = dataset.id
    await updated_document.replace()
    dataset: GenericDatasetMetadataDOC = await GenericDatasetMetadataDOC.get(submission_id)
    updated_submission: Submission = dataset.as_submission()
    updated_submission.id = submission.id
    updated_submission.repository_identifier = submission.repository_identifier
    updated_submission.repository = submission.repository
    updated_submission.submitted = submission.submitted
    await updated_submission.replace()
    dataset = inject_repository_identifier(updated_submission, dataset)
    return dataset


@router.delete("/dataset/{submission_id}",
               response_model=dict,
               summary="Delete a metadata record in catalog",
               description="Deletes a metadata record in catalog along with the submission record",
               )
async def delete_dataset(
    submission_id: PydanticObjectId, user: Annotated[User, Depends(get_current_user)]
):
    submission: Submission = user.submission(submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )
    dataset = await CoreMetadataDOC.get(submission.identifier, with_children=True)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )
    user.submissions.remove(submission)
    await user.save(link_rule=WriteRules.WRITE)
    await submission.delete()
    await dataset.delete()
    return {"deleted_dataset_id": submission_id}


@router.get("/submission/",
            response_model=List[Submission],
            response_model_exclude_none=True,
            summary="Get all submission records for the authenticated user",
            description="Retrieves all submission records for the authenticated user",
            )
async def get_submissions(user: Annotated[User, Depends(get_current_user)]):
    return user.submissions


@router.get("/repository/hydroshare/{identifier}",
            response_model=HSResourceMetadataDOC,
            summary="Register HydroShare resource metadata record in the catalog",
            description="Retrieves the metadata for the resource from HydroShare repository and creates a new "
                        "metadata record in the catalog",
            )
async def register_hydroshare_resource_metadata(
    identifier: str, user: Annotated[User, Depends(get_current_user)]
):
    # check that the user has not already registered this resource
    submission: Submission = user.submission_by_repository(
        repo_type=RepositoryType.HYDROSHARE, identifier=identifier
    )
    if submission is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This resource has already been submitted by this user",
        )
    dataset = await _save_to_db(
        repository_type=RepositoryType.HYDROSHARE, identifier=identifier, user=user
    )
    return dataset


@router.put("/repository/hydroshare/{identifier}",
            response_model=HSResourceMetadataDOC,
            summary="Refresh HydroShare resource metadata record in the catalog",
            description="Retrieves the metadata for the resource from HydroShare repository and updates the existing "
                        "metadata record in the catalog",
            )
async def refresh_dataset_from_hydroshare(
    identifier: str, user: Annotated[User, Depends(get_current_user)]
):
    submission: Submission = user.submission_by_repository(
        repo_type=RepositoryType.HYDROSHARE, identifier=identifier
    )
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )

    dataset = await HSResourceMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )

    dataset = await _save_to_db(
        repository_type=RepositoryType.HYDROSHARE,
        identifier=identifier,
        user=user,
        submission=submission,
    )
    return dataset


@router.put("/repository/s3/netcdf",
            response_model=NetCDFMetadataDOC,
            summary="Register a S3 NetCDF dataset metadata record in the catalog",
            description="Retrieves the metadata for the NetCDF dataset from S3 repository and creates a new metadata "
                        "record in the catalog",
            status_code=status.HTTP_201_CREATED
            )
async def register_s3_netcdf_dataset(request_model: S3Path, user: Annotated[User, Depends(get_current_user)]):
    path = request_model.path
    bucket = request_model.bucket
    endpoint_url = request_model.endpoint_url
    identifier = f"{endpoint_url}+{bucket}+{path}"
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.S3, identifier=identifier)
    dataset = await _save_to_db(repository_type=RepositoryType.S3, identifier=identifier, user=user,
                                submission=submission)
    return dataset


async def _save_to_db(
    repository_type: RepositoryType,
    identifier: str,
    user: User,
    submission: Submission = None,
):
    adapter = get_adapter_by_type(repository_type=repository_type)
    # fetch metadata from repository as catalog dataset
    repo_dataset = await _get_repo_meta_as_catalog_record(
        adapter=adapter, identifier=identifier
    )
    if submission is None:
        # new registration
        await repo_dataset.insert()
        submission = repo_dataset.as_submission()
        submission = adapter.update_submission(
            submission=submission, repo_record_id=identifier
        )
        user.submissions.append(submission)
        await user.save(link_rule=WriteRules.WRITE)
        dataset = repo_dataset
    else:
        # update existing registration
        dataset = await CoreMetadataDOC.get(submission.identifier, with_children=True)
        repo_dataset.id = dataset.id
        await repo_dataset.replace()
        updated_dataset = await CoreMetadataDOC.get(
            submission.identifier, with_children=True
        )
        updated_submission: Submission = updated_dataset.as_submission()
        updated_submission = adapter.update_submission(
            submission=updated_submission, repo_record_id=identifier
        )
        updated_submission.id = submission.id
        updated_submission.submitted = submission.submitted
        await updated_submission.replace()
        dataset = updated_dataset
        submission = updated_submission

    dataset = inject_repository_identifier(submission, dataset)
    return dataset


async def _get_repo_meta_as_catalog_record(adapter, identifier: str):
    try:
        metadata = await adapter.get_metadata(identifier)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{str(ex)}",
        )
    catalog_dataset: Type[CoreMetadataDOC] = adapter.to_catalog_record(metadata)
    return catalog_dataset
