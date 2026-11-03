import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/'
    'IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/'
    'historical_automobile_sales.csv'
)

# Initialize the Dash app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# List of years (1980 - 2023)
year_list = [i for i in range(1980, 2024, 1)]

# Month order for the monthly line chart
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# ---------------------------------------------------------------------------
# TASK 2.1: Title of the application
# ---------------------------------------------------------------------------
app.layout = html.Div([
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}
    ),

    # -----------------------------------------------------------------------
    # TASK 2.2: Dropdown menus (each one in its own division)
    # -----------------------------------------------------------------------
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            value='Select Statistics',
            placeholder='Select a report type',
            style={'width': '80%', 'padding': '3px', 'font-size': '20px',
                   'text-align-last': 'center'}
        )
    ]),

    html.Div([
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value='Select-year',
            placeholder='Select-year',
            style={'width': '80%', 'padding': '3px', 'font-size': '20px',
                   'text-align-last': 'center'}
        )
    ]),

    # -----------------------------------------------------------------------
    # TASK 2.3: Output division
    # -----------------------------------------------------------------------
    html.Div([
        html.Div(id='output-container', className='chart-grid',
                 style={'display': 'flex'}),
    ])
])


# ---------------------------------------------------------------------------
# TASK 2.4: Callbacks
# ---------------------------------------------------------------------------
# Enable / disable the year dropdown depending on the report type
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value'))
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True


# Build the four plots of the selected report
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')])
def update_output_container(selected_statistics, input_year):

    # -----------------------------------------------------------------------
    # TASK 2.5: Recession Period Statistics
    # -----------------------------------------------------------------------
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]

        # Plot 1: average automobile sales per year during recessions (line)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec,
                           x='Year',
                           y='Automobile_Sales',
                           title="Average Automobile Sales Fluctuation over Recession Period"))

        # Plot 2: average vehicles sold by vehicle type (bar)
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title="Average Number of Vehicles Sold by Vehicle Type during Recession"))

        # Plot 3: total advertising expenditure share by vehicle type (pie)
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec,
                          values='Advertising_Expenditure',
                          names='Vehicle_Type',
                          title="Total Expenditure Share by Vehicle Type during Recessions"))

        # Plot 4: effect of unemployment rate on vehicle type and sales (bar)
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data,
                          x='unemployment_rate',
                          y='Automobile_Sales',
                          color='Vehicle_Type',
                          labels={'unemployment_rate': 'Unemployment Rate',
                                  'Automobile_Sales': 'Average Automobile Sales'},
                          title='Effect of Unemployment Rate on Vehicle Type and Sales'))

        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart1), html.Div(children=R_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart3), html.Div(children=R_chart4)],
                     style={'display': 'flex'})
        ]

    # -----------------------------------------------------------------------
    # TASK 2.6: Yearly Statistics
    # (input_year must be a real year, not the initial 'Select-year' text)
    # -----------------------------------------------------------------------
    elif selected_statistics == 'Yearly Statistics' and input_year in year_list:
        yearly_data = data[data['Year'] == input_year]

        # Plot 1: yearly average automobile sales for the whole period (line)
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas,
                           x='Year',
                           y='Automobile_Sales',
                           title='Yearly Average Automobile Sales'))

        # Plot 2: total monthly automobile sales of the selected year (line)
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        mas['Month'] = pd.Categorical(mas['Month'], categories=month_order, ordered=True)
        mas = mas.sort_values('Month')
        Y_chart2 = dcc.Graph(
            figure=px.line(mas,
                           x='Month',
                           y='Automobile_Sales',
                           title='Total Monthly Automobile Sales'))

        # Plot 3: average vehicles sold by vehicle type in the selected year (bar)
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title='Average Vehicles Sold by Vehicle Type in the year {}'.format(input_year)))

        # Plot 4: total advertisement expenditure for each vehicle type (pie)
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                          values='Advertising_Expenditure',
                          names='Vehicle_Type',
                          title='Total Advertisment Expenditure for Each Vehicle'))

        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)],
                     style={'display': 'flex'})
        ]

    # Nothing selected yet
    return []


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
