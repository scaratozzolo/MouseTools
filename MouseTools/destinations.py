import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .parks import Park
from .entertainments import Entertainment
from .attractions import Attraction
from .database import DisneyDatabase

WDW_ID = '80007798'
DLR_ID = '80008297'
DEST_IDS = [WDW_ID, DLR_ID]

WDW_CODE = 'wdw'
DLR_CODE = 'dlr'
DEST_CODES = [WDW_CODE, DLR_CODE]

class Destination(object):

    def __init__(self, dest_code = ''):
        """
        Constructor Function
        Allows access to various destination related data.
        dest_code must be a string.
        """
        try:
            if dest_code not in DEST_CODES:
                raise ValueError()

            self.__dest_code = dest_code

            self.__db = DisneyDatabase()
            conn = sqlite3.connect(self.__db.db_name)
            c = conn.cursor()


            self.__id = c.execute("""SELECT id FROM facilities WHERE entityType = 'Destination' and destination_code = '{}'""".format(self.__dest_code))

            conn.commit()
            conn.close()

        except Exception as e:
            print(e)
            print('That destination is not available. Available destinations: {}'.format(", ".join(DEST_CODES)))
            sys.exit()


    def get_destination_code(self):
        """Returns the destination code"""
        return self.__dest_code

    def get_id(self):
        """Returns the id of the destination"""
        return self.__id

    def get_attraction_ids(self):
        """Returns a list of attraction ids associated with the destination"""
        conn = sqlite3.connect(self.__db.db_name)
        c = conn.cursor()

        ids = []
        for row in c.execute("""SELECT id FROM facilities WHERE destination_code = '{}' and entityType = 'Attraction'""".format(self.__dest_code)).fetchall():
            ids.append(row[0])

        conn.commit()
        conn.close()

        return ids

    def get_entertainment_ids(self):
        """Returns a list of entertainment ids associated with the destination"""
        conn = sqlite3.connect(self.__db.db_name)
        c = conn.cursor()

        ids = []
        for row in c.execute("""SELECT id FROM facilities WHERE destination_code = '{}' and entityType = 'Entertainment'""".format(self.__dest_code)).fetchall():
            ids.append(row[0])

        conn.commit()
        conn.close()

        return ids



    def __str__(self):
        return 'Destination object for {}'.format(self.__destination_name)
