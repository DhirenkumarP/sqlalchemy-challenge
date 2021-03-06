import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()

Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(engine)


most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
most_recent_date


most_recent_date_dt = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

first_date = most_recent_date_dt - dt.timedelta(days=365)
first_date_dt = dt.datetime.strftime(first_date,"%Y-%m-%d")

# Close the session
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"/api/v1.0/start_date/<start_date>/end_date/<end_date><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
   
    session = Session(engine)

    
    year_prcp = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date > first_date_dt).\
        order_by(Measurement.date).all()

    session.close()

    # Convert query results to dictionary
    date_list = []
    prcp_list = []

    for line in year_prcp:
        date_list.append(line[0])
        prcp_list.append(line[1])

    precipitation_dict = dict(zip(date_list,prcp_list))

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations ():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    station_query = session.query(Station.name).\
    group_by(Station.station).all()

    session.close()
    
    # Create list of stations
    station_list = [station[0] for station in station_query]

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs ():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    most_active_station = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station =='USC00519281').\
    filter(Measurement.date > first_date_dt).all()

    session.close()
    
    # Create list of temperature
    temp_list = [temp[1] for temp in most_active_station]

    return jsonify(temp_list)

@app.route('/api/v1.0/start_date/<start_date>')
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    start_date_clean = dt.datetime.strptime(start_date, "%Y-%m-%d")

    tmin_tavg_tmax = session.query(func.min(Measurement.tobs),\
     func.avg(Measurement.tobs),\
     func.max(Measurement.tobs)).\
    filter(Measurement.date <= start_date_clean).all()

    tmin_tavg_tmax_list = [i for i in tmin_tavg_tmax[0]]

    session.close()

    return jsonify(tmin_tavg_tmax_list)

@app.route('/api/v1.0/start_date/<start_date>/end_date/<end_date>')
def start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    start_date_clean = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date_clean = dt.datetime.strptime(end_date, "%Y-%m-%d")

    tmin_tavg_tmax = session.query(func.min(Measurement.tobs),\
     func.avg(Measurement.tobs),\
     func.max(Measurement.tobs)).\
    filter(Measurement.date <= start_date_clean).\
    filter(Measurement.date >= end_date_clean).all()

    tmin_tavg_tmax_list = [i for i in tmin_tavg_tmax[0]]

    session.close()

    return jsonify(tmin_tavg_tmax_list)

if __name__ == "__main__":
    app.run(debug=True)