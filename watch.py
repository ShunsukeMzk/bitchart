import datetime
import logging
import time
from logging import getLogger, StreamHandler, Formatter, FileHandler
from pathlib import Path

import pybitflyer
import requests
import schedule

import conf


logger = getLogger(Path(__file__).name)
logger.setLevel(logging.DEBUG)

stream_handler = StreamHandler()
stream_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

file_handler = FileHandler('log/watch.log')
file_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if not Path('log').exists():
    Path('log').mkdir()

api = pybitflyer.pybitflyer.API()


def exec_per_ten_seconds(job, *args, **kwargs):
    for second in ['00', '10', '20', '30', '40', '50']:
        schedule.every().minute.at(':' + second).do(job, *args, **kwargs)


def watch_price(product_code):
    timestamp = datetime.datetime.now().timestamp()
    try:
        price = api.ticker(product_code=product_code)['ltp']
        latency = datetime.datetime.now().timestamp() - timestamp
        logger.debug(f"product_code: {product_code}, price: {price}, latency: {latency}")
    except Exception as e:
        logger.warning(f"Unable to get price: {e}")
        price = ''
        latency = -1
    with open(f'data/{product_code}.tsv', 'a') as f:
        f.write(f'{int(timestamp)}\t{price}\t{latency}\n')


def main():
    for product in conf.product_code_list:
        exec_per_ten_seconds(watch_price, product)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
