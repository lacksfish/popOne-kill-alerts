import requests
import logging
logger = logging.getLogger()


class Twitcher:
    def __init__(self, twitch_username, access_token, client_id):
        self.username = twitch_username
        self.access_token = access_token
        self.client_id = client_id

        self.BASE_URL = 'https://api.twitch.tv/helix/'

        self.user_id = self._make_twitch_request_get('users', {'login': self.username})['data'][0]['id']

    def _make_twitch_request_post(self, path, data):
        url = f"{self.BASE_URL}{path}"
        headers = {
            'Content-type': 'application/json',
            'Client-Id': self.client_id,
            'Authorization': f"Bearer {self.access_token}"
        }
        r = requests.post(url, json=data, headers=headers)
        res = r.json()
        if 'message' in res:
            logger.warning(res['message'])
        return res

    def _make_twitch_request_get(self, path, data):
        url = f"{self.BASE_URL}{path}"
        headers = {
            'Client-Id': self.client_id,
            'Authorization': f"Bearer {self.access_token}"
        }
        r = requests.get(url, data=data, headers=headers)
        res = r.json()
        if 'message' in res:
            logger.warning(res['message'])
        return res

    def set_stream_marker(self, description):
        return self._make_twitch_request_post('streams/markers', {'user_id': self.user_id, 'description': f"{description}"})

    def create_clip(self):
        return self._make_twitch_request_post('clips', {'broadcaster_id': self.user_id, 'has_delay': True})
