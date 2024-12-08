import dash
from dash import html, dash_table, Input, Output, dcc
import plotly.express as px
from processing import run_pipeline

app = dash.Dash(__name__)
server = app.server

inputs_folder = "./docker_inputs"

cols, data = [], []

app.layout = html.Div(
    [
        html.H1("Portfolio Analysis"),
        html.Button("Click to Analyse Portfolio", id="refresh-button", n_clicks=0),
        html.Div(id="error-message", style={"color": "red"}),
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
        html.H2("Portfolio Performance over Time"),
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
        Output("refresh-button", "children"),
    ],
    Input("refresh-button", "n_clicks"),
)
def refresh_data(n_clicks):
    try:
        cols, data, portfolio, portfolio_return, bad_tickers = run_pipeline(
            inputs_folder
        )

        fig = px.line(
            portfolio,
            x="Date",
            y="PnL",
            labels={"Date": "Date", "PnL": "Profit and Loss"},
        )
        fig.update_traces(mode="lines+markers")

        portfolio_return = f"${portfolio_return:,.2f}"

        if bad_tickers:
            bad_tickers = f"Could not pull prices for: {bad_tickers}. These positions have been ignored."
        else:
            bad_tickers = ""

        return cols, data, fig, portfolio_return, bad_tickers, "Refresh"

    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return [], [], {}, None, error_message, "Refresh"


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
