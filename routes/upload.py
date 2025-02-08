from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from utils.pdf_processor import process_pdf, verify_pdf
from utils.embeddings_generator import create_embeddings, store_embeddings
from utils.Knowlege_graph import build_graph_and_store
from typing import Dict, Any, Optional
from uuid import uuid4
import traceback

router = APIRouter()


class UploadRequest(BaseModel):
    url: HttpUrl


class UploadResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None


@router.post(
    "/",
    response_model=UploadResponse,
    summary="Upload a PDF document",
    description="Upload a PDF document from a provided URL and process it. The document will be processed, embeddings will be created, and a knowledge graph will be built and stored.",
)
async def upload_pdf(request: UploadRequest):
    try:

        # Step 1: Verify that the URL is valid and PDF
        verify_pdf(request.url)

        # Step 2: Process the PDF and extract text chunks
        document_text = process_pdf(request.url)

        # Step 3: Generate ID for the document
        doc_id = str(uuid4())

        # Step 4: Generate embeddings for each chunk
        chunks = create_embeddings(document_text)

        # Step 5: Store embeddings in the vector database with the document ID in case we need it later
        store_embeddings(doc_id, chunks)

        # Step 6: Create and Store the knowledge graph
        build_graph_and_store(doc_id, chunks)

        print("Knowledge Graph Created and stored")
        print(doc_id)
        return {
            "success": True,
            "data": {
                "document_id": doc_id,
            },
        }

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        return {
            "success": False,
            "data": None,
            "error": {
                "message": str(e),
                "type": type(e).__name__,
            },
        }
