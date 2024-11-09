from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.answer_generator import generate_answer
from uuid import uuid4

router = APIRouter()


# Request model to accept doc_id and query
class AnswerRequest(BaseModel):
    doc_id: str
    query: str


# Response model to return the generated answer
class AnswerResponse(BaseModel):
    answer: str


@router.post("/", response_model=AnswerResponse)
async def generate_answer_route(request: AnswerRequest):
    try:
        # Step 1: Generate an answer based on the document ID and query
        answer = generate_answer(request.doc_id, request.query)
        print(answer)

        # Step 2: Return the answer
        return {"answer": answer.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
