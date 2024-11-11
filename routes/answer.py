from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.answer_generator import generate_answer, agent
from uuid import uuid4
import json

router = APIRouter()


# Request model to accept doc_id and query
class AnswerRequest(BaseModel):
    doc_id: str
    query: str


# Response model to return the generated answer
class AnswerResponse(BaseModel):
    success: bool
    data: dict


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
            # Return the answer in the success format
            return {"success": True, "data": {"answer": answer_content}}
        else:
            # Generate an alternative response using the agent
            agent_response = agent.run(request.query)
            return {
                "success": True,
                "data": {
                    "answer": "Sorry, I couldn't find a relevant answer from the document. Here's an alternative answer to your question: "
                    + agent_response
                },
            }

    except Exception as e:
        # Standardized error response
        return {"success": False, "data": None, "error": {"message": str(e)}}
