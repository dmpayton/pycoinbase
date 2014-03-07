import decimal
import httmock
import json
import os
import random
import string
import unittest
import pycoinbase


def random_string(length=32):
    alphabet = getattr(string, 'letters', getattr(string, 'ascii_letters'))
    return ''.join([random.choice(alphabet) for x in range(length)])

API_KEY = random_string()
API_SECRET = random_string()


def this_directory():
    return os.path.dirname(os.path.abspath(__file__))


def load_content(url, method):
    path = url.path.replace('/api/v1/', '').replace('/', '_')
    filename = '{0}.{1}.json'.format(path, method)
    filepath = os.path.join(this_directory(), 'responses', filename)
    try:
        file = open(filepath, 'r')
    except IOError:
        status = 404
        content = '{"success": false, "errors": ["bad request"]}'
    else:
        status = 200
        content = json.loads(file.read())
        file.close()
    return status, content


@httmock.urlmatch(netloc='coinbase.com')
def coinbase_mock(url, response):
    status_code, content = load_content(url, response.method)
    return {
        'content-type': 'application/json',
        'content': content,
        'status_code': status_code
    }


class TestCoinbaseRequest(unittest.TestCase):

    def request(self, path=None):
        path = path or ''
        return pycoinbase.CoinbaseRequest(API_KEY, API_SECRET, path)

    def test_payload(self):
        assert self.request().create_payload(None) == ''
        assert self.request().create_payload({'foo': 'bar'}) == '{"foo": "bar"}'

    def test_url(self):
        url = 'https://coinbase.com/api/v1/balance'
        assert self.request('balance').url == url

    def test_nonce(self):
        n1 = self.request().generate_nonce()
        n2 = self.request().generate_nonce()
        assert n2 > n1

    @httmock.with_httmock(coinbase_mock)
    def test_api(self):
        balance = self.request('account/balance').get()
        assert isinstance(balance, dict)
        assert balance.get('currency') == 'BTC'


class TestCoinbaseAPI(unittest.TestCase):
    def api(self):
        return pycoinbase.CoinbaseAPI(API_KEY, API_SECRET)

    @httmock.with_httmock(coinbase_mock)
    def test_balance(self):
        balance = self.api().balance()
        assert isinstance(balance, decimal.Decimal)

    @httmock.with_httmock(coinbase_mock)
    def test_buy_price(self):
        price = self.api().buy_price()
        assert isinstance(price, decimal.Decimal)

    @httmock.with_httmock(coinbase_mock)
    def test_sell_price(self):
        price = self.api().sell_price(12)
        assert isinstance(price, decimal.Decimal)

    @httmock.with_httmock(coinbase_mock)
    def test_current_price(self):
        price = self.api().buy_price()
        assert isinstance(price, decimal.Decimal)

    @httmock.with_httmock(coinbase_mock)
    def test_button(self):
        button = self.api().button(
            name='test',
            price=decimal.Decimal('1.23'),
            currency='USD',
        )
        assert 'html' in button


if __name__ == '__main__':
    unittest.main()
