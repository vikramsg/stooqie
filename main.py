import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from stooqie.models import TickerColumns
from stooqie.ticker import historical_change_from_ticker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")
logger = logging.getLogger()


@dataclass(frozen=True)
class Settings:
    # If a parquet already contains data for a particular stock that is no more
    # than the following number of days old, use that and don't download
    invalidation_ttl: int = 5

    parquet_path: Path = Path("./data/ticker.parquet")


def _get_ticker_df(ticker: str, *, invalidation_ttl: int, parquet_path: Path) -> pd.DataFrame:
    stored_df = pd.read_parquet(parquet_path)
    historical_change_df = stored_df.loc[stored_df["ticker"] == ticker]

    latest_date = pd.to_datetime(historical_change_df[TickerColumns.date]).max()
    # If date is too old, then fetch
    if abs((latest_date - datetime.now()).days) > invalidation_ttl:
        historical_change_df = historical_change_from_ticker(ticker)

        historical_change_df["ticker"] = ticker
        logger.debug("Ticker %s cache is too old. Fetching...", ticker)

    logger.info("Ticker %s contains %s rows.", ticker, len(historical_change_df))

    return historical_change_df


def main():
    settings = Settings()

    logger.info("Starting the application")
    # Example ticker list
    tickers = ["AAPL.US", "GOOGL.US"]

    ticker_dfs = []
    for ticker in tickers:
        historical_change_df = _get_ticker_df(
            ticker, invalidation_ttl=settings.invalidation_ttl, parquet_path=settings.parquet_path
        )
        ticker_dfs.append(historical_change_df)

    ticker_df = pd.concat(ticker_dfs)
    ticker_df.to_parquet(settings.parquet_path)


if __name__ == "__main__":
    main()
