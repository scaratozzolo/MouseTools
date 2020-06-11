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

WDW_CODE = 'wdw'
DLR_CODE = 'dlr'
DEST_CODES = [WDW_CODE, DLR_CODE]

class Destination(object):

    def __init__(self, id = None, sync_on_init=True):
        """
        Constructor Function
        Allows access to various destination related data.
        dest_code must be a string.
        """
        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(id), headers=getHeaders()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That destination is not available. id: ' + str(id) + '. Available destinations: {}'.format(", ".join(DEST_IDS)))

        self.__id = id

        self.__db = DisneyDatabase(sync_on_init)
        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        dest_data = c.execute("SELECT id, name, doc_id, destination_code, entityType FROM facilities WHERE entityType = 'destination' and id = ?", (self.__id,)).fetchone()
        self.__id = dest_data[0]
        self.__name = dest_data[1]
        self.__doc_id = dest_data[2]
        self.__dest_code = dest_data[3]
        self.__entityType = dest_data[4]
        self.__facilities_data = json.loads(c.execute("SELECT body FROM sync WHERE id = ?", (self.__doc_id,)).fetchone()[0])

        conn.commit()
        conn.close()


    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        conn = sqlite3.connect(DisneyDatabase().db_path)
        c = conn.cursor()
        pos_ids = [row[0] for row in c.execute("SELECT id FROM facilities WHERE entityType = 'destination'")]
        return pos_ids

    def get_destination_code(self):
        """Returns the destination code"""
        return self.__dest_code

    def get_id(self):
        """Returns the id of the destination"""
        return self.__id

    def get_name(self):
        """Returns the name of the destination"""
        return self.__name

    def get_doc_id(self):
        """Returns the doc id"""
        return self.__doc_id

    def get_entityType(self):
        """Returns the entityType"""
        return self.__entityType

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

    def get_entertainment_venue_ids(self):
        """
        Returns a list of Entertainment Venue IDs
        """
        entertainments = []

        data = requests.get(self.__data['links']['entertainmentVenues']['href'], headers=getHeaders()).json()

        for enter in data['entries']:
            try:
                entertainments.append(enter['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass
        return entertainments

    def get_character_ids(self):
        """
        Returns a list of theme or water park IDs
        """
        ids = []

        data = requests.get("https://api.wdpro.disney.go.com/facility-service/characters", headers=getHeaders()).json()

        for entry in data['entries']:
            try:
                ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        return ids

    def get_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for attractions and entertainments for this destination"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE destination_code = ? and (entityType = 'Attraction' or entityType = 'Entertainment')", (self.__dest_code,))]

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
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions and entertainments for this destination"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE destination_code = ? and (entityType = 'Attraction' or entityType = 'Entertainment')", (self.__dest_code,))]

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
                    this['last_updated'] = datetime.strptime(body['lastUpdate'], "%Y-%m-%dT%H:%M:%SZ")
                    this['entityType'] = row[1]
                    data[row[0]] = this
            except Exception as e:
                # print(e)
                continue

        return data

    def get_attraction_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for attractions for this destination"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE destination_code = ? and entityType = 'Attraction'", (self.__dest_code,))]

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

    def get_attraction_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions for this destination"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE destination_code = ? and entityType = 'Attraction'", (self.__dest_code,))]

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
                    this['last_updated'] = datetime.strptime(body['lastUpdate'], "%Y-%m-%dT%H:%M:%SZ")
                    data[row[0]] = this
            except Exception as e:
                # print(e)
                continue

        return data

    def get_entertainment_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for entertainments for this destination"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE destination_code = ? and entityType = 'Entertainment'", (self.__dest_code,))]

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

    def get_entertainment_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for entertainments for this destination"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        ids = [row for row in c.execute("SELECT id, entityType FROM facilities WHERE destination_code = ? and entityType = 'Entertainment'", (self.__dest_code,))]

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
                    this['last_updated'] = datetime.strptime(body['lastUpdate'], "%Y-%m-%dT%H:%M:%SZ")
                    data[row[0]] = this
            except Exception as e:
                # print(e)
                continue

        return data




    def __str__(self):

        return 'Destination object for {}'.format(self.__name)
