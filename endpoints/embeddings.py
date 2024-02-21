from flask import Blueprint, request, Response
from pydantic import BaseModel, ValidationError
from services.encoder import Encoder
from typing import Annotated
import json

router = Blueprint('embeddings', __name__)
encoder = Encoder()

@router.get("")
async def index():
    return { "success": "ok" }

class EmbeddingsPayload(BaseModel):
    prompt: Annotated[str, lambda v: len(v.strip()) > 0]

def validate_embeddings_payload(payload) -> EmbeddingsPayload:
    try:
        return EmbeddingsPayload(**payload)
    except ValidationError as e:
        print(f"Error validating payload: {e}")
        return None

@router.post("")
async def embeddings():
    payload = validate_embeddings_payload(payload=request.json)
    if payload == None:
        return Response(
            json.dumps({ "message": "Bad request!" }), 
            content_type="application/json",
            status=400
        )
    
    return encoder.encode(payload.prompt)
