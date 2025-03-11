import pandas as pd

from stooqie.io import get_ticker_df
from stooqie.models import Settings
from stooqie.utils.log import logger


def main():
    """
    This is for downloading all ticker data. Eventually this will probably be a CRON job.

    Right now this and get_ticker_df are doing very similar jobs.
    """
    settings = Settings()

    logger.info("Starting the application")
    tickers = [ticker.ticker_name for ticker in settings.tickers_to_track]

    ticker_dfs = []
    for ticker in tickers:
        historical_change_df = get_ticker_df(ticker)
        ticker_dfs.append(historical_change_df)

    ticker_df = pd.concat(ticker_dfs)
    ticker_df.to_parquet(settings.parquet_path)


if __name__ == "__main__":
    main()
