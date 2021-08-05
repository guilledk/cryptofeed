'''
Copyright (C) 2017-2021  Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
from cryptofeed.symbols import Symbol
from cryptofeed.exchanges.phemex import Phemex
from cryptofeed.exchanges.dydx import dYdX
from decimal import Decimal

from cryptofeed import FeedHandler
from cryptofeed.callback import BookCallback, FundingCallback, TickerCallback, TradeCallback, FuturesIndexCallback, OpenInterestCallback
from cryptofeed.defines import CANDLES, BID, ASK, BLOCKCHAIN, COINBASE, FUNDING, GEMINI, L2_BOOK, L3_BOOK, OPEN_INTEREST, PERPETUAL, TICKER, TRADES, FUTURES_INDEX, BOOK_DELTA
from cryptofeed.exchanges import (FTX, Binance, BinanceUS, BinanceFutures, Bitfinex, Bitflyer, AscendEX, Bitmex, Bitstamp, Bittrex, Coinbase, Gateio,
                                  HitBTC, Huobi, HuobiDM, HuobiSwap, Kraken, OKCoin, OKEx, Poloniex, Bybit, KuCoin)


# Examples of some handlers for different updates. These currently don't do much.
# Handlers should conform to the patterns/signatures in callback.py
# Handlers can be normal methods/functions or async. The feedhandler is paused
# while the callbacks are being handled (unless they in turn await other functions or I/O)
# so they should be as lightweight as possible
async def ticker(feed, symbol, bid, ask, timestamp, receipt_timestamp):
    print(f'Timestamp: {timestamp} Feed: {feed} Symbol: {symbol} Bid: {bid} Ask: {ask}')


async def delta(feed, symbol, delta, timestamp, receipt_timestamp):
    print(f'Timestamp: {timestamp} Feed: {feed} Symbol: {symbol} Delta Bid Size is {len(delta[BID])} Delta Ask Size is {len(delta[ASK])}')


async def trade(t, receipt_timestamp):
    assert isinstance(t.timestamp, float)
    assert isinstance(t.side, str)
    assert isinstance(t.amount, Decimal)
    assert isinstance(t.price, Decimal)
    print(f"Trade received at {receipt_timestamp}: {t}")


async def book(feed, symbol, book, timestamp, receipt_timestamp):
    print(f'Timestamp: {timestamp} Cryptofeed Receipt: {receipt_timestamp} Feed: {feed} Symbol: {symbol} Book Bid Size is {len(book[BID])} Ask Size is {len(book[ASK])}')


async def funding(**kwargs):
    print(f"Funding Update for {kwargs['feed']}")
    print(kwargs)


async def oi(feed, symbol, open_interest, timestamp, receipt_timestamp):
    print(f'Timestamp: {timestamp} Feed: {feed} Symbol: {symbol} open interest: {open_interest}')


async def volume(**kwargs):
    print(f"Volume: {kwargs}")


async def futures_index(**kwargs):
    print(f"FuturesIndex: {kwargs}")


async def candle_callback(feed, symbol, start, stop, interval, trades, open_price, close_price, high_price, low_price, volume, closed, timestamp, receipt_timestamp):
    print(f"Candle: {timestamp} {receipt_timestamp} Feed: {feed} Symbol: {symbol} Start: {start} Stop: {stop} Interval: {interval} Trades: {trades} Open: {open_price} Close: {close_price} High: {high_price} Low: {low_price} Volume: {volume} Candle Closed? {closed}")


def main():
    config = {'log': {'filename': 'demo.log', 'level': 'INFO'}}
    # the config will be automatically passed into any exchanges set up by string. Instantiated exchange objects would need to pass the config in manually.
    f = FeedHandler(config=config)
    # Note: EXX is extremely unreliable - sometimes a connection can take many many retries
    # from cryptofeed.exchanges import EXX
    # f.add_feed(EXX(symbols=['BTC-USDT'], channels=[L2_BOOK, TRADES], callbacks={L2_BOOK: BookCallback(book), TRADES: TradeCallback(trade)}))
    # *** Kucoin requires an API key for L2 book data! ***
    #f.add_feed(KuCoin(symbols=['BTC-USDT', 'ETH-USDT'], channels=[L2_BOOK, ], callbacks={L2_BOOK: book, BOOK_DELTA: delta, CANDLES: candle_callback, TICKER: ticker, TRADES: trade}))
    #f.add_feed(Gateio(symbols=['BTC-USDT', 'ETH-USDT'], channels=[L2_BOOK], callbacks={CANDLES: candle_callback, L2_BOOK: book, TRADES: trade, TICKER: ticker, BOOK_DELTA: delta}))
    pairs = Binance.symbols()
    f.add_feed(Binance(symbols=pairs, channels=[TRADES], callbacks={TRADES: TradeCallback(trade)}))
    """
    pairs = BinanceUS.symbols()
    f.add_feed(BinanceUS(symbols=pairs, channels=[CANDLES], callbacks={CANDLES: candle_callback}))
    f.add_feed(COINBASE, symbols=['BTC-USD'], channels=[TICKER], callbacks={TICKER: TickerCallback(ticker)})
    f.add_feed(Coinbase(symbols=['BTC-USD'], channels=[TRADES], callbacks={TRADES: TradeCallback(trade)}))
    f.add_feed(Coinbase(subscription={L2_BOOK: ['BTC-USD', 'ETH-USD'], TRADES: ['ETH-USD']}, callbacks={TRADES: TradeCallback(trade), L2_BOOK: BookCallback(book)}))
    f.add_feed(Coinbase(subscription={L3_BOOK: ['LTC-USD']}, callbacks={L3_BOOK: BookCallback(book)}))
    f.add_feed(Bitfinex(symbols=['BTC-USDT'], channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(book)}))
    f.add_feed(Bitfinex(symbols=['BTC'], channels=[FUNDING], callbacks={FUNDING: FundingCallback(funding)}))
    f.add_feed(Poloniex(symbols=['BTC-USDT'], channels=[TICKER, TRADES], callbacks={TICKER: TickerCallback(ticker), TRADES: TradeCallback(trade)}))
    f.add_feed(Poloniex(subscription={TRADES: ['DOGE-BTC'], L2_BOOK: ['LTC-BTC']}, callbacks={TRADES: TradeCallback(trade), L2_BOOK: BookCallback(book)}))
    f.add_feed(GEMINI, subscription={L2_BOOK: ['BTC-USD', 'ETH-USD'], TRADES: ['ETH-USD', 'BTC-USD']}, callbacks={TRADES: TradeCallback(trade), L2_BOOK: BookCallback(book)})
    f.add_feed(HitBTC(channels=[TRADES], symbols=['BTC-USDT'], callbacks={TRADES: TradeCallback(trade)}))
    f.add_feed(HitBTC(channels=[L2_BOOK], symbols=['BTC-USDT'], callbacks={L2_BOOK: BookCallback(book)}))
    f.add_feed(Bitstamp(channels=[L2_BOOK, TRADES], symbols=['BTC-USD'], callbacks={L2_BOOK: BookCallback(book), TRADES: TradeCallback(trade)}))
    bitmex_symbols = Bitmex.symbols()
    f.add_feed(Bitmex(channels=[OPEN_INTEREST], symbols=['BTC-USD-PERP'], callbacks={OPEN_INTEREST: oi}))
    f.add_feed(Bitmex(channels=[TRADES], symbols=bitmex_symbols, callbacks={TRADES: TradeCallback(trade)}))
    f.add_feed(Bitmex(symbols=['BTC-USD-PERP'], channels=[FUNDING, TRADES], callbacks={FUNDING: FundingCallback(funding), TRADES: TradeCallback(trade)}))
    f.add_feed(Bitmex(symbols=['BTC-USD-PERP'], channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(book)}))
    f.add_feed(Kraken(checksum_validation=True, subscription={L2_BOOK: ['BTC-USD'], TRADES: ['BTC-USD'], CANDLES: ['BTC-USD'], TICKER: ['ETH-USD']}, callbacks={L2_BOOK: book, CANDLES: candle_callback, TRADES: TradeCallback(trade), TICKER: TickerCallback(ticker)}))
    sub = {TRADES: ['BTC-USDT', 'ETH-USDT'], L2_BOOK: ['BTC-USDT']}
    f.add_feed(Huobi(subscription=sub, callbacks={TRADES: TradeCallback(trade), L2_BOOK: BookCallback(book)}))
    f.add_feed(Huobi(symbols=['BTC-USDT'], channels=[CANDLES], callbacks={CANDLES: candle_callback}))
    sub = {L2_BOOK: HuobiDM.symbols()[:2]}
    f.add_feed(HuobiDM(subscription=sub, callbacks={TRADES: TradeCallback(trade), L2_BOOK: BookCallback(book)}))
    pairs = ['BTC-USD-PERP', 'ETH-USD-PERP', 'EOS-USD-PERP', 'BCH-USD-PERP', 'BSV-USD-PERP', 'LTC-USD-PERP']
    f.add_feed(HuobiSwap(symbols=pairs, channels=[TRADES, L2_BOOK, FUNDING], callbacks={FUNDING: funding, TRADES: TradeCallback(trade), L2_BOOK: BookCallback(book)}))
    f.add_feed(OKCoin(symbols=['BTC-USD'], channels=[L2_BOOK], callbacks={L2_BOOK: BookCallback(book)}))
    f.add_feed(OKEx(symbols=['BTC-USDT'], channels=[TRADES], callbacks={TRADES: TradeCallback(trade)}))
    f.add_feed(Bittrex(subscription={L2_BOOK: ['BTC-USDT', 'ETH-USDT'], CANDLES: ['BTC-USDT', 'ETH-USDT'], TRADES: ['BTC-USDT', 'ETH-USDT'], TICKER: ['BTC-USDT', 'ETH-USDT']}, callbacks={CANDLES: candle_callback, L2_BOOK: BookCallback(book), TICKER: TickerCallback(ticker), TRADES: TradeCallback(trade)}))
    f.add_feed(FTX(symbols=['ADA-USD-PERP', 'ALGO-USD-PERP', 'ALT-USD-PERP', 'ATOM-USD-PERP', 'BCH-USD-PERP'], channels=[TICKER], callbacks={TICKER: ticker, TRADES: TradeCallback(trade)}))
    f.add_feed(Bybit(symbols=['BTC-USDT-PERP', 'BTC-USD-PERP'], channels=[FUTURES_INDEX, FUNDING, OPEN_INTEREST], callbacks={OPEN_INTEREST: OpenInterestCallback(oi), FUTURES_INDEX: FuturesIndexCallback(futures_index), FUNDING: funding}))
    f.add_feed(Bybit(symbols=['BTC-USDT-PERP', 'BTC-USD-PERP'], channels=[L2_BOOK, TRADES], callbacks={TRADES: trade, L2_BOOK: book}))
    f.add_feed(BLOCKCHAIN, symbols=['BTC-USD', 'ETH-USD'], channels=[L2_BOOK, TRADES], callbacks={L2_BOOK: BookCallback(book), TRADES: trade})
    f.add_feed(AscendEX(symbols=['XRP-USDT', 'BTC-USDT'], channels=[TRADES], callbacks={TRADES: trade, L2_BOOK: book}))
    f.add_feed(Bitflyer(symbols=['BTC-JPY'], channels=[L2_BOOK, TRADES, TICKER], callbacks={L2_BOOK: book, BOOK_DELTA: delta, TICKER: ticker, TRADES: trade}))
    f.add_feed(BinanceFutures(symbols=['BTC-USDT-PERP'], channels=[TICKER], callbacks={TICKER: ticker}))
    f.add_feed(BinanceFutures(subscription={TRADES: ['BTC-USDT-PERP'], CANDLES: ['BTC-USDT-PERP', 'BTC-USDT-PINDEX']}, callbacks={CANDLES: candle_callback, TRADES: trade}))
    f.add_feed(dYdX(symbols=dYdX.symbols(), channels=[L2_BOOK], callbacks={TRADES: trade, L2_BOOK: book, BOOK_DELTA: delta}))
    symbol = Symbol('BTC', 'USD', type=PERPETUAL)
    f.add_feed(Phemex(symbols=[symbol], channels=[CANDLES, TRADES], callbacks={TRADES: trade, L2_BOOK: book, CANDLES: candle_callback}))
    """
    f.run()


if __name__ == '__main__':
    main()
