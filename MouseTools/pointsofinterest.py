import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .database import DisneyDatabase

class PointOfInterest(object):

    def __init__(self, id = '', sync_on_init=True):
        """
        Constructor Function
        Gets all points of interest data available and stores various elements into variables.
        ID must be a string.
        """
        # TODO POI don't have facilitystatus data, self.__doc_id should work for everything
        # Should probably use that for every class instead of string formatting it
        try:
            error = True
            self.__data = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/points-of-interest/{}".format(id), headers=getHeaders()).json()
            try:
                if self.__data['id'] is not None:
                    error = False
            except:
                pass

            if error:
                raise ValueError()

            self.__db = DisneyDatabase(sync_on_init)
            conn = sqlite3.connect(self.__db.db_path)
            c = conn.cursor()


            self.__id = id
            self.__name = self.__data['name']
            self.__entityType = self.__data['type']
            try:
                self.__subType = self.__data['subType']
            except:
                self.__subType = None
            doc_id_query = c.execute("SELECT doc_id from facilities where doc_id LIKE ?", ("%{};entityType=point-of-interest".format(self.__id),)).fetchone()
            self.__doc_id = doc_id_query[0] if doc_id_query is not None else None
            self.__dest_code = c.execute("SELECT destination_code FROM facilities WHERE id = ?", (self.__data['ancestorDestination']['id'].split(';')[0],)).fetchone()[0]
            try:
                self.__anc_park_id = self.__data['links']['ancestorThemePark']['href'].split('/')[-1].split('?')[0]
            except:
                try:
                    self.__anc_park_id = self.__data['links']['ancestorWaterPark']['href'].split('/')[-1].split('?')[0]
                except:
                    self.__anc_park_id = None
            try:
                self.__anc_resort_id = self.__data['links']['ancestorResort']['href'].split('/')[-1].split('?')[0]
            except:
                self.__anc_resort_id = None

            try:
                self.__anc_land_id = self.__data['links']['ancestorLand']['href'].split('/')[-1].split('?')[0]
            except:
                self.__anc_land_id = None

            try:
                self.__anc_ra_id = self.__data['links']['ancestorResortArea']['href'].split('/')[-1].split('?')[0]
            except:
                self.__anc_ra_id = None

            try:
                self.__anc_ev_id = self.__data['links']['ancestorEntertainmentVenue']['href'].split('/')[-1].split('?')[0]
            except:
                self.__anc_ev_id = None

            self.__facilities_data = None

            conn.commit()
            conn.close()

        except Exception as e:
            # print(e)
            print('That point of interest is not available.')
            sys.exit()

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

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):
        return 'PointOfInterest object for {}'.format(self.__name)
