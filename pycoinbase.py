import decimal
import hashlib
import hmac
import json
import os
import requests
import time

BUTTON_TEMPLATES = {
    'iframe': '<iframe src="https://coinbase.com/inline_payments/{code}" style="width:500px;height:160px;border:none;box-shadow:0 1px 3px rgba(0,0,0,0.25);overflow:hidden;" scrolling="no" allowtransparency="true" frameborder="0"></iframe>',
    'page': '<a href="https://coinbase.com/checkouts/{code}" target="_blank"><img alt="{text}" src="https://coinbase.com/assets/buttons/{style}.png"></a>',
    'button': '<div class="coinbase-button" data-code="{code}"></div><script src="https://coinbase.com/assets/button.js" type="text/javascript"></script>',
}


class JSONDecimalEncoder(json.JSONEncoder):
    '''JSONEncoder subclass that knows how to encode decimal types.'''

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(JSONDecimalEncoder, self).default(o)


class CoinbaseAPIError(Exception):
    pass


# class CoinbaseResponse(object):
#     def __init__(self, response):
#         self.response = response
#         self.json = response.json(parse_float=decimal.Decimal)

#     @property
#     def request(self):
#         return self.response.request

#     @property
#     def api_key(self):
#         return self.request.headers['ACCESS_KEY']

#     @property
#     def signature(self):
#         return self.request.headers['ACCESS_SIGNATURE']

#     @property
#     def nonce(self):
#         return self.request.headers['ACCESS_NONCE']


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
        if data is not None:
            return json.dumps(data, cls=JSONDecimalEncoder)
        return ''

    def make_request(self, method, params=None, data=None):
        payload = self.create_payload(data)
        nonce = self.generate_nonce()
        signature = self.generate_signature(nonce, payload)
        response = requests.request(method, self.url,
            params=params,
            data=payload or None,
            headers={
                'content-type': 'application/json',
                'ACCESS_KEY': self.api_key,
                'ACCESS_SIGNATURE': signature,
                'ACCESS_NONCE': nonce,
            }
        )
        if not response.ok:
            raise CoinbaseAPIError(['Coinbase returned non-200 response'])
        return response.json(parse_float=decimal.Decimal)
        # return CoinbaseResponse(response)

    def get(self, params=None):
        return self.make_request('GET', params)

    def post(self, params=None, data=None):
        return self.make_request('POST', params, data)

    def put(self, params=None, data=None):
        return self.make_request('PUT', params, data)

    def delete(self, params=None):
        return self.make_request('DELETE', params)


class CoinbaseAPI(object):
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        if self.api_key is None:
            self.api_key = os.environ.get('COINBASE_API_KEY')

        self.api_secret = api_secret
        if self.api_secret is None:
            self.api_secret = os.environ.get('COINBASE_API_SECRET')

        if self.api_key is None or self.api_secret is None:
            raise TypeError('Missing Coinbase API credentials')

    def request(self, path):
        return CoinbaseRequest(self.api_key, self.api_secret, path)

    def raise_exception(self, errors):
        raise CoinbaseAPIError('\n'.join(errors))

    def address(self):
        '''Get the user's current bitcoin receive address.'''
        data = self.request('account/receive_address').get()
        return data['address']

    def balance(self):
        '''Get the user's account balance in BTC.'''
        data = self.request('account/balance').get()
        return decimal.Decimal(data['amount'])

    def request_money(self, amount, email, notes=None, currency=None):
        data = self.request('transactions/request_money').post(data={
            'transaction': {
                'amount_string': amount,
                'amount_currency_iso': currency or 'BTC',
                'from': email,
                'notes': notes or '',
            }
        })
        if not data['success']:
            self.raise_exception(data['errors'])
        return data['transaction']

    def send_money(self, amount, address, notes=None, currency=None):
        '''Send bitcoins to an email address or bitcoin address.'''
        data = self.request('transactions/send_money').post(data={
            'transaction': {
                'amount_string': amount,
                'amount_currency_iso': currency or 'BTC',
                'to': address,
                'notes': notes or '',
            }
        })
        if not data['success']:
            self.raise_exception(data['errors'])
        return data['transaction']

    def buy_price(self, amount=1):
        '''Get the total buy price for some bitcoin amount.'''
        data = self.request('prices/buy').get(params={
            'qty': amount,
            'currency': 'USD'
        })
        return decimal.Decimal(data['total']['amount'])

    def sell_price(self, amount=1):
        '''Get the total sell price for some bitcoin amount.'''
        data = self.request('prices/sell').get(params={
            'qty': amount,
            'currency': 'USD'
        })
        return decimal.Decimal(data['total']['amount'])

    def current_price(self, amount=1, currency=None):
        currency = currency or 'USD'
        data = self.request('prices/spot_rate').get(params={
            'qty': amount,
            'currency': 'USD'
        })
        return decimal.Decimal(data['amount'])

    def buy(self, amount):
        '''Purchase bitcoin by debiting your U.S. bank account.'''
        data = self.request('buys').post(data={
            'qty': amount,
            'agree_btc_amount_varies': True,
        })
        if not data['success']:
            self.raise_exception(data['errors'])
        return data['transfer']

    def sell(self, amount):
        '''Sell bitcoin and receive a credit to your U.S. bank account.'''
        data = self.request('sell').post(data={
            'qty': amount,
        })
        if not data['success']:
            self.raise_exception(data['errors'])
        return data['transfer']

    def button(self, name, price, currency, button_mode=None, **kwargs):
        payload = {'button': {
            'name': name,
            'price_string': price,
            'price_currency_iso': currency,
        }}
        payload['button'].update(kwargs)
        data = self.request('buttons').post(data=payload)
        if not data.get('success'):
            self.raise_exception([data['error']])
        template = BUTTON_TEMPLATES[button_mode or 'button']
        data['button']['html'] = template.format(**data['button'])
        return data['button']
