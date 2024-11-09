from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.answer_generator import generate_answer, agent
from uuid import uuid4
import json

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
        # Step 2: Parse the 'content' field as JSON
        content_json = json.loads(answer["content"])

        # Step 3: Extract 'content' and 'relevant' from the parsed JSON
        answer_content = content_json["content"]
        is_relevant = content_json["relevant"]

        if is_relevant:
            # Step 2: Return the answer
            return {"answer": answer_content}
        else:
            agent_response = agent.run(request.query)
            return {
                "answer": "Sorry, I couldn't find a relevant answer from the document. Here's an alternative answer to your question:"
                + agent_response
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
