import base64
import datetime

from dash.exceptions import PreventUpdate
from django.shortcuts import render
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash_table, State
from data.components import parse_contents
import pandas as pd
import io
import plotly.express as px



# Create your views here.


def index(request):

    app = DjangoDash(name='index', external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        md=4,
                        id="tab-panel",
                        className="mt-4 shadow-lg",
                        children=[
                            dcc.Tabs(
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

                                            html.Div(id='data-info', className="mt-4"),
                                            dcc.Store(id="store"),
                                            dcc.Store(id="stats-data"),

                                        ]
                                    ),

                                    dcc.Tab(
                                        label="Grafik",
                                        children=[
                                            dbc.Label('X Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='x-axis',),
                                            dbc.Label('Y Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='y-axis', )
                                        ]
                                    ),

                                ]
                            )
                        ]
                    ),

                    dbc.Col(

                        md=7,

                        sm=7,

                        className="mt-4 shadow-lg container",

                        children=[
                            html.H4(["Veri Seti"], className="text-center mt-3"),
                            html.Hr(),
                            dash_table.DataTable(
                                id='table',
                                page_size=10,
                                style_table={'overflowX': 'auto'},
                            )
                        ]
                    ),

                ],
            ),

            dbc.Row(
                children=[
                   dbc.Col(
                       lg=11,
                       md=11,
                       className="container mt-4 shadow-lg mb-4",
                       children=[
                           dbc.Tabs(
                               id="tabs",
                               className="pt-2",
                               children=[
                                   dbc.Tab(
                                       label="İstatistik",
                                       className="p-3",
                                       id="stats-tab",
                                       children=[]
                                   ),

                                   dbc.Tab(
                                       label="Grafikler",
                                       className="p-3",
                                       id="graph-tab",
                                       children=[
                                           dbc.Label("Grafikler", className="p-3"),
                                           dcc.Dropdown(id='graph-option', placeholder='Grafik Seçiniz', options=['line'],),
                                           dcc.Graph(id='graph-plot'),
                                       ]
                                   )
                               ]
                           ),

                       ]
                   )
                ],
            ),


        ], className="container"
    )

    @app.callback(
        Output("table", "data"),
        Output("table", "columns"),
        Output('store', 'data'),
        Output('data-info', 'children'),
        Output('x-axis', 'options'),
        Output('y-axis', 'options'),

        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    )
    def data(contents, filename, date):

        global df

        if contents is None:
            raise PreventUpdate

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
            return html.Div([
                'There was an error processing this file.'
            ])

        table_data = df.to_dict('records')

        columns = [{"name": i, "id": i} for i in df.columns]

        x_axis = [i for i in df.columns]

        y_axis = [i for i in df.columns]

        store_data = df.to_json(date_format='iso', orient='split')

        info = [
            html.Hr(),
            html.Label("Dosya Adı"),
            html.H4(filename),
            html.Hr(),
            html.Label("Değiştirme tarihi"),
            html.P(datetime.datetime.fromtimestamp(date).date()),
        ]

        return table_data, columns, store_data, info, x_axis, y_axis

    @app.callback(
        Output('stats-tab', 'children'),

        Input('store', 'data'),

    )
    def output_from_store(stored_data):

        if stored_data is None:
            raise PreventUpdate

        df = pd.read_json(stored_data, orient='split')

        df = df.describe()

        df.reset_index(inplace=True)

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'overflowX': 'auto'},
            page_size=10
        )

        return table

    @app.callback(
        Output('graph-plot', 'figure'),

        Input('store', 'data'),

        Input('graph-option', 'value'),
        Input('x-axis', 'value'),
        Input('y-axis', 'value'),
    )
    def update_graph(data_store, graph, x_axis, y_axis):

        if data is None:
            raise PreventUpdate

        data_frame = pd.read_json(data_store, orient='split')

        if graph == 'line':

            fig = px.line(data_frame, x=x_axis, y=y_axis, title='Life expectancy in Canada')

            return fig

        else:

            raise PreventUpdate

    return render(request, 'index.html')
