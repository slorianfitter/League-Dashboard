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



#### Styles ####
column_style = {
    "flex": 1, "minWidth": 0,
    "display": "flex", "flexDirection": "column", "gap": "10px",
}

box_style = {                       
    "border": "1px solid #ccc",
    "padding": "10px",
}

player_row_style = {                
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": "space-between",
    "alignItems": "center",
    "gap": "10px",
}

item_grid_style = {"display": "flex", 
                   "flexDirection": "row", 
                   "gap": "0.5px", 
                   "padding": "0.5px", 
                   "alignItems": "center", 
                   "justifyContent": "center"}

text_style = { "fontSize": "14px", 
              "lineHeight": "1.2"}

#### helper functions to create the layout for each player ####

def item_img(item_id):
    return html.Img(src=items_image_map.get(item_id, ""),
                    style={"width": "32px", "height": "32px"})


def player_box(row, icon_left=True):
    return html.Div([
        html.H5(f"{row.riotId_name} #{row.riotId_tag}", style=text_style),
        html.Div([
            html.Img(src=champion_image_map.get(row.champ),
                     style={"width": "64px", "height": "64px"}),

            html.Div([
                html.Div(f"K/D/A: {row.kills}/{row.deaths}/{row.assists}"),
                html.Div(f"Gold: {row.gold}"),
                html.Div(f"Cs: {row.total_cs + row.jgl_camps}"),
            ], style=text_style),

            html.Div([
                html.Div([
                    html.Div([item_img(getattr(row, f"item_{i}")) for i in range(0, 3)],
                             style=item_grid_style),
                    html.Div([item_img(getattr(row, f"item_{i}")) for i in range(3, 6)],
                             style=item_grid_style),
                ]),
                item_img(row.vision_item),
            ], style=item_grid_style),
        ], style={**player_row_style,
                  "flexDirection": "row" if icon_left else "row-reverse"}),
    ], style=box_style)


#### Layout ####
## 2 Columns - 1 for each Team, sorted by participantId 
# -> 1 = Top, 2 = Jgl, 3 = Mid, 4 = Adc, 5 = Sup -> 6 = Top , ....
#  in each row we have one Participant with his stats. 
# -> Name, Gold, Cs, KDA, Items bought, etc...
## It should only give an overview of what happened in the Game
# Deeper analysis of the stat will appear in different pages

header = html.Div([
    html.Div("End of game result", style={"textAlign":"center"})
    ])

drop_down_bar = html.Div([
    dcc.Dropdown(
        options=[
            {"label": str(m), "value": m} for m in df.match_id.unique()
            ],
        id='demo-dropdown',
        placeholder="Select a Match")
    ])

main_layout_style = {"width": "100%",
                    "display": "flex"}
main_layout = html.Div([
    html.Div([
        html.Div(id="blue-side-boxes", style=column_style),
        html.Div(id="red-side-boxes", style=column_style)
    ], style={"display": "flex", "flexDirection": "row", "width": "100%", "gap": "20px"})
], style=main_layout_style)


layout=html.Div([header, drop_down_bar, main_layout], style={"display": "flex", "flexDirection": "column", "gap": "20px", "width": "100%"})



@callback(
    Output('red-side-boxes', 'children'),
    Output('blue-side-boxes', 'children'),
    Input('demo-dropdown', 'value')
)

def update_sides(value):
    match_rows = df[df['match_id'] == value]

    red_rows = match_rows[match_rows['participantId'] > 5]
    blue_rows = match_rows[match_rows['participantId'] <= 5]

    blue_boxes = [player_box(row, icon_left=True) for row in blue_rows.itertuples()]
    red_boxes = [player_box(row, icon_left=False) for row in red_rows.itertuples()]

    return red_boxes, blue_boxes