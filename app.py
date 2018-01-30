import asyncio
import itertools
import os
import time
from pprint import pprint

import binance
from binance.client import Client

import yaml
from aiohttp import web

CONFIG_PATH = '/opt/app/config.yaml'

DELAY = 60  # sec

if not os.path.isfile(CONFIG_PATH):
    raise SystemError('Config file not exists: {}'.format(CONFIG_PATH))


last_response = {}


def get_config():
    with open(CONFIG_PATH, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise SystemError(
                'Error while reading config: {}'.format(CONFIG_PATH))


class Binance(object):
    def __init__(self, app):
        self.config = app['config']
        self.client = Client(
            self.config['binance']['key'],
            self.config['binance']['secret'],
        )

    async def query(self):
        data = {
            'time': int(time.time()),
            'total_invtestment': self.config['total_invtestment']
        }
        info = self.client.get_account()
        balances = info['balances']
        btc_deposits = self.client.get_deposit_history(asset='BTC')
        btc_deposit_count = 0
        for deposit in btc_deposits['depositList']:
            if deposit['status'] == 1 and deposit['asset'] == 'BTC':
                btc_deposit_count += deposit['amount']
        tickers = self.client.get_all_tickers()
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
        btc_delta = btc_balance - btc_deposit_count
        data['btc_usd_amount'] = prices['BTCUSDT']
        data['btc_deposit'] = {
            'count': btc_deposit_count,
            'amount': self.config['btc_deposit_amount'],
        }
        data['btc_now'] = {
            'count': btc_balance,
            'amount': btc_balance * prices['BTCUSDT'],
        }
        data['btc_delta'] = {
            'count': btc_delta,
            'amount': btc_delta * prices['BTCUSDT'],
        }
        data['net_profit'] = (btc_balance * prices['BTCUSDT']) - \
            self.config['total_invtestment']
        return data


async def query(app):
    await asyncio.sleep(1)  # let web server start first
    binance_obj = Binance(app)
    try:
        for i in itertools.count():
            print(i)
            try:
                data = await binance_obj.query()
            except binance.exceptions.BinanceAPIException as e:
                print('Error {}'.format(e))
            else:
                global last_response
                last_response = data
                pprint(data)
            await asyncio.sleep(DELAY)
    except asyncio.CancelledError:
        pass
    finally:
        print('Done Query')


async def start_background_tasks(app):
    app['query_binance'] = app.loop.create_task(query(app))


async def cleanup_background_tasks(app):
    app['query_binance'].cancel()
    await app['query_binance']


async def handle(request):
    return web.json_response(last_response)


if __name__ == "__main__":
    os.system("ntpd -gq")  # run timesync
    config = get_config()
    app = web.Application()
    app['config'] = config
    app.router.add_get('/', handle)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    web.run_app(app)
