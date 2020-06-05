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

    def __init__(self, id = '', sync_on_init=True):
        """
        Constructor Function
        Allows access to various destination related data.
        dest_code must be a string.
        """
        try:
            error = True
            self.__data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(id), headers=getHeaders()).json()
            try:
                if self.__data['id'] is not None:
                    error = False
            except:
                pass

            if error:
                raise ValueError()

            self.__id = id

            self.__db = DisneyDatabase(sync_on_init)
            conn = sqlite3.connect(self.__db.db_path)
            c = conn.cursor()

            dest_data = c.execute("SELECT id, name, doc_id, destination_code FROM facilities WHERE entityType = 'destination' and id = ?", (self.__id,)).fetchone()
            self.__id = dest_data[0]
            self.__name = dest_data[1]
            self.__doc_id = dest_data[2]
            self.__dest_code = dest_data[3]
            self.__facilities_data = json.loads(c.execute("SELECT body FROM sync WHERE id = ?", (self.__doc_id,)).fetchone()[0])

            conn.commit()
            conn.close()



        except Exception as e:
            # print(e)
            print('That destination is not available. Available destinations: {}'.format(", ".join(DEST_IDS)))
            sys.exit()


    def get_destination_code(self):
        """Returns the destination code"""
        return self.__dest_code

    def get_id(self):
        """Returns the id of the destination"""
        return self.__id

    def get_destination_name(self):
        """Returns the name of the destination"""
        return self.__name

    def get_doc_id(self):
        """Returns the doc id"""
        return self.__doc_id

    def get_links(self):
        """Returns a dictionary of related links"""
        return self.__data['links']

    def get_raw_data(self):
        """Returns the raw data from global-facility-service"""
        return self.__data

    def get_raw_facilities_data(self):
        """Returns the raw facilities data currently stored in the database"""
        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()
        data = c.execute("SELECT body FROM sync WHERE id = ?", (self.__doc_id,)).fetchone()[0]
        conn.commit()
        conn.close()

        if data is None:
            return None
        else:
            return json.loads(data)

    def get_attraction_ids(self):
        """
        Returns a list of Attraction IDs
        """
        attractions = []

        data = requests.get(self.__data['links']['attractions']['href'], headers=getHeaders()).json()

        for attract in data['entries']:
            try:
                attractions.append(attract['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass
        return attractions

    def get_entertainment_ids(self):
        """
        Returns a list of Entertainment IDs
        """
        entertainments = []

        data = requests.get(self.__data['links']['entertainments']['href'], headers=getHeaders()).json()

        for enter in data['entries']:
            try:
                entertainments.append(enter['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass
        return entertainments

    def get_park_ids(self):
        """
        Returns a list of theme or water park IDs
        """
        ids = []

        data = requests.get(self.__data['links']['themeParks']['href'], headers=getHeaders()).json()

        for entry in data['entries']:
            try:
                ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        data = requests.get(self.__data['links']['waterParks']['href'], headers=getHeaders()).json()
        try:
            if data['errors'] is not None:
                return ids
        except:
            pass

        for entry in data['entries']:
            try:
                ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        return ids




    def __str__(self):

        return 'Destination object for {}'.format(self.__name)
