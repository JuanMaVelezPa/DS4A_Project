import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
html.H1("Furni Portfolio manager", style={'text-align': 'center'}),
html.Div([html.Button("Download csv", id="btn"), dcc.Download(id="download")]),
html.Br(),
])

@app.callback(Output("download", "data"), [Input("btn", "n_clicks")],prevent_initial_call=True,)
def generate_csv(n_nlicks):
    #return dcc.send_data_frame(df.to_csv, filename="prediction.csv")
    return dcc.send_data_frame(pd.DataFrame().to_csv, filename="prediction.csv")

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)