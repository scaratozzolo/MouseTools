import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders, couchbaseHeaders
from .database import DisneyDatabase

MK_ID = "80007944"
EPCOT_ID = "80007838"
HS_ID = "80007998"
AK_ID = "80007823"
DLP_ID = "330339"
CA_ID = "336894"
TL_ID = "80007981"
BB_ID = "80007834"
PARK_IDS = [MK_ID, EPCOT_ID, HS_ID, AK_ID, DLP_ID, CA_ID, TL_ID, BB_ID]

class Park(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all park data available and stores various elements into variables.
        ID must be a string
        """

        try:

            self.__db = DisneyDatabase()
            conn = sqlite3.connect(self.__db.db_path)
            c = conn.cursor()

            row = c.execute("""SELECT * FROM facilities WHERE id = '{}'""".format(id)).fetchone()
            if row is None:
                raise ValueError()
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

            self.__facilities_data = c.execute("""SELECT body FROM sync WHERE id = '{}.facilities.1_0.en_us.{}.{};entityType={}'""".format(self.__dest_code, self.__entityType, self.__id, self.__entityType)).fetchone()[0]
        except Exception as e:
            print(e)
            print('That park is not available.')
            sys.exit()

    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        conn = sqlite3.connect(DisneyDatabase().db_path)
        c = conn.cursor()
        pos_ids = [row[0] for row in c.execute("""SELECT id FROM facilities WHERE entityType = 'theme-park' or entityType = 'water-park'""")]
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

    def get_raw_facilities_data(self):
        """Returns the raw facilities data currently stored in the database"""
        return self.__facilities_data

    def get_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for attractions and entertainments for this park"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE park_id = ? and (entityType = 'Attraction' or entityType = 'Entertainment')", (self.__id,))]

        data = {}
        for row in ids:
            status_data = c.execute("SELECT body FROM sync WHERE id = ?", ("{}.facilitystatus.1_0.{};entityType={}".format(self.__dest_code, row[0], row[1]),)).fetchone()
            try:
                if status_data is not None:
                    body = json.loads(status_data[0])
                    data[row[0]] = body['waitMinutes']
            except:
                continue

        return data

    def get_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions and entertainments for this park"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE park_id = ? and (entityType = 'Attraction' or entityType = 'Entertainment')", (self.__id,))]

        data = {}
        for row in ids:
            status_data = c.execute("SELECT body FROM sync WHERE id = ?", ("{}.facilitystatus.1_0.{};entityType={}".format(self.__dest_code, row[0], row[1]),)).fetchone()
            try:
                if status_data is not None:
                    body = json.loads(status_data[0])
                    this = {}
                    this['name'] = c.execute("SELECT name FROM facilities WHERE id = ?", (row[0],)).fetchone()[0]
                    this['status'] = body['status']
                    this['wait_time'] = body['waitMinutes']
                    data[row[0]] = this
            except Exception as e:
                # print(e)
                continue

        return data

    def get_status(self):
        """Return current status of the object."""
        if self.__db.channel_exists('{}.today.1_0'.format(self.__dest_code)):
            self.__db.sync_today_channel()
            # maybe just sync this channel? and do same for previous methods
        else:
            self.__db.create_today_channel('{}.today.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        today_data = c.execute("""SELECT body FROM sync WHERE id = '{}.today.1_0.{}'""".format(self.__dest_code, self.__entityType)).fetchone()

        if today_data is None:
            return None
        else:
            body = json.loads(today_data[0])

            return body['facilities'][self.__id + ';entityType=' + self.__entityType][0]['scheduleType']

    def get_last_update(self):
        """Returns facilities last update time as a datetime object"""
        facility_data = json.loads(self.__facilities_data)
        return datetime.strptime(facility_data['lastUpdate'], "%Y-%m-%dT%H:%M:%SZ")
        # TODO check if facilitystatus has a different last update time

    def get_coordinates(self):
        """Returns the object's latitude and longitude"""
        facility_data = json.loads(self.__facilities_data)
        return facility_data['latitude'], facility_data['longitude']

    def get_description(self):
        """Returns the object's descriptions"""
        facility_data = json.loads(self.__facilities_data)
        return facility_data['description']

    def get_list_image(self):
        """Returns the url to the object's list image"""
        facility_data = json.loads(self.__facilities_data)
        return facility_data['listImageUrl']

    def get_facets(self):
        """Returns a list of  dictionaries of the object's facets"""
        facility_data = json.loads(self.__facilities_data)
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
        return 'Park object for {}'.format(self.__name)
