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
                        className="container mt-4 shadow-lg mb-4",
                        md=4,
                        sm=4,
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
                                                    {'label': 'Histogram (Dağılım)', 'value': 'hist'},
                                                ]
                                            ),
                                            dbc.Label('X Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='x-axis', placeholder='X Ekseni Seçiniz'),
                                            dbc.Label('Y Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='y-axis', placeholder="Y Ekseni Seçiniz"),
                                            dbc.Label('Gruplandır', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='color'),
                                            html.Hr()
                                        ]
                                    ),

                                    dcc.Tab(
                                        label="Histogram",
                                        children=[
                                            dbc.Label("Normal", style={"font-weight": "bold"}, className="mt-3"),
                                            dcc.Dropdown(
                                                id='histnorm',
                                                placeholder='Normal',
                                                className="mb-2",
                                                options=[
                                                    {'label': 'Yüzde', 'value': 'percent'},
                                                    {'label': 'Olasılık', 'value': 'probability'},
                                                ]
                                            ),

                                            dbc.Label("Histogram Fonksiyonu", style={"font-weight": "bold"}, className="mt-3"),
                                            dcc.Dropdown(
                                                id='histfunc',
                                                placeholder='Histogram Fonksiyonu',
                                                className="mb-2",
                                                options=[
                                                    {'label': 'Ortalama', 'value': 'avg'},
                                                    {'label': 'Toplam', 'value': 'sum'},
                                                    {'label': 'Count', 'value': 'count'},
                                                ]
                                            ),

                                            dbc.Label("Marjinal", style={"font-weight": "bold"},
                                                      className="mt-3"),
                                            dcc.Dropdown(
                                                id='marginal',
                                                placeholder='Marjinal Grafik',
                                                className="mb-2",
                                                options=[
                                                    {'label': 'Çizgi', 'value': 'rug'},
                                                    {'label': 'Box', 'value': 'box'},
                                                    {'label': 'violin', 'value': 'violin'},
                                                ]
                                            ),



                                            dcc.Checklist(
                                                id="text_auto",
                                                className="mt-3",
                                                options=[
                                                    {'label': 'Değerleri Göster', 'value': True},
                                                ],
                                                value=False
                                            ),

                                            html.Hr()
                                        ]
                                    ),

                                    dcc.Tab(
                                        label="Model",
                                        children=[
                                            dbc.Label("Model", style={"font-weight": "bold"}, className="mt-3"),
                                            dcc.Dropdown(
                                                id='model',
                                                placeholder='Model Seçiniz',
                                                className="mb-2",
                                                options=[
                                                    {'label': 'LinearRegresyon', 'value': 'linear'},
                                                    {'label': 'MultipleLinearRegresyon', 'value': 'mlinear'},
                                                ]
                                            ),

                                            dbc.Label("Bağımlı Değişken", style={"font-weight": "bold"},
                                                      className="mt-3"),
                                            dcc.Dropdown(
                                                id='depend',

                                                placeholder='Bağımlı Değişken',
                                                className="mb-2",

                                            ),

                                            dbc.Label("Bağımsız Değişken", style={"font-weight": "bold"},
                                                      className="mt-3"),

                                            dcc.Dropdown(
                                                id='independ',

                                                placeholder='Bağımsız Değişken',
                                                className="mb-2",

                                            ),

                                            html.Hr()
                                        ]
                                    ),

                                ]
                            )
                        ],
                    ),

                    dbc.Col(
                        className="container mt-4 shadow-lg mb-4",
                        md=8,
                        sm=8,
                        children=[
                            html.H4(["Veri Seti"], className="text-center mt-3"),
                            html.Hr(),
                            html.Div(id="data-table")
                        ],
                    ),

                ],
            ),

            dbc.Row(
                children=[
                    dbc.Col(
                        className="container mt-2 shadow-lg mb-4",
                        children=[
                            dbc.Tabs(
                                id="tabs",
                                className="pt-2",
                                children=[
                                    dcc.Tab(
                                        label="İstatistik",
                                        className="p-3",
                                        id="stats-table",
                                    ),

                                    dcc.Tab(
                                        label="Grafik",
                                        id="graph-tab",
                                        children=[dcc.Graph(id="graph-display")],
                                    ),

                                    dcc.Tab(
                                        label="Model",
                                        id="model-tab",
                                        children=[
                                            dcc.Graph(id="model-graph"),
                                            html.Hr(),
                                            html.Div(id="model-results"),
                                        ]
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

        df = None

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

        Output('depend', 'options'),
        Output('independ', 'options'),

        Input('data-info', 'data'),
        Input('data-filename', 'data'),
    )
    def table(store_data, filename):
        df = None

        if store_data is None:
            raise PreventUpdate

        if 'csv' in filename:

            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(store_data))

        elif 'xls' or "xlsx" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(store_data))

        file_info = [
            html.Hr(),
            html.Label("Dosya Adı"),
            html.H4(filename),
            html.Hr(),
        ]

        axis = [i for i in df.columns]

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

        return file_info, data_table, stats_table, axis, axis, axis, axis, axis

    @app.callback(
        Output("graph-display", "figure"),

        Input("data-info", "data"),
        Input("data-filename", "data"),
        Input("graph-type", "value"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
        Input("color", "value"),
        Input("histnorm", "value"),
        Input("text_auto", "value"),
        Input("histfunc", "value"),
        Input("marginal", "value"),

    )
    def graph_display(data, filename, graph_type, x_axis, y_axis, color, histnorm, text_auto, histfunc, marginal):


        if graph_type is None:
            raise PreventUpdate

        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(data))

        elif 'xls' or "xlsx" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(data))

        if graph_type == 'line':

            if x_axis and y_axis:
                fig = px.line(df, x=x_axis, y=y_axis, color=color)

            else:
                raise PreventUpdate

        elif graph_type == 'hist':
            fig = px.histogram(df, x=x_axis, y=y_axis, histnorm=histnorm, text_auto=bool(text_auto), color=color, histfunc=histfunc, marginal=marginal)

        return fig

    @app.callback(
        Output("model-graph", "figure"),
        Output("model-results", "children"),

        Input("data-info", "data"),
        Input("data-filename", "data"),

        Input("model", "value"),
        Input("depend", "value"),
        Input("independ", "value"),
    )
    def model(data, filename, model, depend, independ):

        global figure, df, results

        if model is None:
            raise PreventUpdate

        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(data))

        elif 'xls' or "xlsx" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(data))

        if model == 'linear':
            figure = px.scatter(df, x=depend, y=independ, trendline="ols")
            trendline_results = px.get_trendline_results(figure)
            results = trendline_results.px_fit_results.iloc[0].summary()

        return figure, html.Pre(children=results.as_text(), style={'whiteSpace': 'pre-wrap','background-color':'lightgray', 'text-align':'center'})


    return render(request, 'index.html')
