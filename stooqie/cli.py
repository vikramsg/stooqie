from argparse import ArgumentParser
from pathlib import Path

from stooqie.dashboard import StockPlotApp
from stooqie.io import write_historical_tickers
from stooqie.models import Settings, settings
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

    update_historical_tickers(settings=settings)
    tickers_for_dashboard = [(ticker.display_name, ticker.ticker_name) for ticker in settings.stock_tickers.values()]

    StockPlotApp(tickers=tickers_for_dashboard).run()


def clean_state(state_path: Path) -> None:
    state_path.unlink()


def cli() -> None:
    argparser = ArgumentParser(prog="stooqie")
    argparser.add_argument(
        "-fc",
        "--from-csv-file",
        type=Path,
        required=False,
        help="CSV file to read Tickers from. Must have only 2 columns, `display_name` and `ticker_name`",
    )

    subparsers = argparser.add_subparsers(dest="command")
    subparsers.add_parser("clean", help="Clean state files if any. Using stooqie again will trigger redownloads.")

    args = argparser.parse_args()

    match args.command:
        case "clean":
            clean_state(settings.parquet_path)
        case _:
            stock_app(csv_file_path=args.from_csv_file)
