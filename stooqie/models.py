from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, StrEnum
from pathlib import Path


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


@dataclass(frozen=True)
class Settings:
    parquet_path: Path = Path("./data/ticker.parquet")

    tickers_to_track: Sequence[Ticker] = tuple([ticker for ticker in Tickers])


settings = Settings()
