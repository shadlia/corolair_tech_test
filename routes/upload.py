# api/routes/upload.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from services.pdf_process import process_pdf
from services.embeddings import create_embeddings, store_embeddings
from services.graph import build_graph_and_store

from uuid import uuid4

router = APIRouter()


class UploadRequest(BaseModel):
    url: HttpUrl


class UploadResponse(BaseModel):
    document_id: str


@router.post(
    "/",
    response_model=UploadResponse,
    summary="Upload a PDF document",
    description="Upload a PDF document from a provided URL and process it. The document will be processed, embeddings will be created, and a knowledge graph will be built and stored.",
)
async def upload_pdf(request: UploadRequest):
    try:
        # Step 1: Verify that the URL is valid - handled by the HttpUrl type in UploadRequest

        # Step 2: Process the PDF and extract text chunks
        document_text = process_pdf(request.url)

        # Step 3: Generate ID for the document
        doc_id = str(uuid4())

        # Step 4: Generate embeddings for each chunk
        chunks = create_embeddings(document_text)

        # Step 5: Store embeddings in the vector database with the document ID in case we need it later
        store_embeddings(doc_id, chunks)

        # Step 4: Crete and Store the knowledge graph
        graph = build_graph_and_store(doc_id, chunks)

        print("Knowledge Graph Created and stored")

        return {"document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
