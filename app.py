import dash
from dash import Dash, html, dcc, callback, Input, Output,State, MATCH, ctx, ALL
import sqlalchemy
import pandas as pd

app = Dash(__name__, use_pages=True)

engine = sqlalchemy.create_engine(
    "postgresql+psycopg2://postgres:sohn2003@localhost:5432/league"
)

df = pd.read_sql_table("match_data_end", engine)

names = df["riotId_name"] + df["riotId_tag"].apply(lambda x: f" #{x}")


sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20vw",
    "backgroundColor": "#a2bdde",
    "border": "1px solid grey",
}

sidebar_element_style = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "0.2vw",
    "padding": "0.2vw",
    "marginTop": "0.2vw",
    "marginBottom": "0.2vw",
    "marginLeft": "0.5vw",
}

content_style = {
    "flexGrow": 1,
    "padding": "16px",
    "minWidth": 0,
    "marginLeft": "20vw",
    "marginRight": "20vw",
    "bottom": 0,
    "top": 0,
    "right": 0,
    "left": 0,
    "position": "fixed"
}

# Styles for buttons
button_active = {
    "border-radius": "12px",
    "fontSize": "1rem",
    "padding": "0.5rem 1rem",
    "backgroundColor": "#c4c5e4",
    "color": "black",
    "width": "100%",
    "border": "1px solid grey"
}

button_inactive = {
    "border-radius": "12px",
    "fontSize": "1rem",
    "padding": "0.5rem 1rem",
    "width": "100%",
    "backgroundColor": "white",
    "color": "black",
    "border": "1px solid grey"
}


sidebar_left = html.Div(
    [
        html.H2(
            "Navigation",
            style={"textAlign": "center"}
        ),

        html.Hr(
            style={"border": "1px solid black"}
        ),

        html.Div(
            [
                html.A(
                    html.Button(
                        "Home",
                        id="btn-home"
                    ),
                    href="/"
                ),
                html.A(
                    html.Button(
                        "Game overview",
                        id="btn-dashboard"
                    ),
                    href="/dashboard"
                ),
                html.A(
                    html.Button(
                        "Team performance charts",
                        id="btn-team-stats"
                    ),
                    href="/team_stats_overview"
                ),
            ],
            style=sidebar_element_style
        )
    ],
    style=sidebar_style
)


#### Right sidebar

sidebar_right = html.Div(
    [
        html.H2(
            "Filters",
            style={"textAlign": "center"}
        ),
        html.Hr(
            style={"border": "1px solid black"}
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {
                            "label": str(m),
                            "value": m
                        }
                        for m in names.unique()
                    ],
                    id="dropdown-names",
                    placeholder="Spieler wählen",
                    persistence=True,
                    persistence_type="session",
                ),
            ],
            style=sidebar_element_style
        ),
        html.Hr(
            style={"border": "1px solid black"}
        ),
        html.Div(
            id="dropdown-matches-container",
            style={
                "overflow": "auto",
                }
        )
    ],

    style={
        **sidebar_style,
        "right": 0,
        "left": "auto"
    }
)

content = html.Div(
    dash.page_container,
    style=content_style
)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dcc.Store(
            id="stored-df",
            storage_type="session"
        ),
        dcc.Store(id="selected-match-id", storage_type="session"),
        sidebar_left,
        content,
        sidebar_right,
    ]
)


### Callbacks


# Highlight the active button

@callback(
    Output("btn-home", "style"),
    Output("btn-dashboard", "style"),
    Output("btn-team-stats", "style"),
    Input("url", "pathname"),
)
def highlight_button_active(pathname):

    return (
        button_active if pathname == "/" else button_inactive,

        button_active if pathname == "/dashboard" else button_inactive,

        button_active if pathname == "/team_stats_overview" else button_inactive,
    )


### Generate match boxes


@callback(
    Output("dropdown-matches-container", "children"),
    Input("dropdown-names", "value"),
    Input("selected-match-id", "data"),
    Input("url", "pathname"),
)
def generate_matches(player, selected_match_id, pathname):

    if not player:
        return []

    full_name = (df["riotId_name"]+ df["riotId_tag"].apply(lambda x: f" #{x}"))

    matches = df.loc[full_name == player]

    if matches.empty:
        return html.P("No matches found for this player.")

    match_boxes = []

    for i, match in matches.iterrows():

        match_id = str(match["match_id"])

        background_color = ( "#ab20c4" if match_id == str(selected_match_id) else "white")

        match_box = html.Button(
            [
                html.Div(
                    f"{match['champ']} - {match['lane']} - win = {match['win']} - {match['game_duration_in_seconds']/60:.2f} min",
                ),
                html.Div(
                    f"KDA: "
                    f"{match['kills']}/"
                    f"{match['deaths']}/"
                    f"{match['assists']}"
                ),
            ],
            id={
                "type": "match-box",
                "match_id": match_id
            },
            n_clicks=0,

            style={
                "width": "100%",
                "padding": "10px",
                "marginBottom": "5px",
                "borderRadius": "10px",
                "border": "1px solid grey",
                "backgroundColor": background_color,
                "cursor": "pointer",
                "textAlign": "center",
            }
        )

        match_boxes.append(match_box)

    return match_boxes

### Store selected match


#data
@callback(
    Output("stored-df","data"),    
    Input({"type": "match-box","match_id": MATCH},"n_clicks"),
    prevent_initial_call=True,
)
def update_stored_data(n_clicks):

    if not n_clicks:
        return dash.no_update

    match_id = ctx.triggered_id["match_id"]
    match_rows = df[
        df["match_id"].astype(str) == str(match_id)
        ]
    return match_rows.to_dict("records")




##### highlight the button - This Callback is required to change the buttons, else we would stick to only one all the time
@callback(
    Output("selected-match-id", "data"), # this is the input of boxes 
    Input({"type": "match-box", "match_id": MATCH},"n_clicks"),
    prevent_initial_call=True,
)
def select_match(n_clicks):

    if not n_clicks:
        return dash.no_update

    return ctx.triggered_id["match_id"]


if __name__ == "__main__":
    app.run(debug=True)