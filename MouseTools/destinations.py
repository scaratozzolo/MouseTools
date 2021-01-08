import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .parks import Park
from .entertainments import Entertainment
from .attractions import Attraction
from .ids import WDW_PARK_IDS, DLR_PARK_IDS, WDW_ID, DLR_ID, DESTINATION_IDS, themeparkapi_ids


class Destination(object):

    def __init__(self, id = None, sync_on_init=True):
        """
        Constructor Function
        Allows access to various destination related data.
        """
        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(id), headers=getHeaders()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That destination is not available. id: ' + str(id) + '. Available destinations: {}'.format(", ".join(DESTINATION_IDS)))

        self.__id = id
        self.__name = self.__data['name']
        self.__entityType = self.__data['type']




    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        return DESTINATION_IDS

    def get_id(self):
        """Returns the id of the destination"""
        return self.__id

    def get_name(self):
        """Returns the name of the destination"""
        return self.__name

    def get_entityType(self):
        """Returns the entityType"""
        return self.__entityType

    def get_links(self):
        """Returns a dictionary of related links"""
        return self.__data['links']

    def get_raw_data(self):
        """Returns the raw data from global-facility-service"""
        return self.__data


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

    def get_themeparkapi_data(self):
        """Returns the list of dictionaries for all parks from the themeparks api"""

        all_data = []

        if self.__id == WDW_ID:
            parks = WDW_PARK_IDS
        else:
            parks = DLR_PARK_IDS

        for id in parks:
            try:
                park = themeparkapi_ids[id]
                all_data.extend(requests.get(f"https://api.themeparks.wiki/preview/parks/{park}/waittime").json())
            except:
                continue

        return all_data
            

    def get_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for attractions and entertainments for this destination"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            try:
                if i['meta']['type'] != "RESTAURANT":
                    times[id] = i['waitTime']
            except:
                times[id] = i['waitTime']

        return times

    def get_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions and entertainments for this destination"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            this = {}
            try:
                if i['meta']['type'] != "RESTAURANT":
                    this['name'] = i['name']
                    this['status'] = i['status']
                    this['wait_time'] = i['waitTime']
                    this['last_updated'] = datetime.strptime(i['lastUpdate'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    this['entityType'] = i['meta']['type'].capitalize()
                    times[id] = this
            except:
                this['name'] = i['name']
                this['status'] = i['status']
                this['wait_time'] = i['waitTime']
                this['last_updated'] = datetime.strptime(i['lastUpdate'], "%Y-%m-%dT%H:%M:%S.%fZ")
                this['entityType'] = "Entertainment"
                times[id] = this

        return times

    def get_attraction_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for attractions for this destination"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            try:
                if i['meta']['type'] == "ATTRACTION":
                    times[id] = i['waitTime']
            except:
                continue

        return times

    def get_attraction_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions for this destination"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            this = {}
            try:
                if i['meta']['type'] == "ATTRACTION":
                    this['name'] = i['name']
                    this['status'] = i['status']
                    this['wait_time'] = i['waitTime']
                    this['last_updated'] = datetime.strptime(i['lastUpdate'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    this['entityType'] = i['meta']['type'].capitalize()
                    times[id] = this
            except:
                continue

        return times

    def get_entertainment_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for entertainments for this destination"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            if 'type' not in i['meta'].keys():
                    times[id] = i['waitTime']

        return times

    def get_entertainment_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for entertainments for this destination"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            this = {}
            if 'type' not in i['meta'].keys():
                this['name'] = i['name']
                this['status'] = i['status']
                this['wait_time'] = i['waitTime']
                this['last_updated'] = datetime.strptime(i['lastUpdate'], "%Y-%m-%dT%H:%M:%S.%fZ")
                this['entityType'] = "Entertainment"
                times[id] = this

        return times

    
    # Deprecated, remove or replace?
    # Replace with all park hours
    # def get_raw_calendar_data(self, date=""):
    #     """
    #     Returns raw calendar data on a date. Date should be in the form yyyy-mm-dd
    #     """
    #     if self.__db.channel_exists('{}.calendar.1_0'.format(self.__dest_code)):
    #         self.__db.sync_calendar_channel()
    #     else:
    #         self.__db.create_calendar_channel('{}.calendar.1_0'.format(self.__dest_code))

    #     conn = sqlite3.connect(self.__db.db_path)
    #     c = conn.cursor()
    #     data = c.execute("SELECT body FROM calendar WHERE date = ?", (date,)).fetchone()
    #     conn.commit()
    #     conn.close()

    #     if data is None:
    #         return None
    #     else:
    #         return json.loads(data[0])

    # Can only get today's refurbishments now, will probably have to change this
    # def get_refurbishments(self, date=""):
    #     """
    #     Returns a list of tuples in the form of (id, entityType) that are under refurbishment on a specified date
    #     date = "YYY-MM-DD"
    #     """
    #     if date == "":
    #         DATE = datetime.today()
    #     else:
    #         year, month, day = date.split('-')
    #         DATE = datetime(int(year), int(month), int(day))

    #     STRDATE = "{}-{}-{}".format(DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day)))
    #     date = self.get_raw_calendar_data(STRDATE)

    #     ids = []
    #     try:
    #         for i in date['refurbishments']:
    #             split = i['facilityId'].split(";")
    #             id = split[0]
    #             entityType = split[1].split("=")[-1]
    #             ids.append((id, entityType))
    #     except Exception as e:
    #         print(e)

    #     return ids

    # Similar to refurbishments, can only get today's
    # def get_closed(self, date=""):
    #     """
    #     Returns a list of tuples in the form of (id, entityType) that are under closed on a specified date
    #     date = "YYY-MM-DD"
    #     """
    #     if date == "":
    #         DATE = datetime.today()
    #     else:
    #         year, month, day = date.split('-')
    #         DATE = datetime(int(year), int(month), int(day))

    #     STRDATE = "{}-{}-{}".format(DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day)))
    #     date = self.get_raw_calendar_data(STRDATE)

    #     ids = []
    #     try:
    #         for i in date['closed']:
    #             split = i['facilityId'].split(";")
    #             id = split[0]
    #             entityType = split[1].split("=")[-1]
    #             ids.append((id, entityType))
    #     except Exception as e:
    #         print(e)

    #     return ids

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):

        return 'Destination object for {}'.format(self.__name)
