import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .parks import Park
from .pointsofinterest import PointOfInterest
from .database import DisneyDatabase


class Entertainment(object):

    def __init__(self, id = '', sync_on_init=True):
        """
        Constructor Function
        Gets all entertainment data available and stores various elements into variables.
        ID must be a string.
        """

        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/entertainments/{}".format(id), headers=getHeaders()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That entertainment is not available. id: ' + id)

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
        doc_id_query = c.execute("SELECT doc_id from facilities where doc_id LIKE ?", ("%{};entityType={}".format(self.__id, self.__entityType),)).fetchone()
        self.__doc_id = doc_id_query[0] if doc_id_query is not None else None
        self.__facilities_data = self.get_raw_facilities_data()
        # ID: 266858 doesn't have any of this information which causes a problem.
        try:
            self.__anc_dest_id = self.__data['ancestorDestination']['id'].split(';')[0]
            self.__dest_code = c.execute("SELECT destination_code FROM facilities WHERE id = ?", (self.__anc_dest_id,)).fetchone()[0]
        except:
            self.__anc_dest_id = None
            self.__dest_code = None

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



        conn.commit()
        conn.close()

    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        entertainments = []

        dest_data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(self.__anc_dest_id), headers=getHeaders()).json()
        data = requests.get(dest_data['links']['entertainments']['href'], headers=getHeaders()).json()

        for enter in data['entries']:
            try:
                entertainments.append(enter['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        return entertainments

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

    def get_ancestor_destination_id(self):
        """Return object ancestor theme or water park id"""
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

    def get_raw_facilities_data(self):
        """Returns the raw facilities data currently stored in the database"""
        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()
        data = c.execute("SELECT body FROM sync WHERE id = ?", (self.__doc_id,)).fetchone()
        conn.commit()
        conn.close()

        if data is None:
            return None
        else:
            return json.loads(data[0])

    def get_raw_facilitystatus_data(self):
        """Returns the raw facilitystatus data from the database after syncing with Disney (returns most recent data)"""
        if self.__db.channel_exists('{}.facilitystatus.1_0'.format(self.__dest_code)):
            self.__db.sync_facilitystatus_channel()
        else:
            self.__db.create_facilitystatus_channel('{}.facilitystatus.1_0'.format(self.__dest_code))

        conn = sqlite3.connect(self.__db.db_path)
        c = conn.cursor()

        data = c.execute("SELECT body FROM sync WHERE id = ?", ("{}.facilitystatus.1_0.{};entityType=Entertainment".format(self.__dest_code, self.__id),)).fetchone()
        if data is None:
            return None
        else:
            return json.loads(data[0])

    def get_wait_time(self):
        """Return current wait time of the object. Returns None if object doesn't have a wait time or no wait currently exists (eg. closed)"""
        data = self.get_raw_facilitystatus_data()
        if data is None:
            return None
        else:
            return data['waitMinutes']

    def get_status(self):
        """Return current status of the object."""
        data = self.get_raw_facilitystatus_data()
        if data is None:
            return None
        else:
            return data['status']
        # TODO might have to change this from facilitystatus data to scheduleType from today, or test if none from status then get from today instead

    def fastpass_available(self):
        """Returns a boolean of whether this object has FastPass"""
        data = self.get_raw_facilitystatus_data()
        if data is None:
            return False
        else:
            return data['fastPassAvailable'] == 'true'

    def fastpass_times(self):
        """Returns the current start and end time of the FastPass"""
        start_time = None
        end_time = None

        if self.fastpass_available():
            data = self.get_raw_facilitystatus_data()

            start_time = datetime.strptime(data['fastPassStartTime'], "%Y-%m-%dT%H:%M:%SZ")
            end_time = datetime.strptime(data['fastPassEndTime'], "%Y-%m-%dT%H:%M:%SZ")

        return start_time, end_time

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
            try:
                return facility_data['facets']
            except:
                return None

    def admission_required(self):
        """Returns boolean of admission required"""
        return self.__data['admissionRequired']

    def check_associated_characters(self):
        """
        Checks if object has any associated characters
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=getHeaders())
        data = json.loads(s.content)

        if data['total'] > 0:
            return True
        else:
            return False

    def get_number_associated_characters(self):
        """
        Gets the total number of characters associated with this object
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=getHeaders())
        data = json.loads(s.content)

        return data['total']

    def get_associated_characters(self):
        """
        Returns a list of associated characters Character objects
        """
        from .characters import Character
        chars = []

        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=getHeaders())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            try:
                chars.append(Character(data['entries'][i]['links']['self']['href'].split('/')[-1]))
            except:
                pass
        return chars

    def get_associated_characters(self):
        """
        Returns a list of associated characters IDs
        """
        from .characters import Character
        chars = []

        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=getHeaders())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            try:
                chars.append(data['entries'][i]['links']['self']['href'].split('/')[-1])
            except:
                pass

        return chars

    def check_related_locations(self):
        """
        Returns true if it has related locations, false if none
        """
        try:
            check = self.__data['relatedLocations']
            return True
        except:
            return False

    def get_related_locations(self):
        """
        Returns the related locations of the entertainment
        """
        locs = []
        try:
            if self.check_related_locations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1].split('?')[0]

                    if type == 'point-of-interest':
                        locs.append(PointOfInterest(loc_id))
                    else:
                        print('no class for {} at this time'.format(type))
            return locs
        except:
            return locs

    def get_related_location_ids(self):
        """
        Returns the related locations of the entertainment as a tuple (id, type)
        """
        locs = []
        try:
            if self.check_related_locations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1].split('?')[0]

                    locs.append((loc_id, type))

            return locs
        except:
            return locs


    def get_start_date(self):
        """
        Gets the start date of the entertainment and returns it as a datetime object. If there is no start date, returns None
        """
        date = self.__data['startDate']
        if date == "":
            return None

        date = date.split('-')
        return datetime(int(date[0]), int(date[1]), int(date[2]))

    def get_end_date(self):
        """
        Gets the start date of the entertainment and returns it as a datetime object. If there is no start date, returns None.
        """
        date = self.__data['endDate']
        if date == "":
            return None

        date = date.split('-')
        return datetime(int(date[0]), int(date[1]), int(date[2]))

    def get_duration(self):
        """
        Returns the string format of the duration of the entertainment as provided by Disney
        """
        return self.__data['duration']

    def get_duration_minutes(self):
        """
        Returns the duration of the entertainment in minutes as a float
        """
        dur = self.__data['duration'].split(':')
        return float(int(dur[0])*60 + int(dur[1]) + int(dur[2])/60)

    def get_duration_seconds(self):
        """
        Returns the duration of the entertainment in seconds as an integer
        """
        dur = self.__data['duration'].split(':')
        return int(self.get_duration_minutes())*60 + int(dur[2])

    def get_schedule(self, date="", timestamp=False):
        """
        Returns a list of dictionaries for the specified date's schedule in the form of [{start_time, end_time}]
        date = "YYYY-MM-DD"
        If you don't pass a date, it will get today's schedule
        timestamp = False
        Whether to return datetime objects or timestamps
        """

        if date == "":
            DATE = datetime.today()
        else:
            year, month, day = date.split('-')
            DATE = datetime(int(year), int(month), int(day))

        strdate = "{}-{}-{}".format(DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day)))
        data = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}".format(self.__id, strdate), headers=getHeaders()).json()

        schedule = []

        try:
            for entry in data['schedules']:
                if entry['type'] == 'Performance Time':
                    this = {}
                    start_time = datetime.strptime("{} {}".format(entry['date'], entry['startTime']), "%Y-%m-%d %H:%M:%S")
                    end_time = datetime.strptime("{} {}".format(entry['date'], entry['endTime']), "%Y-%m-%d %H:%M:%S")
                    if timestamp:
                        this['start_time'] = start_time.timestamp()
                        this['end_time'] = end_time.timestamp()
                    else:
                        this['start_time'] = start_time
                        this['end_time'] = end_time
                    schedule.append(this)
        except Exception as e:
            # print(e)
            pass

        return schedule


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
        return 'Entertainment object for {}'.format(self.__name)
