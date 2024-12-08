import pandas as pd
from processing import process_positions_into_trades

def test_positions_into_trades():
    input_df = pd.DataFrame({
            "Date": ["2024-08-30", "2024-09-03", "2024-09-04", "2024-09-05", "2024-09-06"],
            "AAPL": [0, 0, 13, 24, 0],
        })
    tickers = ["AAPL"]

    output = process_positions_into_trades(input_df, tickers)

    expected = pd.DataFrame({
            "Date": pd.to_datetime(["2024-08-30", "2024-09-03", "2024-09-04", "2024-09-05", "2024-09-06"]).date,
            "Ticker": ["AAPL", "AAPL", "AAPL", "AAPL", "AAPL"],
            "Trx": [0.0, 0.0, 13.0, 11.0, -24.0],
        })
    
    pd.testing.assert_frame_equal(output, expected)
 