import os

import pandas as pd
import numpy as np

import requests

import api_config

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


@app.route("/")
def index():
    """Homepage requested."""
    return render_template("index.html")

# Example starter
@app.route("/names")
def names():
    """Return a list of sample names."""

    text = 'some text'

    # Return a list of the column names (sample names)
    return (text)

@app.route("/data")
def newnames():
    """Data requested"""
    # Create the url
    baseURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude='
    lat = '30.276930'
    lon = '-97.743102'
    queryURL = baseURL + lat + '&longitude=' + lon
    #queryURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude=30.276930&longitude=-97.743102'
    # Headers for the request
    headers = {
        'Accept': 'application/json',
        'APIKey': api_config.api_key_atomm
        }

    response = requests.get(queryURL, headers=headers)
    print(response)

    print(queryURL)

    # Return the property data in JSON format
    return (queryURL)


if __name__ == "__main__":
    app.run()
