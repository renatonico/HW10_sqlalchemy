
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation values:"
        f"/api/precipitation<br/>"
        f"Weather station list:"
        f"/api/stations<br/>"
        f"Temperature values:"
        f"/api/temperature<br/>"
        f"Enter a start date to get min,max and avg temps:"
        f"/api/yyyy-mm-dd<br/>"
        f"Enter start and end dates to get min,max and avg temps:"
        f"/api/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"<br/>"
        f"NOTE THAT:<br/>"
        f"Dates must be in the format YYYY-MM-DD (numeric)<br/>"
        f"Dates range from 2010-01-01 to 2017-08-23<br/>"
    )


@app.route("/api/precipitation")
def precipitation():
    """Return the JSON representation of the dictionary result from the query"""
    # Calculate the date 1 year ago from the last data point in the database
    last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date_str[0],"%Y-%m-%d").date()
    year_ago = last_date - dt.timedelta(days=365)
    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    #prpc = list(np.ravel(results))

    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    dictreturn = dict(results)

    return jsonify(dictreturn)

@app.route("/api/stations")
def stations():
    """Return the JSON list of stations"""
    # Perform a query to retrieve the stations names
    results = session.query(Station.name).all()
    
    return jsonify(results)

@app.route("/api/temperature")
def temperature():
    """Return the JSON representation of the dictionary result from the query"""
    # Calculate the date 1 year ago from the last data point in the database
    last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date_str[0],"%Y-%m-%d").date()
    year_ago = last_date - dt.timedelta(days=365)
    # Perform a query to retrieve the date and temperature
    results = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= year_ago).all()

    # Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    dictreturn = dict(results)

    return jsonify(dictreturn)

@app.route("/api/", defaults={"start":"2010-01-01"})
@app.route("/api/<start>")
def start(start):
   
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    from_temps = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        from_temps.append(temp_dict)

    return jsonify(from_temps)


@app.route("/api/", defaults={"start":"2010-01-01","end":"2017-08-23"})
@app.route("/api/<start>/<end>")
def startend(start,end):
   
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_temps = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        all_temps.append(temp_dict)

    return jsonify(all_temps)

if __name__ == '__main__':
    app.run(debug=True)
