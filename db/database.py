from pymongo import MongoClient
from pymongo.database import Database
from decouple import config

def get_database() -> Database:
    CONNECTION_STRING = config('MONGO_URI') 
    client = MongoClient(CONNECTION_STRING)

    return client['conversations']
  