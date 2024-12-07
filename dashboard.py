import dash
from dash import html, dash_table
import pandas as pd

data = pd.read_csv('./inputs/portfolio.csv')

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Portfolio Analysis"),
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in data.columns],
        data=data.to_dict('records'),
        style_table={'width': '75%'}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
