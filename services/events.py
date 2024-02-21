from decouple import config
import requests
from typing import Any

API_URL = config("API_URL")
API_KEY = config("API_KEY")

class Events:
    def publish(self, user_id: int, event: Any):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        url = API_URL + '/api/events/' + str(user_id)
        response = requests.post(url=url, json=event, headers=headers)
        return response.status_code == 204
