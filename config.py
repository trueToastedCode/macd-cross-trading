from datetime import timedelta
from periodic_simpletime import PeriodicSimpleTime


TIMEFRAME       = timedelta(minutes=5)
KLINES_SYMBOL   = 'BTCUSDT'
KLINES_INTERVAL = '5m'
PERIOD          = PeriodicSimpleTime(minute=5)
INIT_TIMEDELTA  = timedelta(days=3)
CACHE_SIZE      = 500
COOKIE_FILE     = 'papertrading.txt'
PAPER_SYMBOL    = 'BITSTAMP:BTCUSD'
MAX_ERROR_COUNT = 3

ATR_LEN                            = 14
RSI_LEN                            = 14
EMA_SHORT_SRC                      = 'Close'
EMA_SHORT_LEN                      = 12
EMA_LONG_SRC                       = 'Close'
EMA_LONG_LEN                       = 26
MACD_LINE_LEN                      = 9
TOTAL_SIGNAL_MAX_RSI               = 76
TOTAL_SIGNAL_MACD_MAX_CANDLE_COUNT = 14

MIN_BALANCE = 150
AMOUNT_USE  = 0.99
SLAT_RATIO  = 1.2
TPSL_RATIO  = 2.6
