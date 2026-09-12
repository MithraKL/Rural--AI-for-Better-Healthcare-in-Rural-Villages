from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import DatasetMetadata
from backend.schemas import UploadResponse, DatasetMetadataOut
from backend.data.ingestion import read_upload, ingest_dataframe, SOURCE_GRANULARITY
from backend.services.pipeline import recompute_all

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(
    source_name: str = Form(..., description="One of RHS, HMIS, NFHS, DLHS, AHS, Anganwadi"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    try:
        df = read_upload(file.filename, content)
    except ValueError as e:
        return UploadResponse(success=False, message=str(e), errors=[str(e)])

    result = ingest_dataframe(db, source_name, df)
    if not result.success:
        return UploadResponse(success=False, message="Upload failed validation.", errors=result.errors)

    dataset = DatasetMetadata(
        source_name=source_name, file_name=file.filename,
        granularity=SOURCE_GRANULARITY[source_name], row_count=result.inserted,
        is_demo=False,
        notes=f"Uploaded by user. {result.duplicates_dropped} duplicate(s) dropped, "
              f"{result.missing_values_filled} missing value(s) imputed with column median.",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return UploadResponse(
        success=True,
        message=f"Ingested {result.inserted} of {result.row_count} row(s) for {source_name}. "
                f"Run /api/data/recompute to refresh AI scores with this new data.",
        dataset=DatasetMetadataOut.model_validate(dataset),
        errors=result.errors,
    )


@router.get("/datasets", response_model=list[DatasetMetadataOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(DatasetMetadata).order_by(DatasetMetadata.uploaded_at.desc()).all()


@router.post("/recompute")
def recompute(db: Session = Depends(get_db)):
    summary = recompute_all(db)
    return {"message": "Pipeline recomputed.", **summary}
