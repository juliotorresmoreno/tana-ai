import json
from typing import Annotated
from flask import Blueprint, request, Response
from pydantic import BaseModel, ValidationError
from services.generator import Generator
from langchain.schema import HumanMessage

router = Blueprint('generate', __name__)
generator = Generator()

@router.get("status")
async def status():
    return { "success": "ok" }


class GeneratePayload(BaseModel):
    prompt: Annotated[str, lambda v: len(v.strip()) > 0]

def validate_generate_payload(payload) -> GeneratePayload:
    try:
        return GeneratePayload(**payload)
    except ValidationError as e:
        print(f"Error validating payload: {e}")
        return None

@router.post("")
async def generate():
    payload = validate_generate_payload(payload=request.json)
    if payload == None:
        return Response(
            json.dumps({ "message": "Bad request!" }), 
            content_type="application/json",
            status=400
        )
        
    messages = [
        HumanMessage(content=payload.prompt)
    ]
    
    return generator.generate(messages)
