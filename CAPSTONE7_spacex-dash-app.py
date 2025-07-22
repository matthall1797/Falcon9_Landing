# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},     
                                            ],
                                            value='ALL',
                                            placeholder='Select Launch Site',
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                # TASK 3: Add a slider to select payload range
html.Div([
    html.Div([
        html.H3('Payload Mass Range (kg)', style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 20}),
        dcc.RangeSlider(
            id='payload-slider',
            min=min_payload, max=max_payload, step = 1000,
            marks={
                0:'0',
                2500:'2500',
                5000: '5000',
                7500: '7500',
                10000: '10000'
            },
            value=[min_payload, max_payload]
        )
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '10px'}),
    html.Br(),
]),

html.Div(dcc.Graph(id='success-payload-scatter-chart')),

])
# Function decorator to specify function input and output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
    )
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class']==1].groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(
            success_counts,
            values='count', 
            names='Launch Site', 
            title='Successful Lauches from Each Site'
            )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_failure_counts = filtered_df['class'].value_counts().reset_index()
        success_failure_counts.columns = ['class', 'count']
        success_failure_counts['class'] = success_failure_counts['class'].map({1: "Success", 0: 'Epic Fail'})
        fig = px.pie(
            success_failure_counts,
            values='count', 
            names='class', 
            title=f'Percent Successful Launches from {entered_site}',
            color = 'class',
            color_discrete_map={
                'Success': 'green',
                'Epic Fail': 'red'
            }
            )
    return fig


# TASK 4: Add a scatter chart to show the correlation between payload and launch success
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')]
    )
def get_scatter_plot(entered_site,payload):
    low, high = payload
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                                (spacex_df['Payload Mass (kg)'] <= high)]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= low) & 
                                (spacex_df['Payload Mass (kg)'] <= high)]

    fig = px.scatter(
        filtered_df,
        x = 'Payload Mass (kg)',
        y = 'class',
        color = 'Booster Version Category',
        title = 'Successes and Failures vs Payload'
)

    return fig

                                
# Run the app
if __name__ == '__main__':
    app.run()
