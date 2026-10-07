import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import sqlalchemy

dash.register_page(__name__, path="/", name="Home")

header_style = {"textAlign": "center", "marginBottom": "20px"}
header = html.Div(html.H1("Welcome to the Home Page"), style=header_style)
main_layout = html.Div(id="selected-profile")

layout = html.Div([header, main_layout])


@callback(
    Output("selected-profile", "children"),
    Input("dropdown-names", "value"),
)
def show_selected_name(value):
    print(value)   

    if not value:
        return "Kein Spieler ausgewählt."

    return f"Player: {value}"