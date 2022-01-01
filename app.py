import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime

def listToString(s): 
    
    # initialize an empty string
    str1 = "" 
    
    # traverse in the string  
    for ele in s: 
        str1 += ele  
    
    # return string  
    return str1 

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement= Base.classes.measurement
Station= Base.classes.station

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
	    f"/api/v1.0/tobs<br/>"
	    f"/api/v1.0/<start><br/>"
	    f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    l_date = listToString(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
	
    last_date = datetime.fromisoformat(l_date)
	
    first_date = last_date - dt.timedelta(days=365)
	
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    date_prcp = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= first_date).\
    order_by(Measurement.date).all()

    session.close()
    # Create a dictionary from the row data 
    
    date_prcp_dict = dict(date_prcp)    
    return jsonify(date_prcp_dict)
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/station")
def station():

# Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations= list(np.ravel(results))

    return jsonify(all_stations)
# Query the dates and temperature observations of the most active station for the last year of data.
# return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create  session (link) from Python to the DB
    session = Session(engine) 

    station_counts = session.query(Station.station,Station.name,func.count(Measurement.station)).group_by(Station.name).\
    order_by(func.count(Measurement.station).desc()).\
    filter(Station.station == Measurement.station).all()

    most_active_station = station_counts[0][0]

    l_date = listToString(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    last_date = datetime.fromisoformat(l_date)
    first_date = last_date - dt.timedelta(days=365)

    result = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.station == most_active_station ).\
    filter(Measurement.date >= first_date).all()
    
    session.close()

    temp_list = list(np.ravel(result))
    return jsonify(temp_list)

# When given the start only, calculate TMIN, TAVG, and TMAX 
# for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def index(start):
    session = Session(engine)  
    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)) .\
    filter(Measurement.date>=start).all()  
    session.close()

    list1 = list(np.ravel(result))
    return jsonify(list1)
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
# for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    session = Session(engine) 
    result = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)) .\
    filter(Measurement.date>=start) .\
    filter(Measurement.date<=end ).all()
    session.close()

    list2 = list(np.ravel(result))
    return jsonify(list2)

if __name__ == '__main__':
    app.run(debug=True)
