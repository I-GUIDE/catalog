from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from api.models.catalog import DatasetMetadataDOC


router = APIRouter()


@router.post("/dataset/", response_model=DatasetMetadataDOC, status_code=status.HTTP_201_CREATED)
async def create_dataset(document: DatasetMetadataDOC):
    await document.insert()
    return document


@router.get("/dataset/{document_id}", response_model=DatasetMetadataDOC)
async def get_dataset(document_id: PydanticObjectId):
    document = await DatasetMetadataDOC.get(document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    return document


@router.get("/dataset/", response_model=List[DatasetMetadataDOC])
async def get_datasets():
    documents = await DatasetMetadataDOC.find_all().to_list()
    return documents


@router.put("/dataset/{document_id}", response_model=DatasetMetadataDOC)
async def update_dataset(document_id: PydanticObjectId, updated_document: DatasetMetadataDOC):
    dataset = await DatasetMetadataDOC.get(document_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    await dataset.set(updated_document.dict(exclude_unset=True))
    dataset = await DatasetMetadataDOC.get(document_id)
    return dataset


@router.delete("/dataset/{document_id}", response_model=dict)
async def delete_dataset(document_id: PydanticObjectId):
    dataset = await DatasetMetadataDOC.get(document_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset metadata record was not found")
    await dataset.delete()
    return {"deleted_dataset_id": document_id}
