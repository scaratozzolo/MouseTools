import requests
import json
from datetime import datetime, timedelta
import pytz
from .auth import get_headers
from .parks import Park
from .pointsofinterest import PointOfInterest
from .ids import themeparkapi_ids, WDW_ID, DLR_ID



class Entertainment(object):

    def __init__(self, id = None):
        """
        Constructor Function
        Gets all entertainment data available and stores various elements into variables.
        """

        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/entertainments/{}".format(id), headers=get_headers()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That entertainment is not available. id: ' + str(id))

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
                    self.__anc_park_id = self.__data['ancestorThemeParkId'].split(';')[0]
                except:
                    try:
                        self.__anc_park_id = self.__data['ancestorWaterParkId'].split(';')[0]
                    except:
                        self.__anc_park_id = None

        try:
            self.__anc_resort_id = self.__data['links']['ancestorResort']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_resort_id = self.__data['ancestorResortId'].split(';')[0]
            except:
                self.__anc_resort_id = None

        try:
            self.__anc_land_id = self.__data['links']['ancestorLand']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_land_id = self.__data['ancestorLandId'].split(';')[0]
            except:
                self.__anc_land_id = None

        try:
            self.__anc_ra_id = self.__data['links']['ancestorResortArea']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ra_id = self.__data['ancestorResortAreaId'].split(';')[0]
            except:
                self.__anc_ra_id = None

        try:
            self.__anc_ev_id = self.__data['links']['ancestorEntertainmentVenue']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ev_id = self.__data['ancestorEntertainmentVenueId'].split(';')[0]
            except:
                self.__anc_ev_id = None
                
        
        if self.__anc_dest_id == WDW_ID:
            self.__time_zone = pytz.timezone('US/Eastern')
        elif self.__anc_dest_id == DLR_ID:
            self.__time_zone = pytz.timezone('US/Pacific')
        else:
            self.__time_zone = pytz.utc



    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        entertainments = []

        dest_data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(self.__anc_dest_id), headers=get_headers()).json()
        data = requests.get(dest_data['links']['entertainments']['href'], headers=get_headers()).json()

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

    def get_time_zone(self):
        """Returns pytz timezone object"""
        return self.__time_zone

    def get_raw_data(self):
        """Returns the raw data from global-facility-service"""
        return self.__data

    def get_themeparkapi_data(self):
        """Returns the dictionary from the themepark api for the given id"""
        park = themeparkapi_ids[self.__anc_park_id]
        themepark_id = f"{park}_{self.__id}"
        all_data = requests.get(f"https://api.themeparks.wiki/preview/parks/{park}/waittime").json()
        for i in all_data:
            if i["id"] == themepark_id:
                return i
        return None

    def get_wait_time(self):
        """Return current wait time of the object. Returns None if object doesn't have a wait time or no wait currently exists (eg. closed)"""
        data = self.get_themeparkapi_data()
        if data is None:
            return None
        else:
            return data['waitTime']

    def get_status(self):
        """Return current status of the object."""
        data = self.get_themeparkapi_data()
        if data is None:
            return None
        else:
            return data['status']

    def fastpass_available(self):
        """Returns a boolean of whether this object has FastPass"""
        data = self.get_themeparkapi_data()
        if data is None:
            return False
        else:
            return data['fastPass']

    def get_last_update_time(self):
        """Returns facilities last update time as a datetime object"""
        facility_data = self.get_themeparkapi_data()
        if facility_data is None:
            return None
        else:
            update_time = datetime.strptime(facility_data['lastUpdate'], "%Y-%m-%dT%H:%M:%S.%fZ")
            update_time = update_time.replace(tzinfo=pytz.utc)
            update_time = update_time.astimezone(self.__time_zone)
            return update_time

    def get_coordinates(self):
        """Returns the object's latitude and longitude"""
        try:
            return self.__data['coordinates']['Guest Entrance']['gps']
        except:
            return None

    def get_description(self):
        """Returns the object's description"""
        facility_data = self.__data
        if facility_data is None:
            return None
        else:
            try:
                return facility_data['descriptions']['shortDescription']['sections']['body']
            except:
                return None

    def get_media(self):
        """Returns a dictionary of dictionaries of media relating to the entity"""
        facility_data = self.__data
        if facility_data is None:
            return None
        else:
            return facility_data['media']

    def get_facets(self):
        """Returns a list of  dictionaries of the object's facets"""
        facility_data = self.get_themeparkapi_data()
        if facility_data is None:
            return None
        else:
            try:
                return facility_data['facets']
            except:
                return None

    def get_classifications(self):
        """Returns a dictionary of lists of classifications related to the entity"""

        classifications = {}

        try:
            for i in self.__data['classifications']:
                id = i['id'].split("/")[-1]
                if id not in classifications:
                    classifications[id] = [i['text']]
                else:
                    classifications[id].append(i['text'])
        except:
            pass

        return classifications

    def admission_required(self):
        """Returns boolean of admission required"""
        return self.__data['admissionRequired']

    def check_associated_characters(self):
        """
        Checks if object has any associated characters
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=get_headers())
        data = json.loads(s.content)

        if data['total'] > 0:
            return True
        else:
            return False

    def get_number_associated_characters(self):
        """
        Gets the total number of characters associated with this object
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=get_headers())
        data = json.loads(s.content)

        return data['total']

    def get_associated_characters(self):
        """
        Returns a list of associated characters Character objects
        """
        from .characters import Character
        chars = []

        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=get_headers())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            try:
                chars.append(Character(data['entries'][i]['links']['self']['href'].split('/')[-1]))
            except:
                pass

        return chars

    def get_associated_character_ids(self):
        """
        Returns a list of associated characters IDs
        """
        chars = []

        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType={}".format(self.__id, self.__entityType), headers=get_headers())
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
        data = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}".format(self.__id, strdate), headers=get_headers()).json()

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
