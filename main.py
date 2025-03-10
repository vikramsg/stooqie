import logging

import pandas as pd

from stooqie.models import Settings
from stooqie.ticker import get_ticker_df

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")
logger = logging.getLogger()


def main():
    settings = Settings()

    logger.info("Starting the application")
    tickers = settings.tickers_to_track

    ticker_dfs = []
    for ticker in tickers:
        historical_change_df = get_ticker_df(
            ticker, invalidation_ttl=settings.invalidation_ttl, parquet_path=settings.parquet_path
        )
        ticker_dfs.append(historical_change_df)

    ticker_df = pd.concat(ticker_dfs)
    ticker_df.to_parquet(settings.parquet_path)


if __name__ == "__main__":
    main()
