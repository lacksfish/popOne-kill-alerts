import requests
import logging
import time
logger = logging.getLogger()


class Twitcher:
    def __init__(self, twitch_username, client_secret, client_id):
        self.username = twitch_username
        self.client_secret = client_secret
        self.access_token = None
        self.client_id = client_id

        self.BASE_URL = 'https://api.twitch.tv/helix/'

        # AUTH
        self._auth()

        self.user_id = self._make_twitch_request_get('users', {'login': self.username})['data'][0]['id']

    def _auth(self):
        print('Authenticating with Twitch ...')

        auth_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'channel:manage:broadcast clips:edit'
        }

        auth_url = 'https://id.twitch.tv/oauth2/token'

        curr_time = time.time()
        r = requests.post(auth_url, params=auth_params)
        res = r.json()
        self.access_token = res['access_token']
        self.scope = res['scope']
        self.expiry_ts = curr_time + res['expires_in']
        import datetime
        dt = datetime.datetime.fromtimestamp(self.expiry_ts)
        print(f"Authenticated until {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    def _make_twitch_request_post(self, path, data, base_url=None):
        url = f"{self.BASE_URL if not base_url else base_url}{path}"
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

    def _make_twitch_request_get(self, path, data, base_url=None):
        url = f"{self.BASE_URL if not base_url else base_url}{path}"
        headers = {
            'Client-Id': self.client_id,
            'Authorization': f"Bearer {self.access_token}"
        }
        r = requests.get(url, params=data, headers=headers)
        res = r.json()
        if 'message' in res:
            logger.warning(res['message'])
        return res

    def set_stream_marker(self, description):
        return self._make_twitch_request_post('streams/markers', {'user_id': self.user_id, 'description': f"{description}"})

    def create_clip(self):
        return self._make_twitch_request_post('clips', {'broadcaster_id': self.user_id, 'has_delay': True})
