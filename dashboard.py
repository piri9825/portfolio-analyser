import dash
from dash import html, dash_table, Input, Output
import pandas as pd
import os

app = dash.Dash(__name__)
server = app.server

inputs_folder = "./docker_inputs"

def load_data():
    filenames = [f for f in os.listdir(inputs_folder) if f.endswith('.csv')]
    if filenames:
        filename = filenames[0]
        df = pd.read_csv(f'{inputs_folder}/{filename}')
        cols = [{"name": i, "id": i} for i in df.columns]
        data = df.to_dict('records')
    else:
        cols = []
        data = []

    return cols, data

cols, data = load_data()

app.layout = html.Div([
    html.H1("Portfolio Analysis"),
    html.Button("Refresh Data", id="refresh-button", n_clicks=0),
    dash_table.DataTable(
        id='data-table',
        columns=cols,
        data=data,
        style_table={'width': '75%'}
    )
])

# Callback to refresh the data
@app.callback(
    [Output("data-table", "columns"),
     Output("data-table", "data"),
     ],
    Input("refresh-button", "n_clicks")
)
def refresh_data(n_clicks):
    cols, data = load_data()
    
    return cols, data

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
