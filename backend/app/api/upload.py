from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from ingestion.pipeline import DocumentIngestionPipeline


router = APIRouter(tags=["Upload"])

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload and ingest a PDF document.
    """

    suffix = Path(
        file.filename or ""
    ).suffix.lower()

    if suffix != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    filename = (
        f"{uuid4()}{suffix}"
    )

    file_path = (
        UPLOAD_FOLDER / filename
    )

    try:
        with open(
            file_path,
            "wb",
        ) as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        pipeline = (
            DocumentIngestionPipeline()
        )

        result = pipeline.process_document(
            str(file_path)
        )

        return {
            "success": True,
            "filename": file.filename,
            "stored_filename": filename,
            "message": (
                "Document ingested successfully."
            ),
            "metadata": result.get(
                "metadata",
                {},
            ),
            "chunks": len(
                result.get(
                    "chunks",
                    [],
                )
            ),
            "images": len(
                result.get(
                    "images",
                    [],
                )
            ),
            "tables": len(
                result.get(
                    "tables",
                    [],
                )
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {exc}",
        )