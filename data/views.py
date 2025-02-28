from django.shortcuts import render
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc

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
                                            ]
                                        ),

                                        dcc.Tab(
                                            label="Tab 2",
                                            children=[

                                            ]
                                        ),

                                    ]
                                )
                            ]
                        ),

                        dbc.Col(
                            md=8,
                            id="table",
                            className="mt-4 p-2 shadow-lg",
                            children=[

                            ]
                        ),
                    ],
                ),

                html.Div(id="graph", ),

            ], className="container"
        )

    @app.callback(
        Output("table", "figure"),
        Input("upload-data", "contents"),
    )
    def data(content, filename):
        pass

    return render(request, 'index.html')