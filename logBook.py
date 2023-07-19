#! /bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing
import argparse, logging
import sqlalchemy,sqlalchemy_utils
import sqlalchemy.orm
from sqlalchemy.orm import validates

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Bundle
from nicegui import ui

Base = sqlalchemy.orm.declarative_base()
# define the table for countries with the capital and the continent
class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    capital = Column(String)
    continent = Column(String)

# define the table for the HAM radio prefixes
class Prefix(Base):
    __tablename__ = "prefixes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prefix = Column(String)
    country_id = Column(Integer, ForeignKey("countries.id"))


# define the table for the HAM radio stations
class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prefix_id = Column(Integer, ForeignKey("prefixes.id"))
    number = Column(Integer)
    suffix = Column(String)

# define the table for the HAM radio modes
class Mode(Base):
    __tablename__ = "modes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mode = Column(String)

# define the table for the HAM radio contacts
class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey("stations.id"))
    # add the date and time in UTC
    date = Column(sqlalchemy.DateTime(timezone=True))
    # add the frequency in MHz
    frequency = Column(sqlalchemy.Float)
    # add the mode
    mode_id = Column(Integer, ForeignKey("modes.id"))
    # add the signal report Readability ensure that the value is between 1 and 5
    signal_report_R = Column(Integer, sqlalchemy.CheckConstraint("signal_report_R BETWEEN 1 AND 5"))
    # add the signal report Strength ensure that the value is between 1 and 9
    signal_report_S = Column(Integer, sqlalchemy.CheckConstraint("signal_report_S BETWEEN 1 AND 9"))
    # add the signal report Tone ensure that the value is between 1 and 9 or -1 for not used do not use 0
    signal_report_T = Column(Integer, sqlalchemy.CheckConstraint("signal_report_T BETWEEN -1 AND 9 AND signal_report_T != 0"))
    # add a boolean for Aurora
    aurora = Column(sqlalchemy.Boolean)
    # ensure that the signal_report_T is -1 if aurora is true
    @validates("aurora")
    def validate_aurora(self, key, aurora):
        if aurora:
            self.signal_report_T = -1
        return aurora
    # add a boolean for received QSL card
    qsl_received = Column(sqlalchemy.Boolean)
    # add a boolean for sent QSL card
    qsl_sent = Column(sqlalchemy.Boolean)
    # add a boolean for other requested QSL card
    qsl_requested = Column(sqlalchemy.Boolean)
    # add a text field for comments
    comment = Column(sqlalchemy.Text)
    last_modified = Column(sqlalchemy.DateTime(timezone=True), onupdate=sqlalchemy.func.now())  # auto update the last modified date and time

def get_free_TCP_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    # initialize the parser of arguments
    parser = argparse.ArgumentParser(description="logbook for amateur radio")
    # add a argument group for software logging
    logging_group = parser.add_argument_group("logging")
    # add a countinuous argument for logging level
    logging_group.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    # add a argument for logging file
    logging_group.add_argument("-l", "--log", type=str, default="logbook.log", help="log file")
    # add a argument group for the database connection
    database_group = parser.add_argument_group("database")
    # add a argument for the database connection string default is sqlite in the current directory
    database_group.add_argument("-d", "--database", type=str, default="sqlite:///logbook.db", help="database connection string (default: sqlite:///logbook.db)")
    # parse the arguments
    args = parser.parse_args()
    # initialize the logging and set the logging level
    logging.basicConfig(
        filename=args.log,
        level=logging.DEBUG if args.verbose > 1 else logging.INFO if args.verbose > 0 else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s"
        )
    # log the arguments
    for arg in vars(args):
        logging.debug("{}: {}".format(arg, getattr(args, arg)))
    # log the start of the program
    logging.info("start of the program")
    # connect to the database and create the tables if not exists
    engine = sqlalchemy.create_engine(args.database)
    Base.metadata.create_all(engine)
    # create the session
    global Sessions
    Sessions = sqlalchemy.orm.sessionmaker(bind=engine)
    
       
    # start the UI in native mode without auto reload
    # ToDO: native mode does not work
    ui.run(reload=False, native=False,dark=True, title="Picard's logbook", port=get_free_TCP_port())

@ui.page('/')
async def index():
    with ui.header(elevated=True).style("background-color: black; color: white;").classes("items-center justify-between"):
        ui.label("Picard's logbook").style("font-size: 2em;")

class GPSException(Exception):
    def __init__(self, message = "GPS exception"):
        self.message = message
        super().__init__(self.message)
import gps
class gpshelper:
    def __init__(self, host="127.0.0.1", port=2947):
        self.host = host
        self.port = port
        self.gpsd = None
        self.running = False
    
    def connect(self):
        try:
            self.gpsd = gps.gps(host=self.host, port=self.port)
        except:
            raise GPSException("can not connect to GPSD")
    
    def disconnect(self):
        try:
            self.gpsd.close()
        except:
            raise GPSException("can not disconnect from GPSD")
    
    def check_running(self):
        try:
            self.connect()
            self.running = True
            self.disconnect()
        except:
            self.running = False


if __name__ in {"__main__", "__mp_main__"}:
    multiprocessing.freeze_support()
    gps = gpshelper()
    gps.check_running()
    main()