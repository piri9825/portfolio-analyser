import pandas as pd
from processing import (
    process_positions_into_trades,
    get_date_values,
    process_prices,
    calculate_pnl,
)
from datetime import date


def test_positions_into_trades():
    input_df = pd.DataFrame(
        {
            "Date": [
                "2024-08-30",
                "2024-09-03",
                "2024-09-04",
                "2024-09-05",
                "2024-09-06",
            ],
            "AAPL": [0, 0, 13, 24, 0],
        }
    )
    tickers = ["AAPL"]

    output = process_positions_into_trades(input_df, tickers)

    expected = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2024-08-30", "2024-09-03", "2024-09-04", "2024-09-05", "2024-09-06"]
            ).date,
            "Ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
            "Trx": [0.0, 0.0, 13.0, 11.0, -24.0],
        }
    )

    pd.testing.assert_frame_equal(output, expected)


def test_get_date_values():
    input_df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-08-30",
                    "2024-09-03",
                    "2024-09-04",
                    "2024-09-05",
                    "2024-09-06",
                ]
            ).date
        }
    )
    min_date, max_date, max_date_plus_one = get_date_values(input_df)

    assert min_date == date(2024, 8, 30)
    assert max_date == date(2024, 9, 6)
    assert max_date_plus_one == date(2024, 9, 7)


def test_process_prices():
    input_df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-08-30",
                    "2024-09-03",
                    "2024-09-04",
                    "2024-09-05",
                    "2024-09-06",
                ]
            ).date,
            "Ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
            "High": [230.146792, 228.748326, 221.536270, 225.232189, 224.992472],
            "Low": [227.230003, 220.926929, 217.240993, 221.276549, 219.528482],
        }
    )

    output, bad_tickers = process_prices(input_df)

    expected = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-08-30",
                    "2024-09-03",
                    "2024-09-04",
                    "2024-09-05",
                    "2024-09-06",
                ]
            ).date,
            "Ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
            "High": [230.146792, 228.748326, 221.536270, 225.232189, 224.992472],
            "Low": [227.230003, 220.926929, 217.240993, 221.276549, 219.528482],
            "Price": [228.688398, 224.837628, 219.388632, 223.254369, 222.260477],
        }
    )
    pd.testing.assert_frame_equal(output, expected)
    assert bad_tickers == []


def test_process_prices_bad_tickers():
    input_df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-08-30",
                ]
            ).date,
            "Ticker": [
                "BADTICKER",
            ],
            "High": [None],
            "Low": [None],
        }
    )

    output, bad_tickers = process_prices(input_df)

    assert output.empty
    assert bad_tickers == ["BADTICKER"]


def test_calculate_pnl():
    input_df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-08-30",
                    "2024-09-03",
                    "2024-09-04",
                    "2024-09-05",
                    "2024-09-06",
                ]
            ).date,
            "Ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
            "Trx": [0.0, 0.0, 13.0, 11.0, -24.0],
        }
    )

    input_prices = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-08-30",
                    "2024-09-03",
                    "2024-09-04",
                    "2024-09-05",
                    "2024-09-06",
                ]
            ).date,
            "Ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
            "Price": [228.688398, 224.837628, 219.388632, 223.254369, 222.260477],
        }
    )

    df = calculate_pnl(input_df, input_prices)

    assert df["PnL"].tolist() == [
        0,
        0,
        -2852.05,
        -5307.85,
        26.40,
    ]
