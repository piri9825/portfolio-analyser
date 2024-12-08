import pandas as pd
import os

def load_data(inputs_folder):
        df, tickers = load_data_and_validate_schema(inputs_folder)
        df = process_positions_into_trades(df, tickers)

        cols = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict('records')
        return cols, data

def load_data_and_validate_schema(inputs_folder):
    filenames = [f for f in os.listdir(inputs_folder) if f.endswith('.csv')]
    if len(filenames) != 1:
        raise ValueError('Need a singular .csv file in the inputs folder.')

    filename = filenames[0]
    df = pd.read_csv(f'{inputs_folder}/{filename}')

    if 'Date' not in df.columns:
        raise ValueError('Missing column "Date" in csv.')
    
    tickers = [col for col in df.columns if col != 'Date']
    num_tickers = df[tickers].select_dtypes("number").columns.tolist()
    non_num_tickers = [t for t in tickers if t not in num_tickers]

    if non_num_tickers:
        raise ValueError(f'The following tickers need to contain numbers: {non_num_tickers}')
    
    return df, tickers

def process_positions_into_trades(df, tickers):
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df = df.sort_values('Date')
    df[tickers] = df[tickers].diff(axis=0).fillna(0)
    df = df.melt(id_vars=["Date"], var_name="Ticker", value_name="Trx")

    return df