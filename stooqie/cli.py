from stooqie.dashboard import StockPlotApp
from stooqie.io import write_historical_tickers
from stooqie.models import Settings
from stooqie.utils.log import logger


def main() -> None:
    """
    This is for downloading all ticker data. Eventually this will probably be a CRON job.

    TODO: Need to bring back caching and length logic
    """
    settings = Settings()

    logger.info("Starting the application")
    tickers = [ticker.ticker_name for _, ticker in settings.stock_tickers.items()]

    write_historical_tickers(
        tickers, parquet_path=settings.parquet_path, parquet_invalidation_ttl=settings.parquet_invalidation_ttl
    )


def cli() -> None:
    main()
    StockPlotApp().run()


if __name__ == "__main__":
    main()
