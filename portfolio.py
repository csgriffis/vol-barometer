from typing import List, Tuple

import alpaca_trade_api as tradeapi

from barometer import VolatilityLevels
from config import Config
from logger import logger
from strategy import Strategy, vol_level_literal


class Portfolio:
    def __init__(self, config: Config, strategies: List[Strategy], vol_levels: VolatilityLevels):
        # init alpaca client
        self.alpaca = tradeapi.REST(config['ALPACA_API_KEY'], config['ALPACA_API_SECRET'],
                                    config['ALPACA_API_BASE_URL'], 'v2')
        self.strategies = strategies
        self.vol_levels = vol_levels
        self.blocklist = set()

    def rebalance(self, barometer: float):
        """
        rebalance adjusts positions based on the provided volatility barometer value
        :param barometer: the current volatility barometer value used to rebalance portfolio
        :return:
        """
        # close any open orders before re-balancing
        self._remove_orders()

        # get volatility level literal
        vol_level = self._get_vol_level(barometer)

        logger.info('volatility values', barometer=barometer, volatility_level=vol_level)

        # get target allocation
        target = self._get_target_allocation(vol_level)
        target_positions = [t[0] for t in target]

        # get active positions
        positions = self.alpaca.list_positions()

        # remove existing positions that do not exist in the target allocation
        for position in positions:
            if target_positions.count(position.symbol) == 0:
                logger.info('closing position', symbol=position.symbol)
                # position not in target allocation; close
                self.alpaca.close_position(position.symbol)
            else:
                # position exists for target; do not adjust
                logger.info('target position exists', symbol=position.symbol)
                self.blocklist.add(position.symbol)

        # get account equity
        equity = int(float(self.alpaca.get_account().equity))

        for [ticker, weight] in target:
            logger.debug('iterating target', ticker=ticker, weight=weight)
            # create order if ticker is not in blocklist
            if self.blocklist.isdisjoint({ticker}):
                if ticker != '':
                    logger.info('submitting order', ticker=ticker)
                    # set notional ($ amount) instead of trying to calculate a quantity
                    self.alpaca.submit_order(symbol=ticker, order_class='simple', notional=(equity * weight))

    def _get_target_allocation(self, vol_level: vol_level_literal) -> List[Tuple[str, float]]:
        """
        build target allocation for all strategies
        :return: a list of (ticker, weight) tuples that represent the desired portfolio allocation
        """
        symbols = [s.get_symbol(vol_level) for s in self.strategies]
        weights = [s.strategy['weight'] for s in self.strategies]
        return list(zip(symbols, weights))

    def _get_vol_level(self, barometer: float) -> vol_level_literal:
        """
        retrieve the volatility level based on the barometer value
        :param barometer:
        :return vol_level_literal: volatility level key
        """
        for k in self.vol_levels:
            if barometer < self.vol_levels[k]:
                return k

    def _remove_orders(self):
        """
        remove_orders cancels all open orders
        :return:
        """
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            logger.info('canceling order', order_id=order.id)
            self.alpaca.cancel_order(order.id)
