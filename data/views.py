import base64
import datetime

from dash.exceptions import PreventUpdate
from django.shortcuts import render
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash_table, State
from data.components import navbar
import pandas as pd
import io
import plotly.express as px


# Create your views here.


def index(request):
    app = DjangoDash(
        name='index',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        update_title="Güncelleniyor...",
    )

    app.layout = html.Div(
        className="container",

        children=[
            dbc.Row(
                children=[
                    navbar,
                    dbc.Col(
                        md=4,
                        sm=4,
                        children=[
                            dbc.Tabs(
                                id="tabs",
                                className="pt-2",
                                children=[

                                    dcc.Tab(
                                        label="Veri",

                                        id="data",

                                        children=[

                                            html.Label(['Dosya Seçiniz'], className="mt-3",
                                                       style={"font-weight": "bold"}),

                                            dcc.Upload(
                                                id='upload-data',
                                                children=html.Div([
                                                    'Sürükle yada Bırak ',
                                                    html.A(['Dosya Seç'], style={'font-weight': 'bold'}),
                                                ]),
                                                style={
                                                    'width': '100%',
                                                    'height': '60px',
                                                    'lineHeight': '60px',
                                                    'borderWidth': '1px',
                                                    'borderStyle': 'dashed',
                                                    'borderRadius': '5px',
                                                    'textAlign': 'center',
                                                    'margin': 'auto',
                                                    'margin-top': '2%',
                                                    'margin-bottom': '2%',
                                                },
                                                # Allow multiple files to be uploaded
                                                multiple=False
                                            ),

                                            dcc.Store(id="data-info"),
                                            dcc.Store(id="data-filename"),
                                            html.Div(id='file-info', className="mt-4"),

                                        ]
                                    ),

                                    dcc.Tab(
                                        label="Grafik",
                                        children=[
                                            dbc.Label("Grafik", style={"font-weight": "bold"}, className="mt-3"),
                                            dcc.Dropdown(
                                                id='graph-type',
                                                placeholder='Grafik Seçiniz',
                                                options=[
                                                    {'label': 'Line', 'value': 'line'},
                                                ]
                                            ),
                                            dbc.Label('X Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='x-axis'),
                                            dbc.Label('Y Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='y-axis'),
                                            dbc.Label('Gruplandır', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='color'),
                                            html.Hr()
                                        ]
                                    ),

                                ]
                            )
                        ],
                        className="container mt-4 shadow-lg mb-4",
                    ),

                    dbc.Col(
                        md=8,
                        sm=8,
                        children=[
                            html.H4(["Veri Seti"], className="text-center mt-3"),
                            html.Hr(),
                            html.Div(id="data-table")
                        ],
                        className="container mt-4 shadow-lg mb-4",
                    ),

                ],
            ),

            dbc.Row(
                children=[
                    dbc.Col(

                        className="container mt-4 shadow-lg mb-4",
                        children=[
                            dbc.Tabs(
                                id="tabs",
                                className="pt-2",
                                children=[
                                    dcc.Tab(
                                        label="İstatistik",
                                        className="p-3",
                                        id="stats-table",
                                        children=[

                                        ]
                                    ),

                                    dcc.Tab(
                                        label="Grafikler",
                                        className="p-3",
                                        id="graph-tab",
                                    )
                                ]
                            ),

                        ]
                    )
                ],
            ),

        ],

    )

    @app.callback(
        Output('data-info', 'data'),
        Output('data-filename', 'data'),

        Input("upload-data", "contents"),
        State("upload-data", "filename"),
    )
    def read_data(contents, filename):

        global df

        if contents is None:
            raise PreventUpdate

        content_type, content_string = str(contents).split(',')

        decoded = base64.b64decode(content_string).decode('utf-8')

        return decoded, filename

    @app.callback(
        Output("file-info", "children"),
        Output('data-table', 'children'),
        Output('stats-table', 'children'),
        Output('x-axis', 'options'),
        Output('y-axis', 'options'),
        Output('color', 'options'),

        Input('data-info', 'data'),
        Input('data-filename', 'data'),
    )
    def table(store_data, filename):
        global df

        if store_data is None:
            raise PreventUpdate

        if 'csv' in filename:

            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(store_data))

        elif 'xls' in filename:

            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(store_data))

        file_info = [
            html.Hr(),
            html.Label("Dosya Adı"),
            html.H4(filename),
            html.Hr(),
        ]

        x_axis = [i for i in df.columns]
        y_axis = [i for i in df.columns]
        color = [i for i in df.columns]

        data_table = [dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
        )]

        df = df.describe()
        df.reset_index(inplace=True)

        stats_table = [dash_table.DataTable(
            id='stats-table',
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={'overflowX': 'auto'},
            page_size=10
        )]

        return file_info, data_table, stats_table, x_axis, y_axis, color

    @app.callback(
        Output("graph-tab", "children"),

        Input("data-info", "data"),
        Input("data-filename", "data"),
        Input("graph-type", "value"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("color", "value"),
    )
    def graph_display(data, filename, graph_type, x_axis, y_axis, color):
        global df, fig, graph

        if graph_type is None:
            raise PreventUpdate

        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(data))

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(data))

        if graph_type == 'line':

            if x_axis and y_axis:
                fig = px.line(df, x=x_axis, y=y_axis)
                if color is not None:
                    fig = px.line(df, x=x_axis, y=y_axis, color=color)
            else:
                raise PreventUpdate

        return dcc.Graph(figure=fig)

    return render(request, 'index.html')
