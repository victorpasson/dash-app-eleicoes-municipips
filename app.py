# Importando os módulos
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
from urllib.request import urlopen
import json

external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# Datasets
df = pd.read_csv("oficial.csv")

with urlopen('https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json') as response:
    geojson = json.load(response)


app.layout = html.Div([
    html.Div([
        html.Label("Escolha um Estado"),
        dcc.Dropdown(
            ['RONDÔNIA', 'ACRE', 'AMAZONAS', 'RORAIMA', 'PARÁ', 'AMAPÁ',
            'TOCANTINS', 'MARANHÃO', 'PIAUÍ', 'CEARÁ', 'RIO GRANDE DO NORTE',
            'PARAÍBA', 'PERNAMBUCO', 'ALAGOAS', 'SERGIPE', 'BAHIA',
            'MINAS GERAIS', 'ESPÍRITO SANTO', 'RIO DE JANEIRO', 'SÃO PAULO',
            'PARANÁ', 'SANTA CATARINA', 'RIO GRANDE DO SUL',
            'MATO GROSSO DO SUL', 'MATO GROSSO', 'GOIÁS', 'DISTRITO FEDERAL'], 'SÃO PAULO',
           id='yaxis-column'),

    ], style={'width': '49%','display': 'inline-block'}),
    html.Div([html.P('Dash by: João Victor'), html.A("Linkedin", href="https://www.linkedin.com/in/victorpasson/", target='_blank', style={'text-decoration': 'none', 'margin-right':60, 'color':'#636EFA'}),
    html.A("Github", href="https://github.com/victorpasson", target='_blank', style={'text-decoration': 'none', 'margin-right':60, 'color':'#636EFA'}),
    html.A("Portfólio", href="https://victorpasson.github.io/", target='_blank', style={'text-decoration': 'none', 'color':'#636EFA'})], 
            style={'width': '49%','display': 'inline-block', 'float':'right'}),
    html.Br(),

    html.Div([dcc.Graph(id='output-3', config={'displayModeBar': False, 'scrollZoom': False})], style={'width': '49%','display': 'inline-block', 'float':'left'}),
    html.Div([dcc.Graph(id='output-1', config={'displayModeBar': False, 'scrollZoom': False}), 
            dcc.Graph(id='output-2', config={'displayModeBar': False, 'scrollZoom': False})], style={'display': 'inline-block', 'width': '49%', 'float':'right'}),
    dcc.Store(id='intermediate-data')
])
    

@app.callback(
    Output('intermediate-data', 'data'),
    Input('yaxis-column', 'value')
)
def clean_data(input_1):
    cleaned = df[df['uf'] == input_1]
    return cleaned.to_json(date_format='iso', orient='split')

@app.callback(
    Output('output-1', 'figure'),
    Input('intermediate-data', 'data')
)
def update_graph2(jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')

    fig = px.scatter(dff, x="pib_perc", y="porcentagem", color="partido", log_x=True,
                 hover_name="NO_MUNICIPIO", hover_data=["uf", "partido", "porcentagem", "vap"],
                 color_discrete_map={
                     "PT": "#EF553B",
                     "PL": "#636EFA"
                }, template="simple_white", 
                labels={'partido':'Vencedor', "pib_perc": "PIB per capita", "uf": "Estado", 
                        "porcentagem": "% Votação", "vap": "Votos"})

    fig.update_layout()

    fig.update_traces(marker=dict(size=10))
    fig.update_xaxes(title="PIB per capita (log)")
    fig.update_yaxes(title="Porcentagem")
    fig.update_layout(legend=dict(
                        title="Partido"
                    ),
                    title={
                    'text': "Relação: Pib Per Capita x % Votação",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'}, transition_duration=1000)

    return fig


@app.callback(
    Output('output-2', 'figure'),
    Input('intermediate-data', 'data')
)
def update_graph3(jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')

    fig = go.Figure()

    fig.add_trace(go.Histogram(x = dff[dff["partido"] == "PL"]["IDEB"], name="PL", 
                                xbins=dict(
                                    start=0,
                                    end=7.65,
                                    size=0.4), marker_color="#636EFA"))


    fig.add_trace(go.Histogram(x = dff[dff["partido"] == "PT"]["IDEB"], name="PT", 
                                xbins=dict(
                                    start=0,
                                    end=7.65,
                                    size=0.4), marker_color="#EF553B"))

    # Overlay para ambos histogramas
    fig.update_layout(barmode="overlay", template="simple_white",
                        legend=dict(
                        title="Partido"),
                        title={
                        "text":"Sobreposição Histogramas Nota IDEB",
                        "y":0.95,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top"}, transition_duration=2000)
    fig.update_traces(opacity=0.75)

    return fig

@app.callback(
    Output('output-3', 'figure'),
    Input('intermediate-data', 'data')
)
def update_graph(jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')

    fig = px.choropleth(dff, geojson=geojson, color="partido", hover_name="NO_MUNICIPIO", 
        hover_data=["uf", "porcentagem", "vap"],
        locations="id", featureidkey="properties.id",
        projection="mercator", 
        labels={'partido':'Vencedor', "id": "ID", "uf": "Estado", "porcentagem": "% Votação", "vap": "Votos"},
        color_discrete_map={
                     "PT": "#EF553B",
                     "PL": "#636EFA"})

    fig.update_traces(marker_line_width=0.5, marker_line_color='black')
    fig.update_geos(fitbounds="locations", visible=False, resolution=50)

    fig.update_layout(height=900, margin={"r":0,"t":0,"l":0,"b":0}, legend=dict(
        title="Partido",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ), transition_duration=1000)
    
    return fig


if __name__ == "__main__":
    app.run_server()