from decouple import config
from chromadb.api import ClientAPI
from langchain_community.chat_models import ChatOllama
from typing import Literal, TypedDict, List, Union
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from db.database import get_database
from datetime import datetime

CHROMA_HOST = config('CHROMA_HOST')
CHROMA_PORT = config('CHROMA_PORT')

chat = ChatOllama()

class Roles(TypedDict):
    human: str
    system: str
    ai: str

roles: Roles = {
    'human': 'human',
    'system': 'system',
    'ai': 'ai'
}

Format = Literal['messages', 'documents', 'json']

class Conversation:
    chromadb: ClientAPI
    
    def __init__(self) -> None:
        self.database = get_database()

    def add_message(self, collection_name: str, msg: str, rol: str, date: datetime = datetime.utcnow()):
        collection = self.database.get_collection(collection_name)
        payload = { 
            "content": msg, 
            "rol": rol,
            "created_at": date
        }
        result = collection.insert_one(payload)
        payload['id'] = str(result.inserted_id)
        formatted_date = payload['created_at'].strftime('%Y-%m-%d %H:%M:%S ') + "UTC"
        payload['created_at'] = formatted_date
        del payload['_id']
        return payload
        
    def add_title(self, collection_name: str, msg: str):
        collection = self.database.get_collection(collection_name)
        if msg == "" or collection.count_documents({}) > 0:
            return None
        return self.add_message(
            collection_name=collection_name, 
            msg=msg, rol=roles['system']
        )
        
    def add_human_message(self, collection_name: str, msg: str, date: datetime = datetime.utcnow()):
        return self.add_message(
            collection_name=collection_name, 
            msg=msg, rol=roles['human'], date=date
        )
        
    def add_system_message(self, collection_name: str, msg: str, date: datetime = datetime.utcnow()):
        return self.add_message(
            collection_name=collection_name, 
            msg=msg, rol=roles['system'], date=date
        )
        
    def add_ai_message(self, collection_name: str, msg: str, date: datetime = datetime.utcnow()):
        return self.add_message(
            collection_name=collection_name, 
            msg=msg, rol=roles['ai'], date=date
        )
        
    def delete(self, collection_name: str):
        try:
            self.chromadb.delete_collection(collection_name)
        except Exception as e:
            pass

    def get_conversation(self, collection_name: str) -> List[Union[SystemMessage, HumanMessage]]:
        messages = self.get_messages(collection_name)
    
        response = []
        for message in messages:
            payload = { "content": message['content'] }
            
            if message['rol'] == roles['human']:
                current = HumanMessage(**payload)
            elif message['rol'] == roles['ai']:
                current = AIMessage(**payload)
            else:
                current = SystemMessage(**payload)
                
            response.append(current)
                
        return response
    
    def get_messages(self, collection_name: str) -> List[Union[SystemMessage, HumanMessage]]:
        collection = self.database.get_collection(collection_name)
        messages = collection.find().sort("created_at", 1)
        
        formatted_messages = []
        for message in messages:
            formatted_date = message['created_at'].strftime('%Y-%m-%d %H:%M:%S ') + "UTC"
            formatted_messages.append({
                "id": message['_id'].__str__(),
                "content": message['content'],
                "rol": message['rol'],
                "created_at": formatted_date
            })
        return formatted_messages
