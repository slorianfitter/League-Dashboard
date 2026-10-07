import io
import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path="/team_stats_overview", name="Team Stats Overview")

header = html.Div(html.H1(""))

main_layout = html.Div()


layout = html.Div([
    header,
    main_layout,

    html.Div(id="data-info"),
])


@callback(
    Output("data-info", "children"),
    Input("stored-df", "data")
)
def load_stored_data(data):
    if not data:
        return html.P("No match selected yet — pick one on the main page first.")

    df = pd.DataFrame(data) 

    fig = px.bar(df, x="champ", y="gold", color="lane", title="Gold earned by each champion")
    return html.Div([
        dcc.Graph(figure=fig)
    ])