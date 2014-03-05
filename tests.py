import unittest
from pycoinbase import CoinbaseRequest

API_KEY = '<API_KEY>'
API_SECRET = '<API_SECRET>'


class TestCoinbaseRequest(unittest.TestCase):
    def request(self, path=None):
        path = path or ''
        return CoinbaseRequest(API_KEY, API_SECRET, path)

    def test_payload(self):
        assert self.request().create_payload(None) == ''
        assert self.request().create_payload({}) == ''
        assert self.request().create_payload({'foo': 'bar'}) == '{"foo": "bar"}'

    def test_url(self):
        url = 'https://coinbase.com/api/v1/balance'
        assert self.request('balance').url == url

    def test_nonce(self):
        n1 = self.request().generate_nonce()
        n2 = self.request().generate_nonce()
        assert n2 > n1

    def test_api(self):
        balance = self.request('account/balance').get()
        assert isinstance(balance, dict)
        assert balance.get('currency') == 'BTC'


if __name__ == '__main__':
    unittest.main()
