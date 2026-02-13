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


@dataclass
class HistoricalOffsetColumn:
    """
    Dataclass to keep track of all historical offset columns we will add to the stocks parquet

    Attributes:
        column_name: Name of column
        years: Number of years offset. Note that by offset we always mean going back
        months: num of months
        days: num of days
    """

    column_name: str
    years: int
    months: int
    days: int


class HistoricalOffsetColumns(HistoricalOffsetColumn, Enum):
    """
    Columns in the Stock that we want to add for doing historical change tracking
    """

    one = "offset_one", 1, 0, 0
    two = "offset_two", 2, 0, 0
    five = "offset_five", 5, 0, 0
    ten = "offset_ten", 10, 0, 0
    twenty = "offset_twenty", 20, 0, 0

    def __repr__(self) -> str:
        return self.value


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
    # Location of parquet where we store post processed ticker data.
    parquet_path: Path = Path.home() / Path(".local/state/stooqie/data/ticker.parquet")

    # How stale can the ticker data in the parquet be before we redownload.
    parquet_invalidation_ttl: int = 5

    stock_ticker_path: Path = Path(__file__).parent.parent / Path("data/stock_tickers.csv")

    def __post_init__(self):
        self.parquet_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def stock_tickers(self) -> dict[str, Ticker]:
        return StockTickers.from_csv(csv_path=self.stock_ticker_path).tickers


settings = Settings()
