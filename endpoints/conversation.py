import json
from flask import Blueprint, request, Response
from services.generator import Generator
from services.conversation import Conversation
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from typing import Annotated
from pydantic import BaseModel, ValidationError

router = Blueprint('conversation', __name__)
conversation = Conversation()
generator = Generator()

@router.get("")
async def index():
    return { "success": "ok" }

@router.delete("/<string:collection_name>")
async def delete(collection_name: str):
    conversation.delete(collection_name)
    
    return Response(
        json.dumps({ "message": "Conversation deleted!" }), 
        content_type="application/json",
        status=200
    )

@router.get("/<string:collection_name>")
async def find(collection_name: str):
    messages = conversation.get_conversation(collection_name)
    result = [ ]
    for i in range(len(messages)):
        if type(messages[i]) == HumanMessage:
            result.append({ "id": messages[i].name, "content": messages[i].content, "user": "human" })
        elif type(messages[i]) == AIMessage:
            result.append({ "id": messages[i].name, "content": messages[i].content, "user": "ai" })
        else:
            result.append({ "id": messages[i].name, "content": messages[i].content, "user": "system" })
    
    return result

class GeneratePayload(BaseModel):
    title: Annotated[str, lambda v: len(v.strip()) > 0]
    prompt: Annotated[str, lambda v: len(v.strip()) > 0]

def validate_generate_payload(payload) -> GeneratePayload:
    try:
        return GeneratePayload(**payload)
    except ValidationError as e:
        print(f"Error validating payload: {e}")
        return None

@router.post("/<string:collection_name>")
async def generate(collection_name: str):
    payload = validate_generate_payload(payload=request.json)
    if payload == None:
        return Response(
            json.dumps({ "message": "Bad request!" }), 
            content_type="application/json",
            status=400
        )
    
    conversation.add_title(collection_name, payload.title)
    messages = conversation.get_conversation(collection_name)
    messages.append(HumanMessage(content=payload.prompt))
    
    def resolve_fn(msg: str):
        conversation.add_human_message(collection_name, payload.prompt)
        conversation.add_ai_message(collection_name, msg)
    
    return generator.generate(messages=messages, resolve_fn=resolve_fn)
