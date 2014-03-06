import decimal
import os
import unittest
import pycoinbase

API_KEY = os.environ.get('COINBASE_API_KEY')
API_SECRET = os.environ.get('COINBASE_API_SECRET')


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

    def test_api(self):
        balance = self.request('account/balance').get()
        assert isinstance(balance, dict)
        assert balance.get('currency') == 'BTC'


class TestCoinbaseAPI(unittest.TestCase):
    def api(self):
        return pycoinbase.CoinbaseAPI(API_KEY, API_SECRET)

    def test_balance(self):
        balance = self.api().balance()
        assert isinstance(balance, decimal.Decimal)

    def test_buy_price(self):
        price = self.api().buy_price()
        assert isinstance(price, decimal.Decimal)

    def test_sell_price(self):
        price = self.api().sell_price()
        assert isinstance(price, decimal.Decimal)

    def test_current_price(self):
        price = self.api().buy_price()
        assert isinstance(price, decimal.Decimal)

    def test_button(self):
        button = self.api().button(
            name='test',
            price=decimal.Decimal('1.23'),
            currency='USD',
            type='subscription',
            style='subscription_large',
            repeat='monthly',
            custom='USER:112358',
            button_mode='iframe'
        )
        assert 'html' in button
        assert 'iframe' in button['html']
        assert button['code'] in button['html']
        assert button['custom'] == 'USER:112358'


if __name__ == '__main__':
    unittest.main()
