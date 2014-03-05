import decimal
import hashlib
import hmac
import json
import requests
import time


class CoinbaseRequest(object):
    coinbase_url = 'https://coinbase.com/api/v1'

    def __init__(self, api_key, api_secret, path):
        self.api_key = api_key
        self.api_secret = api_secret
        self.path = path

    @property
    def url(self):
        return '{0}/{1}'.format(self.coinbase_url, self.path)

    def generate_nonce(self):
        return int(time.time() * 1e6)

    def generate_signature(self, nonce, payload):
        message = '{0}{1}{2}'.format(nonce, self.url, payload)
        return hmac.new(self.api_secret.encode(), message.encode(),
            hashlib.sha256).hexdigest()

    def create_payload(self, data):
        return json.dumps(data) if data else ''

    def make_request(self, method, params=None, data=None):
        payload = self.create_payload(data)
        nonce = self.generate_nonce()
        signature = self.generate_signature(nonce, payload)
        response = requests.request(method, self.url,
            params=params,
            data=payload or None,
            headers={
                'ACCESS_KEY': self.api_key,
                'ACCESS_SIGNATURE': signature,
                'ACCESS_NONCE': nonce,
            }
        )
        return response.json(parse_float=decimal.Decimal)

    def get(self, params=None):
        return self.make_request('GET', params)

    def post(self, params=None, data=None):
        return self.make_request('POST', params, data)

    def put(self, params=None, data=None):
        return self.make_request('PUT', params, data)

    def delete(self, params=None):
        return self.make_request('DELETE', params)


class CoinbaseAPI(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def request(self, path):
        return CoinbaseRequest(self.api_key, self.api_secret, path)
