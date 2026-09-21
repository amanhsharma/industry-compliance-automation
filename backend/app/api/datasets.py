from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.dataset import DatasetUpload
from app.models.record import TransactionRecord
from app.schemas.dataset import DatasetUploadResponse, TransactionRecordResponse
from app.api.deps import get_current_user, require_roles
from app.services.ingestion import process_csv_upload

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "compliance_officer"]))
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV format (.csv) is currently supported for ingestion"
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty"
        )

    try:
        # Multi-tenant query scoping: Dataset and records are strictly bound to current_user.tenant_id
        dataset, rows_count, violations_count = process_csv_upload(
            db=db,
            file_content=content,
            filename=file.filename,
            tenant_id=current_user.tenant_id,
            uploaded_by_id=current_user.id
        )
        return dataset
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during CSV processing: {str(e)}"
        )

@router.get("", response_model=List[DatasetUploadResponse])
def list_datasets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Multi-tenant query scoping: Always filter by tenant_id to isolate data
    datasets = db.query(DatasetUpload)\
        .filter(DatasetUpload.tenant_id == current_user.tenant_id)\
        .order_by(DatasetUpload.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return datasets

@router.get("/{dataset_id}/records", response_model=List[TransactionRecordResponse])
def list_dataset_records(
    dataset_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Multi-tenant query scoping: Verify dataset belongs to user's tenant
    dataset = db.query(DatasetUpload).filter(
        DatasetUpload.id == dataset_id,
        DatasetUpload.tenant_id == current_user.tenant_id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    records = db.query(TransactionRecord)\
        .filter(
            TransactionRecord.dataset_id == dataset_id,
            TransactionRecord.tenant_id == current_user.tenant_id
        )\
        .order_by(TransactionRecord.created_at.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return records
