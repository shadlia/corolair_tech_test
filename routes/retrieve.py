from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.graph import retrieve_relevant_chunks_from_db

router = APIRouter()


# Request model to accept doc_id and query
class RetrieveRequest(BaseModel):
    document_id: str
    query: str

    class Config:
        schema_extra = {
            "example": {"document_id": "12345", "query": "What is the meaning of AI?"}
        }


# Response model for returning the relevant chunks
class Chunk(BaseModel):
    node_id: str
    text: str
    similarity: float


class RetrieveResponse(BaseModel):
    document_id: str
    relevant_chunks: list[Chunk]


@router.post(
    "/",
    response_model=RetrieveResponse,
    summary="Retrieve relevant chunks from a document based on a query",
    description="This endpoint retrieves relevant chunks from a specified document based on the provided query. "
    "It uses a search mechanism that finds the most similar chunks to the query and returns them as part of the response.",
    response_description="A list of relevant chunks containing the text and similarity score that matched the query",
    responses={500: {"description": "Internal Server Error"}},
)
async def retrieve_relevant_chunks(request: RetrieveRequest):
    """
    Endpoint to retrieve relevant chunks from the database using the provided document ID and query string.
    """
    try:
        # Step 1: Call the service to get relevant chunks
        relevant_chunks = retrieve_relevant_chunks_from_db(
            request.document_id, request.query
        )

        # Step 2: Return the relevant chunks
        return {"document_id": request.document_id, "relevant_chunks": relevant_chunks}

    except Exception as e:
        # Raise an HTTPException if an error occurs
        raise HTTPException(status_code=500, detail=str(e))
