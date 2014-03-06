pycoinbase
==========

Python library for the Coinbase API

* **Author**: [Derek Payton](http://dmpayton.com)
* **Version**: Very Alpha
* **License**: MIT

**TODO:**

* OAuth (via requests-oauthlib?)
* Mock tests to avoid actual calls to the API
* Proper documentation in Sphinx

Low-level API
-------------

This is the baseline functionality for talking the the Coinbase API. You can
pass any endpoint to `coinbase.request()` and call the appropriate HTTP method
on the resulting `CoinbaseRequest` object. The low-level API is a direct
1-to-1 mapping to the Coinbase API.

```
>>> import pycoinbase
>>> coinbase = pycoinbase.CoinbaseAPI('API_KEY', 'API_SECRET')

# Account balance
>>> coinbase.request('account/balance').get()
{u'currency': u'BTC', u'amount': u'36.62800000'}

# Recent transactions, page 4
>>> coinbase.request('transactions').get(params={'page': 4})
{u'transactions': [...], ...}

# Buy some bitcoin
>>> coinbase.request('buys').post(data={'qty': 2.5})
{u'success': True, u'transfer': {...}}
```

High-level API
--------------

These are a set of helper methods and shortcuts to commonly used functions.

```
>>> import pycoinbase
>>> coinbase = pycoinbase.CoinbaseAPI('API_KEY', 'API_SECRET')

# Get the user's account balance in BTC.
>>> coinbase.balance()
Decimal('36.62800000')

# Get the user's current bitcoin receive address.
>>> coinbase.address()
"muVu2JZo8PbewBHRp6bpqFvVD87qvqEHWA"

# send/request money
>>> coinbase.send_money()
>>> coinbase.request_money()

# Bitcoin pricing
>>> coinbase.buy_price()
>>> coinbase.sell_price()
>>> coinbase.current_price()

# Buy and sell Bitcoin
>>> coinbase.buy()
>>> coinbase.sell()

# Create pament buttons, pages, and iframes
>>> coinbase.button()
```
