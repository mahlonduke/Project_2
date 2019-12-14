import os

import pandas as pd
import numpy as np

import requests

from config import api_key

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


@app.route("/")
def index():
    """Homepage requested."""
    return render_template("index.html")


@app.route("/data")
def names():
    """Data requested"""
    # Create the url
    baseURL = 'https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/snapshot?pagesize=100&radius=50&latitude='
    lat = ''
    lon = ''
    queryURL = baseURL + lat + '&longitude=' + lon

    # Headers for the request
    headers = {
        'Accept': 'application/json',
        'APIKey': api_key
        }

    response = requests.get(queryURL, headers=headers)
    response = response['property']

    # Return the property data in JSON format
    return jsonify(response)


if __name__ == "__main__":
    app.run()
