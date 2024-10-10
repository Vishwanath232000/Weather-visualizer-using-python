# Weather Dashboard Application

This application is built using Dash and Plotly to visualize weather data for multiple cities. It fetches real-time weather information from an API and allows users to explore temperature fluctuations, current weather conditions, and compare temperatures across selected cities.

## Key Features
- Interactive temperature graphs for selected cities.
- Dynamic city selection using a dropdown menu.
- Map visualization of cities with temperature markers.
- Comparison of temperatures across selected cities.
- Displays the top 10 cities by current temperature.

## Technologies Used
- **Dash**: A Python framework for building web applications.
- **Plotly**: A graphing library for creating interactive charts.
- **Python Weather API**: Used to fetch real-time weather data.

## Code Explanation

### 1. Imports
```python
from dash import Dash, html, dcc, Input, Output, callback, callback_context
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import asyncio
import os
import python_weather

app = Dash(__name__)


### 2. Initialization
python
Copy code
app = Dash(__name__)
Initializes a Dash application.
### 3. Data Structures
python
Copy code
long = []
lat = []
city_names = []
temperature_data = {
    "Los Angeles": [],
    "New York": []
}
current_weather = {
    "Los Angeles": " ",
    "New York": " "
}
color_coordinates = {
    "Los Angeles": " ",
    "New York": " "
}
Temperature_description = {}
Initializes lists and dictionaries to store data from the weather API.
### 4. Async Weather API Function
python
Copy code
async def getweather():
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        with open('city.txt', 'r') as file:
            for data in file:
                data = str(data.strip())
                weather = await client.get(data)
                # Process weather data...
Defines an asynchronous function to fetch weather data for cities listed in a file (city.txt). It retrieves temperature, coordinates, and descriptions for each city and stores them in the corresponding data structures.
### 5. API Starter Function
python
Copy code
def api_starter():
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(getweather())
Ensures compatibility with Windows and starts the asynchronous weather fetching process.
### 6. Layout Definition
python
Copy code
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
Defines the layout of the Dash app, including a map for cities, a dropdown for city selection, and several graphs for temperature visualization.
### 7. Callbacks
Temperature Graph Update
python
Copy code
@callback(
    Output('temperature-graph', 'figure'),
    [Input('city-dropdown', 'value'), Input('city-map', 'clickData')]
)
def update_temperature_graph_dropdown(selected_city, clickData):
    # Updates the temperature graph based on selected city or clicked map point
Updates the temperature graph when a city is selected from the dropdown or when a point on the map is clicked.
Dropdown Update from Map
python
Copy code
@callback(
    Output('city-dropdown', 'value'),
    Input('city-map', 'clickData')
)
def update_dropdown(clickData):
    # Updates the dropdown based on the city clicked on the map
Updates the city dropdown based on the city clicked on the map.
City Map Update
python
Copy code
@callback(
    Output('city-map', 'figure'),
    Input('city-dropdown', 'value')
)
def update_city_map(selected_city):
    # Updates the city map with markers and temperatures
Renders the city map with markers that show the current temperature for each city.
Selected City Temperature Bar
python
Copy code
@callback(
    Output('selected_city_temperature_bar', 'figure'),
    Input('city-map', 'selectedData')
)
def update_selected_city_temperature_bar(selected_data):
    # Updates bar chart comparing temperatures of selected cities
Displays a bar chart comparing temperatures of the cities selected on the map.
Top 10 Cities Bar Chart
python
Copy code
@callback(
    Output('top_temperature_bar', 'figure'),
    Input('city-dropdown', 'value')
)
def update_top_temperature_bar(selected_city):
    # Updates the bar chart of the top 10 cities by temperature
Renders a bar chart showing the top 10 cities by current temperature.
### 8. Running the App
python
Copy code
if __name__ == '__main__':
    app.run_server(debug=True)
Starts the Dash app in debug mode.
How to Run
Install the required packages:
bash
Copy code
pip install dash plotly python_weather
Create a city.txt file containing city names (one per line).
Run the application:
bash
Copy code
python app.py
Open a web browser and go to http://127.0.0.1:8050/ to view the dashboard.
