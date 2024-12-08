import pandas as pd
import os
from datetime import timedelta
import yfinance as yf


def load_data_and_validate_schema(inputs_folder):
    filenames = [f for f in os.listdir(inputs_folder) if f.endswith(".csv")]
    if len(filenames) != 1:
        raise ValueError("Need a singular .csv file in the inputs folder.")

    filename = filenames[0]
    df = pd.read_csv(f"{inputs_folder}/{filename}")

    if "Date" not in df.columns:
        raise ValueError('Missing column "Date" in csv.')

    tickers = [col for col in df.columns if col != "Date"]
    num_tickers = df[tickers].select_dtypes("number").columns.tolist()
    non_num_tickers = [t for t in tickers if t not in num_tickers]

    if non_num_tickers:
        raise ValueError(
            f"The following tickers need to contain numbers: {non_num_tickers}"
        )

    return df, tickers


def process_positions_into_trades(df, tickers):
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.sort_values("Date")
    df[tickers] = df[tickers].diff(axis=0).fillna(0)
    df = df.melt(id_vars=["Date"], var_name="Ticker", value_name="Trx")

    return df


def get_date_values(df):
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    max_date_plus_one = max_date + timedelta(1)

    return min_date, max_date, max_date_plus_one


def get_prices_from_yfinance(tickers, min_date, max_date_plus_one):
    # auto_adjust=False mimics Execution Price better as you would not adjust your Execution Price of trades
    prices = yf.download(tickers, min_date, max_date_plus_one, auto_adjust=False)
    prices = prices[["Low", "High"]]
    prices = prices.stack(["Ticker"], future_stack=True).reset_index()

    return prices


def process_prices(prices):
    prices["Date"] = pd.to_datetime(prices["Date"]).dt.date
    prices["Price"] = prices[["Low", "High"]].mean(axis=1)
    bad_tickers = prices.loc[prices["Price"].isna(), "Ticker"].unique().tolist()
    prices = prices.loc[~prices["Ticker"].isin(bad_tickers)]

    return prices, bad_tickers


def load_data(inputs_folder):
    df, tickers = load_data_and_validate_schema(inputs_folder)
    df = process_positions_into_trades(df, tickers)

    min_date, max_date, max_date_plus_one = get_date_values(df)

    prices = get_prices_from_yfinance(tickers, min_date, max_date_plus_one)

    prices, bad_tickers = process_prices(prices)

    cols = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict("records")
    return cols, data
