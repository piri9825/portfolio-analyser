import dash
from dash import html, dash_table, Input, Output
from processing import load_data

app = dash.Dash(__name__)
server = app.server

inputs_folder = "./docker_inputs"

cols, data = [], []

app.layout = html.Div(
    [
        html.H1("Portfolio Analysis"),
        html.Button("Refresh Data", id="refresh-button", n_clicks=0),
        dash_table.DataTable(
            id="data-table", columns=cols, data=data, style_table={"width": "75%"}
        ),
        html.Div(id="error-message", style={"color": "red"}),
    ]
)

try:
    cols, data = load_data(inputs_folder)
    error_message = ""
except ValueError as e:
    error_message = f"Error: {str(e)}"


# Callback to refresh the data
@app.callback(
    [
        Output("data-table", "columns"),
        Output("data-table", "data"),
        Output("error-message", "children"),
    ],
    Input("refresh-button", "n_clicks"),
)
def refresh_data(n_clicks):
    try:
        cols, data = load_data(inputs_folder)
        return cols, data, ""
    except ValueError as e:
        error_message = f"Error: {str(e)}"
        return [], [], error_message


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
