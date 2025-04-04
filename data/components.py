import base64
import pandas as pd
import io
from dash import html
import dash_bootstrap_components as dbc
import numpy as np
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go


# ############ HELPER FUNCTIONS ############
def build_range(X, y, mesh_size=.02, margin=.25):
    """
    Create an x range and a y range for building meshgrid
    """
    x_min = X[:, 0].min() - margin
    x_max = X[:, 0].max() + margin
    y_min = X[:, 1].min() - margin
    y_max = X[:, 1].max() + margin

    xrange = np.arange(x_min, x_max, mesh_size)
    yrange = np.arange(y_min, y_max, mesh_size)

    return xrange, yrange

def build_figure(X, y, Z, xrange, yrange):

    X_train, X_test, y_train, y_test = train_test_split(
        X, y.astype(str), test_size=0.25, random_state=0)

    trace_specs = [
        [X_train, y_train, '0', 'Train', 'square'],
        [X_train, y_train, '1', 'Train', 'circle'],
        [X_test, y_test, '0', 'Test', 'square-dot'],
        [X_test, y_test, '1', 'Test', 'circle-dot']
    ]

    fig = go.Figure(data=[
        go.Scatter(
            x=X[y==label, 0], y=X[y==label, 1],
            name=f'{split}, y={label}',
            mode='markers', marker_symbol=marker
        )
        for X, y, label, split, marker in trace_specs
    ])
    fig.update_traces(
        marker_size=12, marker_line_width=1.5,
        marker_color="lightyellow"
    )

    fig.add_trace(
        go.Contour(
            x=xrange, y=yrange, z=Z,
            showscale=False, colorscale='RdBu',
            opacity=0.4, name='Score', hoverinfo='skip'
        )
    )

    return fig


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
