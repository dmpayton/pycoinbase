pycoinbase
==========

Python library for the Coinbase API

**TODO:**

* Helper methods (High-level API)
* OAuth (via requests-oauthlib?)
* Mock tests to avoid actual calls to the API

Low-level API
-------------

```
>>> from pycoinbase import CoinbaseAPI
>>> coinbase = CoinbaseAPI('API_KEY', 'API_SECRET')
>>> coinbase.request('account/balance').get()
{u'currency': u'BTC', u'amount': u'36.62800000'}
```

High-level API
--------------

```
>>> from pycoinbase import CoinbaseAPI
>>> coinbase = CoinbaseAPI('API_KEY', 'API_SECRET')
>>> coinbase.balance()
Decimal('36.62800000')
```
