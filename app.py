# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

import numpy as np
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
# Use the Base class to reflect the database tables
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
measurement = Base.classes.measurement
station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Welcome - this is the API page for the Hawaii precipitation data as part of the SQLAlchemy Challenge")
    return (
        f"Available Routes:<br/>"
        "<br/>"
        f"Static Routes:<br/>"
        f"/api/v1.0/precipitation - view all precipitation data<br/>"
        f"/api/v1.0/stations - view details of the data collection stations<br/>"
        f"/api/v1.0/tobs - view info from the most active station in the last year of data collected<br/>"
        "<br/>"
        f"Dynamic Routes:<br/>"
        f"/api/v1.0/yyyy-mm-dd -  this is the START date<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd -  this reflects a <START date> / <END date> timeframe<br/>"
    )

#----------------------------------------------------------------

# precipitation (static)
@app.route("/api/v1.0/precipitation")

def precipitation():
    print('Precipitation data request made...')

    # obtain the date and precipitation
    precipitation_data = session.query(measurement.date, measurement.prcp).all()
    session.close()

    # precip dictionary to jsonify
    precip_dict = {}
    for date, prcp in precipitation_data:
        precip_dict[date] = prcp

    # jsonify
    return jsonify(precip_dict)

#----------------------------------------------------------------

# stations (static)
@app.route("/api/v1.0/stations")

def stations():
    print('Station data request made...')

    # Query to get station data
    station_data = session.query(station.name, station.station, station.latitude, station.longitude, station.elevation).distinct().all()
    session.close()

    # station dictionary to jsonify
    station_dict = {}
    for name, station_id, latitude, longitude, elevation in station_data:
        station_dict[station_id] = {
            "name": name,
            "station": station_id,
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation
        }

    # jsonify
    return jsonify(station_dict)

#----------------------------------------------------------------

# most active station for past year
@app.route("/api/v1.0/tobs")
def tobs():
    print("Details of most active station request made...")

    # Query to get the details of the most active station (in last 365 days of data)
    most_active = session.query(measurement.date, measurement.tobs).filter(measurement.station == "USC00519281").filter(measurement.date >= dt.date(2016, 8, 23)).all()
    session.close()

    # Convert query results into a list of dictionaries
    most_active_list = []
    for date, tobs in most_active:
        most_active_dict = {
            "Date": date,
            "Temperature": tobs
                           }
        most_active_list.append(most_active_dict)

    # jsonify
    return jsonify(most_active_list)

#----------------------------------------------------------------

# Dynamic route - listing a start date and retrieving max/min/avg
@app.route("/api/v1.0/<start>")
def dynamic_start(start):
    print("Request for max/min/avg with a start date given...")

    # Convert `start` string to a date object to ensure correct date format
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400

    # Query using the converted start date
    start_query = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
                    filter(measurement.date >= start_date).all()
    session.close()

    # Convert query result into a dictionary
    temps_start_dict = {
        "Min": start_query[0][0],
        "Average": start_query[0][1],
        "Max": start_query[0][2]
    }

    # jsonify
    return jsonify(temps_start_dict)
#----------------------------------------------------------------

# Dynamic route - listing a start date & end date, retrieving max/min/avg
@app.route("/api/v1.0/<start_date>/<end_date>")
def dynamic_start_fin(start_date,end_date):
    print(f"Request for max/min/avg with date range from {start_date} to {end_date}...")

    # Convert `start_date` and `end_date` strings to date objects
    try:
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
        
    # Query for temperature statistics between the start and end dates
    query_result = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
                    filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    # Convert query result into a dictionary
    temps_range_dict = {
        "Start Date": str(start_date),
        "End Date": str(end_date),
        "Min Temperature": query_result[0][0],
        "Average Temperature": query_result[0][1],
        "Max Temperature": query_result[0][2]
    }

    # jsonify
    return jsonify(temps_range_dict)

if __name__ == "__main__":
    app.run(debug=True)
