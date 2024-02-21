import json
from flask import Blueprint, request, Response
from services.generator import Generator
from services.conversation import Conversation
from services.events import Events
from langchain.schema import HumanMessage
from typing import Annotated
from pydantic import BaseModel, ValidationError
from datetime import datetime

router = Blueprint('conversation', __name__)
conversation = Conversation()
generator = Generator()
events = Events()

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
    messages = conversation.get_messages(collection_name)
    return messages

class GeneratePayload(BaseModel):
    title: Annotated[str, lambda v: len(v.strip()) > 0]
    prompt: Annotated[str, lambda v: len(v.strip()) > 0]
    user_id: Annotated[int, lambda v: len(v.strip()) > 0]
    connection_id: Annotated[int, lambda v: len(v.strip()) > 0]

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
    
    title_message = conversation.add_title(collection_name, payload.title)
    if title_message:
        event = {**title_message, "connection_id": payload.connection_id}
        events.publish(user_id=payload.user_id, event=event)
        
    messages = conversation.get_conversation(collection_name)
    messages.append(HumanMessage(content=payload.prompt))
    date: datetime = datetime.utcnow()
    
    def resolve_fn(msg: str):
        human_message = conversation.add_human_message(collection_name, payload.prompt, date)
        if human_message:
            event = {**human_message, "connection_id": payload.connection_id}
            events.publish(user_id=payload.user_id, event=event)
        
        ai_message = conversation.add_ai_message(collection_name, msg, datetime.utcnow())
        if ai_message:
            event = {**ai_message, "connection_id": payload.connection_id}
            events.publish(user_id=payload.user_id, event=event)
    
    return generator.generate(messages=messages, resolve_fn=resolve_fn)
