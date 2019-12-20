# ------------------------------------------------------------------------------
import requests
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import inspect
from sqlalchemy import Table
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.engine.url import URL

import api_config
# ------------------------------------------------------------------------------
app = Flask(__name__)
# ------------------------------------------------------------------------------
# Homepage/index route
@app.route("/")
def index():
    """Homepage requested."""

    # Configure the database connection
    engine = create_engine(f"postgresql://postgres:{api_config.postgresPass}@localhost:5432/project2")
    m = MetaData()

    # Define the SQL tables' structure
    tableSales = Table('sales', m,
        Column('sale_id', Integer, primary_key=True),
        Column('lat', Float, nullable=True),
        Column('lon', Float),
        Column('squarefeet', Integer),
        Column('bathrooms', Float),
        Column('bedrooms', Integer),
        Column('salePrice', Float),
        Column('yearBuilt', Integer)
        )

    tableSummary = Table('summary', m,
        Column('summary_id', Integer, primary_key=True),
        Column('city', String),
        Column('totalProperties', Integer),
        Column('pricePerBed', Float),
        Column('pricePerBath', Float),
        Column('pricePerSquareFoot', Float),
        Column('averageBeds', Float),
        Column('averageBaths', Integer),
        Column('averageYearBuilt', Integer)
    )

    # Drop the existing tables from the DB, so fresh data can be inserted
    tableSales.drop(engine)
    tableSummary.drop(engine)

    # Create the tables fresh so that new data can be inserted
    tableSales.create(engine)
    tableSummary.create(engine)

    # Function to handle the querying of data from the API.  Accepts a string which corresponds to the city you're pulling data on
    def pullData(city):
        if city == 'sanfrancisco':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=37.807570&longitude=-122.258336'
        elif city == 'newyork':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=40.711102&longitude=-74.000501'
        elif city == 'chicago':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=41.851808&longitude=-87.633122'
        elif city == 'denver':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=39.747891&longitude=-104.986956'
        elif city == 'austin':
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=30.276930&longitude=-97.743102'
        else:
            print(f"An invalid city was selected.  The selection was: {city}.")
            print(f"Returning San Francisco data by default")
            queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=37.807570&longitude=-122.258336'


        # Setup the headers for the request
        headers = {
            'Accept': 'application/json',
            'APIKey': api_config.api_key_atomm
            }

        # Get the data
        response = requests.get(queryURL, headers=headers)

        # Log the query URL to console for troubleshooting
        print(f"Query URL: {queryURL}")
        # Log the response code to console for troubleshooting
        print(f"Response code: {response}")

        # Pull just the valuable data out
        propertyData = response.json()['property']

        # Variables for tracking the property details
        # For both summary and sales tables
        tracker = 1

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
                sale_id = tracker,
                lat = lat,
                lon = lon,
                squarefeet = squarefeet,
                bathrooms = bathrooms,
                bedrooms = bedrooms,
                salePrice = salePrice,
                yearBuilt = yearBuilt
                )
            conn = engine.connect()
            conn.execute(ins)



            # Create the summary data from the individual sale data
            totalPrice += salePrice
            totalBaths += bathrooms
            totalBeds += bedrooms
            totalSquareFeet += squarefeet
            averageYearBuilt += yearBuilt

            # Increase the tracker for next iteration
            tracker += 1


        # Calculate the averages
        pricePerBed =  round(totalPrice / totalBeds, 2)
        pricePerBath = round(totalPrice / totalBaths, 2)
        pricePerSquareFoot = round(totalPrice / totalSquareFeet, 2)
        averageBeds = totalBeds / totalProperties
        averageBaths = totalBaths / totalProperties
        averageYearBuilt = int(round(averageYearBuilt / totalProperties, 0))

        # Insert the summary data to the DB
        ins = tableSummary.insert().values(
            summary_id=1,
            city=city,
            totalProperties=totalProperties,
            pricePerBed=pricePerBed,
            pricePerBath=pricePerBath,
            pricePerSquareFoot=pricePerSquareFoot,
            averageBeds=averageBeds,
            averageBaths=averageBaths,
            averageYearBuilt=averageYearBuilt
            )
        conn = engine.connect()
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
# Route to query the ATOMM API based on the user's selection
@app.route("/data/<selection>")
def queryAPI(selection):
    """Data requested"""

    # Print the selection variable for troubleshooting
    print(f"User's Selection: {selection}")

    # Create the URL, based on the selection variable's value
    if selection == 'sanfrancisco':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=37.807570&longitude=-122.258336'
    elif selection == 'newyork':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=40.711102&longitude=-74.000501'
    elif selection == 'chicago':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=41.851808&longitude=-87.633122'
    elif selection == 'denver':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=39.747891&longitude=-104.986956'
    else:
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=30.276930&longitude=-97.743102'

    # Setup the headers for the request
    headers = {
        'Accept': 'application/json',
        'APIKey': api_config.api_key_atomm
        }

    # Get the data
    response = requests.get(queryURL, headers=headers)

    # Log the query URL to console for troubleshooting
    print(f"Query URL: {queryURL}")
    # Log the response code to console for troubleshooting
    print(f"Response code: {response}")

    # Transverse the property object to eliminate unnecessary data structure in response, and
    # return it in JSON format
    return jsonify(response.json()['property'])


# ------------------------------------------------------------------------------
# Route to query the ATOMM API based on the user's selection, and calculate summary data
@app.route("/summary/<selection>")
def queryAPIsummary(selection):
    """Summary Data requested"""

    # Print the selection variable for troubleshooting
    print(f"User's Selection: {selection}")

    # Create the URL, based on the selection variable's value
    if selection == 'sanfrancisco':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=37.807570&longitude=-122.258336'
    elif selection == 'newyork':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=40.711102&longitude=-74.000501'
    elif selection == 'chicago':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=41.851808&longitude=-87.633122'
    elif selection == 'denver':
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=39.747891&longitude=-104.986956'
    else:
        queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=30.276930&longitude=-97.743102'

    # Setup the headers for the request
    headers = {
        'Accept': 'application/json',
        'APIKey': api_config.api_key_atomm
        }

    # Get the data
    response = requests.get(queryURL, headers=headers)

    # Log the query URL to console for troubleshooting
    print(f"Query URL: {queryURL}")
    # Log the response code to console for troubleshooting
    print(f"Response code: {response}")

    # Pull just the valuable data out
    propertyData = response.json()['property']


    # Variables for tracking the property details
    tracker = 1
    totalPrice = 0
    totalBeds = 0
    totalBaths = 0
    totalSquareFeet = 0
    totalProperties = len(propertyData)
    averageBeds = 0
    averageBaths = 0
    averageYearBuilt = 0

    # Loop through the response to pull out the property details
    for i in propertyData:
        totalPrice += i['sale']['amount']['saleamt']
        totalBaths += i['building']['rooms']['bathstotal']
        totalBeds += i['building']['rooms']['beds']
        totalSquareFeet += i['building']['size']['universalsize']
        # Ignore the year if it's 0 AKA unknown
        if i['summary']['yearbuilt'] != 0:
            averageYearBuilt += i['summary']['yearbuilt']
        tracker += 1


    # Calculate the averages
    pricePerBed =  round(totalPrice / totalBeds, 2)
    pricePerBath = round(totalPrice / totalBaths, 2)
    pricePerSquareFoot = round(totalPrice / totalSquareFeet, 2)
    averageBeds = totalBeds / totalProperties
    averageBaths = totalBaths / totalProperties
    averageYearBuilt = int(round(averageYearBuilt / totalProperties, 0))

    # Print the results for troubleshooting
    print(f"Total properties reviewed: {totalProperties}")
    print(f"Average price per bed: {pricePerBed}")
    print(f"Average price per bath: {pricePerBath}")
    print(f"Average price per square foot: {pricePerSquareFoot}")
    print(f"Average number of bedrooms per property: {averageBeds}")
    print(f"Average number of bathrooms per property: {averageBaths}")
    print(f"Average year built: {averageYearBuilt}")

    # Combine the results into a dictionary so that it can be returned
    results = {
        "Total Properties": totalProperties,
        "Average Price Per Bed": pricePerBed,
        "Average Price Per Bath": pricePerBath,
        "Average Price Per Square Foot": pricePerSquareFoot,
        "Average Number of Bedrooms": averageBeds,
        "Average Number of Bathrooms": averageBaths,
        "Average Year Built": averageYearBuilt
    }

    return jsonify(results)

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
# ------------------------------------------------------------------------------
