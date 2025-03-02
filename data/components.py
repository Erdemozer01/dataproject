import base64
import pandas as pd
import io
from dash import html
import dash_bootstrap_components as dbc

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"


def parse_contents(contents, filename, date):
    content_type, content_string = str(contents).split(',')

    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


navbar = dbc.Navbar(
    color="dark",
    dark=True,
    fixed=True,
    sticky="top",
    className="rounded-2 mt-2",
    children=dbc.Container(

        children=[
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand("Data Science", className="ms-2")),
                    ],
                    align=True,
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
        ],

    ),

)
