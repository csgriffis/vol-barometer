import os
from typing import TypedDict

from alpaca_trade_api.common import URL


class Config(TypedDict):
    ALPACA_API_KEY: str
    ALPACA_API_SECRET: str
    ALPACA_API_BASE_URL: URL


def build_config() -> Config:
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_API_SECRET')
    alpaca_base_url = os.getenv('ALPACA_API_BASE_URL')

    config: Config = {
        'ALPACA_API_KEY': str(api_key),
        'ALPACA_API_SECRET': str(api_secret),
        'ALPACA_API_BASE_URL': URL(alpaca_base_url)
    }

    return config
