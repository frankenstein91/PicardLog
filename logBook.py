#! /bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing
import argparse, logging
import sqlalchemy
from nicegui import ui


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


if __name__ in {"__main__", "__mp_main__"}:
    multiprocessing.freeze_support()
    main()