# dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
import datetime as dt

# database
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# session
session = Session(engine)

# setup flask
app = Flask(__name__)

# routes
@app.route("/")
def home():
    return ("Hawaii Weather Data Homepage!<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "Please enter start date in below api in the format YYYY-MM-DD<br/>"
    "/api/v1.0/<start><br/>"
    "Please enter start and end dates in below api in the format YYYY-MM-DD<br/>"
    "/api/v1.0/<start>/<end>")

# Precipitation
 
@app.route("/api/v1.0/precipitation")
def precipitation():   
     
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = most_recent[0]
    year_before = last_date.replace(year = (last_date.year - 1))
    year_before = year_before.strftime("%Y-%m-%d")

    precip_list = []
    precip = session.query(Station.name, Measurement.date, Measurement.prcp).filter(Measurement.station==Station.station).filter(Measurement.date>=year_before).order_by(Measurement.date).all()
    for p in precip:
        # print({"date":p[0],"tobs":p[1]})
        precip_list.append({"station":p[0],"date":p[1],"prcp":p[2]})

    return jsonify(precip_list)

# Stations

@app.route("/api/v1.0/stations")
def stations():    
    stations = session.query(Station.station, Station.name, Measurement.station, func.count(Measurement.tobs)).filter(Station.station == Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    station_List = []
    for s in stations:
        station_List.append({"station":s[0],"name":s[1]})

    return jsonify(station_List)

# tobs

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = most_recent[0]
    year_before = last_date.replace(year = (last_date.year - 1))
    year_before = year_before.strftime("%Y-%m-%d")

    tobs = session.query(Station.name,Measurement.date, Measurement.tobs).filter(Measurement.station==Station.station).filter(Measurement.date>=year_before).order_by(Measurement.date).all()
    tobs_List = []
    for t in tobs:
       tobs_List.append({"station":t[0],"date":t[1],"temperature observation":t[2]})
    
    return jsonify(tobs_List)


@app.route("/api/v1.0/<start>")
def start(start):

    start_date = datetime.strptime(start, '%Y-%m-%d')
   
    minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    #print(f"Minimum temp: {minimum}")
    average = session.query(func.round(func.avg(Measurement.tobs))).filter(Measurement.date >= start_date).scalar()
    # print(f"Average temp: {average}")
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    # print(f"Maximum temp: {maximum}")
    
    result = [{"Minimum":minimum},{"Maximum":maximum},{"Average":average}]
    
    return jsonify(result)


@app.route("/api/v1.0/<start>/<end>")
def StartEnd(start,end):

     start_date = datetime.strptime(start, '%Y-%m-%d')
     end_date = datetime.strptime(end, '%Y-%m-%d')

     minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date)).scalar()
     # print(f"Minimum temp: {minimum}")
     average = session.query(func.round(func.avg(Measurement.tobs))).filter(Measurement.date.between(start_date, end_date)).scalar()
     # print(f"Average temp: {average}")
     maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date)).scalar()
     # print(f"Maximum temp: {maximum}")
        
     result = [{"Minimum":minimum},{"Maximum":maximum},{"Average":average}]
    
     return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)