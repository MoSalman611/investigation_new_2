import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import callback_context
import psycopg2
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import json
import io
import base64
from psycopg2 import pool
import traceback

# # Create a connection pool
# connection_pool = psycopg2.pool.SimpleConnectionPool(
#     1, 20,
#     host="localhost",
#     port="5432",
#     database="homicide_main",
#     user="postgres",
#     password="Khiz1234"
# )

# def get_db_connection():
#     return connection_pool.getconn()

# def release_db_connection(conn):
#     connection_pool.putconn(conn)

#import main
with open("za.json") as f:
    geojson_data = json.load(f)

# Database connection
conn = psycopg2.connect(
    host="localhost", port="5432", database="homicide_main",
    user="postgres", password="Khiz1234")

engine = create_engine("postgresql://postgres:Khiz1234@localhost:5432/homicide_main")
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
    {'label': 'Yes', 'value': 'Y'},
    {'label': 'No', 'value': 'N'}
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
            html.H3("Upload CSV to Import Data in to the Current Table"),
            dcc.Upload(id='upload-data-1', children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}, multiple=False, accept=".csv"),
            html.Div(id='upload-output-1'),
            html.Hr(),
            html.H3("Upload CSV to Import Data in to a New Table"),
            dcc.Upload(id='upload-data-2', children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}, multiple=False, accept=".csv"),
            html.Div(id='upload-output-2')
        ]),
    ], className="mb-4")
])

# # Data Display Layout
# data_display_layout = dbc.Container([
#     dbc.Card([
#         dbc.CardHeader("Homicide Data Display"),
#         dbc.CardBody([
#             html.Div([
#             dcc.Input(
#                 id = 'duplicate-column-input',
#                 type = 'text',
#                 placeholder = 'Enter column names separated by commas',
#                 style = {'width' : '60%'}
#             ),
#             dbc.Button("Check for Duplicates", id='check-duplicates-button', n_clicks=0, color = "warning"),
#             dbc.Button("Delete duplicates", id = 'delete-duplicates-button', n_clicks=0, color = "danger"),
#         ], style = {'display': 'flex', 'gap': '80px'}),
            
#             html.Div(id='duplicates-message'),            
#             dbc.Label("Select Columns to Display"),
#             dcc.Checklist(
#                 id='column-checklist',
#                 options=[{'label': col, 'value': col} for col in ['article_id','news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province', 'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes']],
#                 value=['article_id','news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province', 'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes'],
#                 inline=True
#             ),
#             html.Div(id='table-container')
#         ]),
#     ], className="mb-4")
# ])



#Data display layout
data_display_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Display"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Input(
                        id='duplicate-column-input',
                        type='text',
                        placeholder='Enter column names separated by commas',
                        style={'width': '100%'}
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Button("Check for Duplicates", id='check-duplicates-button', n_clicks=0, color="warning", className="me-2"),
                    dbc.Button("Delete duplicates", id='delete-duplicates-button', n_clicks=0, color="danger"),
                ], width=6, className="d-flex justify-content-end")
            ], className="mb-3"),
            
            html.Div(id='duplicates-message', className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Input(
                        id='delete-record-input',
                        type='text',
                        placeholder='Enter the article_id which needs to be deleted',
                        style={'width': '100%'}
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Button("Delete Data", id='delete-record-button', n_clicks=0, color="primary"),
                ], width=6, className="d-flex justify-content-end")
            ], className="mb-3"),
            
            dbc.Label("Select Columns to Display", className="mt-3"),
            dcc.Checklist(
                id='column-checklist',
                options=[{'label': col, 'value': col} for col in ['article_id','news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province', 'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes']],
                value=['article_id','news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province', 'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes'],
                inline=True
            ),
            dbc.Button("Display Table", id = 'display-button', color = "success", className = "mt-3" ),
            html.Div(id='table-container',  className="mt-3")
        ]),
    ], className="mb-4")
])
app.layout = dbc.Container([
    data_display_layout
])


# 4 plot code that works
# # Data Visualization Layout
# data_visualization_layout = dbc.Container([
#     dbc.Card([
#         dbc.CardHeader("Homicide Data Visualization"),
#         dbc.CardBody([
#             dbc.Row([
#                 dbc.Col([
#                     dbc.Label("Select Plot Category"),
#                     dcc.Dropdown(
#                         id='plot-category-dropdown',
#                         options=[{'label': 'Homicides Over Time', 'value': 'homicides_over_time'}, {'label': 'Geographical Distribution', 'value': 'geographical_distribution'}],
#                         placeholder="Select a plot category"
#                     )
#                 ], width=6),
#                 dbc.Col([
#                     dbc.Label("Select Plot Type"),
#                     dcc.Dropdown(
#                         id='plot-type-dropdown',
#                         options=[],
#                         placeholder="Select a plot type"
#                     )
#                 ], width=6),
#             ]),
#             html.Div(id='plot-container', style={'textAlign': 'center', 'margin': '20px'})
#         ]),
#     ], className="mb-4")
# ])

#9 code plot that works or not we dont know
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
                        options=[{'label': 'Homicides Over Time', 'value': 'homicides_over_time'}, {'label': 'Geographical Distribution', 'value': 'geographical_distribution'}, {'label': 'Demographic Insights', 'value': 'demographic_insights'}, {'label': 'Victim Perpetrator Relationship', 'value': 'victim_perpetrator_relationship'}, {'label' : 'Multivariate Comparisons', 'value' : 'multivariate_comparisons'}],
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
    conn.close()

    return "Data successfully inserted!"

# Handle CSV Export
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    if n_clicks:
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            query = "SELECT * FROM homicide_news"
            df = pd.read_sql(query, conn)
            return dcc.send_data_frame(df.to_csv, "homicide_complete.csv")



# Handle CSV Upload
@app.callback(
    Output('upload-output-1', 'children'),
    Input('upload-data-1', 'contents'),
    prevent_initial_call=True
)
def upload_csv(contents):
    if contents:
        # Split the contents into metadata and base64-encoded data
        content_type, content_string = contents.split(',')
        
        # Decode the base64-encoded string
        decoded = base64.b64decode(content_string)

        try:
            # Specify semicolon as the delimiter and handle bad lines
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=';', on_bad_lines='skip')
            print(df.head())  # Print first few rows for debugging
            
            # Try appending the data to the database
            df.to_sql('homicide_news', engine, if_exists='append', index=False)
            return "CSV data appended successfully."

        except pd.errors.ParserError as e:
            return f"Parsing error: {e}"

        except UnicodeDecodeError as e:
            return f"Decoding error: {e}"

        except Exception as e:
            return f"An error occurred: {e}"

    return "No contents provided."


@app.callback(
    Output('upload-output-2', 'children'),
    Input('upload-data-2', 'contents'),
    prevent_initial_call= True
)
def upload_csv_to_new_table(contents):
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep = ';', on_bad_lines='skip')
            df.to_sql('homicide_complete', engine, if_exists='append', index = False)
            return "CSV data appended to a table homicide_complete successfully."
        except pd.errors.ParserError as e:
            return f"Parsing error: {e}"
        except UnicodeDecodeError as e:
            return f"An error occured: {e}"
        
        except Exception as e:
            return f"An error occurred: {e}"
    return "No contents provided"

@app.callback(
    [Output('duplicates-message', 'children'),
     Output('table-container', 'children')],
    [Input('check-duplicates-button', 'n_clicks'),
     Input('delete-duplicates-button', 'n_clicks'),
     Input('display-button', 'n_clicks'),
     Input('column-checklist', 'value'),
     Input('delete-record-button', 'n_clicks')],
    [State('duplicate-column-input', 'value'),
     State('delete-record-input', 'value')]
)

# def update_data_display(check_clicks, delete_clicks, selected_columns, duplicate_columns):
#     return handle_duplicates_and_display(check_clicks, delete_clicks, selected_columns, duplicate_columns)
def update_data_display(check_clicks, delete_clicks, display_clicks, selected_columns,delete_clicks_data, duplicate_columns, delete_record_id):
    ctx = dash.callback_context
    if not ctx.triggered:
        print("No input was triggered.")
        return dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"Triggered by: {triggered_id}")

    if triggered_id == 'check-duplicates-button':
        message = check_duplicates(check_clicks, duplicate_columns)
        return message, dash.no_update
    elif triggered_id == 'delete-duplicates-button':
        message, table = delete_duplicates(delete_clicks, duplicate_columns, selected_columns)
        return message, table
    elif triggered_id == 'delete-record-button':
        print(f"Attempting to delete record with ID: {delete_record_id}")
        message, table = delete_record(delete_clicks_data, delete_record_id, selected_columns)
        print(f"Delete operation result: {message}")
        return message, table
    elif triggered_id == 'display-button':
        message, table = display_selected_columns(display_clicks, selected_columns)
        print(f"display_selected_columns returned: message='{message}', table={'not None' if table is not None else 'None'}")
        return message, table

    print("No condition was met.")
    return dash.no_update, dash.no_update

# def display_selected_columns(selected_columns):
#     if not selected_columns:
#         return "No columns selected.", None
    
#     try:
#         with psycopg2.connect(
#             host="localhost", port="5432", database="homicide_main",
#             user="postgres", password="Khiz1234"
#         ) as conn:
#             query = f"SELECT {', '.join(selected_columns)} FROM homicide_news"
#             df = pd.read_sql_query(query, conn)
        
#         table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
#         return "", table  # Return empty string for 'duplicates-message' and the table
#     except Exception as e:
#         print(f"Error in display_selected_columns: {str(e)}")
#         return f"An error occurred: {str(e)}", None
def display_selected_columns(n_clicks, selected_columns):    
    if n_clicks is None or n_clicks == 0:
        return "Please click the 'Display Table' button to show data", None
    
    if not selected_columns:
        print("No columns selected.")
        return "No columns selected. Please select atleast one column", None

    try:
        # if isinstance(selected_columns, str):
        #     selected_columns = [selected_columns]
            
        print(f"Attempting to fetch data for columns: {', '.join(selected_columns)}")
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            query = f"SELECT {', '.join(selected_columns)} FROM homicide_news"  
            print(f"Executing query: {query}")
            df = pd.read_sql_query(query, conn)
        
        print(f"Query executed successfully. Dataframe shape: {df.shape}")
        if df.empty:
            print("The resulting dataframe is empty.")
            return "No data found for the selected columns.", None
        
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        print("Table created successfully.")
        return "", table  # Return empty string for 'duplicates-message' and the table
    except Exception as e:
        error_msg = f"Error in display_selected_columns: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, None
    

# def handle_duplicates_and_display(check_clicks, delete_clicks, selected_columns, duplicate_columns):
#     ctx = callback_context
#     if not ctx.triggered:
#         return dash.no_update, dash.no_update
    
#     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

#     if triggered_id == 'check-duplicates-button':
#         return check_duplicates(check_clicks, duplicate_columns), dash.no_update
#     elif triggered_id == 'delete-duplicates-button':
#         message, table = delete_duplicates(delete_clicks, duplicate_columns)
#         return message, table
#     elif triggered_id == 'column-checklist':
#         message, table = display_selected_columns(selected_columns)
#         return message, table

#     return dash.no_update, dash.no_update

def check_duplicates(n_clicks, columns):
    if n_clicks is None or n_clicks == 0:
        return ""

    if not columns:
        return "Please enter one or more columns to check for duplicates."

    column_list = [col.strip() for col in columns.split(',')]
    
    with psycopg2.connect(
        host="localhost", port="5432", database="homicide_main",
        user="postgres", password="Khiz1234"
    ) as conn:
        query = f"""
            SELECT {', '.join(column_list)}, COUNT(*) 
            FROM homicide_news 
            GROUP BY {', '.join(column_list)}
            HAVING COUNT(*) > 1
        """
        df = pd.read_sql(query, conn)
    print("Hello there_check dup")
    if df.empty:
        return "No duplicate records found based on the selected columns."
    else:
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

# def delete_duplicates(n_clicks, column_name, columns_to_display):
#     if n_clicks == 0 or not column_name:
#         return '', dash.no_update
    
#     try:
#         with psycopg2.connect(
#             host="localhost", port="5432", database="homicide_main",
#             user="postgres", password="Khiz1234"
#         ) as conn:
#             with conn.cursor() as cursor:
#                 # Check if the column exists
#                 cursor.execute(f"""
#                     SELECT column_name 
#                     FROM information_schema.columns 
#                     WHERE table_name='homicide_news' AND column_name='{column_name}'
#                 """)
#                 if not cursor.fetchone():
#                     return f"Column '{column_name}' not found.", dash.no_update

#                 # Create duplicates table if it doesn't exist
#                 cursor.execute("""
#                     CREATE TABLE IF NOT EXISTS duplicates (
#                         LIKE homicide_news INCLUDING ALL
#                     )
#                 """)

#                 # Insert duplicates into the duplicates table
#                 cursor.execute(f"""
#                     INSERT INTO duplicates
#                     SELECT * FROM homicide_news
#                     WHERE {column_name} IN (
#                         SELECT {column_name}
#                         FROM homicide_news
#                         GROUP BY {column_name}
#                         HAVING COUNT(*) > 1
#                     )
#                 """)

#                 # Count the number of duplicates
#                 cursor.execute(f"""
#                     SELECT COUNT(*) FROM duplicates
#                 """)
#                 duplicate_count = cursor.fetchone()[0]

#                 # Delete duplicates from the main table
#                 cursor.execute(f"""
#                     DELETE FROM homicide_news
#                     WHERE ctid NOT IN (
#                         SELECT MIN(ctid)
#                         FROM homicide_news
#                         GROUP BY {column_name}
#                     )
#                 """)

#                 # Fetch the cleaned data
#                 cursor.execute(f"SELECT {', '.join(columns_to_display)} FROM homicide_news")
#                 cleaned_data = cursor.fetchall()
                
#                 conn.commit()

#             # Create DataFrame from cleaned data
#             df_cleaned = pd.DataFrame(cleaned_data, columns=columns_to_display)
#             table = dbc.Table.from_dataframe(df_cleaned, striped=True, bordered=True, hover=True)

#             return f"{duplicate_count} duplicates deleted and saved to 'duplicates' table.", table
#     except Exception as e:
#         print(f"Error in delete_duplicates: {str(e)}")  # Log the error
#         return f"An error occurred: {str(e)}", dash.no_update
#     print("Hello there_delete dup")
    
def delete_duplicates(n_clicks, column_name, columns_to_display):
    if n_clicks == 0 or not column_name:
        return '', dash.no_update
    
    try:
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            with conn.cursor() as cursor:
                # Check if the column exists
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='homicide_news' AND column_name='{column_name}'
                """)
                if not cursor.fetchone():
                    return f"Column '{column_name}' not found.", dash.no_update

                # Create duplicates table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS duplicates (
                        LIKE homicide_news INCLUDING ALL
                    )
                """)

                # Insert duplicates into the duplicates table, ignoring conflicts
                cursor.execute(f"""
                    INSERT INTO duplicates
                    SELECT * FROM homicide_news
                    WHERE {column_name} IN (
                        SELECT {column_name}
                        FROM homicide_news
                        GROUP BY {column_name}
                        HAVING COUNT(*) > 1
                    )
                    ON CONFLICT (article_id) DO NOTHING
                """)

                # Count the number of duplicates
                cursor.execute(f"""
                    SELECT COUNT(*) FROM (
                        SELECT {column_name}
                        FROM homicide_news
                        GROUP BY {column_name}
                        HAVING COUNT(*) > 1
                    ) as subquery
                """)
                duplicate_count = cursor.fetchone()[0]

                # Delete duplicates from the main table
                cursor.execute(f"""
                    DELETE FROM homicide_news
                    WHERE ctid NOT IN (
                        SELECT MIN(ctid)
                        FROM homicide_news
                        GROUP BY {column_name}
                    )
                """)

                # Fetch the cleaned data
                cursor.execute(f"SELECT {', '.join(columns_to_display)} FROM homicide_news")
                cleaned_data = cursor.fetchall()
                
                conn.commit()

            # Create DataFrame from cleaned data
            df_cleaned = pd.DataFrame(cleaned_data, columns=columns_to_display)
            table = dbc.Table.from_dataframe(df_cleaned, striped=True, bordered=True, hover=True)

            return f"{duplicate_count} duplicate groups found. Duplicates removed from main table and saved to 'duplicates' table.", table
    except Exception as e:
        print(f"Error in delete_duplicates: {str(e)}")  # Log the error
        return f"An error occurred: {str(e)}", dash.no_update

# @app.callback(
#     [Output('delete-record-message', 'children')]
# )
# def delete_record(n_clicks, article_id, selected_columns):
#     if n_clicks is None or n_clicks == 0:
#         return '', dash.no_update
    
#     if not article_id: 
#         return "Please enter an article_id to delete the data entry.", dash.no_update
    
#     try: 
#         with psycopg2.connect(
#             host = "localhost", port = "5432", database = "homicide_main",
#             user = "postgres", password = "Khiz1234"
#         ) as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute("DELETE FROM homicide_news WHERE article_id = %s", (article_id,))
#                 delete_count = cursor.rowcount
                
#             if delete_count == 0:
#                 return "No record found with article_id {article_id}.", dash.no_update
        
#         # Fetch the updated data
#             query = f"SELECT {', '.join(selected_columns)} FROM homicide_news"
#             df = pd.read_sql_query(query, conn)
                
#             conn.commit()
        
#         table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
#         return f"Record with article_id {article_id} has been deleted.", table
    
#     except Exception as e:
#         print(f"Error in delete_record: {str(e)}")
#         return f"An error occurred: {str(e)}", dash.no_update


#This one works, please remember that or else it will be a problem.
######################################################################

def delete_record(n_clicks, article_id, selected_columns):
    if not article_id or n_clicks == 0:
        return '', dash.no_update
    
    if not article_id: 
        return "Please enter an article_id to delete the data entry.", dash.no_update
    
    try:
        # Convert article_id to integer
        article_id = int(article_id)
        
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM homicide_news WHERE article_id = %s", (article_id,))
                delete_count = cursor.rowcount
                
            if delete_count == 0:
                return f"No record found with article_id {article_id}.", dash.no_update
            
            # Fetch the updated data
            query = f"SELECT {', '.join(selected_columns)} FROM homicide_news"
            df = pd.read_sql_query(query, conn)
                    
            conn.commit()
        
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        return f"Record with article_id {article_id} has been deleted.", table
    
    except ValueError:
        return "Invalid article_id. Please enter a valid integer.", dash.no_update
    except Exception as e:
        print(f"Error in delete_record: {str(e)}")
        return f"An error occurred: {str(e)}", dash.no_update
#################################################
#the new delete that might not work

# def delete_record(n_clicks, article_id, selected_columns):
#     if n_clicks == 0 or not article_id:
#         return '', dash.no_update
    
#     try:
#         article_id = int(article_id)
#         with psycopg2.connect(
#             host="localhost", port="5432", database="homicide_main",
#             user="postgres", password="Khiz1234"
#         ) as conn:
#             with conn.cursor() as cursor:
#                 # Check if the column exists
#                 cursor.execute(f"""
#                     SELECT column_name 
#                     FROM information_schema.columns 
#                     WHERE table_name='homicide_news' AND column_name='{article_id}'
#                 """)
#                 if not cursor.fetchone():
#                     return "Error: 'article_id' column does not exist in the table.", dash.no_update
                
#                 # Check if the article_id exists in the table
#                 cursor.execute(f"SELECT 1 FROM homicide_news WHERE article_id = %s", (article_id,))
#                 if not cursor.fetchone():
#                     return f"Article id '{article_id}' not found.", dash.no_update


#                 # Create duplicates table if it doesn't exist
#                 cursor.execute("""
#                     CREATE TABLE IF NOT EXISTS duplicates (
#                         LIKE homicide_news INCLUDING ALL
#                     )
#                 """)

#                 # # Insert duplicates into the duplicates table, ignoring conflicts
#                 # cursor.execute(f"""
#                 #     INSERT INTO duplicates
#                 #     SELECT * FROM homicide_news
#                 #     WHERE {article_id} IN (
#                 #         SELECT {article_id}
#                 #         FROM homicide_news
#                 #         GROUP BY {article_id}
#                 #     )
#                 #     ON CONFLICT (article_id) DO NOTHING
#                 # """)
                
#                 # Insert the record to be deleted into the duplicates table
#                 cursor.execute("""
#                     INSERT INTO duplicates
#                     SELECT * FROM homicide_news
#                     WHERE article_id = %s
#                 """, (article_id,))
                
#                  # Delete the record from the main table
#                 cursor.execute("DELETE FROM homicide_news WHERE article_id = %s", (article_id,))

#                 # # Count the number of duplicates
#                 # cursor.execute(f"""
#                 #     SELECT COUNT(*) FROM (
#                 #         SELECT {article_id}
#                 #         FROM homicide_news
#                 #         GROUP BY {article_id}
#                 #     ) as subquery
#                 # """)
#                 # duplicate_count = cursor.fetchone()[0]

#                 # # Delete duplicates from the main table
#                 # cursor.execute(f"""
#                 #     DELETE FROM homicide_news
#                 #     WHERE ctid NOT IN (
#                 #         SELECT MIN(ctid)
#                 #         FROM homicide_news
#                 #         GROUP BY {article_id}
#                 #     )
#                 # """)
                
                
#                 cursor.execute(f"SELECT {', '.join(selected_columns)} FROM homicide_news")
#                 cleaned_data = cursor.fetchall()
                
#                 conn.commit()

#             # Create DataFrame from cleaned data
#             df_cleaned = pd.DataFrame(cleaned_data, columns=selected_columns)
#             table = dbc.Table.from_dataframe(df_cleaned, striped=True, bordered=True, hover=True)

#             return f"The record with the article_id {article_id} has been deleted from the table and saved in the duplicates table.", table
#     except Exception as e:
#         print(f"Error in delete_record: {str(e)}")  # Log the error
#         return f"An error occurred: {str(e)}", dash.no_update

                
                
    #             # Fetch the cleaned data
    #             cursor.execute(f"SELECT {', '.join(selected_columns)} FROM homicide_news")
    #             cleaned_data = cursor.fetchall()
                
    #             conn.commit()

    #         # Create DataFrame from cleaned data
    #         df_cleaned = pd.DataFrame(cleaned_data, columns=selected_columns)
    #         table = dbc.Table.from_dataframe(df_cleaned, striped=True, bordered=True, hover=True)

    #         return f"The record with the article_id {article_id} is deleted from the table and saved in the duplicates table. ", table
    # except Exception as e:
    #     print(f"Error in delete_record: {str(e)}")  # Log the error
    #     return f"An error occurred: {str(e)}", dash.no_update




# # Handle Plot Type Dropdown based on Plot Category
# @app.callback(
#     Output('plot-type-dropdown', 'options'),
#     Input('plot-category-dropdown', 'value'),
# )

# def update_plot_type_dropdown(category_value):
#     if category_value == 'homicides_over_time':
#         return [{'label': 'Line Plot', 'value': 'line_plot'}, {'label': 'Bar Chart', 'value': 'bar_chart'}]
#     if category_value == 'geographical_distribution':
#         return [{'label': 'Choropleth Map', 'value' : 'choropleth_map'}, {'label' : 'Heat Map', 'value' : 'heat_map'}]
#     return []

# @app.callback(
#     Output('plot-container', 'children'),
#     Input('plot-category-dropdown', 'value'),
#     Input('plot-type-dropdown', 'value'),
# )

# def render_plot(category_value, plot_type_value):
#     fig = None  # Initialize fig to None

#     if not category_value or not plot_type_value:
#         return "Please select a plot type."

#     if category_value == 'homicides_over_time':
#         query = """
#             SELECT victim_name, date_of_death 
#             FROM homicide_news
#             GROUP BY victim_name, date_of_death
#         """
#         df = pd.read_sql(query, engine)
#         df['date_of_death'] = pd.to_datetime(df['date_of_death'])
#         df['year_of_death'] = df['date_of_death'].dt.year
#         data = df.groupby('year_of_death').size().reset_index(name='count')

#         if plot_type_value == 'line_plot':
#             fig = px.line(data, x='year_of_death', y='count', title='Homicides Over Time')
#         elif plot_type_value == 'bar_chart':
#             fig = px.bar(data, x='year_of_death', y='count', title='Homicides Over Time')
        
#     elif category_value == 'geographical_distribution':
#         query = """
#             SELECT place_of_death_province, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
#             FROM homicide_news 
#             GROUP BY place_of_death_province
#         """
#         df = pd.read_sql(query, engine)

#         if plot_type_value == 'choropleth_map':
#             fig = px.choropleth(df, 
#                                 geojson=geojson_data, 
#                                 locations='place_of_death_province', 
#                                 featureidkey="properties.name", 
#                                 color='count', 
#                                 title='Homicides by Province',
#                                 scope='africa')

#             fig.update_geos(fitbounds="locations")  # Focus on South Africa
        
#         elif plot_type_value == 'heat_map':
#             query = """
#                 SELECT latitude, longitude, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
#                 FROM homicide_news 
#                 WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
#                 GROUP BY latitude, longitude
#             """
#             df = pd.read_sql(query, engine)

#             fig = px.density_mapbox(df, 
#                                     lat='latitude', 
#                                     lon='longitude', 
#                                     z='count', 
#                                     radius=10,
#                                     center=dict(lat=-30, lon=25),  
#                                     zoom=5,
#                                     mapbox_style="stamen-terrain",
#                                     title='Heat Map of Homicides')

#     if fig:
#         return dcc.Graph(figure=fig)
    
#     return "Please select a plot type."

# Handle Plot Type Dropdown based on Plot Category
@app.callback(
    Output('plot-type-dropdown', 'options'),
    Input('plot-category-dropdown', 'value'),
)
def update_plot_type_dropdown(category_value):
    if category_value == 'homicides_over_time':
        return [{'label': 'Line Plot', 'value': 'line_plot'}, {'label': 'Bar Chart', 'value': 'bar_chart'}]
    elif category_value == 'geographical_distribution':
        return [{'label': 'Choropleth Map', 'value': 'choropleth_map'}, {'label': 'Heat Map', 'value': 'heat_map'}]
    elif category_value == 'demographic_insights':
        return [
            {'label': 'Bar Chart (Race Breakdown)', 'value': 'race_bar_chart'}, 
            {'label': 'Age Distribution Histogram', 'value': 'age_histogram'},
            {'label': 'Gender Comparison Plot', 'value': 'gender_comparison'}
        ]
    elif category_value == 'victim_perpetrator_relationship':
        return [{'label': 'Relationship Bar Chart', 'value': 'relationship_bar_chart'}, {'label': 'Heatmap', 'value': 'relationship_heatmap'}]
    elif category_value == 'multivariate_comparisons':
        return [{'label': 'Scatter Plot', 'value': 'scatter_plot'}, {'label': 'Bubble Plot', 'value': 'bubble_plot'}]
    return []

# Render Plot Based on Selected Category and Plot Type
@app.callback(
    Output('plot-container', 'children'),
    Input('plot-category-dropdown', 'value'),
    Input('plot-type-dropdown', 'value'),
)
def render_plot(category_value, plot_type_value):
    fig = None  # Initialize fig to None

    if not category_value or not plot_type_value:
        return "Please select a plot type."

    # Homicides Over Time
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

    # Geographical Distribution
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

    # Demographic Insights
    elif category_value == 'demographic_insights':
        if plot_type_value == 'race_bar_chart':
            query = """
                SELECT race_of_victim, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
                FROM homicide_news 
                GROUP BY race_of_victim
            """
            df = pd.read_sql(query, conn)
            fig = px.bar(df, x='race_of_victim', y='count', title='Race Breakdown of Victims')

        elif plot_type_value == 'age_histogram':
            query = """
                SELECT DISTINCT ON (victim_name, date_of_death) age_of_victim
                FROM homicide_news
                WHERE age_of_victim IS NOT NULL
            """
            df = pd.read_sql(query, conn)

            if df.empty:
                return "No valid age data available."
            
            fig = px.histogram(df, x='age_of_victim', nbins=20, title='Age Distribution of Homicide Victims')

        elif plot_type_value == 'gender_comparison':
            query = """
                SELECT perpetrator_gender, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
                FROM homicide_news
                WHERE perpetrator_gender IS NOT NULL
                GROUP BY perpetrator_gender
            """
            df = pd.read_sql(query, conn)
            fig = px.bar(df, x='perpetrator_gender', y='count', title='Gender Comparison of Perpetrators')

    # Category: Victim-Perpetrator Relationship
    elif category_value == 'victim_perpetrator_relationship':
        if plot_type_value == 'relationship_bar_chart':
            query = """
                SELECT perpetrator_relationship_to_victim, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
                FROM homicide_news 
                WHERE perpetrator_relationship_to_victim IS NOT NULL
                GROUP BY perpetrator_relationship_to_victim
            """
            df = pd.read_sql(query, conn)

            fig = px.bar(df, 
                         x='perpetrator_relationship_to_victim', 
                         y='count', 
                         title='Homicides by Victim-Perpetrator Relationship')

        elif plot_type_value == 'relationship_heatmap':
            query = """
                SELECT perpetrator_relationship_to_victim, mode_of_death_specific, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
                FROM homicide_news 
                WHERE perpetrator_relationship_to_victim IS NOT NULL AND mode_of_death_specific IS NOT NULL
                GROUP BY perpetrator_relationship_to_victim, mode_of_death_specific
            """
            df = pd.read_sql(query, conn)

            fig = px.density_heatmap(df, 
                                     x='perpetrator_relationship_to_victim', 
                                     y='mode_of_death_specific', 
                                     z='count', 
                                     title='Relationship vs Mode of Death Heatmap')

    elif category_value == 'multivariate_comparisons':
        if  plot_type_value == 'scatter_plot':
                query = """
                    SELECT type_of_location, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as homicide_count 
                    FROM homicide_news 
                    WHERE type_of_location IS NOT NULL 
                    GROUP BY type_of_location
                """
                df = pd.read_sql(query, conn)

                # Scatter plot of location type vs homicide count
                fig = px.scatter(
                    df,
                    x='type_of_location', 
                    y='homicide_count',
                    title='Location Type vs Homicide Count',
                    labels={
                        'type_of_location': 'Location Type',
                        'homicide_count': 'Homicide Count'
                    },
                    size='homicide_count',  # Size of points by homicide count
                    color='homicide_count'  # Color points by homicide count
                )
                fig.update_traces(marker_size=10) 

        elif plot_type_value == 'bubble_plot':
            query = """
                SELECT mode_of_death_specific, suspect_convicted, COUNT(DISTINCT victim_name || ' ' || date_of_death::text) as count 
                FROM homicide_news 
                WHERE mode_of_death_specific IS NOT NULL AND suspect_convicted IS NOT NULL
                GROUP BY mode_of_death_specific, suspect_convicted
            """
            df = pd.read_sql(query, conn)

            fig = px.scatter(df, 
                             x='mode_of_death_specific', 
                             y='suspect_convicted', 
                             size='count', 
                             color='suspect_convicted', 
                             title='Mode of Death vs Conviction Rates with Frequency Bubble Size')

    if fig:
        return dcc.Graph(figure=fig)

    return "Please select a plot type."


if __name__ == '__main__':
    app.run_server(debug=True)