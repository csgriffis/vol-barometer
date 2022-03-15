import logging
import os

from flask import Flask

from barometer import barometer
from config import build_config
from portfolio import Portfolio
from strategy import Strategy

app = Flask(__name__)

# todo: move to new package?
logging.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s', level=logging.DEBUG)


@app.route('/')
def healthcheck():
    # health check endpoint for startup
    return '', 204


@app.route('/rebalance')
def main():
    # define strategies
    leveraged_defensive_rotation = Strategy({
        'weight': 0.25,
        'symbols': {
            'minimum': 'VGLT',
            'moderate': 'QLD',
            'average': 'QLD',
            'elevated': 'XLU',
            'extreme': ''
        }
    })
    leveraged_tactical_balanced = Strategy({
        'weight': 0.25,
        'symbols': {
            'minimum': 'MVV',
            'moderate': 'MVV',
            'average': 'MVV',
            'elevated': 'IEF',
            'extreme': 'GLD'
        }
    })
    leveraged_strategic_tail_risk = Strategy({
        'weight': 0.25,
        'symbols': {
            'minimum': 'SSO',
            'moderate': 'SSO',
            'average': 'SSO',
            'elevated': 'IYR',
            'extreme': 'VIXM'
        }
    })
    vol_trend = Strategy({
        'weight': 0.25,
        'symbols': {
            'minimum': 'SVXY',
            'moderate': 'SVXY',
            'average': 'SVXY',
            'elevated': '',
            'extreme': ''
        }
    })

    # get config
    config = build_config()

    # setup portfolio
    portfolio = Portfolio(
        config=config,
        strategies=[
            leveraged_defensive_rotation,
            leveraged_tactical_balanced,
            leveraged_strategic_tail_risk,
            vol_trend
        ],
        vol_levels={
            'minimum': 20,
            'moderate': 40,
            'average': 60,
            'elevated': 80,
            'extreme': 100
        }
    )

    # retrieve current barometer value
    v = barometer()

    # rebalance portfolio
    portfolio.rebalance(v)

    return '', 204


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
