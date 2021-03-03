import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .ids import themeparkapi_ids


class Park(object):

    def __init__(self, id = None):
        """
        Constructor Function
        Gets all park data available and stores various elements into variables.
        """

        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/theme-parks/{}".format(id), headers=getHeaders()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            self.__data = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/water-parks/{}".format(id), headers=getHeaders()).json()
            try:
                if self.__data['id'] is not None:
                    error = False
            except:
                pass

        if error:
            raise ValueError('That park is not available. id: ' + str(id))



        self.__id = id
        self.__name = self.__data['name']
        self.__entityType = self.__data['type']
        try:
            self.__subType = self.__data['subType']
        except:
            self.__subType = None

        try:
            self.__anc_dest_id = self.__data['ancestorDestination']['id'].split(';')[0]
        except:
            self.__anc_dest_id = None

        try:
            self.__anc_park_id = self.__data['links']['ancestorThemePark']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_park_id = self.__data['links']['ancestorWaterPark']['href'].split('/')[-1].split('?')[0]
            except:
                try:
                    self.__anc_park_id = self.__facilities_data['ancestorThemeParkId'].split(';')[0]
                except:
                    try:
                        self.__anc_park_id = self.__facilities_data['ancestorWaterParkId'].split(';')[0]
                    except:
                        self.__anc_park_id = None

        try:
            self.__anc_resort_id = self.__data['links']['ancestorResort']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_resort_id = self.__facilities_data['ancestorResortId'].split(';')[0]
            except:
                self.__anc_resort_id = None

        try:
            self.__anc_land_id = self.__data['links']['ancestorLand']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_land_id = self.__facilities_data['ancestorLandId'].split(';')[0]
            except:
                self.__anc_land_id = None

        try:
            self.__anc_ra_id = self.__data['links']['ancestorResortArea']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ra_id = self.__facilities_data['ancestorResortAreaId'].split(';')[0]
            except:
                self.__anc_ra_id = None

        try:
            self.__anc_ev_id = self.__data['links']['ancestorEntertainmentVenue']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ev_id = self.__facilities_data['ancestorEntertainmentVenueId'].split(';')[0]
            except:
                self.__anc_ev_id = None


    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        ids = []

        dest_data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(self.__anc_dest_id), headers=getHeaders()).json()
        data = requests.get(dest_data['links']['themeParks']['href'], headers=getHeaders()).json()

        for entry in data['entries']:
            try:
                ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        data = requests.get(dest_data['links']['waterParks']['href'], headers=getHeaders()).json()
        try:
            for entry in data['entries']:
                try:
                    ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
                except:
                    pass
        except:
            pass

        return ids

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

    def get_ancestor_destination_id(self):
        """Return object ancestor destination id"""
        return self.__anc_dest_id

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

    def get_themeparkapi_data(self):
        """Returns the list of dictionaries from the themepark api for the given id"""
        park = themeparkapi_ids[self.__anc_park_id]
        all_data = requests.get(f"https://api.themeparks.wiki/preview/parks/{park}/waittime").json()
        return all_data

    def get_wait_times(self):
        """Returns a list of dictionaries in the form of {rideid:time} for attractions and entertainments for this park"""
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
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions and entertainments for this park"""
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
        """Returns a list of dictionaries in the form of {rideid:time} for attractions for this park"""
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
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for attractions for this park"""
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
        """Returns a list of dictionaries in the form of {rideid:time} for entertainments for this park"""
        data = self.get_themeparkapi_data()

        times = {}

        for i in data:
            id = i['id'].split("_")[-1]
            if 'type' not in i['meta'].keys():
                    times[id] = i['waitTime']

        return times

    def get_entertainment_wait_times_detailed(self):
        """Returns a list of dictionaries in the form of {rideid:{name, status, wait_time}} for entertainments for this park"""
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

    # Figure out how to get the current status
    # def get_status(self):
    #     """Return current status of the object."""
    #     park = themeparkapi_ids[self.__anc_park_id]
    #     all_data = requests.get(f"https://api.themeparks.wiki/preview/parks/{park}/calendar").json()

    def get_coordinates(self):
        """Returns the object's latitude and longitude"""
        try:
            return self.__data['coordinates']['Guest Entrance']['gps']
        except:
            return None

    def get_description(self):
        """Returns the object's descriptions"""
        try:
            long_desc = self.__data["descriptions"]["MM - " + self.__name]["text"].replace("<p>", "").split('</p>')[0]
            return long_desc
        except:
            return None

    def get_media(self):
        """Returns a dictionary of dictionaries of media relating to the entity"""
        facility_data = self.__data
        if facility_data is None:
            return None
        else:
            return facility_data['media']

    def admission_required(self):
        """Returns boolean of admission required"""
        return self.__data['admissionRequired']

    def get_hours(self, date = ""):
        """
        Gets the object's hours on a specific day and returns them as a datetime object.
        Returns the object's hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
        Extra Magic hours will return None if there are none for today.
        If all hours are None then Disney has no hours for that day.
        date = "YYYY-MM-DD"
        If you don't pass a date, it will get today's hours
        """

        if date == "":
            DATE = datetime.today()
        else:
            year, month, day = date.split('-')
            DATE = datetime(int(year), int(month), int(day))

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}-{}-{}".format(self.__id, DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day))), headers=getHeaders())
        data = json.loads(s.content)

        operating_hours_start = None
        operating_hours_end = None
        extra_hours_start = None
        extra_hours_end = None

        try:
            for i in range(len(data['schedules'])):
                if data['schedules'][i]['type'] == 'Operating':
                    operating_hours_start = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    if int(data['schedules'][i]['endTime'][0:2]) >= 0 and int(data['schedules'][i]['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days=1)
                        operating_hours_end = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
                    else:
                        operating_hours_end = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

                if data['schedules'][i]['type'] == "Special Ticketed Event":
                    extra_hours_start = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    if int(data['schedules'][i]['endTime'][0:2]) >= 0 and int(data['schedules'][i]['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days=1)
                        extra_hours_end = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
                    else:
                        operating_hours_end = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

        except KeyError:
            pass
        return operating_hours_start, operating_hours_end, extra_hours_start, extra_hours_end

    def get_advisories(self):
        """
        Gets all the advisories for the park and returns a list in the form of [{id, name}].
        May take some time because it has to go to every link for each advisory.
        """

        advisories = []

        for i in range(len(self.__data['advisories'])):
            data = requests.get(self.__data['advisories'][i]['links']['self']['href'], headers=getHeaders()).json()
            this = {}
            this['id'] = data['id']
            this['name'] = data['name']
            advisories.append(this)

        return advisories

    def get_entertainment_ids(self):
        """Returns a list of entertainments for this object"""
        ids = []

        data = requests.get("https://api.wdpro.disney.go.com/facility-service/{}s/{}/entertainments?region=us".format(self.__entityType, self.__id), headers=getHeaders()).json()

        for entry in data['entries']:
            try:
                ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        return ids

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __eq__(self, other):
        """
        Checks if objects are equal
        """
        return self.__id == other.get_id()

    def __str__(self):
        return 'Park object for {}'.format(self.__name)

# TODO get attraction_ids
