from typing import Annotated, List, Type

from beanie import PydanticObjectId, WriteRules
from fastapi import APIRouter, Depends, HTTPException, status

from api.adapters.utils import get_adapter_by_type, RepositoryType
from api.authentication.user import get_current_user
from api.models.catalog import (
    T,
    CoreMetadataDOC,
    GenericDatasetMetadataDOC,
    HSResourceMetadataDOC,
    NetCDFMetadataDOC,
)
from api.models.user import Submission, User, SubmissionType, S3Path


router = APIRouter()

# TODO: create endpoints to register netcdf and raster datasets - these endpoints will take a path to the
#  metadata json file and will create a new metadata record in the catalog. Use S3 (minIO) as the metadata file path


def inject_repository_identifier(
    submission: Submission,
    document: T,
) -> T:
    if submission.repository_identifier:
        document.repository_identifier = submission.repository_identifier
    return document


def inject_submission_type(submission: Submission, document: T) -> T:
    if submission.repository is None:
        document.submission_type = SubmissionType.IGUIDE_FORM
    else:
        document.submission_type = submission.repository
    return document


def inject_submission_s3_path(submission: Submission, document: T) -> T:
    if submission.s3_path:
        document.s3_path = submission.s3_path
    else:
        document.s3_path = None
    return document


@router.post(
    "/dataset/generic",
    response_model=GenericDatasetMetadataDOC,
    summary="Create a new generic dataset metadata record in catalog with user provided metadata",
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
    document = inject_repository_identifier(submission, document)
    document = inject_submission_type(submission, document)
    document = inject_submission_s3_path(submission, document)
    return document


@router.get(
    "/dataset/generic/{submission_id}",
    response_model=GenericDatasetMetadataDOC,
    summary="Get a generic dataset metadata record",
    description="Retrieves a generic dataset metadata record by submission identifier",
    response_model_exclude_none=True,
)
async def get_generic_dataset(submission_id: PydanticObjectId):
    document: GenericDatasetMetadataDOC = await _get_metadata_doc(
        submission_id, GenericDatasetMetadataDOC
    )
    return document


@router.get(
    "/dataset/netcdf/{submission_id}",
    response_model=NetCDFMetadataDOC,
    summary="Get a netcdf dataset metadata record",
    description="Retrieves a netcdf dataset metadata record by submission identifier",
    response_model_exclude_none=True,
)
async def get_netcdf_dataset(submission_id: PydanticObjectId):
    document: NetCDFMetadataDOC = await _get_metadata_doc(
        submission_id, NetCDFMetadataDOC
    )
    return document


@router.get(
    "/dataset/hs-resource/{submission_id}",
    response_model=HSResourceMetadataDOC,
    response_model_exclude_none=True,
    summary="Get a HydroShare resource metadata record",
    description="Retrieves a HydroShare resource metadata record by submission identifier",
)
async def get_hydroshare_dataset(submission_id: PydanticObjectId):
    document: HSResourceMetadataDOC = await _get_metadata_doc(
        submission_id, HSResourceMetadataDOC
    )
    return document


@router.get(
    "/dataset/",
    response_model=List[CoreMetadataDOC],
    response_model_exclude_none=True,
    summary="Get all dataset metadata records for the authenticated user",
    description="Retrieves all dataset metadata records for the authenticated user",
)
async def get_datasets(user: Annotated[User, Depends(get_current_user)]):
    documents = [
        inject_repository_identifier(
            submission, await CoreMetadataDOC.find_one(
                CoreMetadataDOC.id == submission.identifier, with_children=True).project(CoreMetadataDOC)
        )
        for submission in user.submissions
    ]
    documents = [
        inject_submission_type(submission, document)
        for submission, document in zip(user.submissions, documents)
    ]
    documents = [
        inject_submission_s3_path(submission, document)
        for submission, document in zip(user.submissions, documents)
    ]
    return documents


@router.put(
    "/dataset/generic/{submission_id}",
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
    dataset = await _update_dataset(updated_document=updated_document, original_document=dataset, submission=submission)
    return dataset


@router.delete(
    "/dataset/{submission_id}",
    response_model=dict,
    summary="Delete a metadata record from the catalog",
    description="Deletes a metadata record in catalog along with the submission record",
    status_code=status.HTTP_200_OK,
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
            summary="Get all submission records for the authenticated user",
            description="Retrieves all submission records for the authenticated user",
            status_code=status.HTTP_200_OK,
            )
async def get_submissions(user: Annotated[User, Depends(get_current_user)]):
    return user.submissions


@router.get("/repository/hydroshare/{identifier}",
            response_model=HSResourceMetadataDOC,
            summary="Register HydroShare resource metadata record in the catalog",
            description="Retrieves the metadata for the resource from HydroShare repository and creates a new "
                        "metadata record in the catalog",
            status_code=status.HTTP_201_CREATED,
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
        repository_type=RepositoryType.HYDROSHARE, identifier=identifier,
        meta_model_type=HSResourceMetadataDOC, user=user
    )
    return dataset


@router.put("/repository/hydroshare/{identifier}",
            response_model=HSResourceMetadataDOC,
            summary="Refresh HydroShare resource metadata record in the catalog",
            description="Retrieves the metadata for the resource from HydroShare repository and updates the existing "
                        "metadata record in the catalog",
            status_code=status.HTTP_200_OK,
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
        meta_model_type=HSResourceMetadataDOC,
        submission=submission,
    )
    return dataset


@router.post("/repository/s3/generic",
             response_model=GenericDatasetMetadataDOC,
             summary="Register a S3 generic dataset metadata record in the catalog",
             description="Retrieves the metadata for the generic dataset from S3 repository and creates a new metadata "
                         "record in the catalog",
             status_code=status.HTTP_201_CREATED
             )
async def register_s3_generic_dataset(s3_path: S3Path, user: Annotated[User, Depends(get_current_user)]):
    identifier = s3_path.identifier
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.S3, identifier=identifier)
    identifier = s3_path.access_url
    dataset = await _save_to_db(repository_type=RepositoryType.S3, identifier=identifier, user=user,
                                meta_model_type=GenericDatasetMetadataDOC,
                                submission=submission)
    return dataset


@router.post("/repository/s3/netcdf",
             response_model=NetCDFMetadataDOC,
             summary="Register a S3 NetCDF dataset metadata record in the catalog",
             description="Retrieves the metadata for the NetCDF dataset from S3 repository and creates a new metadata "
                         "record in the catalog",
             status_code=status.HTTP_201_CREATED
             )
async def register_s3_netcdf_dataset(s3_path: S3Path, user: Annotated[User, Depends(get_current_user)]):
    identifier = s3_path.identifier
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.S3, identifier=identifier)
    identifier = s3_path.access_url
    dataset = await _save_to_db(repository_type=RepositoryType.S3, identifier=identifier, user=user,
                                meta_model_type=NetCDFMetadataDOC,
                                submission=submission)
    return dataset


@router.post(
    "/dataset-s3/",
    response_model=GenericDatasetMetadataDOC,
    summary="Create a new generic dataset metadata record in catalog with user provided metadata for a S3 data object",
    status_code=status.HTTP_201_CREATED
)
async def create_dataset_s3(
        s3_path: S3Path,
        document: GenericDatasetMetadataDOC,
        user: Annotated[User, Depends(get_current_user)]
):
    """User provides the metadata for the dataset and the path to the S3 object. The metadata is saved
    to the catalog. The S3 object is not fetched. Also, the metadata is currently not saved to the S3 object.
    """

    identifier = s3_path.identifier
    submission: Submission = user.submission_by_repository(repo_type=RepositoryType.S3, identifier=identifier)
    if submission is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset metadata record was not found",
        )
    await document.insert()
    submission = document.as_submission()
    submission.repository_identifier = identifier
    submission.repository = RepositoryType.S3
    submission.s3_path = s3_path
    user.submissions.append(submission)
    await user.save(link_rule=WriteRules.WRITE)
    document = inject_repository_identifier(submission, document)
    document = inject_submission_type(submission, document)
    document = inject_submission_s3_path(submission, document)
    return document


@router.put(
    "/dataset-s3/{submission_id}",
    response_model=GenericDatasetMetadataDOC,
    summary="Update an existing generic dataset metadata record in catalog with user provided"
            " metadata for a S3 data object",
    description="Validates the user provided metadata and updates an existing dataset metadata ",
    status_code=status.HTTP_200_OK
)
async def update_dataset_s3(
        s3_path: S3Path,
        submission_id: PydanticObjectId,
        document: GenericDatasetMetadataDOC,
        user: Annotated[User, Depends(get_current_user)]
):
    """User provides the updated metadata for the dataset and the path to the S3 object. The metadata is saved
    to the catalog. The S3 object is not fetched. Also, the metadata is currently not saved to the S3 object.
    We are also allowing the user to update the S3 path as part of the metadata update. Is that a good idea?
    """

    identifier = s3_path.identifier
    submission: Submission = user.submission(submission_id)
    if submission is None or submission.repository != RepositoryType.S3:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset metadata record was not found",
        )

    dataset: GenericDatasetMetadataDOC = await GenericDatasetMetadataDOC.get(submission.identifier)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Dataset metadata record was not found")

    submission.repository_identifier = identifier
    submission.s3_path = s3_path
    dataset = await _update_dataset(updated_document=document, original_document=dataset, submission=submission)
    return dataset


async def _save_to_db(
    repository_type: RepositoryType,
    identifier: str,
    user: User,
    meta_model_type: Type[T],
    submission: Submission = None,
) -> T:
    adapter = get_adapter_by_type(repository_type=repository_type)
    # fetch metadata from repository as catalog dataset
    repo_dataset = await _get_repo_meta_as_catalog_record(
        adapter=adapter, identifier=identifier, meta_model_type=meta_model_type
    )
    s3_path = None
    if repository_type == RepositoryType.S3:
        s3_endpoint_url, bucket, path = identifier.split("+")
        s3_path = S3Path(path=path, bucket=bucket, endpoint_url=s3_endpoint_url)
        identifier = s3_path.identifier
    if submission is None:
        # new registration
        await repo_dataset.insert()
        submission = repo_dataset.as_submission()
        submission = adapter.update_submission(
            submission=submission, repo_record_id=identifier
        )
        submission.s3_path = s3_path
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
        updated_submission.s3_path = s3_path
        await updated_submission.replace()
        dataset = updated_dataset
        submission = updated_submission

    dataset = inject_repository_identifier(submission, dataset)
    dataset = inject_submission_type(submission, dataset)
    dataset = inject_submission_s3_path(submission, dataset)
    return dataset


async def _get_repo_meta_as_catalog_record(adapter, identifier: str, meta_model_type: Type[T]) -> T:
    metadata = await adapter.get_metadata(identifier)
    catalog_dataset: T = adapter.to_catalog_record(metadata, meta_model_type=meta_model_type)
    return catalog_dataset


async def _get_metadata_doc(submission_id: PydanticObjectId, meta_model_type: Type[T]) -> T:
    submission: Submission = await Submission.find_one(
        Submission.identifier == submission_id
    )
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata record was not found",
        )

    document: meta_model_type = await meta_model_type.get(submission.identifier)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metadata record was not found",
        )

    document = inject_repository_identifier(submission, document)
    document = inject_submission_type(submission, document)
    document = inject_submission_s3_path(submission, document)
    return document


async def _update_dataset(updated_document: T, original_document: T,
                          submission: Submission):
    updated_document.id = original_document.id
    await updated_document.replace()
    dataset: T = await CoreMetadataDOC.get(original_document.id, with_children=True)
    updated_submission: Submission = dataset.as_submission()
    updated_submission.id = submission.id
    updated_submission.repository_identifier = submission.repository_identifier
    updated_submission.repository = submission.repository
    updated_submission.submitted = submission.submitted
    updated_submission.s3_path = submission.s3_path
    await updated_submission.replace()
    dataset = inject_repository_identifier(updated_submission, dataset)
    dataset = inject_submission_type(updated_submission, dataset)
    dataset = inject_submission_s3_path(updated_submission, dataset)
    return dataset
