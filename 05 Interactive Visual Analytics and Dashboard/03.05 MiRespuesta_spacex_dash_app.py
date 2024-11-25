# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

#creo un df con la lista de Launch Site y le agrego al inicio un df con 1 registro 
#para All Sites. El df lo utilizo para recorrer y crear cada site en el
#dcc.Dropdown,  id='site-dropdown'
site_list_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
site_list_df = site_list_df[['Launch Site']]
site_list_df['value'] = site_list_df['Launch Site']
site_list_df = pd.concat([pd.DataFrame([['All Sites', 'ALL']],columns=['Launch Site', 'value']),site_list_df], ignore_index=True)


# Create a dash application
app = dash.Dash(__name__)
#help(dcc.Dropdown)
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([        
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[{'label': row['Launch Site'], 'value': row['value']} for index, row in site_list_df.iterrows()],
                                        value='ALL',
                                        placeholder='Select a option',
                                        searchable=True
                                    )
                                ]),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={0: '0',2500: '2500', 5000 : '5000', 7500  : '7500', 10000 : '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
        
    if entered_site == 'ALL':
        # Filter the data for Success Launch (class == 1)
        filtered_df = spacex_df[spacex_df['class'] == 1]
        data=filtered_df.groupby('Launch Site').sum()
        fig = px.pie(data, values='class', 
        names=data.index, 
        title='Total Success Launches By Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        # Filter the data for Site Launch
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        #print(filtered_df)
        data=filtered_df.groupby(['class']).count()
        fig = px.pie(data, values='Launch Site', 
        names=data.index, 
        title='Success/Failed Launch for Site: '+ entered_site)
        return fig
                

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
            Output(component_id='success-payload-scatter-chart', component_property='figure'),
            [Input(component_id='site-dropdown', component_property='value'), 
             Input(component_id="payload-slider", component_property="value")])

def get_scatter_chart(entered_site, range_payload):
    
    if entered_site == 'ALL':
        #Filtrar los datos para que coincidan con los rangos del payload-slider
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] <= range_payload[1]) &
                                (spacex_df['Payload Mass (kg)'] >= range_payload[0])]
        fig = px.scatter(filtered_df, 
                        x='Payload Mass (kg)',
                        y='class',
                        color="Booster Version Category",
                        title='Correlation between Payload and Success for All Sites '
                        )        
        return fig
    else:                
        #filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        #filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] <= range_payload[1]]
        #filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] >= range_payload[0]]
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] <= range_payload[1]) &
                                (spacex_df['Payload Mass (kg)'] >= range_payload[0])]
        fig = px.scatter(filtered_df, 
                        x='Payload Mass (kg)',
                        y='class',
                        color="Booster Version Category",
                        title='Correlation between Payload and Success for Sites: ' + entered_site
                        )        
        return fig
        


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
