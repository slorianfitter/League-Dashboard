import dash
from dash import Dash, html, dcc, callback, Input, Output

app = Dash(__name__, use_pages=True)

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

content_style = {"flexGrow": 1,
                "padding": "16px",
                "minWidth": 0,
                "marginLeft": "20vw",
                "marginRight": "20vw",}

# Styles for buttons 
button_active = {"border-radius":"12px", 
                "fontSize":"1rem", 
                "padding":"0.5rem 1rem",
                "backgroundColor": "#c4c5e4", 
                "color": "white", 
                "width":"100%",
                "color": "black", 
                "border":"1px solid grey"}

button_inactive = {"border-radius":"12px",
                    "fontSize":"1rem", 
                    "padding":"0.5rem 1rem", 
                    "width":"100%", 
                    "backgroundColor": "white", 
                    "color": "black", 
                    "border":"1px solid grey"}


sidebar = html.Div(
    [
        html.H2("Navigation", style={"textAlign":"center"}),
        html.Hr(style={"border": "1px solid black"}),
        html.Div([
            html.A(html.Button("Home", id="btn-home"), href="/"), # this Button does nothing right now!
            html.A(html.Button("Team performance overview", id="btn-dashboard"), href="/dashboard")            
        ], style=sidebar_element_style)
    ], style=sidebar_style
)

content = html.Div(dash.page_container, style=content_style)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@callback(
    Output("btn-home", "style"),
    Output("btn-dashboard", "style"),
    Input("url", "pathname"),
)

def highlight_button_active(pathname):
    return (
        button_active if pathname == "/" else button_inactive,
        button_active if pathname == "/dashboard" else button_inactive,
    )


if __name__ == "__main__":
    app.run(debug=True)