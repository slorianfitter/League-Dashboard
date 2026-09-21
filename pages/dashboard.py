import dash
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import sqlalchemy


dash.register_page(__name__)


#### Data import ####

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:sohn2003@localhost:5432/league")

df = pd.read_sql_table("match_data_end", engine)
items = pd.read_sql_table("Items", engine)
champion = pd.read_sql_table("Champions", engine)

#### Data dictionaries to obtain the icon links ####
## Key = unique name / unique Id number ; value = Link to image (DataDragon)

champion_image_map = dict(zip(champion["champ_id"], champion["icon_link"]))
items_image_map = dict(zip(items["item_id"].astype(int), items["icon_link"]))



#### Layout ####
## 2 Columns - 1 for each Team, sorted by participantId 
# -> 1 = Top, 2 = Jgl, 3 = Mid, 4 = Adc, 5 = Sup -> 6 = Top , ....
#  in each row we have one Participant with his stats. 
# -> Name, Gold, Cs, KDA, Items bought, etc...
## It should only give an overview of what happened in the Game
# Deeper analysis of the stat will appear in different pages

layout = html.Div([
    html.H1("League Match Dashboard", style={"textAlign": "center"}),
    dcc.Dropdown(
        options=[
            {"label": str(m), "value": m} for m in df.match_id.unique()
            ],
        id='demo-dropdown',
        placeholder="Select a Match"),
    html.Div([        
        html.Div([
            html.H2("Blue Side"),
            html.Div(id="blue-side-boxes", 
                    style={
                    "display": "flex",
                    "flexDirection": "column"})
                ]),

        html.Div([
            html.H2("Red Side"),
            html.Div(id="red-side-boxes", 
                     style={
                    "display": "flex",
                    "flexDirection": "column"})
                ]),

            ], style={
        "display": "flex",
        "flexDirection": "row"})
    ])


@callback(
    Output('red-side-boxes', 'children'),
    Output('blue-side-boxes', 'children'),
    Input('demo-dropdown', 'value')
)
def update_sides(value):
    if value is None:
        empty = [html.Div("—") for _ in range(5)]
        return empty, empty

    match_rows = df[df['match_id'] == value]

    red_rows = match_rows[match_rows['participantId'] > 5]
    blue_rows = match_rows[match_rows['participantId'] <= 5]

    blue_boxes = [
                html.Div([
                    html.H5(f"{row.riotId_name} #{row.riotId_tag}"),
                    html.Div([
    
                        html.Div([
                            html.Img(
                            src= champion_image_map.get(row.champ),
                            style={
                                            "width": "64px",
                                            "height": "64px"
                                        }
                        ),
                            html.Div([
                                html.Div(
                                    f"K/D/A: {row.kills}/{row.deaths}/{row.assists}"
                            
                                ),
                                    html.Div(f"Gold: {row.gold}"),
                                    html.Div(f"Cs: {row.total_cs + row.jgl_camps}")
                                    ],
                                        style={"display": "flex",
                                                "flexDirection": "column",
                                                "gap":"10px"}),
    
                        html.Div([
                            html.Div([
                                html.Div([
                                html.Img(
                                    src=items_image_map.get(getattr(row, f'item_{i}'),""),
                                    style={
                                        "width": "32px",
                                        "height": "32px"
                                    }
                                )
                                for i in range(0, 3)
                                    ],
                                    style={
                                            "display": "flex",
                                            "flexDirection": "row",
                            }),
                                html.Div([
                                    html.Img(
                                        src=items_image_map.get(getattr(row, f'item_{i}'),""),
                                        style={
                                            "width": "32px",
                                            "height": "32px"
                                        }
                                    )
                                    for i in range(3, 6)
                                        ],
                                        style={
                                                "display": "flex",
                                                "flexDirection": "row",
                                })
                            ]),
                            html.Img(
                                    src=items_image_map.get(row.vision_item),
                                    style={
                                        "width": "32px",
                                        "height": "32px"
                                    })
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "row",
                        })
    
                            ],
                        style={
                            "display": "flex",
                            "flexDirection": "row"
                        }),                        
    
                    ], style={"flexDirection":"row"})            
    
                ], style={"flexDirection":"column"})                  
    
            for row in blue_rows.itertuples()
    ]
    red_boxes = [
                    html.Div([
                        html.H5(f"{row.riotId_name} #{row.riotId_tag}"),
                        html.Div([
        
                            html.Div([
                                html.Img(
                                src= champion_image_map.get(row.champ),
                                style={
                                                "width": "64px",
                                                "height": "64px"
                                            }
                            ),
                                html.Div([
                                    html.Div(
                                        f"K/D/A: {row.kills}/{row.deaths}/{row.assists}"
                                
                                    ),
                                        html.Div(f"Gold: {row.gold}"),
                                        html.Div(f"Cs: {row.total_cs + row.jgl_camps}")
                                        ],
                                            style={"display": "flex",
                                                    "flexDirection": "column",
                                                    "gap":"10px"}),
        
                            html.Div([
                                html.Div([
                                    html.Div([
                                    html.Img(
                                        src=items_image_map.get(getattr(row, f'item_{i}'),""),
                                        style={
                                            "width": "32px",
                                            "height": "32px"
                                        }
                                    )
                                    for i in range(0, 3)
                                        ],
                                        style={
                                                "display": "flex",
                                                "flexDirection": "row",
                                }),
                                    html.Div([
                                        html.Img(
                                            src=items_image_map.get(getattr(row, f'item_{i}'),""),
                                            style={
                                                "width": "32px",
                                                "height": "32px"
                                            }
                                        )
                                        for i in range(3, 6)
                                            ],
                                            style={
                                                    "display": "flex",
                                                    "flexDirection": "row",
                                    })
                                ]),
                                html.Img(
                                        src=items_image_map.get(row.vision_item),
                                        style={
                                            "width": "32px",
                                            "height": "32px"
                                        })
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "row",
                            })
        
                                ],
                            style={
                                "display": "flex",
                                "flexDirection": "row"
                            }),                        
        
                        ], style={"flexDirection":"row"})            
        
                    ], style={"flexDirection":"column"})                  
        
                for row in red_rows.itertuples()
        ]
    

    # blue boxes are straight copy paste from red boxes, just with an adaption that the champ icon will be listed left not right
    
    
    return red_boxes, blue_boxes



