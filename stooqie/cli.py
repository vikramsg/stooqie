from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from stooqie.bump import bump_dataframe
from stooqie.dashboard import BumpPlotApp, StockPlotApp
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


def stock_bump(csv_file_path: Path | None = None) -> None:
    if csv_file_path is not None:
        assert csv_file_path.exists(), "Input file path does not exist."
    settings = Settings() if csv_file_path is None else Settings(stock_ticker_path=csv_file_path)

    update_historical_tickers(settings=settings)

    bump_dataframe(parquet_file=settings.parquet_path)


def bump_dashboard(csv_file_path: Path | None = None) -> None:
    if csv_file_path is not None:
        assert csv_file_path.exists(), "Input file path does not exist."
    settings = Settings() if csv_file_path is None else Settings(stock_ticker_path=csv_file_path)

    update_historical_tickers(settings=settings)

    # Run analysis for 2x, 5x, 10x factors and combine results
    bump_factors = [2, 5, 10]
    all_bump_dfs = []
    for factor in bump_factors:
        df = bump_dataframe(settings.parquet_path, bump_factor_filter=factor)
        df["min_bump_factor"] = factor  # Tag the result with the minimum factor it satisfied
        all_bump_dfs.append(df)

    if not all_bump_dfs:
        logger.info("No stocks found with the specified bump factors.")
        return

    combined_df = pd.concat(all_bump_dfs)

    # Keep only the highest bump factor for each ticker
    # Sort by ticker and then by the actual 'bump' value (which is the factor)
    combined_df = combined_df.sort_values(by=["ticker", "bump"], ascending=[True, False])

    # Drop duplicates, keeping the first (highest bump) for each ticker
    combined_df = combined_df.drop_duplicates(subset=["ticker"], keep="first")

    # Prepare data for the dashboard
    tickers_for_dashboard = [
        (f"{row['ticker']} ({row['bump']:.1f}x)", row["ticker"]) for _, row in combined_df.iterrows()
    ]

    BumpPlotApp(tickers=tickers_for_dashboard).run()


def cli() -> None:
    argparser = ArgumentParser(prog="stooqie")

    csv_file_args = ("-fc", "--from-csv-file")
    csv_file_kwargs = {
        "type": Path,
        "required": False,
        "help": "CSV file to read Tickers from. Must have only 2 columns, `display_name` and `ticker_name`",
    }
    argparser.add_argument(*csv_file_args, **csv_file_kwargs)

    subparsers = argparser.add_subparsers(dest="command")

    subparsers.add_parser("clean", help="Clean state files if any. Using stooqie again will trigger redownloads.")

    bump_parser = subparsers.add_parser("bump", help="Show stocks that have had big bumps, both positive and negative!")
    bump_parser.add_argument(*csv_file_args, **csv_file_kwargs)

    # ADD NEW COMMAND
    bump_dashboard_parser = subparsers.add_parser(
        "bump-dashboard", help="Show stocks that have had big bumps in a TUI dashboard."
    )
    bump_dashboard_parser.add_argument(*csv_file_args, **csv_file_kwargs)

    args = argparser.parse_args()

    match args.command:
        case "clean":
            clean_state(settings.parquet_path)
        case "bump":
            stock_bump(csv_file_path=args.from_csv_file)
        case "bump-dashboard":  # ADD NEW CASE
            bump_dashboard(csv_file_path=args.from_csv_file)
        case _:
            stock_app(csv_file_path=args.from_csv_file)
