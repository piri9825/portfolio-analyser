import pandas as pd
from datetime import timedelta
import yfinance as yf


def validate_schema(df):
    if "Date" not in df.columns:
        raise ValueError('Missing column "Date" in file.')

    tickers = [col for col in df.columns if col != "Date"]
    num_tickers = df[tickers].select_dtypes("number").columns.tolist()
    non_num_tickers = [t for t in tickers if t not in num_tickers]

    if non_num_tickers:
        raise ValueError(
            f"The following ticker columns need to contain numbers only: {non_num_tickers}"
        )

    return df, tickers


def process_positions_into_trades(df, tickers):
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.sort_values("Date")
    df.iloc[-1, 1:] = 0
    df[tickers] = df[tickers].diff(axis=0).fillna(0)
    df = df.melt(id_vars=["Date"], var_name="Ticker", value_name="Trx")

    return df


def get_date_values(df):
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    max_date_plus_one = max_date + timedelta(1)

    return min_date, max_date, max_date_plus_one


def get_prices_from_yfinance(tickers, min_date, max_date_plus_one):
    # auto_adjust=False mimics Execution Price better as you would not adjust your Execution Price of trades unless you also adjust the buy/sell quantity
    prices = yf.download(tickers, min_date, max_date_plus_one, auto_adjust=True)
    prices = prices[["Low", "High"]]
    prices = prices.stack(["Ticker"], future_stack=True).reset_index()

    return prices


def process_prices(prices):
    prices["Date"] = pd.to_datetime(prices["Date"]).dt.date
    prices["Price"] = prices[["Low", "High"]].mean(axis=1)
    bad_tickers = prices.loc[prices["Price"].isna(), "Ticker"].unique().tolist()
    prices = prices.loc[~prices["Ticker"].isin(bad_tickers)]

    return prices, bad_tickers


def calculate_pnl(df, prices):
    df = df.merge(prices[["Date", "Ticker", "Price"]], on=["Date", "Ticker"])
    df["Cashflow"] = df["Trx"] * df["Price"] * -1
    df["PnL"] = df.groupby("Ticker")["Cashflow"].cumsum()
    df["PnL"] = df["PnL"].round(2)

    return df


def calculate_portfolio_returns(df, max_date):
    df = df.groupby("Date")["PnL"].sum().reset_index()
    df["PnL"] = df["PnL"].round(2)
    portfolio_return = df.loc[df["Date"] == max_date, "PnL"].iloc[0]

    return portfolio_return


def get_best_and_worst_performers(df, max_date):
    df = df.loc[df["Date"] == max_date, ["Ticker", "PnL"]].sort_values(
        "PnL", ascending=False
    )
    df = pd.concat([df.head(5), df.tail(5)])

    return df


def calculate_portfolio_value_over_time(df, prices):
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df.sort_values("Date")
    df = df.melt(id_vars=["Date"], var_name="Ticker", value_name="Position")

    df = df.merge(prices[["Date", "Ticker", "Price"]], on=["Date", "Ticker"])
    df["PortfolioValue"] = df["Position"] * df["Price"]
    df = df.groupby(["Date"])["PortfolioValue"].sum().reset_index()
    df["PortfolioValue"] = df["PortfolioValue"].round(2)

    return df


def run_pipeline(inputs_folder):
    pos, tickers = validate_schema(inputs_folder)
    df = process_positions_into_trades(pos, tickers)

    min_date, max_date, max_date_plus_one = get_date_values(df)

    prices = get_prices_from_yfinance(tickers, min_date, max_date_plus_one)

    prices, bad_tickers = process_prices(prices)

    df = calculate_pnl(df, prices)

    portfolio_return = calculate_portfolio_returns(df, max_date)

    performers = get_best_and_worst_performers(df, max_date)

    cols = [{"name": i, "id": i} for i in performers.columns]
    data = performers.to_dict("records")

    portfolio = calculate_portfolio_value_over_time(pos, prices)

    return cols, data, portfolio, portfolio_return, bad_tickers
