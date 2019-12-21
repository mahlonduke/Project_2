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
# Homepage/index route
@app.route("/")
def index():
    """Homepage requested."""

    # Configure the database connection

    # This engine is for testing locally
    # engine = create_engine(f"postgresql://postgres:{api_config.postgresPass}@localhost:5432/project2")
    # This engine is for use in Heroku
    engine = create_engine(f"postgresql://{api_config.pgUser}:{api_config.pgPass}@{api_config.pgHost}/{api_config.pgDB}")

    conn = engine.connect()
    m = MetaData()

    # Create the tables if they don't already exist
    conn.execute('CREATE TABLE IF NOT EXISTS sales (\
    	sale_id SERIAL PRIMARY KEY,\
    	city VARCHAR(20),\
    	lat FLOAT,\
    	lon FLOAT,\
    	squarefeet INT,\
    	yearBuilt INT,\
    	bathrooms FLOAT,\
    	bedrooms INT,\
    	saleprice FLOAT\
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
    	averageYearBuilt INT\
    );')

    # Define the table structure for queries to the 'sales' table
    tableSales = Table('sales', m,
        Column('city', String),
        Column('lat', Float, nullable=True),
        Column('lon', Float),
        Column('squarefeet', Integer),
        Column('bathrooms', Float),
        Column('bedrooms', Integer),
        Column('saleprice', Float),
        Column('yearbuilt', Integer)
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
        Column('averageyearbuilt', Integer)
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
            city = 'Chicago'
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
        # For just the summary table
        totalPrice = 0
        totalBeds = 0
        totalBaths = 0
        totalSquareFeet = 0
        totalProperties = len(propertyData)
        averageBeds = 0
        averageBaths = 0
        averageYearBuilt = 0

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

            # Insert the individual sale's data into the DB's sales table
            ins = tableSales.insert().values(
                city = city,
                lat = lat,
                lon = lon,
                squarefeet = squarefeet,
                bathrooms = bathrooms,
                bedrooms = bedrooms,
                saleprice = salePrice,
                yearbuilt = yearBuilt
                )
            conn.execute(ins)

            # Calculate the summary data from the individual sale data
            totalPrice += salePrice
            totalBaths += bathrooms
            totalBeds += bedrooms
            totalSquareFeet += squarefeet
            averageYearBuilt += yearBuilt

        # Calculate the averages
        pricePerBed =  round(totalPrice / totalBeds, 2)
        pricePerBath = round(totalPrice / totalBaths, 2)
        pricePerSquareFoot = round(totalPrice / totalSquareFeet, 2)
        averageBeds = totalBeds / totalProperties
        averageBaths = totalBaths / totalProperties
        averageYearBuilt = int(round(averageYearBuilt / totalProperties, 0))

        # Insert the summary data to the DB
        ins = tableSummary.insert().values(
            city=city,
            totalproperties=totalProperties,
            priceperbed=pricePerBed,
            priceperbath=pricePerBath,
            pricepersquarefoot=pricePerSquareFoot,
            averagebeds=averageBeds,
            averagebaths=averageBaths,
            averageyearbuilt=averageYearBuilt
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
# Boilerplate for running the code as an app through Flask
if __name__ == "__main__":
    app.run()
# ------------------------------------------------------------------------------
