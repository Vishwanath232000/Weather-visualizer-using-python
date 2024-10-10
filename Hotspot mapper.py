
from dash import Dash, html, dcc, Input, Output, callback, callback_context
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import asyncio
import os
import python_weather
app = Dash(__name__)
#Creating variables and dictionaries to store data from API
long = []
lat = []

city_names=[]
temperature_data = {
    "Los Angeles": [],
    "New York": []
}
current_weather={
"Los Angeles": " ",
    "New York": " "
}
color_coordinates={
"Los Angeles": " ",
    "New York": " "
}
Temperature_description={}

#API function
async def getweather():
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        with open('city.txt', 'r') as file:
            for data in file:
                # sending values to their resptive lists and formating them
                data = str(data.strip())
                weather = await client.get(data)

                # Print basic weather details
                # print(f"Current temperature: {weather.temperature}°F")
                # print(f"Current location : {weather.location}")
                #  print(f"Description: {weather.description}")
                # print(f"Coordinates: {weather.coordinates}")
                i = 0
                city_names.append(weather.location)

                if weather.location not in Temperature_description:
                    Temperature_description[weather.location] = " "
                Temperature_description[weather.location]=weather.description
                if weather.location not in color_coordinates:
                    color_coordinates[weather.location] = " "
                if int(weather.temperature)>80:
                    color_coordinates[weather.location]='Red'
                else:
                    color_coordinates[weather.location] = 'Blue'


                if weather.location not in current_weather:
                    current_weather[weather.location] = " "

                current_weather[weather.location]=weather.temperature


                lat.append(weather.coordinates[0])
                long.append(weather.coordinates[1])

                if weather.location not in temperature_data:
                    temperature_data[weather.location] = []

                for daily in weather.daily_forecasts:
                    i = i + 1
                    '''
                    print(f"Day: {daily.date}")'''
                    for hourly in daily.hourly_forecasts:
                        '''  print(f'  --> Time: {hourly.time}, Temperature: {hourly.temperature}°F')'''
                        temperature_data[weather.location].append(hourly.temperature)
                    if i > 0:
                        break
def api_starter():
    # see https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    # for more details
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(getweather())


api_starter()


#The app starts here , when you refresh the page the app does not call the API again it starts from here

#HTML and graphs are created using dash function
app.layout = html.Div([
    dcc.Graph(id='city-map', clickData={'points': [{'hovertext': ''}]}),
    dcc.Dropdown(
        options=[{'label': city, 'value': city} for city in city_names],
        value='',
        id='city-dropdown'
    ),
    dcc.Graph(id='temperature-graph'),
    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'gap': '20px'}, children=[
        dcc.Graph(id='selected_city_temperature_bar', figure={}),
        dcc.Graph(id='top_temperature_bar', figure={}),
    ])
])
#The time scale
x_axis_value=["00:00", "03:00","06:00","09:00"," 12:00","15:00","18:00","21:00"]

#The call back function below will help to update the temperature variation graph
@callback(
    Output('temperature-graph', 'figure'),
    [Input('city-dropdown', 'value'),
    Input('city-map', 'clickData')]
)

#The function updates the graph when clicked on graph or dropdown
def update_temperature_graph_dropdown(selected_city, clickData):
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'city-dropdown':
        city = selected_city
    elif trigger_id == 'city-map':
        if clickData and 'points' in clickData and clickData['points']:
            city_hovertext = clickData['points'][0]['hovertext']
            city = city_hovertext.split('<br>')[0].strip()
        else:
            raise PreventUpdate

    if city:
        temperatures = temperature_data.get(city, [])
        current_temperature=current_weather[city]
        description=Temperature_description[city]
        fig = go.Figure(data=go.Scatter(x=x_axis_value, y=temperatures, mode='lines+markers'))
        fig.update_layout(
            title=f'Temperature Fluctuations in {city} and the current temperature is {current_temperature}°F ,{description} ',
            xaxis_title='Hour',
            yaxis_title='Temperature (Fahrenheit)',
            xaxis=dict(showgrid=False),  # Hide grid lines
            yaxis=dict(showgrid=False),  # Hide grid lines
        )
        return fig
    else:
        return go.Figure()  # Return an empty figure

#The below call back function updates the dropdown when clicked on map
@callback(
    Output('city-dropdown', 'value'),
    Input('city-map', 'clickData')
)
def update_dropdown(clickData):
    if clickData and 'points' in clickData and clickData['points']:
        city = clickData['points'][0]['hovertext']
        return city
    else:
        return ''

#The below function updates graph with city names
@callback(
    Output('city-map', 'figure'),
    Input('city-dropdown', 'value')

)
def update_city_map(selected_city):
    fig = go.Figure()

    # Add markers for all cities
    for i in range(len(city_names)):
        fig.add_trace(go.Scattermapbox(
            lon=[long[i]],
            lat=[lat[i]],
            mode='markers',
            hovertext=[f"{city_names[i]}<br>Current Temperature: {current_weather[city_names[i]]}°F"],
            marker=dict(size=10, color=color_coordinates[city_names[i]]),
            textposition='bottom center',
            hoverinfo = 'text',
        ))

    fig.update_layout(
        title='Hotspot Mapper of 100 US cities',
        mapbox=dict(
            style="open-street-map",
            center=dict(lon=sum(long) / len(long), lat=sum(lat) / len(lat)),
            zoom=4
        ),
        showlegend=False,
        height=800  # Adjust the height of the map
    )

    return fig
#function used to get graph of selected cities
@callback(
    Output('selected_city_temperature_bar', 'figure'),
    Input('city-map', 'selectedData')
)
def update_selected_city_temperature_bar(selected_data):
    if selected_data:
        selected_cities = [point['hovertext'].split('<br>')[0].strip() for point in selected_data['points']]
        sorted_cities = sorted([(city, current_weather[city]) for city in selected_cities], key=lambda x: x[1], reverse=True)

        x_values = [city for city, temp in sorted_cities]
        y_values = [temp for city, temp in sorted_cities]

        fig = go.Figure(data=[go.Bar(x=x_values, y=y_values)])
        fig.update_layout(
            title='Temperature comparison of seleted cities ',
            xaxis_title='City',
            yaxis_title='Temperature (Fahrenheit)',
            height=600,
            width=1000,
            margin=go.layout.Margin(l=50, r=50, t=50, b=70),
            font=dict(color='white'),
            plot_bgcolor='black',
            paper_bgcolor='black',
            xaxis=dict(showgrid=False),  # Hide grid lines
            yaxis=dict(showgrid=False),
            autosize=True
        )

        return fig
    else:
        return go.Figure()  # Return an empty figure

#Top ten cities function
@callback(
    Output('top_temperature_bar', 'figure'),
    Input('city-dropdown', 'value')
)
def update_top_temperature_bar(selected_city):
    '''if not selected_city:
        return go.Figure()'''


    # Get the top 10 cities by current temperature
    sorted_cities = sorted(current_weather.items(), key=lambda x: x[1], reverse=True)[:10]

    # Prepare data for the bar chart
    x_values = [city for city, temp in sorted_cities]
    y_values = [temp for city, temp in sorted_cities]

    fig = go.Figure(data=[go.Bar(x=x_values, y=y_values)])
    fig.update_layout(
        title='Top 10 Cities by Current Temperature',
        xaxis_title='City',
        yaxis_title='Temperature (Fahrenheit)',
        height=600,
        width=1000,
        margin=go.layout.Margin(l=50, r=50, t=50, b=50),
        font=dict(color='white'),
        plot_bgcolor='black',
        paper_bgcolor='black',
        xaxis=dict(showgrid=False),  # Hide grid lines
        yaxis=dict(showgrid=False),
        autosize=True
    )

    return fig

#The app is run here
if __name__ == '__main__':
    app.run_server(debug=True)
