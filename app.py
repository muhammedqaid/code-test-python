from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

app = Dash(__name__)

df = pd.read_csv('event_data_new.csv')


def datetime_to_date(row):
    return row['created'].split(' ')[0]


# ---- Data set up
df['date'] = pd.to_datetime(df['created']).dt.date
# print(df)

# groupby state - for map visualisations
GBstate = df.groupby(['state']).agg(count=('eventValue', 'count'))
GBstate['sum_value'] = df.groupby(['state']).agg(sum_value=('eventValue', 'sum'))
GBstate = GBstate.reset_index()
# print(GBstate)

# groupby date and state - for line chart
GBdate_state = df.groupby(['date', 'state']).agg(count=('date', 'count')).reset_index()
# print(GBdate_state)


# ---- App config
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# define base html of visualisation app
app.layout = html.Div(style={'backgroundColor': colors['background'], 'font-size': '150%', 'margin':{"r": 0, "t": 0, "l": 0, "b": 0}}, children=[
    html.H1(
        children='Events across states',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'padding-top': '3%',
            'margin-top': '0%'
        }
    ),

    html.Div(children='This visualised the number and sum value of events across states between 2022-08-22 and 2022-10-21. Please use the radio button to switch between the total number of events per state (Event count per state) and the sum value of events per state (Sum value per state).', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': '4%',
        'padding-top': '2%'
    }),

    html.Div(children=[
        dcc.RadioItems(
            ['Event count per state', 'Sum value per state'],
            'Event count per state',
            id='map-type',  # The id for input of updateMap()
            inline=True,
            style={"color": colors['text'], "margin-right": "20px"}
        ),

        dcc.Graph(
            id='map',
            style={'padding-top': '3%'}
        )
    ], style={'textAlign': 'center', "margin": "auto", 'align-items': 'center', 'justify-content': 'center', 'padding-left': '10%', 'padding-right': '10%'}),

    html.H1(
        children='Temporal Trends',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'padding-top': '3%'
        }
    ),

    html.Div(html.P(['This visualised the daily event count from 2022-08-22 to 2022-10-21. To screw down to a specfic state, select it from the dropdown.', html.Br(), html.Br(), 'Please note the 5 day moving average is also calculated, howver as you screw down, the data becomes more scarce so days with no events, are not plotted or contributing to the moving avergae. In these cases its is more of a 5-\'point\' moving avergae as opposed to a 5-day moving average']), style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding': '5%',
        'padding-top': '2%'
    }),

    html.Div(children=[

        html.Div(
            dcc.Dropdown(
                np.insert(GBstate['state'].unique(), 0, 'All States'),
                'All States',
                id='line-state',  # The id for input of updateLine()
                style={"color": colors['text'], "background-color": "LightBlue", 'padding': '0%', 'width': '100%'}
            ),
            style={ 'display': 'flex', 'padding-left': '25%', 'padding-bottom': '2%', 'width':"50%", 'textAlign': 'center', 'align-items': 'center', 'justify-content': 'center'}
        ),

        dcc.Graph(
            id='line',
        )

    ], style={'padding': 10, 'textAlign': 'center', 'padding-left': '10%', 'padding-right': '10%'}),

])


@app.callback(
    Output('map', 'figure'),
    Input('map-type', 'value'))  # input from map radiobutton
def update_map(map_type):
    if map_type == 'Event count per state':
        map = go.Figure(data=go.Choropleth(
            locations=GBstate['state'],
            z=GBstate['count'].astype(float),
            locationmode='USA-states',
            colorscale="Viridis"
        ))
    else:
        map = go.Figure(data=go.Choropleth(
            locations=GBstate['state'],
            z=GBstate['sum_value'].astype(float),
            locationmode='USA-states',
            colorscale="Viridis"
        ))

    map.update_layout(
        geo_scope='usa',  # limite map scope to USA
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        geo_bgcolor=colors['background']
    )

    return map


@app.callback(
    Output('line', 'figure'),
    Input('line-state', 'value'))  # input from line chart dropdown
def update_line(state):
    if state != 'All States':
        GBDate_4st8 = GBdate_state[GBdate_state['state']==state]
        GBDate_4st8['MA'] = GBDate_4st8.rolling(window=5).mean()
        line = px.line(GBDate_4st8, x='date', y=['count', 'MA'])
        # print(GBDate_4st8)

    else:
        GBDate_4All = df.groupby(['date']).agg(count=('date', 'count')).reset_index()
        GBDate_4All['MA'] = GBDate_4All.rolling(window=5).mean()
        line = px.line(GBDate_4All, x='date', y=['count', 'MA'])
        # print(GBDate_4All)

    line.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        geo_bgcolor=colors['background'],
        legend_title=None,
        legend=dict(
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=0.05
        )
    )
    trace_names = {'count': "Daily Events", 'MA': "5-day Moving Average"}

    line.for_each_trace(lambda t: t.update(name=trace_names[t.name],
                        legendgroup=trace_names[t.name],
                        hovertemplate=t.hovertemplate.replace(t.name, trace_names[t.name]))
                        )

    line.update_xaxes(title_text='Date', showgrid=True, gridwidth=0.5, gridcolor='LightBlue')
    line.update_yaxes(title_text='Daily Event Count', showgrid=True, gridwidth=0.5, gridcolor='LightBlue')
    line.update_traces(line=dict(width=3.5),
                       hovertemplate='<b>Date</b>: %{x}<br>' + '<b>Value</b>: %{y}<br>',
                       )
    return line


if __name__ == '__main__':
    app.run_server(debug=True)