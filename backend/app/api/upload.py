from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from ingestion.pipeline import IngestionPipeline

router = APIRouter(tags=["Upload"])

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload PDF or JSON document.
    """

    suffix = Path(file.filename).suffix.lower()

    if suffix not in [".pdf", ".json"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and JSON files are supported."
        )

    filename = f"{uuid4()}{suffix}"

    file_path = UPLOAD_FOLDER / filename

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pipeline = IngestionPipeline()

        if suffix == ".pdf":
            pipeline.ingest_pdf(str(file_path))
        else:
            pipeline.ingest_json(str(file_path))

        return {
            "success": True,
            "filename": file.filename,
            "message": "Document ingested successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )