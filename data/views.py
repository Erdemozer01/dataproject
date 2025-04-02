import base64
import io

from dash.exceptions import PreventUpdate
from django.shortcuts import render
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash import Input, Output, html, dcc, dash_table, State
from sklearn import preprocessing
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from data.components import navbar, build_range, build_figure
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.formula.api as sm

import statsmodels.api as stm
from sklearn.cluster import KMeans
import plotly.graph_objs as go


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
                                                multiple=False,

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
                                                    {'label': 'Box', 'value': 'box'},
                                                    {'label': 'Bar', 'value': 'bar'},
                                                    {'label': 'Heatmap', 'value': 'heatmap'},
                                                    {'label': 'Koorelasyon Matrix', 'value': 'corr_heatmap'},
                                                ]
                                            ),
                                            dbc.Label('X Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='x-axis', placeholder='X Ekseni Seçiniz'),
                                            dbc.Label('Y Ekseni', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='y-axis', placeholder="Y Ekseni Seçiniz"),
                                            dbc.Label('Gruplandır', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='color'),
                                            dbc.Label('Renklendirme', className="mt-3", style={"font-weight": "bold"}),
                                            dcc.Dropdown(id='colorscales', options=px.colors.named_colorscales(), value='viridis'),
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

                                            dbc.Label("Histogram Fonksiyonu", style={"font-weight": "bold"},
                                                      className="mt-3"),
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
                                                    {'label': 'K-means clustering', 'value': 'kmc'},
                                                    {'label': 'K-Nearest Neighbors', 'value': 'knn'},
                                                ]
                                            ),

                                            dbc.Label("Bağımsız Değişken (y)", style={"font-weight": "bold"},
                                                      className="mt-3"),
                                            dcc.Dropdown(
                                                id='independ',

                                                placeholder='Bağımlı Değişken',
                                                className="mb-2",
                                            ),

                                            dbc.Label("Bağımlı Değişken (x)", style={"font-weight": "bold"},
                                                      className="mt-3"),

                                            dcc.Dropdown(
                                                id='depend',
                                                multi=True,
                                                placeholder='Bağımsız Değişken',
                                                className="mb-2",
                                            ),

                                            dbc.Label("Kümeleme Sayısı", style={"font-weight": "bold"},
                                                      className="mt-3"),

                                            dbc.Input(id="cluster-count", type="number", value=3),

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
                            dcc.Tabs(
                                [
                                    dcc.Tab(
                                        label="Veri seti",
                                        id="data-table",
                                    ),

                                    dcc.Tab(
                                        label="Tahmin",
                                        id="data-predict",
                                    ),

                                ]
                            )
                        ],
                    ),

                ],
            ),

            dbc.Row(
                children=[

                    dbc.Col(
                        className="container mt-2 shadow-lg mb-4",
                        children=[
                            dcc.Tabs(
                                id="tabs",
                                className="pt-2 mb-2",
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
                                            html.Pre(
                                                id="model-results",
                                                style={'whiteSpace': 'pre-wrap', 'text-align': 'center'}
                                            ),

                                        ]
                                    ),

                                    dcc.Tab(
                                        label="Model İstatistik Tablosu",
                                        className="p-3",
                                        id="model-stats-table",
                                    ),
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

        stats_table = None

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

        data_table = [
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
            )
        ]

        df = df.describe()

        df.reset_index(inplace=True)

        stats_table = [
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ]

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
            fig = px.line(df, x=x_axis, y=y_axis, color=color)

        elif graph_type == 'hist':
            fig = px.histogram(df, x=x_axis, y=y_axis, histnorm=histnorm, text_auto=bool(text_auto), color=color,
                               histfunc=histfunc, marginal=marginal)

        elif graph_type == 'box':
            fig = px.box(df, x=x_axis, y=y_axis, color=color)

        elif graph_type == 'bar':
            fig = px.bar(df, x=x_axis, y=y_axis, color=color, barmode="group")

        elif graph_type == 'heatmap':

            fig = px.density_heatmap(df, x=x_axis, y=y_axis, histnorm=histnorm, text_auto=bool(text_auto))

        elif graph_type == 'corr_heatmap':
            fig = px.imshow(df.corr(), text_auto=True, aspect="auto", color_continuous_scale="viridis")

        return fig

    @app.callback(

        Output("model-graph", "figure"),
        Output("model-results", "children"),
        Output('model-stats-table', 'children'),
        Output('data-predict', 'children'),

        Input("data-info", "data"),
        Input("data-filename", "data"),

        Input("model", "value"),
        Input("depend", "value"),
        Input("independ", "value"),
        Input("cluster-count", "value"),

    )
    def model(data, filename, model, depend, independ, n_clusters):

        global figure, df, results, st_table, data_predict, summary

        if model is None:
            raise PreventUpdate

        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(data))

        elif 'xls' or "xlsx" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(data))

        if model == 'linear':

            data_predict = None

            figure = px.scatter(df, x=depend, y=independ, trendline="ols", trendline_scope="overall")

            y = df[independ]

            x = df[depend[0]]

            x = stm.add_constant(x)

            stats_model = stm.OLS(y, x).fit()

            results = stats_model.summary()

            summary = results.as_text()

            df = df.describe()

            df.reset_index(inplace=True)

            st_table = [

                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    style_table={'overflowX': 'auto'},
                    page_size=10
                )

            ]

        elif model == 'mlinear':

            data_predict = None

            figure = px.scatter(df, x=depend, y=independ, trendline="ols", trendline_scope="overall")

            X = df[depend]

            y = df[independ]

            # Initialize the StandardScaler object
            scaler = StandardScaler()

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Add a constant to the model
            X_train_sm = stm.add_constant(X_train)

            model_sm = stm.OLS(y_train, X_train_sm).fit()

            results = model_sm.summary()

            summary = results.as_text()

            df = df.describe()

            df.reset_index(inplace=True)

            st_table = [
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    style_table={'overflowX': 'auto'},
                    page_size=10
                )
            ]

        elif model == 'kmc':

            data_predict = None

            x = depend[0]

            y = independ

            df = df.loc[:, [x, y]]

            df.dropna(inplace=True)

            km = KMeans(n_clusters=max(n_clusters, 1))

            km.fit(df.values)

            df["cluster"] = km.labels_

            centers = km.cluster_centers_

            data = [
                go.Scatter(
                    x=df.loc[df.cluster == c, x],
                    y=df.loc[df.cluster == c, y],
                    mode="markers",
                    marker={"size": 8},
                    name="Kümeleme {}".format(c),
                )
                for c in range(n_clusters)
            ]

            data.append(
                go.Scatter(
                    x=centers[:, 0],
                    y=centers[:, 1],
                    mode="markers",
                    marker={"color": "#000", "size": 12, "symbol": "diamond"},
                    name="Kümeleme Merkezi",
                )
            )

            layout = {"xaxis": {"title": x}, "yaxis": {"title": y}}

            figure = go.Figure(data=data, layout=layout)

            independ = f"{independ} ~ "

            depend = " + ".join(depend)

            formula = independ + depend

            stats_model = sm.ols(formula=formula, data=df).fit()

            results = stats_model.summary()

            summary = results.as_text()

            df = df.describe()

            df.reset_index(inplace=True)

            st_table = [
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    style_table={'overflowX': 'auto'},
                    page_size=10
                )
            ]

        elif model == 'knn':

            figure = None

            summary = None

            X = df[depend]
            y = df[independ].values

            # Veri setini eğitim ve test setlerine ayırma
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Veriyi ölçeklendirme
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # KNN modelini oluşturma ve eğitme
            knn = KNeighborsClassifier(n_neighbors=n_clusters)
            knn.fit(X_train_scaled, y_train)

            # Tahmin yapma
            y_pred = knn.predict(X_test_scaled)

            # Değerlendirme
            accuracy = accuracy_score(y_test, y_pred)
            print(f"Doğruluk: {accuracy}")
            print(classification_report(y_test, y_pred))


            df_predict = pd.concat([df[independ], df[depend], pd.Series(y_pred)], names=[depend, independ, "Tahmin"], axis=1)

            # table
            df = pd.concat([df[depend], df[independ]])

            data_st = df.describe()

            data_st.reset_index(inplace=True)

            st_table = [
                dash_table.DataTable(
                    data=data_st.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in data_st.columns],
                    style_table={'overflowX': 'auto'},
                    page_size=10
                )
            ]

            data_predict = [
                dash_table.DataTable(
                    data=df_predict.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df_predict.columns],
                    style_table={'overflowX': 'auto'},
                    page_size=10
                ),
                html.Div([f'Model Doğruluğu : %{round(accuracy * 10000, 2)}'], style={'marginBottom': 20, "marginLeft": 20}),
            ]

        return figure, summary, st_table, data_predict

    return render(request, 'index.html')
