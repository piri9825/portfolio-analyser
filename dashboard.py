import base64
import io
from pathlib import Path
from plistlib import InvalidFileException

import plotly.express as px
import dash

# dbc offers better styling/layout
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output, dash_table
from dash.exceptions import PreventUpdate

from processing import run_pipeline

# Add dbc css for a nice base style
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div(
    children=[
        # Use dbc Row/Col for more precise layout
        dbc.Row(
            children=[
                html.H1("Portfolio Analysis"),
                html.P("Example portfolio analysis tool"),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    # Upload
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(
                            ["Drag and Drop or ", html.A("Select Files")]
                        ),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                        },
                    ),
                ),
                dbc.Col(
                    # Cool alert widget that goes away after 6 seconds
                    dbc.Alert(
                        color="danger", id="error-message", is_open=False, duration=6000
                    ),
                ),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Row(id="pnl"),
                        dbc.Row(id="winners"),
                        dbc.Row(id="losers"),
                    ],
                    width=1,
                ),
                dbc.Col(id="output-graph"),
            ],
            style={"height": "50%"},
        ),
    ],
    style={"padding": 20},
)


def process_file(contents: str, filename: str) -> pd.DataFrame:
    process_functions = {".xlsx": pd.read_excel, ".csv": pd.read_csv}
    suffix = Path(
        filename
    ).suffix  # Safer, just in case someone has a file with periods in the name

    # Contents is base64 encoded string
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    # Use get to prevent the Key error
    if func := process_functions.get(suffix):
        return func(io.BytesIO(decoded))

    # If not matched it is an invalid file
    raise InvalidFileException(
        f"{suffix} is not supported, please use: {list(process_functions.keys())}"
    )


@app.callback(
    [
        Output("error-message", "children"),
        Output("error-message", "is_open"),
        Output("output-graph", "children"),
        Output("pnl", "children"),
        Output("winners", "children"),
        Output("losers", "children"),
    ],
    [
        Input("upload-data", "contents"),
        Input("upload-data", "filename"),
    ],
)
def refresh_data(contents: str, filename: str):
    if not filename:
        # All functions are ran on refresh, check actual inputs have been triggered
        # You should have done this previously by checking if n_clicks > 0
        raise PreventUpdate()

    try:
        df = process_file(contents, filename)
    except InvalidFileException as exception:
        # Tight try/except, explicit error
        return [str(exception), True, "", "", "", ""]

    try:
        cols, data, portfolio, portfolio_return, bad_tickers = run_pipeline(
            df, [x for x in df.columns.tolist() if x != "Date"]
        )
    except Exception as exception:
        # I didn't have time to check all the exceptions
        return [str(exception), True]

    if bad_tickers:
        return [
            "",
            "",
            "",
            "",
        ]

    winners = sorted(data, key=lambda x: x["PnL"], reverse=True)[:5]
    losers = sorted(data, key=lambda x: x["PnL"])[:5]

    fig = px.line(
        portfolio,
        x="Date",
        y="PnL",
        labels={"Date": "Date", "PnL": "Profit and Loss"},
    )
    fig.update_traces(mode="lines+markers")
    return [
        (
            f"Could not pull prices for: {bad_tickers}. These positions have been ignored."
            if bad_tickers
            else ""
        ),
        True if bad_tickers else "",
        dcc.Graph(figure=fig),
        f"P&L: {portfolio_return:,.2f}",
        html.Div(
            children=[
                html.H2("Winners"),
                dash_table.DataTable(data=winners),
            ]
        ),
        html.Div(
            children=[
                html.H2("Losers"),
                dash_table.DataTable(data=losers),
            ]
        ),
    ]


# try:
#         cols, data, portfolio, portfolio_return, bad_tickers = run_pipeline(
#             inputs_folder
#         )
#
#
#         portfolio_return = f"${portfolio_return:,.2f}"
#
#
#         return cols, data, fig, portfolio_return, bad_tickers, "Refresh"
#
#     except ValueError as e:
#         error_message = f"Error: {str(e)}"
#         return [], [], {}, None, error_message, "Refresh"
#
#
if __name__ == "__main__":
    app.run_server(
        debug=True,
        # host="0.0.0.0", # Not needed locally - in production you would use a WSGI like gunicorn/uvicorn (https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
        port=8050,
    )
