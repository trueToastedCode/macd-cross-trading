import logging
import os
from periodic_simpletime import get_next_periodic_dt

from .cache_processing.cache_processing import CacheProcessing
from ..signal import *
from ..paper_trading.paper_trading import PaperTrading, Side, Type
from ..binance.klines_client import KlinesClient
from ..binance.make_trading_cache import make_trading_cache
from ..wait_connection import wait_connection


class MyStrategy:
    @classmethod
    async def create(cls, config):
        self = MyStrategy()
        self.config = config
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cookie_path = os.path.join(
            *os.path.split(dir_path)[:-2], 'cookies', config.COOKIE_FILE)
        self.paper_trading = PaperTrading.create_paper_trading_with_cookie_file(
            cookie_path=cookie_path,
            default_symbol=config.PAPER_SYMBOL
        )
        self.klines_client = await KlinesClient.create(
            symbol=config.KLINES_SYMBOL,
            interval=config.KLINES_INTERVAL
        )
        self.cache_processing = CacheProcessing(
            timeframe=config.TIMEFRAME,
            atr_len=config.ATR_LEN,
            rsi_len=config.RSI_LEN,
            ema_short_src=config.EMA_SHORT_SRC,
            ema_short_len=config.EMA_SHORT_LEN,
            ema_long_src=config.EMA_LONG_SRC,
            ema_long_len=config.EMA_LONG_LEN,
            macd_line_len=config.MACD_LINE_LEN,
            total_signal_macd_max_candle_count=config.TOTAL_SIGNAL_MACD_MAX_CANDLE_COUNT,
            total_signal_max_rsi=config.TOTAL_SIGNAL_MAX_RSI
        )
        self.trading_cache = await make_trading_cache(
            period=config.PERIOD,
            klines_client=self.klines_client,
            time_delta=config.INIT_TIMEDELTA,
            cache_size=config.CACHE_SIZE,
            cache_processing=self.cache_processing
        )
        self.last_id = None
        return self

    def long(self):
        logging.info('Received a long signal, try to open position')

        try:
            account = self.paper_trading.get_account()
        except Exception as e:
            logging.error(e)
            return

        # abort long if position is open
        if self.last_id:
            orders = account['orders']
            for order in orders:
                try:
                   parent = order['parent']
                except KeyError:
                    continue
                if parent == self.last_id:
                    logging.info('Position still open, abort')
                    return
            self.last_id = None

        # fetch and verify balance
        balance = account['account']['balance']
        if balance < self.config.MIN_BALANCE:
            logging.error(f'Balance is {balance}, expected at least {self.config.MIN_BALANCE}')
            return

        # amount, stop-loss take-profit
        df = self.trading_cache.df

        amount = (balance * self.config.AMOUNT_USE) / df.Close[-1]
        amount = PaperTrading.quantity_to_precision(amount)

        stop_loss = df.Close[-1] - self.config.SLAT_RATIO * df.ATR[-1]
        stop_loss = PaperTrading.price_to_precision(stop_loss)

        take_profit = df.Close[-1] + self.config.SLAT_RATIO * df.ATR[-1] * self.config.TPSL_RATIO
        take_profit = PaperTrading.price_to_precision(take_profit)

        logging.info(f'Open Long [ amount: {amount}, tp: {take_profit}, sl: {stop_loss} ]')

        # market order
        try:
            order = self.paper_trading.place_order(
                side=Side.BUY,
                type=Type.MARKET,
                quantity=amount,
                take_profit=take_profit,
                stop_loss=stop_loss
            )
        except Exception as e:
            logging.error(e)
            return
        self.last_id = order['id']

        logging.info('Open Long ok')

    async def run(self):
        quote_error_count = 0
        klines_error_count = 0

        while True:
            try:
                self.paper_trading.quote_token()
            except Exception as e:
                quote_error_count += 1
                logging.error(e)
                if quote_error_count == self.config.MAX_ERROR_COUNT:
                    logging.error('Reached max quote error count')
                    return
                wait_connection()
                continue
            quote_error_count = 0

            next_dt = get_next_periodic_dt(self.config.PERIOD)
            try:
                df = await self.klines_client.fetch_klines_with_next_periodic_dt(next_dt)
            except Exception as e:
                klines_error_count += 1
                logging.error(e)
                if klines_error_count == self.config.MAX_ERROR_COUNT:
                    logging.error('Reached max klines error count')
                    return
                wait_connection()
                continue
            klines_error_count = 0

            new_data_int_idx = self.trading_cache.concat(df)
            df = self.trading_cache.df

            if new_data_int_idx == len(df):
                logging.warning('No data has been added to cache, skipping interval')
                continue

            self.cache_processing.process_cache(df, new_data_int_idx)

            if df.index[-1] != next_dt - self.config.TIMEFRAME:
                logging.warning('Latest cache index doesn\'t match expected Datetime, ignoring signals')
                continue

            signal = df.TotalSignal[-1]
            if signal == LONG_SIGNAL:
                self.long()
            else:
                logging.debug('Received a nothing to do signal')
