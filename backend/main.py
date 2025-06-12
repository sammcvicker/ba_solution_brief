from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from .get_context_from_docs import get_context_from_docs
from .get_document_bytes_from_model import get_document_bytes_from_model
from .get_model_from_context import get_model_from_context

app = FastAPI(
    title="File Processing API",
    description="API for processing uploaded files and returning PDF",
)


def process_files_to_pdf(files: List[UploadFile]) -> bytes:
    """
    Placeholder function that would process the uploaded files and return PDF bytes.
    This function is not implemented - you would add your processing logic here.
    """
    context: str = get_context_from_docs(files)  # Group 1
    model: BaseModel = get_model_from_context(context)  # Group 2
    document_bytes: bytes = get_document_bytes_from_model(model, context)  # Group 3
    return document_bytes


@app.post("/generate-document")
async def generate_document(files: List[UploadFile] = File(...)):
    """
    Process uploaded files and return a PDF file for download.

    Args:
        files: List of uploaded files to process

    Returns:
        PDF file as binary response
    """
    try:
        # Validate that files were uploaded
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        # Call the processing function (placeholder for now)
        pdf_bytes = process_files_to_pdf(files)

        # Return PDF as downloadable file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=processed_files.pdf"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "File Processing API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
