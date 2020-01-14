# ------------------------------------------------------------------------------
# Library dependencies
import requests
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import inspect
from sqlalchemy import Table
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.engine.url import URL

# Local file dependencies
import api_config
# ------------------------------------------------------------------------------
# Boilerplate for creating the app via Flask
app = Flask(__name__)
# ------------------------------------------------------------------------------
# Configure the database connection

# This engine is for testing locally
# engine = create_engine(f"postgresql://postgres:{api_config.postgresPass}@localhost:5432/project2")

# This engine is for use in Heroku
engine = create_engine(f"postgresql://{api_config.pgUser}:{api_config.pgPass}@{api_config.pgHost}/{api_config.pgDB}")

# This is for all connections
conn = engine.connect()
m = MetaData()
# ------------------------------------------------------------------------------
# Homepage/index route
@app.route("/")
def index():
    """Homepage requested."""

    # One-time commands (because TRUNCATE is used later on) to drop the sales and summary tables.  Meant to be used for Heroku, since local Postgres can have the commands run directly
    try:
        conn.execute('DROP TABLE IF EXISTS sales;')
        conn.execute('DROP TABLE IF EXISTS summary;')
    except:
        print("Drop table failed")

    # Create the tables if they don't already exist
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS sales (\
        	sale_id SERIAL PRIMARY KEY,\
        	city VARCHAR(20),\
        	lat FLOAT,\
        	lon FLOAT,\
        	squarefeet INT,\
        	bathrooms FLOAT,\
        	bedrooms INT,\
        	salePrice FLOAT,\
            yearBuilt INT,\
            saleYear INT\
        );')
        conn.execute('CREATE TABLE IF NOT EXISTS summary (\
        	summary_id SERIAL PRIMARY KEY,\
        	city VARCHAR(20),\
        	totalProperties INT,\
        	pricePerBed FLOAT,\
        	pricePerBath FLOAT,\
        	pricePerSquareFoot FLOAT,\
        	averageBeds INT,\
        	averageBaths INT,\
        	averageYearBuilt INT,\
            averageSaleYear INT\
        );')
    except:
        print("Table creation failed")

    # Define the table structure for queries to the 'sales' table
    tableSales = Table('sales', m,
        Column('city', String),
        Column('lat', Float, nullable=True),
        Column('lon', Float),
        Column('squarefeet', Integer),
        Column('bathrooms', Float),
        Column('bedrooms', Integer),
        Column('saleprice', Float),
        Column('yearbuilt', Integer),
        Column('saleyear', Integer),
        extend_existing=True
        )

    # Define the table structure for queries to the 'summary' table
    tableSummary = Table('summary', m,
        Column('city', String),
        Column('totalproperties', Integer),
        Column('priceperbed', Float),
        Column('priceperbath', Float),
        Column('pricepersquarefoot', Float),
        Column('averagebeds', Float),
        Column('averagebaths', Integer),
        Column('averageyearbuilt', Integer),
        Column('averagesaleyear', Integer),
        extend_existing=True
    )

    # Truncate the existing tables to remove any previous data
    conn.execute('TRUNCATE summary CASCADE;')
    conn.execute('TRUNCATE sales CASCADE;')

    # Function to handle the querying of data from the API.  Accepts a string which corresponds to the city you're pulling data on
    def pullData(city):
        # Set parameters based on the city whose data is being queries
        if city == 'sanfrancisco':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=37.807570&longitude=-122.258336'
            city = 'San Francisco'
        elif city == 'newyork':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=40.711102&longitude=-74.000501'
            city = 'New York'
        elif city == 'chicago':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=41.851808&longitude=-87.633122'
            city = 'Chicago'
        elif city == 'denver':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=39.747891&longitude=-104.986956'
            city = 'Denver'
        elif city == 'austin':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=30.276930&longitude=-97.743102'
            city = 'Austin'
        else:
            print(f"An invalid city was selected.  The selection was: {city}.")
            print(f"Returning San Francisco data by default")
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=37.807570&longitude=-122.258336'

        # Setup the headers for the request
        headers = {
            'Accept': 'application/json',
            'APIKey': api_config.api_key_atomm
            }

        # Request the data from the ATOMM API
        response = requests.get(queryURL, headers=headers)

        # Log the query URL to console for troubleshooting
        print(f"Query URL: {queryURL}")
        # Log the response code to console for troubleshooting
        print(f"Response code: {response}")

        # Pull just the valuable data out of the response
        propertyData = response.json()['property']

        # Variables for tracking the property details
        # For just the sales table
        lat = 0.00
        lon = 0.00
        squarefeet = 0
        yearBuilt = 0
        bathrooms = 0.00
        bedrooms = 0
        salePrice = 0.00
        saleYear = 0
        # For just the summary table
        totalPrice = 0
        totalBeds = 0
        totalBaths = 0
        totalSquareFeet = 0
        totalProperties = len(propertyData)
        averageBeds = 0
        averageBaths = 0
        averageYearBuilt = 0
        averageSaleYear = 0

        # Loop through the response
        for i in propertyData:
            # Pull out data on each individual sale
            lat = i['location']['latitude']
            lon = i['location']['longitude']
            squarefeet = i['building']['size']['universalsize']
            bathrooms = i['building']['rooms']['bathstotal']
            bedrooms = i['building']['rooms']['beds']
            salePrice = i['sale']['amount']['saleamt']
            yearBuilt = i['summary']['yearbuilt']
            saleYear = int(i['sale']['amount']['salerecdate'].split("-")[0])

            # Insert the individual sale's data into the DB's sales table
            ins = tableSales.insert().values(
                city = city,
                lat = lat,
                lon = lon,
                squarefeet = squarefeet,
                bathrooms = bathrooms,
                bedrooms = bedrooms,
                saleprice = salePrice,
                yearbuilt = yearBuilt,
                saleyear = saleYear
                )
            conn.execute(ins)

            # Calculate the summary data from the individual sale data
            totalPrice += salePrice
            totalBaths += bathrooms
            totalBeds += bedrooms
            totalSquareFeet += squarefeet
            averageYearBuilt += yearBuilt
            averageSaleYear += saleYear

        # Calculate the averages
        pricePerBed =  round(totalPrice / totalBeds, 2)
        pricePerBath = round(totalPrice / totalBaths, 2)
        pricePerSquareFoot = round(totalPrice / totalSquareFeet, 2)
        averageBeds = totalBeds / totalProperties
        averageBaths = totalBaths / totalProperties
        averageYearBuilt = int(round(averageYearBuilt / totalProperties, 0))
        averageSaleYear = int(round(averageSaleYear / totalProperties, 0))

        # Insert the summary data to the DB
        ins = tableSummary.insert().values(
            city=city,
            totalproperties=totalProperties,
            priceperbed=pricePerBed,
            priceperbath=pricePerBath,
            pricepersquarefoot=pricePerSquareFoot,
            averagebeds=averageBeds,
            averagebaths=averageBaths,
            averageyearbuilt=averageYearBuilt,
            averagesaleyear=averageSaleYear
            )
        conn.execute(ins)

        return None

    # Call the pullData function for each city
    pullData('sanfrancisco')
    pullData('newyork')
    pullData('chicago')
    pullData('denver')
    pullData('austin')

    return render_template("index.html")
# ------------------------------------------------------------------------------
# Data route for sales
@app.route("/sales/<location>/<date>")
def dataPullSales(location, date):
    """Sales data requested."""

    # Convert the supplied location into the capitalized format for querying Postgres
    if location == 'sanfrancisco':
        location = 'San Francisco'
    elif location == 'newyork':
        location = 'New York'
    elif location == 'chicago':
        location = 'Chicago'
    elif location == 'denver':
        location = 'Denver'
    elif location == 'austin':
        location = 'Austin'
    else:
        print(f"An invalid city was selected.  The selection was: {location}.")
        print(f"Returning San Francisco data by default")
        location = 'San Francisco'

    # Log the requested location and date to console for troubleshooting
    print(f"Sales data requested.")
    print(f"Location requested: {location}")
    print(f"Date requested: {date}")

    # Pull the sales data from the DB based on the supplied location and date
    salesResponse = conn.execute(f'SELECT * FROM sales WHERE city = \'{location}\' AND saleyear = {date};').fetchall()

    # Pull the data
    city = [r for r, in pullSaleData('city', location, date)]
    lat = [r for r, in pullSaleData('lat', location, date)]
    lon = [r for r, in pullSaleData('lon', location, date)]
    squarefeet = [r for r, in pullSaleData('squarefeet', location, date)]
    bathrooms = [r for r, in pullSaleData('bathrooms', location, date)]
    bedrooms = [r for r, in pullSaleData('bedrooms', location, date)]
    saleprice = [r for r, in pullSaleData('saleprice', location, date)]
    yearbuilt = [r for r, in pullSaleData('yearbuilt', location, date)]
    saleyear = [r for r, in pullSaleData('saleyear', location, date)]

    # Format the data to send as a JSON payload
    salesData = {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "squarefeet": squarefeet,
        "bathrooms": bathrooms,
        "bedrooms": bedrooms,
        "saleprice": saleprice,
        "yearbuilt": yearbuilt,
        "saleyear": saleyear
    }

    # Return the sales data as JSON
    return jsonify(salesData)
# ------------------------------------------------------------------------------
# Data route for summary
@app.route("/summary/<location>/<date>")
def dataPullSummary(location, date):
    """Summary data requested."""

    # Convert the supplied location into the capitalized format for querying Postgres
    if location == 'sanfrancisco':
        location = 'San Francisco'
    elif location == 'newyork':
        location = 'New York'
    elif location == 'chicago':
        location = 'Chicago'
    elif location == 'denver':
        location = 'Denver'
    elif location == 'austin':
        location = 'Austin'
    else:
        print(f"An invalid city was selected.  The selection was: {location}.")
        print(f"Returning San Francisco data by default")
        location = 'San Francisco'

    # Log the requested location and date to console for troubleshooting
    print(f"Summary data requested.")
    print(f"Location requested: {location}")
    print(f"Date requested: {date}")

    # Check for an empty result
    emptySetTest = [r for r, in pullSummaryData('city', location, date)]
    if emptySetTest == []:
        # Change the requested date to one with data for the selected city
        if location == 'San Francisco':
            date = 2013
        if location == 'New York':
            date = 2013
        if location == 'Chicago':
            date = 2014
        if location == 'Denver':
            date = 2015
        if location == 'Austin':
            date = 2014

    # Pull the data
    city = [r for r, in pullSummaryData('city', location, date)]
    totalproperties = [r for r, in pullSummaryData('totalproperties', location, date)]
    priceperbed = [r for r, in pullSummaryData('priceperbed', location, date)]
    priceperbath = [r for r, in pullSummaryData('priceperbath', location, date)]
    pricepersquarefoot = [r for r, in pullSummaryData('pricepersquarefoot', location, date)]
    averagebeds = [r for r, in pullSummaryData('averagebeds', location, date)]
    averagebaths = [r for r, in pullSummaryData('averagebaths', location, date)]
    averageyearbuilt = [r for r, in pullSummaryData('averageyearbuilt', location, date)]
    averagesaleyear = [r for r, in pullSummaryData('averagesaleyear', location, date)]

    # Format the data to send as a JSON payload
    summaryData = {
        "city": city,
        "totalproperties": totalproperties,
        "priceperbed": priceperbed,
        "priceperbath": priceperbath,
        "pricepersquarefoot": pricepersquarefoot,
        "averagebeds": averagebeds,
        "averagebaths": averagebaths,
        "averageyearbuilt": averageyearbuilt,
        "averagesaleyear": averagesaleyear
    }

    # Return the summary data as JSON
    return jsonify(summaryData)


# Income CSV file route
@app.route("/getIncomeCSV")
def getIncomeCSV():
    with open("income.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                     "attachment; filename=income.csv"})

   
# ------------------------------------------------------------------------------
# Function for pulling sale data from Postgres
def pullSaleData(column, location, date):
    response = conn.execute(f'SELECT {column} FROM sales WHERE city = \'{location}\' AND saleyear = {date};').fetchall()

    return (response)
# ------------------------------------------------------------------------------
# Function for pulling summary data from Postgres
def pullSummaryData(column, location, date):
    response = conn.execute(f'SELECT {column} FROM summary WHERE city = \'{location}\' AND averagesaleyear = {date};').fetchall()

    return (response)
# ------------------------------------------------------------------------------
# Boilerplate for running the code as an app through Flask
if __name__ == "__main__":
    app.run()
# ------------------------------------------------------------------------------
