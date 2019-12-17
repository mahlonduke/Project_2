import os

import pandas as pd
import numpy as np

import requests

import api_config

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Homepage/index route
@app.route("/")
def index():
    """Homepage requested."""
    return render_template("index.html")

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


if __name__ == "__main__":
    app.run()
