import pandas as pd
import os

def load_data(inputs_folder):
    filenames = [f for f in os.listdir(inputs_folder) if f.endswith('.csv')]
    if len(filenames) != 1:
        raise ValueError('Need a singular .csv file in the inputs folder.')
    else:
        filename = filenames[0]
        df = pd.read_csv(f'{inputs_folder}/{filename}')
        cols = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict('records')
        return cols, data
