#!/usr/bin/env python
import getpass
import json
import os

from binance.client import Client

CONFIG_PATH = '/opt/app/config.js'


def get_creds():
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as fptr:
            data = json.load(fptr)
        key = data['exchanges']['binance']['key']
        secret = data['exchanges']['binance']['secret']
    else:
        key = getpass.getpass('Enter api key: ')
        secret = getpass.getpass('Enter api secret: ')
    return key, secret


def main():
    api_key, api_secret = get_creds()
    client = Client(api_key, api_secret)
    info = client.get_account()
    balances = info['balances']
    btc_deposits = client.get_deposit_history(asset='BTC')
    btc_deposit_amount = 0.0
    for deposit in btc_deposits['depositList']:
        if deposit['status'] == 1 and deposit['asset'] == 'BTC':
            btc_deposit_amount += deposit['amount']
    tickers = client.get_all_tickers()
    prices = {}
    for ticker in tickers:
        prices[ticker['symbol']] = float(ticker['price'])
    # set a base trade rate
    prices['BTCBTC'] = 1.0
    btc_balance = 0.0
    for asset in balances:
        symbol = asset['asset'] + 'BTC'
        position = (float(asset['free']) + float(asset['locked']))
        if position > 0.00001:
            btc_balance += position * prices[symbol]
    print("Account value: {} BTC".format(btc_balance))
    print("Raw input: {} BTC".format(btc_deposit_amount))
    print("Net Profit: {} BTC".format((btc_balance - btc_deposit_amount)))
    print("USD value: {}".format((btc_balance * prices['BTCUSDT'])))
    print("USD profit: {}".format(
          ((btc_balance - btc_deposit_amount) * prices['BTCUSDT'])))


if __name__ == "__main__":
    main()
