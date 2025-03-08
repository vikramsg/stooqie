from io import StringIO

import pandas as pd
import requests


def get_historical_data(ticker) -> pd.DataFrame:
    """
    Fetch historical stock data for a given ticker from Stooq and return it as a DataFrame.
    """
    url = f"https://stooq.com/q/d/l/?s={ticker}&i=d"
    response = requests.get(url)
    csv_data = StringIO(response.text)
    df = pd.read_csv(csv_data)
    return df

if __name__ == "__main__":
    ticker = "AAPL"
    df = get_historical_data(ticker)
    print(df.head())
