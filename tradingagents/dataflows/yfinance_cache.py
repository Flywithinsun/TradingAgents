"""Small process-local cache for repeated yfinance lookups."""

from __future__ import annotations

import functools
from typing import Any

import yfinance as yf

from .stockstats_utils import yf_retry


def _normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


@functools.lru_cache(maxsize=256)
def get_cached_ticker(ticker: str) -> yf.Ticker:
    """Reuse Ticker objects across repeated lookups in the same process."""
    return yf.Ticker(_normalize_ticker(ticker))


@functools.lru_cache(maxsize=256)
def get_ticker_info(ticker: str) -> dict[str, Any]:
    info = yf_retry(lambda: get_cached_ticker(ticker).info) or {}
    return dict(info)


def get_ticker_history(ticker: str, start_date: str, end_date: str):
    """Return a defensive copy of historical data for one ticker/date range."""
    data = yf_retry(
        lambda: get_cached_ticker(ticker).history(start=start_date, end=end_date)
    )
    return data.copy()


@functools.lru_cache(maxsize=256)
def get_balance_sheet_data(ticker: str, frequency: str):
    ticker_obj = get_cached_ticker(ticker)
    if frequency == "quarterly":
        data = yf_retry(lambda: ticker_obj.quarterly_balance_sheet)
    else:
        data = yf_retry(lambda: ticker_obj.balance_sheet)
    return data.copy()


@functools.lru_cache(maxsize=256)
def get_cashflow_data(ticker: str, frequency: str):
    ticker_obj = get_cached_ticker(ticker)
    if frequency == "quarterly":
        data = yf_retry(lambda: ticker_obj.quarterly_cashflow)
    else:
        data = yf_retry(lambda: ticker_obj.cashflow)
    return data.copy()


@functools.lru_cache(maxsize=256)
def get_income_statement_data(ticker: str, frequency: str):
    ticker_obj = get_cached_ticker(ticker)
    if frequency == "quarterly":
        data = yf_retry(lambda: ticker_obj.quarterly_income_stmt)
    else:
        data = yf_retry(lambda: ticker_obj.income_stmt)
    return data.copy()


@functools.lru_cache(maxsize=256)
def get_insider_transactions_data(ticker: str):
    data = yf_retry(lambda: get_cached_ticker(ticker).insider_transactions)
    if data is None:
        return None
    return data.copy()


@functools.lru_cache(maxsize=256)
def get_ticker_news(ticker: str, count: int):
    news = yf_retry(lambda: get_cached_ticker(ticker).get_news(count=count))
    return list(news or [])


@functools.lru_cache(maxsize=256)
def search_news(query: str, news_count: int):
    search = yf_retry(
        lambda: yf.Search(
            query=query,
            news_count=news_count,
            enable_fuzzy_query=True,
        )
    )
    return list(search.news or [])
