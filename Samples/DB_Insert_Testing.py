import requests
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import inspect
from sqlalchemy import Table
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.engine.url import URL

dbPass = '88653680Dd!'
engine = create_engine(f"postgresql://postgres:{dbPass}@localhost:5432/project2")
m = MetaData()

# Define the SQL table's structure
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

# Drop the table
tableSummary.drop(engine)

# Create the tables fresh
tableSummary.create(engine)

summary_id = [1, 2, 3]
city = ['sanfrancisco', 'sanfrancisco', 'sanfrancisco']
totalProperties = [1, 2, 3]
pricePerBed = [1, 2, 3]
pricePerBath = [1, 2, 3]
pricePerSquareFoot = [1, 2, 3]
averageBeds = [1, 2, 3]
averageBaths = [1, 2, 3]
averageYearBuilt = [1, 2, 3]

# Insert individual values
ins = tableSummary.insert().values(
    summary_id=1,
    city='city',
    totalProperties=1,
    pricePerBed=1,
    pricePerBath=1,
    pricePerSquareFoot=1,
    averageBeds=1,
    averageBaths=1,
    averageYearBuilt=2000
    )

# Insert as a list
# ins = tableSummary.insert().values(
#     summary_id=summary_id,
#     city=city,
#     totalProperties=totalProperties,
#     pricePerBed=pricePerBed,
#     pricePerBath=pricePerBath,
#     pricePerSquareFoot=pricePerSquareFoot,
#     averageBeds=averageBeds,
#     averageBaths=averageBaths,
#     averageYearBuilt=averageYearBuilt
#     )
conn = engine.connect()
conn.execute(ins)
