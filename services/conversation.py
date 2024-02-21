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

    def add_message(self, collection_name: str, msg: str, rol: str):
        collection = self.database.get_collection(collection_name)
        collection.insert_one({ 
            "content": msg, 
            "rol": rol,
            "created_at": datetime.utcnow()
        })
        
    def add_title(self, collection_name: str, msg: str):
        collection = self.database.get_collection(collection_name)
        if msg == "" or collection.count_documents({}) > 0:
            return
        self.add_message(
            collection_name=collection_name, 
            msg=msg, rol=roles['system']
        )
        
    def add_human_message(self, collection_name: str, msg: str):
        self.add_message(collection_name=collection_name, msg=msg, rol=roles['human'])
        
    def add_system_message(self, collection_name: str, msg: str):
        self.add_message(collection_name=collection_name, msg=msg, rol=roles['system'])
        
    def add_ai_message(self, collection_name: str, msg: str):
        self.add_message(collection_name=collection_name, msg=msg, rol=roles['ai'])
        
    def delete(self, collection_name: str):
        try:
            self.chromadb.delete_collection(collection_name)
        except Exception as e:
            pass

    def get_conversation(self, collection_name: str) -> List[Union[SystemMessage, HumanMessage]]:
        collection = self.database.get_collection(collection_name)
        result = collection.find()
    
        response = []
        for document in result:
            if document['rol'] == roles['human']:
                response.append(HumanMessage(name=str(document['_id']), content=document['content']))
            elif document['rol'] == roles['ai']:
                response.append(AIMessage(name=str(document['_id']), content=document['content']))
            else:
                response.append(SystemMessage(name=str(document['_id']), content=document['content']))
                
        return response