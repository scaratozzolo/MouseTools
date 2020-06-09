import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .database import DisneyDatabase


class Facility(object):

    def __init__(self, id = '', sync_on_init=True):
        """
        Constructor Function
        Gets all facility data available and stores various elements into variables.
        ID must be a string
        """
        # TODO Maybe turn this into a base class

        self.__db = DisneyDatabase(sync_on_init)
        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        row = c.execute("SELECT * FROM facilities WHERE id = ?", (id,)).fetchone()
        if row is None:
            raise ValueError('That facility is not available. id: ' + id)
        else:
            self.__id = row[0]
            self.__name = row[1]
            self.__entityType = row[2]
            self.__subType = row[3]
            self.__doc_id = row[4]
            self.__dest_code = row[5]
            self.__anc_park_id = row[6]
            self.__anc_resort_id = row[7]
            self.__anc_land_id = row[8]
            self.__anc_ra_id = row[9]
            self.__anc_ev_id = row[10]

        self.__facilities_data = c.execute("SELECT body FROM sync WHERE id = ?", (self.__doc_id,)).fetchone()[0]

    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        conn = sqlite3.connect(DisneyDatabase().db_path)
        c = conn.cursor()
        pos_ids = [row[0] for row in c.execute("SELECT id FROM facilities WHERE entityType ?", (self.__entityType,))]
        return pos_ids

    def get_id(self):
        """Return object id"""
        return self.__id

    def get_name(self):
        """Return object name"""
        return self.__name

    def get_entityType(self):
        """Return object entityType"""
        return self.__entityType

    def get_subType(self):
        """Return object subType"""
        return self.__subType

    def get_doc_id(self):
        """Return object doc id"""
        return self.__doc_id

    def get_destination_code(self):
        """Return object destination code"""
        return self.__dest_code

    def get_ancestor_park_id(self):
        """Return object ancestor theme or water park id"""
        return self.__anc_park_id

    def get_ancestor_resort_id(self):
        """Return object ancestor resort id"""
        return self.__anc_resort_id

    def get_ancestor_land_id(self):
        """Return object land id"""
        return self.__anc_land_id

    def get_ancestor_resort_area_id(self):
        """Return object resort area id"""
        return self.__anc_ra_id

    def get_ancestor_entertainment_venue_id(self):
        """Return object entertainment venue id"""
        return self.__anc_ev_id

    def get_links(self):
        """Returns a dictionary of related links"""
        return self.__data['links']

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

    def get_status(self):
        """Return current status of the object."""
        if self.__db.channel_exists('{}.today.1_0'.format(self.__dest_code)):
            self.__db.sync_today_channel()
            # maybe just sync this channel? and do same for previous methods
        else:
            self.__db.create_today_channel('{}.today.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        today_data = c.execute("SELECT body FROM sync WHERE id = ?", ('{}.today.1_0.{}'.format(self.__dest_code, self.__entityType),)).fetchone()

        if today_data is None:
            return None
        else:
            body = json.loads(today_data[0])

            return body['facilities'][self.__id + ';entityType=' + self.__entityType][0]['scheduleType']

    def get_last_update(self):
        """Returns facilities last update time as a datetime object"""
        facility_data = self.get_raw_facilities_data()
        if facility_data is None:
            return None
        else:
            return datetime.strptime(facility_data['lastUpdate'], "%Y-%m-%dT%H:%M:%SZ")

    def get_coordinates(self):
        """Returns the object's latitude and longitude"""
        facility_data = self.get_raw_facilities_data()
        if facility_data is None:
            return None
        else:
            return facility_data['latitude'], facility_data['longitude']

    def get_description(self):
        """Returns the object's descriptions"""
        facility_data = self.get_raw_facilities_data()
        if facility_data is None:
            return None
        else:
            return facility_data['description']

    def get_list_image(self):
        """Returns the url to the object's list image"""
        facility_data = self.get_raw_facilities_data()
        if facility_data is None:
            return None
        else:
            return facility_data['listImageUrl']

    def get_facets(self):
        """Returns a list of  dictionaries of the object's facets"""
        facility_data = self.get_raw_facilities_data()
        if facility_data is None:
            return None
        else:
            return facility_data['facets']

    def get_todays_hours(self):
        """Returns the start and end times for the object. Will return None, None if closed"""
        start_time = None
        end_time = None

        if self.__db.channel_exists('{}.today.1_0'.format(self.__dest_code)):
            self.__db.sync_today_channel()
            # maybe just sync this channel? and do same for previous methods
        else:
            self.__db.create_today_channel('{}.today.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        today_data = c.execute("SELECT body FROM sync WHERE id = ?", ("{}.today.1_0.{}".format(self.__dest_code, self.__entityType),)).fetchone()

        if today_data is None:
            return start_time, end_time
        else:
            body = json.loads(today_data[0])

            if body['facilities'][self.__id + ';entityType=' + self.__entityType][0]['scheduleType'] == 'Closed' or body['facilities'][self.__id + ';entityType=Attraction'][0]['scheduleType'] == 'Refurbishment':
                return start_time, end_time

            start_time = datetime.strptime(body['facilities'][self.__id + ';entityType=' + self.__entityType][0]['startTime'], "%Y-%m-%dT%H:%M:%SZ")
            end_time = datetime.strptime(body['facilities'][self.__id + ';entityType=' + self.__entityType][0]['endTime'], "%Y-%m-%dT%H:%M:%SZ")

            return start_time, end_time

    def __eq__(self, other):
        """
        Checks if objects are equal
        """
        return self.__id == other.get_id()

    def __str__(self):
        return 'Facility object for {}'.format(self.__name)
