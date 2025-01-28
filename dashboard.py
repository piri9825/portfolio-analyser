import dash
from dash import html, dash_table, Input, Output, dcc
from dash.exceptions import PreventUpdate
import base64
import pandas as pd
from pathlib import Path
import io
from plistlib import InvalidFileException
import plotly.express as px
from processing import run_pipeline

app = dash.Dash(__name__)
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


cols, data = [], []

app.layout = html.Div(
    [
        html.H1("Portfolio Analysis"),
        html.Div(id="error-message", style={"color": "red"}),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select a File")]),
            style={
                "width": "50%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "auto",
            },
            multiple=False,
        ),
        html.Div(
            [html.H3("Overall P&L:"), html.H1(id="final-pnl-display")],
            style={
                "border": "1px solid #ccc",
                "padding": "20px",
                "borderRadius": "10px",
                "textAlign": "center",
                "width": "200px",
                "margin": "10px auto",
            },
        ),
        html.H2("Portfolio Value over Time"),
        dcc.Graph(id="time-series-chart"),
        html.H2("Best and Worst Performers"),
        dash_table.DataTable(
            id="data-table", columns=cols, data=data, style_table={"width": "50%"}
        ),
    ]
)


@app.callback(
    [
        Output("data-table", "columns"),
        Output("data-table", "data"),
        Output("time-series-chart", "figure"),
        Output("final-pnl-display", "children"),
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
        cols, data, portfolio, portfolio_return, bad_tickers = run_pipeline(df)

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

        return cols, data, fig, portfolio_return, bad_tickers

    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return [], [], {}, None, error_message


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
