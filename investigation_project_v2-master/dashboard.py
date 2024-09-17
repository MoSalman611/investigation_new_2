import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import psycopg2
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import json
import io
import base64

#import main
with open("za.json") as f:
    geojson_data = json.load(f)

# Database connection
conn = psycopg2.connect(
    host="localhost", port="5432", database="homicide_main",
    user="postgres", password="deadlocked611")

# Define options
provinces = {
    'Western Cape': ['Cape Town', 'Stellenbosch', 'George'],
    'Eastern Cape': ['Port Elizabeth', 'East London', 'Grahamstown'],
    'Gauteng': ['Johannesburg', 'Pretoria', 'Soweto'],
    # Add more provinces and towns here
}

race_options = [
    {'label': 'African', 'value': 'African'},
    {'label': 'White', 'value': 'White'},
    {'label': 'Coloured', 'value': 'Coloured'},
    {'label': 'Indian/Asian', 'value': 'Indian/Asian'},
    {'label': 'Other', 'value': 'Other'}
]

relationship_options = [
    {'label': 'Family', 'value': 'Family'},
    {'label': 'Friend', 'value': 'Friend'},
    {'label': 'Acquaintance', 'value': 'Acquaintance'},
    {'label': 'Stranger', 'value': 'Stranger'},
    {'label': 'Other', 'value': 'Other'}
]

bool_options = [
    {'label': 'Yes', 'value': True},
    {'label': 'No', 'value': False}
]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


# Navbar
navbar = dbc.NavbarSimple(
    brand="Homicide Media Tracker",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Data Entry", href="/")),
        dbc.NavItem(dbc.NavLink("Data Display", href="/display")),
        dbc.NavItem(dbc.NavLink("Data Visualization", href="/visualization")),
    ]
)

# Footer
footer = html.Footer(
    "Homicide Media Tracker © 2024",
    style={'text-align': 'center', 'padding': '20px', 'background': '#f1f1f1'}
)

# Data Entry Layout
data_entry_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Entry"),
        dbc.CardBody([
            dbc.Row([dbc.Col([dbc.Label("News Report URL"), dbc.Input(id='url-input', type='text', placeholder="Enter news report URL")], width=6)]),
            dbc.Row([dbc.Col([dbc.Label("News Outlet"), dbc.Input(id='outlet-input', type='text', placeholder="Enter news outlet")], width=6),
                     dbc.Col([dbc.Label("Date of Publication"), dbc.Input(id='publication-date-input', type='date')], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Author"), dbc.Input(id='author-input', type='text', placeholder="Enter author name")], width=6),
                     dbc.Col([dbc.Label("Headline"), dbc.Input(id='headline-input', type='text', placeholder="Enter headline")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Number of Subs"), dbc.Input(id='subs-input', type='text', placeholder="Enter Number of Subs")], width=6),
                     dbc.Col([dbc.Label("Wire Service"), dbc.Input(id='wire-input', type='text', placeholder="Enter Wire Service")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Victim Name"), dbc.Input(id='victim-name-input', type='text', placeholder="Enter victim name")], width=6),
                     dbc.Col([dbc.Label("Date of Death"), dbc.Input(id='death-date-input', type='date')], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Age of Victim"), dbc.Input(id='victim-age-input', type='number', placeholder="Enter victim age")], width=6),
                     dbc.Col([dbc.Label("Race of Victim"), dcc.Dropdown(id='race-dropdown', options=race_options, placeholder="Select race")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Type of Location"), dbc.Input(id='location-type-input', type='text', placeholder="Enter type of location")], width=6),
                     dbc.Col([dbc.Label("Province"), dcc.Dropdown(id='province-dropdown', options=[{'label': k, 'value': k} for k in provinces.keys()], placeholder="Select a province")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Town"), dcc.Dropdown(id='town-dropdown', placeholder="Select a town")], width=6),
                     dbc.Col([dbc.Label("Sexual Assault"), dcc.Dropdown(id='sexual-assault-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Mode of Death"), dbc.Input(id='mode-of-death-input', type='text', placeholder="Enter mode of death")], width=6),
                     dbc.Col([dbc.Label("Robbery"), dcc.Dropdown(id='robbery-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Suspect Arrested"), dcc.Dropdown(id='suspect-arrested-dropdown', options=bool_options, placeholder="Select option")], width=6),
                     dbc.Col([dbc.Label("Suspect Convicted"), dcc.Dropdown(id='suspect-convicted-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Perpetrator Name"), dbc.Input(id='perp-name-input', type='text', placeholder="Enter perpetrator name")], width=6),
                     dbc.Col([dbc.Label("Perp Relationship"), dcc.Dropdown(id='relationship-dropdown', options=relationship_options, placeholder="Select relationship")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Multiple Murders"), dcc.Dropdown(id='multi-murder-dropdown', options=bool_options, placeholder="Select option")], width=6),
                     dbc.Col([dbc.Label("Extreme Violence"), dcc.Dropdown(id='extreme-violence-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Intimate Femicide"), dcc.Dropdown(id='intimate-femicide-dropdown', options=bool_options, placeholder="Select option")], width=6),
                     dbc.Col([dbc.Label("Notes"), dbc.Textarea(id='notes-input', placeholder="Enter additional notes")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Button("Submit", id="submit-button", color="success", className="mt-3"),
            html.Div(id="output-message", className="mt-3"),
            dbc.Button("Export to CSV", id="export-button", color="secondary", className="mt-3"),
            dcc.Download(id="download-dataframe-csv"),
            html.Hr(),
            html.H3("Upload CSV to Import Data"),
            dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}, multiple=False, accept=".csv"),
            html.Div(id='upload-output')
        ]),
    ], className="mb-4")
])

# Data Display Layout
data_display_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Display"),
        dbc.CardBody([
            dbc.Button("Check for Duplicates", id='check-duplicates-button', n_clicks=0, color="warning"),
            html.Div(id='duplicates-message'),
            dbc.Label("Select Columns to Display"),
            dcc.Checklist(
                id='column-checklist',
                options=[{'label': col, 'value': col} for col in ['news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province', 'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes']],
                value=['news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province', 'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes'],
                inline=True
            ),
            html.Div(id='table-container')
        ]),
    ], className="mb-4")
])

# Data Visualization Layout
data_visualization_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Visualization"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select Plot Category"),
                    dcc.Dropdown(
                        id='plot-category-dropdown',
                        options=[{'label': 'Homicides Over Time', 'value': 'homicides_over_time'}, {'label': 'Geographical Distribution', 'value': 'geographical_distribution'}],
                        placeholder="Select a plot category"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Select Plot Type"),
                    dcc.Dropdown(
                        id='plot-type-dropdown',
                        options=[],
                        placeholder="Select a plot type"
                    )
                ], width=6),
            ]),
            html.Div(id='plot-container', style={'textAlign': 'center', 'margin': '20px'})
        ]),
    ], className="mb-4")
])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'),
    footer
])

# Callbacks to switch pages
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/display':
        return data_display_layout
    elif pathname == '/visualization':
        return data_visualization_layout
    else:
        return data_entry_layout


# Province-Town Callback
@app.callback(
    Output('town-dropdown', 'options'),
    Input('province-dropdown', 'value')
)
def update_town_dropdown(province_value):
    if province_value:
        return [{'label': town, 'value': town} for town in provinces[province_value]]
    return []

# Handle Data Submission
@app.callback(
    Output('output-message', 'children'),
    Input('submit-button', 'n_clicks'),
    State('url-input', 'value'),
    State('outlet-input', 'value'),
    State('publication-date-input', 'value'),
    State('author-input', 'value'),
    State('headline-input', 'value'),
    State('subs-input', 'value'),
    State('wire-input', 'value'),
    State('victim-name-input', 'value'),
    State('death-date-input', 'value'),
    State('victim-age-input', 'value'),
    State('race-dropdown', 'value'),
    State('location-type-input', 'value'),
    State('province-dropdown', 'value'),
    State('town-dropdown', 'value'),
    State('sexual-assault-dropdown', 'value'),
    State('mode-of-death-input', 'value'),
    State('robbery-dropdown', 'value'),
    State('suspect-arrested-dropdown', 'value'),
    State('suspect-convicted-dropdown', 'value'),
    State('perp-name-input', 'value'),
    State('relationship-dropdown', 'value'),
    State('multi-murder-dropdown', 'value'),
    State('extreme-violence-dropdown', 'value'),
    State('intimate-femicide-dropdown', 'value'),
    State('notes-input', 'value')
)
def submit_form(n_clicks, url, outlet, pub_date, author, headline, subs, wire, victim_name, death_date,
                victim_age, race, location_type, town, province, sexual_assault, mode_of_death, 
                robbery, suspect_arrested, suspect_convicted, perp_name, relationship,
                multi_murder, extreme_violence, femicide, notes):
    if n_clicks is None:
        return ""

    # Ensure that the connection is correctly committed
    try:
        # Establish a new connection
        conn = psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="deadlocked611"
        )
        cur = conn.cursor()

        # Prepare the SQL insert statement
        insert_query = '''INSERT INTO homicide_news 
                 (news_report_url, news_report_platform, date_of_publication, author, news_report_headline, no_of_subs, 
                  wire_service, victim_name, date_of_death, age_of_victim, race_of_victim, type_of_location, 
                  place_of_death_town, place_of_death_province, sexual_assault, mode_of_death_specific, robbery_y_n_u, 
                  suspect_arrested, suspect_convicted, perpetrator_name, perpetrator_relationship_to_victim, 
                  multiple_murder, extreme_violence_y_n_m_u, intimate_femicide_y_n_u, notes)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''


        values = (url, outlet, pub_date, author, headline, subs, wire, victim_name, death_date,
                victim_age, race, location_type, province, town, sexual_assault, mode_of_death, 
                robbery, suspect_arrested, suspect_convicted, perp_name, relationship, 
                multi_murder, extreme_violence, femicide, notes)

        
        # Execute the insertion
        cur.execute(insert_query, values)
        conn.commit()  # Ensure the transaction is committed
        cur.close()  # Close the cursor

        return "Data successfully inserted!"

    except Exception as e:
        conn.rollback()  # Rollback in case of an error
        return f"Error: {str(e)}"
    
    finally:
        conn.close()  # Ensure the connection is always closed


# Handle CSV Export
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    if n_clicks:
        query = "SELECT * FROM homicide_news"
        df = pd.read_sql(query, conn)
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + base64.b64encode(csv_string.encode()).decode()
        return dcc.send_data_frame(csv_string, "homicide_complete.csv")
    return None

# Handle CSV Upload
@app.callback(
    Output('upload-output', 'children'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def upload_csv(contents):
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df.to_sql('homicide_complete', engine, if_exists='append', index=False)
        return "CSV data uploaded successfully."
    return ""

# Handle Column Display in Data Display Page
@app.callback(
    Output('table-container', 'children'),
    Input('column-checklist', 'value')
)
def display_table(selected_columns):
    if selected_columns:
        try:
            # Build the query with selected columns
            query = f"SELECT {', '.join(selected_columns)} FROM homicide_news"
            df = pd.read_sql(query, conn)
            
            # Return table only if DataFrame is not empty
            if not df.empty:
                return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
            else:
                return "No data available for the selected columns."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        return "Please select at least one column to display."


# Handle Plot Type Dropdown based on Plot Category
@app.callback(
    Output('plot-type-dropdown', 'options'),
    Input('plot-category-dropdown', 'value'),
    
)

def update_plot_type_dropdown(category_value):
    if category_value == 'homicides_over_time':
        return [{'label': 'Line Plot', 'value': 'line_plot'}, {'label': 'Bar Chart', 'value': 'bar_chart'}]
    if category_value == 'geographical_distribution':
        return [{'label': 'Choropleth Map', 'value' : 'choropleth_map'}, {'label' : 'Heat Map', 'value' : 'heat_map'}]
    return []

@app.callback(
    Output('plot-container', 'children'),
    Input('plot-category-dropdown', 'value'),
    Input('plot-type-dropdown', 'value'),
)
def render_plot(category_value, plot_type_value):
    fig = None  # Initialize fig to None

    if not category_value or not plot_type_value:
        return "Please select a plot type."

    if category_value == 'homicides_over_time':
        query = """
            SELECT victim_name, date_of_death 
            FROM homicide_news
            GROUP BY victim_name, date_of_death
        """
        df = pd.read_sql(query, conn)
        df['date_of_death'] = pd.to_datetime(df['date_of_death'])
        df['year_of_death'] = df['date_of_death'].dt.year
        data = df.groupby('year_of_death').size().reset_index(name='count')

        if plot_type_value == 'line_plot':
            fig = px.line(data, x='year_of_death', y='count', title='Homicides Over Time')
        elif plot_type_value == 'bar_chart':
            fig = px.bar(data, x='year_of_death', y='count', title='Homicides Over Time')
        
    elif category_value == 'geographical_distribution':
        query = """
            SELECT place_of_death_province, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
            FROM homicide_news 
            GROUP BY place_of_death_province
        """
        df = pd.read_sql(query, conn)

        if plot_type_value == 'choropleth_map':
            fig = px.choropleth(df, 
                                geojson=geojson_data, 
                                locations='place_of_death_province', 
                                featureidkey="properties.name", 
                                color='count', 
                                title='Homicides by Province',
                                scope='africa')

            fig.update_geos(fitbounds="locations")  # Focus on South Africa
        
        elif plot_type_value == 'heat_map':
            query = """
                SELECT latitude, longitude, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
                FROM homicide_news 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
                GROUP BY latitude, longitude
            """
            df = pd.read_sql(query, conn)

            fig = px.density_mapbox(df, 
                                    lat='latitude', 
                                    lon='longitude', 
                                    z='count', 
                                    radius=10,
                                    center=dict(lat=-30, lon=25),  
                                    zoom=5,
                                    mapbox_style="stamen-terrain",
                                    title='Heat Map of Homicides')

    if fig:
        return dcc.Graph(figure=fig)
    
    return "Please select a plot type."




if __name__ == '__main__':
    app.run_server(debug=True)