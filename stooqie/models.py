from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum
from pathlib import Path

import pandas as pd


class TickerColumns(StrEnum):
    """
    Columns in the Ticker that we get from Stooq
    """

    date = "Date"
    open = "Open"
    high = "High"
    low = "Low"
    close = "Close"
    volume = "Volume"


@dataclass
class Ticker:
    display_name: str
    ticker_name: str


class Tickers(Ticker, Enum):
    apple = ("Apple", "AAPL.US")
    google = ("Google", "GOOGL.US")
    amazon = ("Amazon", "AMZN.US")
    microsoft = ("Microsoft", "MSFT.US")


@dataclass
class StockTickers:
    """
    We want a dict that has key as the lower case name and value as Ticker.
    We want to read this from a csv file.
    """

    tickers: dict[str, Ticker]

    @staticmethod
    def from_csv(csv_path: Path) -> StockTickers:
        ticker_df = pd.read_csv(csv_path).drop_duplicates()

        assert len(ticker_df) > 0, "Ticker CSV file is empty."

        tickers: dict[str, Ticker] = {}
        for _, row in ticker_df.iterrows():
            name = row["display_name"].lower()  # type: ignore
            tickers[name] = Ticker(display_name=row["display_name"], ticker_name=row["ticker_name"])  # type:ignore

        return StockTickers(tickers=tickers)


@dataclass(frozen=True)
class Settings:
    parquet_path: Path = Path("./data/ticker.parquet")

    stock_ticker_path: Path = Path("./data/stock_tickers.csv")

    stock_tickers: dict[str, Ticker] = StockTickers.from_csv(csv_path=stock_ticker_path).tickers


settings = Settings()
