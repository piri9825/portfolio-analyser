from dash import _dash_renderer, Dash, html, dash_table, Input, Output, dcc
from dash.exceptions import PreventUpdate
import base64
import pandas as pd
from pathlib import Path
import io
from plistlib import InvalidFileException
import plotly.express as px
import dash_mantine_components as dmc
from processing import run_pipeline

_dash_renderer._set_react_version("18.2.0")

app = Dash(__name__, external_stylesheets=dmc.styles.ALL)
server = app.server


def process_file(contents, filename):
    read_functions = {".csv": pd.read_csv, ".xlsx": pd.read_excel}
    suffix = Path(filename).suffix

    content_type, content_string = contents.split(",")
    file_stream = io.BytesIO(base64.b64decode(content_string))

    if suffix in read_functions.keys():
        df = read_functions[suffix](file_stream)
        return df
    else:
        raise InvalidFileException(
            f"Ensure file is one of the following types: {list(read_functions.keys())}"
        )


app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    children=[
        dmc.Box(dmc.Center(dmc.Title("Portfolio Analysis", order=1)), p=30),
        dmc.Box(id="error-message", style={"color": "red"}),
        dmc.Box(
            dmc.Center(
                dcc.Upload(
                    id="upload-data",
                    children=dmc.Box(
                        ["Drag and Drop or ", html.A("Select a File")],
                        bd="2px dashed blue.6",
                        p=30,
                    ),
                    multiple=False,
                )
            )
        ),
        dmc.Box(
            id="content",
            children=[
                dmc.Box(
                    [
                        dmc.Title("Overall P&L:", order=3),
                        dmc.Title(id="final-pnl-display"),
                    ],
                    bd="1px solid #ccc",
                    p=20,
                    ta="center",
                    m="15px auto",
                ),
                dmc.Title("Portfolio Value over Time", order=2),
                dcc.Graph(id="time-series-chart"),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Title("Best Performers", order=2),
                                dmc.Box(id="winners"),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Title("Worst Performers", order=2),
                                html.Div(id="losers"),
                            ],
                            span=6,
                        ),
                    ]
                ),
            ],
            style={"display": "none"},
        ),
    ],
)


@app.callback(
    [
        Output("winners", "children"),
        Output("losers", "children"),
        Output("time-series-chart", "figure"),
        Output("final-pnl-display", "children"),
        Output("content", "style"),
        Output("error-message", "children"),
    ],
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
)
def refresh_data(contents, filename):
    if not filename:
        raise PreventUpdate()

    try:
        df = process_file(contents, filename)
        winners, losers, portfolio, portfolio_return, bad_tickers = run_pipeline(df)

        winners = dash_table.DataTable(data=winners)
        losers = dash_table.DataTable(data=losers)

        fig = px.line(
            portfolio,
            x="Date",
            y="PortfolioValue",
            labels={"Date": "Date", "PortfolioValue": "Portfolio Value"},
        )
        fig.update_traces(mode="lines+markers")

        portfolio_return = f"${portfolio_return:,.2f}"

        if bad_tickers:
            bad_tickers = f"Could not pull prices for: {bad_tickers}. These positions have been ignored."
        else:
            bad_tickers = ""

        return winners, losers, fig, portfolio_return, {"display": "block"}, bad_tickers

    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return {}, {}, {}, None, {"display": "none"}, error_message


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
