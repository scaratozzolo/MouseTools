import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders, couchbaseHeaders
from .parks import Park
from .database import DisneyDatabase


class Attraction(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all attraction data available and stores various elements into variables.
        Must pass id as string
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

            self.__facilities_data = c.execute("""SELECT body FROM sync WHERE id = '{}.facilities.1_0.en_us.attraction.{};entityType=Attraction'""".format(self.__dest_code, self.__id)).fetchone()[0
                                                                                                                                                                                                    ]
        except Exception as e:
            print(e)
            # conn = sqlite3.connect(DisneyDatabase().db_path)
            # c = conn.cursor()
            # pos_attrs = [row[0] for row in c.execute("""SELECT id FROM facilities WHERE entityType = 'Attraction'""")]
            # print('That attraction is not available. Available ids: {}'.format(', '.join(pos_attrs)))
            print('That attraction is not available.')
            sys.exit()


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

    def get_raw_facilitystatus_data(self):
        """Returns the raw facilitystatus data from the database after syncing with Disney (returns most recent data)"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_database()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        status_data = c.execute("""SELECT body FROM sync WHERE id = '{}.facilitystatus.1_0.{};entityType=Attraction'""".format(self.__dest_code, self.__id)).fetchone()
        return status_data

    def get_wait_time(self):
        """Return current wait time of the object. Returns None if object doesn't have a wait time or no wait currently exists (eg. closed)"""
        status_data = self.get_raw_facilitystatus_data()
        if status_data is None:
            return None
        else:
            body = json.loads(status_data[0])
            return body['waitMinutes']

    def get_status(self):
        """Return current status of the object."""
        status_data = self.get_raw_facilitystatus_data()
        if status_data is None:
            return None
        else:
            body = json.loads(status_data[0])
            return body['status']
        # TODO might have to change this from facilitystatus data to scheduleType from today, or test if none from status then get from today instead

    def fastpass_available(self):
        """Returns a boolean of whether this object has FastPass"""
        status_data = self.get_raw_facilitystatus_data()
        if status_data is None:
            return False
        else:
            body = json.loads(status_data[0])
            return body['fastPassAvailable'] == 'true'

    def fastpass_times(self):
        """Returns the current start and end time of the FastPass"""
        start_time = None
        end_time = None

        if self.fastpass_available():
            status_data = self.get_raw_facilitystatus_data()
            body = json.loads(status_data[0])

            start_time = datetime.strptime(body['fastPassStartTime'], "%Y-%m-%dT%H:%M:%SZ")
            end_time = datetime.strptime(body['fastPassEndTime'], "%Y-%m-%dT%H:%M:%SZ")

        return start_time, end_time

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
            self.__db.sync_database()
            # maybe just sync this channel? and do same for previous methods
        else:
            self.__db.create_today_channel('{}.today.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        today_data = c.execute("""SELECT body FROM sync WHERE id = '{}.today.1_0.Attraction'""".format(self.__dest_code)).fetchone()

        if today_data is None:
            return start_time, end_time
        else:
            body = json.loads(today_data[0])

            if body['facilities'][self.__id + ';entityType=Attraction'][0]['scheduleType'] == 'Closed' or body['facilities'][self.__id + ';entityType=Attraction'][0]['scheduleType'] == 'Refurbishment':
                return start_time, end_time

            start_time = datetime.strptime(body['facilities'][self.__id + ';entityType=Attraction'][0]['startTime'], "%Y-%m-%dT%H:%M:%SZ")
            end_time = datetime.strptime(body['facilities'][self.__id + ';entityType=Attraction'][0]['endTime'], "%Y-%m-%dT%H:%M:%SZ")

            return start_time, end_time

    def __str__(self):
        return 'Attraction object for {}'.format(self.__name)
