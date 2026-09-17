from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import sqlalchemy

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/league")
df = pd.read_sql_table("match_data_end", engine)
items = pd.read_sql_table("Items", engine)
items_image_map = dict(zip(items["item_id"].astype(int), items["icon_link"]))

champion = pd.read_sql_table("Champions", engine)
champion_image_map = dict(zip(champion["champ_id"], champion["icon_link"]))

app = Dash()

box_style = {
    "border": "1px solid #ccc",
    "borderRadius": "8px",
    "padding": "10px",
    "backgroundColor": "white",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
    "textAlign": "center"
}

outer_style = {
    "border": "2px solid #333",
    "flex": "1"          
}

app.layout = html.Div([

    html.H1("League Match Dashboard", style={"textAlign": "center"}),

    dcc.Dropdown(
        options=[{"label": str(m), "value": m} for m in df.match_id.unique()],
        id='demo-dropdown',
        placeholder="Select a match"
    ),

    
    html.Div([
                
        html.Div([
            html.H2("Blue Side"),
            html.Div(id="blue-side-boxes", style={
                "display": "flex",
                "flexDirection": "column",
                "gap": "10px"
            })
        ], style={**outer_style, "backgroundColor": "#f0f0ff"}),

        
        html.Div([
            html.H2("Red Side"),
            html.Div(id="red-side-boxes", style={
                "display": "flex",
                "flexDirection": "column",
                "gap": "10px"
            })
        ], style={**outer_style, "backgroundColor": "#fff0f0"}),


    ], style={
        "display": "flex",
        "flexDirection": "row",
        "gap": "20px",
        "maxWidth": "1000px",
        "margin": "20px auto"
    })

])


@callback(
    Output('red-side-boxes', 'children'),
    Output('blue-side-boxes', 'children'),
    Input('demo-dropdown', 'value')
)
def update_sides(value):
    if value is None:
        empty = [html.Div("—", style=box_style) for _ in range(5)]
        return empty, empty

    match_rows = df[df['match_id'] == value]

    red_rows = match_rows[match_rows['participantId'] > 5]
    blue_rows = match_rows[match_rows['participantId'] <= 5]

    red_boxes = [
        html.Div([
            html.H5(f"{row.riotId_name} #{row.riotId_tag}"),

            html.Div([

                html.Div(
                    [
                        html.Div(f"K/D/A: {row.kills}/{row.deaths}/{row.assists}", style=box_style),

                        html.Div([
                            
                                    html.Img(
                                        src=items_image_map.get(getattr(row, f'item_{i}'), ""),
                                        style={"width": "32px", "height": "32px"}) for i in range(0, 6)
                                     
                    
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "row",
                                "gap": "5px"
                            }
                        )
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "5px"
                    }
                ),
                html.Img(
                    src= champion_image_map.get(row.champ),
                    style=box_style
                )
            ], style={
                "display": "flex",
                "flexDirection": "row",
                "gap": "5px"
            })

        ], style=box_style)
        for row in red_rows.itertuples()
    ]



    # blue boxes are straight copy paste from red boxes, just with an adaption that the champ icon will be listed left not right
    blue_boxes = [
        html.Div([
            html.H5(f"{row.riotId_name} #{row.riotId_tag}"),

            html.Div([

                html.Img(
                    src= champion_image_map.get(row.champ),
                    style=box_style
                ),

                html.Div([
                    html.Div(
                        f"K/D/A: {row.kills}/{row.deaths}/{row.assists}",
                        style=box_style
                    ),

                    html.Div([
                        html.Img(
                            src=items_image_map.get(
                                getattr(row, f'item_{i}'),
                                ""
                            ),
                            style={
                                "width": "32px",
                                "height": "32px"
                            }
                        )
                        for i in range(0, 6)
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "row",
                        "gap": "5px"
                    })
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "5px"
                })

            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "gap": "5px"
            })

        ], style=box_style)

        for row in blue_rows.itertuples()
    ]

    return red_boxes, blue_boxes


if __name__ == '__main__':
    app.run(debug=True)


    