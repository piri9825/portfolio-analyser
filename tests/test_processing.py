import pandas as pd
from processing import process_positions_into_trades, get_date_values
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
