import pandas as pd
import requests
from io import StringIO


def main():
    ticker = "AAPL"  # Example ticker
    df = get_historical_data(ticker)
    print(df)


def get_historical_data(ticker):
    """
    Fetch historical stock data for a given ticker from Stooq and return it as a DataFrame.
    """
    url = f"https://stooq.com/q/d/l/?s={ticker}&i=d"
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        print(f"Failed to fetch data for {ticker}")
        return None

    main()
