from argparse import ArgumentParser
from pathlib import Path

from stooqie.dashboard import StockPlotApp
from stooqie.io import write_historical_tickers
from stooqie.models import Settings
from stooqie.utils.log import logger


def update_historical_tickers(settings: Settings) -> None:
    """
    This is for downloading all ticker data. Eventually this will probably be a CRON job.
    """
    logger.info("Starting the application")
    tickers = [ticker.ticker_name for _, ticker in settings.stock_tickers.items()]

    write_historical_tickers(
        tickers, parquet_path=settings.parquet_path, parquet_invalidation_ttl=settings.parquet_invalidation_ttl
    )


def stock_app(csv_file_path: Path | None = None) -> None:
    if csv_file_path is not None:
        assert csv_file_path.exists(), "Input file path does not exist."
    settings = Settings() if csv_file_path is None else Settings(stock_ticker_path=csv_file_path)

    # This is really, really slow!
    update_historical_tickers(settings=settings)
    tickers_for_dashboard = [(ticker.display_name, ticker.ticker_name) for ticker in settings.stock_tickers.values()]

    StockPlotApp(tickers=tickers_for_dashboard).run()


def cli() -> None:
    argparser = ArgumentParser(prog="stooqie")
    argparser.add_argument(
        "-fc",
        "--from-csv-file",
        type=Path,
        required=False,
        help="CSV file to read Tickers from. Must have only 2 columns, `display_name` and `ticker_name`",
    )

    args = argparser.parse_args()
    stock_app(csv_file_path=args.from_csv_file)
